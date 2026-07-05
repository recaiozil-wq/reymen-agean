# -*- coding: utf-8 -*-
"""
broker.py â€” MessageBroker: queue.Queue tabanlÄ±, thread-safe mesajlaÅŸma katmanÄ±.

Mevcut threading yapÄ±sÄ±na %90 uyumlu:
  - ThreadPoolExecutor (8 worker) â†’ consumer pool
  - threading.Thread (daemon=True) â†’ background consumer
  - threading.local() â†’ correlation ID tracing
  - asyncio GEREKSÄ°Z, ThreadPoolExecutor yeterli

KullanÄ±m:
    broker = MessageBroker(max_workers=4)
    broker.abone_ol(MesajTipi.HATA, hata_handler)
    broker.baslat()  # background thread'de baÅŸlar
    broker.yayinla(Mesaj(MesajTipi.HATA, {"hata": "test"}))
    broker.durdur()
"""

from __future__ import annotations

import json
import logging
import queue
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


# â”€â”€ Mesaj Tipleri â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class MesajTipi(Enum):
    """Sistemdeki tüm mesaj tipleri. Her tip bir consumer queue'suna karÅŸÄ±lÄ±k gelir."""

    # Ã‡özüm döngüsü
    HATA = auto()  # hata_cozucu'ya: hata yakalandÄ±, çözüm üret
    COZUM_ARA = auto()  # ogrenme'ye: çözüm hafÄ±zasÄ±nda ara
    COZUM_BULUNDU = auto()  # orchestrator'a: çözüm bulundu, uygula
    COZUM_KAYDET = auto()  # ogrenme'ye: baÅŸarÄ±lÄ± çözümü kaydet
    BECERI_KRISTAL = auto()  # closed_learning_loop'a: skill kartÄ± oluÅŸtur

    # Workflow pipeline
    GOREV_BASLAT = auto()  # motor'a: yeni görev baÅŸlat
    GOREV_PLANLA = auto()  # planlayÄ±cÄ±ya: görevi alt adÄ±mlara böl
    GOREV_DOGRULA = auto()  # doÄŸrulayÄ±cÄ±ya: ön koÅŸullarÄ± kontrol et
    GOREV_KOD = auto()  # kodlayÄ±cÄ±ya: Python script'i üret
    GOREV_TEST = auto()  # testçiye: script'i çalÄ±ÅŸtÄ±r/doÄŸrula
    GOREV_INCELE = auto()  # inceleyiciye: kodu gözden geçir
    GOREV_KAYDET = auto()  # kaydediciye: .py dosyasÄ±na yaz
    GOREV_BASARILI = auto()  # orchestrator'a: görev tamam
    GOREV_HATA = auto()  # orchestrator'a: görev baÅŸarÄ±sÄ±z

    # Tool çaÄŸrÄ±larÄ±
    TOOL_CALL = auto()  # conversation_loop'a: tool çaÄŸrÄ±sÄ± hazÄ±r
    TOOL_SONUC = auto()  # conversation_loop'a: tool sonucu döndü

    # Kontrol
    DURDUR = auto()  # broker'Ä± kapat


@dataclass
class Mesaj:
    """Thread-safe mesaj veri yapÄ±sÄ±."""

    tip: MesajTipi
    veri: dict = field(default_factory=dict)
    kaynak: str = ""
    correlation_id: str = ""
    timestamp: float = field(default_factory=time.time)

    def __repr__(self) -> str:
        return f"Mesaj({self.tip.name}, corr={self.correlation_id[:8]}, kaynak={self.kaynak})"


# â”€â”€ Mesaj KuyruÄŸu (thread-safe) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class MesajKuyrugu:
    """Her consumer için ayrÄ± queue + abone yönetimi."""

    def __init__(self, tip: MesajTipi):
        self.tip = tip
        self.kuyruk: queue.Queue[Mesaj] = queue.Queue()
        self.aboneler: list[Callable[[Mesaj], None]] = []

    def abone_ekle(self, callback: Callable[[Mesaj], None]):
        self.aboneler.append(callback)

    def mesaj_at(self, mesaj: Mesaj):
        self.kuyruk.put_nowait(mesaj)

    def mesaj_al(self, timeout: float = 1.0) -> Optional[Mesaj]:
        try:
            return self.kuyruk.get(timeout=timeout)
        except queue.Empty:
            return None

    def abone_sayisi(self) -> int:
        return len(self.aboneler)


# â”€â”€ Message Broker â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class MessageBroker:
    """
    Merkezi mesajlaÅŸma katmanÄ±.

    - Her MesajTipi için ayrÄ± queue
    - ThreadPoolExecutor consumer pool
    - Abonelik bazlÄ± routing
    - Otomatik correlation ID
    """

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._kuyruklar: dict[MesajTipi, MesajKuyrugu] = {}
        self._running = False
        self._threads: list[threading.Thread] = []
        self._executor: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Tüm mesaj tipleri için queue oluÅŸtur
        for tip in MesajTipi:
            self._kuyruklar[tip] = MesajKuyrugu(tip)

    # â”€â”€ Abone Yönetimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def abone_ol(self, tip: MesajTipi, callback: Callable[[Mesaj], None]) -> None:
        """Bir mesaj tipine abone ol. Callback consumer thread'de çalÄ±ÅŸÄ±r."""
        kuyruk = self._kuyruklar.get(tip)
        if kuyruk:
            kuyruk.abone_ekle(callback)

    def abone_ol_liste(self, abonelikler: list[tuple[MesajTipi, Callable]]) -> None:
        """Toplu abonelik."""
        for tip, cb in abonelikler:
            self.abone_ol(tip, cb)

    # â”€â”€ Mesaj Gönderme â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def yayinla(self, mesaj: Mesaj) -> None:
        """Bir mesajÄ± ilgili queue'suna gönder."""
        if not self._running:
            logger.warning("[Broker] Ã‡alÄ±ÅŸmÄ±yor, mesaj atÄ±ldÄ±: %s", mesaj)
            return
        kuyruk = self._kuyruklar.get(mesaj.tip)
        if kuyruk:
            mesaj.correlation_id = mesaj.correlation_id or uuid.uuid4().hex[:12]
            kuyruk.mesaj_at(mesaj)

    def yayinla_basit(self, tip: MesajTipi, veri: dict, kaynak: str = "") -> None:
        """HÄ±zlÄ± mesaj gönderme (Mesaj nesnesi oluÅŸturmadan)."""
        mesaj = Mesaj(tip=tip, veri=veri, kaynak=kaynak)
        self.yayinla(mesaj)

    # â”€â”€ Consumer Thread â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _consumer_loop(self, kuyruk: MesajKuyrugu) -> None:
        """Tek bir queue için consumer thread döngüsü."""
        thread_name = threading.current_thread().name
        logger.debug(
            "[Broker] Consumer baÅŸladÄ±: %s <- %s", thread_name, kuyruk.tip.name
        )

        while self._running:
            mesaj = kuyruk.mesaj_al(timeout=0.5)
            if mesaj is None:
                continue
            if mesaj.tip == MesajTipi.DURDUR:
                break

            # Abonelere daÄŸÄ±t
            for abone in kuyruk.aboneler:
                try:
                    abone(mesaj)
                except Exception as e:
                    logger.error("[Broker] Abone hatasÄ± (%s): %s", kuyruk.tip.name, e)

        logger.debug("[Broker] Consumer durdu: %s", thread_name)

    # â”€â”€ BaÅŸlat / Durdur â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def baslat(self) -> None:
        """
        Her mesaj tipi için bir consumer thread baÅŸlatÄ±r.
        Thread'ler daemon=True olduÄŸu için ana thread bitince otomatik kapanÄ±r.
        """
        if self._running:
            return
        self._running = True

        for tip, kuyruk in self._kuyruklar.items():
            if kuyruk.abone_sayisi() > 0 or tip in (MesajTipi.DURDUR,):
                t = threading.Thread(
                    target=self._consumer_loop,
                    args=(kuyruk,),
                    name=f"broker-{tip.name.lower()}",
                    daemon=True,
                )
                t.start()
                self._threads.append(t)

        logger.info("[Broker] %d consumer thread baÅŸlatÄ±ldÄ±", len(self._threads))

    def durdur(self) -> None:
        """Tüm consumer thread'leri durdur."""
        self._running = False
        # DURDUR mesajÄ± göndererek bekleyen thread'leri uyandÄ±r
        for kuyruk in self._kuyruklar.values():
            kuyruk.mesaj_at(Mesaj(MesajTipi.DURDUR, kaynak="broker"))
        logger.info("[Broker] Durduruldu")

    # â”€â”€ Durum â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def durum(self) -> dict:
        """Broker durum raporu."""
        return {
            "running": self._running,
            "threads": len(self._threads),
            "kuyruklar": {
                tip.name: {
                    "abone": kuyruk.abone_sayisi(),
                    "boyut": kuyruk.kuyruk.qsize(),
                }
                for tip, kuyruk in self._kuyruklar.items()
                if kuyruk.abone_sayisi() > 0 or kuyruk.kuyruk.qsize() > 0
            },
        }


# â”€â”€ YardÄ±mcÄ± Fonksiyonlar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def mesaj_gonder(
    broker: Optional[MessageBroker], tip: MesajTipi, veri: dict, kaynak: str = ""
) -> None:
    """Broker varsa mesaj gönder, yoksa sessiz geç."""
    if broker:
        broker.yayinla(Mesaj(tip=tip, veri=veri, kaynak=kaynak or __name__))


# â”€â”€ Singleton â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_broker_instance: Optional[MessageBroker] = None
_broker_lock = threading.Lock()


def get_broker(max_workers: int = 4) -> MessageBroker:
    """Tekil broker instance'Ä± (thread-safe)."""
    global _broker_instance
    if _broker_instance is None:
        with _broker_lock:
            if _broker_instance is None:
                _broker_instance = MessageBroker(max_workers=max_workers)
    return _broker_instance
