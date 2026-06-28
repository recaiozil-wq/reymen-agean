#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/mcp_health.py — MCP Health Check.

MCP sunucularının bağlantı testi, config doğrulaması ve timeout kontrolü.
Hem mcp_manager.py (dış MCP sunucuları) hem de mcp_serve.py (ReYMeN'in
kendi MCP sunucusu) için health check sağlar.

Kullanım:
    python -m tools.mcp_health                         # Tüm MCP sunucularını kontrol et
    python -m tools.mcp_health --serve                  # Sadece mcp_serve.py'yi kontrol et
    python -m tools.mcp_health --sunucu github          # Belirli bir sunucuyu kontrol et
    python -m tools.mcp_health --json                   # JSON çıktı
"""

import asyncio
import json
import os
import socket
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# ── Yol sabitleri ──────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent.resolve()
CONFIG_PATH = ROOT / "config.yaml"
SERVE_PATH = ROOT / "mcp_serve.py"
TOOLS_DIR = Path(__file__).parent.resolve()

# ── Loglama (opsiyonel loguru, yoksa logging) ─────────────────────────
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("hermes.mcp_health")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# ═══════════════════════════════════════════════════════════════════════
# TOOL_META — ReYMeN ToolRegistry / Motor uyumu
# ═══════════════════════════════════════════════════════════════════════
TOOL_META = {
    "aciklama": (
        "MCP (Model Context Protocol) sunucularının sağlık kontrolünü yapar. "
        "TOOL_META ile MCP sunucularının bağlantı testi, yapılandırma doğrulaması "
        "ve zaman aşımı kontrolünü gerçekleştirir. mcp_manager.py üzerinden dış "
        "MCP sunucularını ve mcp_serve.py üzerinden ReYMeN'in kendi MCP sunucusunu "
        "kontrol eder."
    ),
    "kategori": "sistem",
    "parametreler": [
        {
            "ad": "sunucu",
            "tip": "str",
            "zorunlu": False,
            "varsayilan": "",
            "aciklama": (
                "Kontrol edilecek MCP sunucu adı. Boş bırakılırsa tüm sunucular "
                "ve mcp_serve.py kontrol edilir."
            ),
        },
        {
            "ad": "timeout",
            "tip": "int",
            "zorunlu": False,
            "varsayilan": 10,
            "aciklama": "Her sunucu için bağlantı zaman aşımı (saniye).",
        },
        {
            "ad": "detayli",
            "tip": "bool",
            "zorunlu": False,
            "varsayilan": False,
            "aciklama": "True ise her sunucu için ayrıntılı (transport, tool sayısı, süre) rapor döndürür.",
        },
    ],
    "ornek": (
        'MCP_SAGLIK()\n'
        'MCP_SAGLIK(sunucu="github", timeout=5, detayli=True)'
    ),
}


# ═══════════════════════════════════════════════════════════════════════
# Veri Modelleri
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class HealthCheckResult:
    """Tek bir bileşenin sağlık kontrol sonucu."""
    ad: str
    durum: str  # "basarili" | "uyari" | "hata" | "yok"
    mesaj: str
    sure_ms: float = 0.0
    detay: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_short_str(self) -> str:
        """Kısa tek satır gösterim."""
        ikon = {"basarili": "✓", "uyari": "⚠", "hata": "✗", "yok": "·"}
        return f"{ikon.get(self.durum, '?')} {self.ad}: {self.mesaj} ({self.sure_ms:.0f}ms)"


@dataclass
class HealthReport:
    """Toplu sağlık kontrol raporu."""
    zaman: str = field(default_factory=lambda: datetime.now().isoformat())
    sunucular: list[HealthCheckResult] = field(default_factory=list)
    config: Optional[HealthCheckResult] = None
    serve: Optional[HealthCheckResult] = None
    ozet: dict[str, int] = field(default_factory=lambda: {"toplam": 0, "basarili": 0, "uyari": 0, "hata": 0, "yok": 0})

    def ekle(self, sonuc: HealthCheckResult) -> None:
        self.sunucular.append(sonuc)
        self.ozet["toplam"] += 1
        self.ozet[sonuc.durum] = self.ozet.get(sonuc.durum, 0) + 1

    @property
    def saglikli_mi(self) -> bool:
        """Tüm kontroller başarılı mı? (config ve serve yoksa da başarılı sayılır)"""
        return self.ozet.get("hata", 0) == 0

    def to_dict(self) -> dict:
        return {
            "zaman": self.zaman,
            "ozet": self.ozet,
            "saglikli_mi": self.saglikli_mi,
            "config": self.config.to_dict() if self.config else None,
            "serve": self.serve.to_dict() if self.serve else None,
            "sunucular": [s.to_dict() for s in self.sunucular],
        }

    def raporla(self, json_cikti: bool = False) -> str:
        """İnsan okunabilir veya JSON rapor üret."""
        if json_cikti:
            return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

        satirlar = [
            "╔══════════════════════════════════════════════╗",
            "║         MCP Health Check Raporu              ║",
            "╚══════════════════════════════════════════════╝",
            f"Zaman: {self.zaman}",
            "",
            "── Config ──",
            f"  {self.config.to_short_str() if self.config else '  · (kontrol edilmedi)'}",
            "",
            "── mcp_serve.py ──",
            f"  {self.serve.to_short_str() if self.serve else '  · (kontrol edilmedi)'}",
            "",
            "── MCP Sunucuları ──",
        ]
        if self.sunucular:
            for s in self.sunucular:
                satirlar.append(f"  {s.to_short_str()}")
            satirlar.append("")
            satirlar.append(f"Özet: {self.ozet['basarili']}/{self.ozet['toplam']} başarılı, "
                           f"{self.ozet['uyari']} uyarı, {self.ozet['hata']} hata")
        else:
            satirlar.append("  (tanımlı sunucu yok)")

        durum_str = "✓ SAĞLIKLI" if self.saglikli_mi else "✗ SORUN VAR"
        satirlar.extend(["", f"GENEL DURUM: {durum_str}"])
        return "\n".join(satirlar)


# ═══════════════════════════════════════════════════════════════════════
# Config Doğrulama
# ═══════════════════════════════════════════════════════════════════════

def config_dogrula() -> HealthCheckResult:
    """config.yaml'daki mcp_servers yapılandırmasını doğrula."""
    basla = time.perf_counter()

    if not CONFIG_PATH.exists():
        sure = (time.perf_counter() - basla) * 1000
        return HealthCheckResult(
            ad="config.yaml",
            durum="yok",
            mesaj=f"Dosya bulunamadı: {CONFIG_PATH}",
            sure_ms=round(sure, 1),
        )

    try:
        import yaml
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
    except Exception as e:
        sure = (time.perf_counter() - basla) * 1000
        return HealthCheckResult(
            ad="config.yaml",
            durum="hata",
            mesaj=f"YAML okuma hatası: {e}",
            sure_ms=round(sure, 1),
        )

    servers = cfg.get("mcp_servers", {})
    sure = (time.perf_counter() - basla) * 1000

    if not isinstance(servers, dict):
        return HealthCheckResult(
            ad="config.yaml",
            durum="hata",
            mesaj="mcp_servers bir dict olmalı",
            sure_ms=round(sure, 1),
        )

    if not servers:
        return HealthCheckResult(
            ad="config.yaml",
            durum="uyari",
            mesaj="mcp_servers boş ({}), sunucu tanımlı değil",
            sure_ms=round(sure, 1),
            detay={"sunucu_sayisi": 0},
        )

    # Her sunucunun yapılandırmasını kontrol et
    hatali = 0
    detay_liste = []
    for ad, srv_cfg in servers.items():
        if not isinstance(srv_cfg, dict):
            hatali += 1
            detay_liste.append({"ad": ad, "durum": "hata", "sorun": "Config bir dict değil"})
            continue

        transport = srv_cfg.get("transport", "tcp")
        sorunlar = []

        if transport == "stdio":
            command = srv_cfg.get("command")
            if not command:
                sorunlar.append("stdio için 'command' gerekli")
            elif isinstance(command, str):
                # Tek string → geçerli ama list olmalı
                sorunlar.append("'command' list formatında olmalı: ['komut', 'arg1']")
        elif transport == "http":
            if not srv_cfg.get("url"):
                sorunlar.append("http için 'url' gerekli")
        elif transport == "tcp":
            port = srv_cfg.get("port", 9100)
            if not isinstance(port, int) or port < 1 or port > 65535:
                sorunlar.append(f"Geçersiz port: {port}")
        else:
            sorunlar.append(f"Bilinmeyen transport: {transport}")

        if transport not in ("stdio", "http", "tcp"):
            sorunlar.append(f"Desteklenmeyen transport tipi: '{transport}'")

        durum = "hata" if sorunlar else "basarili"
        if sorunlar:
            hatali += 1
        detay_liste.append({
            "ad": ad,
            "transport": transport,
            "durum": durum,
            "sorunlar": sorunlar if sorunlar else None,
        })

    genel_durum = "basarili" if hatali == 0 else "hata"
    genel_mesaj = (
        f"{len(servers)} sunucu, {hatali} hatalı"
        if hatali > 0
        else f"{len(servers)} sunucu, tamamı geçerli"
    )

    return HealthCheckResult(
        ad="config.yaml",
        durum=genel_durum,
        mesaj=genel_mesaj,
        sure_ms=round(sure, 1),
        detay={
            "sunucu_sayisi": len(servers),
            "hatali_sayisi": hatali,
            "sunucular": detay_liste,
        },
    )


# ═══════════════════════════════════════════════════════════════════════
# mcp_serve.py Sağlık Kontrolü
# ═══════════════════════════════════════════════════════════════════════

def serve_saglik_kontrol(timeout: int = 10) -> HealthCheckResult:
    """mcp_serve.py dosyasının varlığını ve çalıştırılabilirliğini kontrol et.

    mcp_serve.py'yi bir alt süreç olarak başlatır, initialize + ping
    istekleri göndererek yanıt verdiğini doğrular.
    """
    basla = time.perf_counter()

    # Dosya kontrolü
    if not SERVE_PATH.exists():
        sure = (time.perf_counter() - basla) * 1000
        return HealthCheckResult(
            ad="mcp_serve.py",
            durum="yok",
            mesaj=f"Dosya bulunamadı: {SERVE_PATH}",
            sure_ms=round(sure, 1),
        )

    # Python syntax kontrolü
    try:
        compile(SERVE_PATH.read_text(encoding="utf-8"), str(SERVE_PATH), "exec")
    except SyntaxError as e:
        sure = (time.perf_counter() - basla) * 1000
        return HealthCheckResult(
            ad="mcp_serve.py",
            durum="hata",
            mesaj=f"Python syntax hatası: {e}",
            sure_ms=round(sure, 1),
            detay={"syntax_hata": str(e)},
        )

    # mcp_serve.py'yi çalıştır ve initialize + ping gönder
    try:
        proc = subprocess.Popen(
            [sys.executable, str(SERVE_PATH)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(ROOT),
            text=True,
        )

        # Initialize isteği
        init_req = json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "initialize"
        }) + "\n"

        try:
            stdout, stderr = proc.communicate(input=init_req, timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate(timeout=2)
            sure = (time.perf_counter() - basla) * 1000
            return HealthCheckResult(
                ad="mcp_serve.py",
                durum="hata",
                mesaj=f"Zaman aşımı ({timeout}s): initialize yanıt vermedi",
                sure_ms=round(sure, 1),
            )

        sure = (time.perf_counter() - basla) * 1000

        # Yanıtı parse et
        try:
            yanit = json.loads(stdout.strip())
        except json.JSONDecodeError:
            stderr_ilk = stderr[:500] if stderr else "(yok)"
            return HealthCheckResult(
                ad="mcp_serve.py",
                durum="hata",
                mesaj=f"Geçersiz JSON yanıtı. stderr: {stderr_ilk}",
                sure_ms=round(sure, 1),
                detay={"stdout": stdout[:500], "stderr": stderr_ilk},
            )

        # initialize başarılı mı?
        if "error" in yanit:
            return HealthCheckResult(
                ad="mcp_serve.py",
                durum="hata",
                mesaj=f"initialize hatası: {yanit['error'].get('message', 'bilinmeyen')}",
                sure_ms=round(sure, 1),
                detay={"hata": yanit["error"]},
            )

        # tools/list ile yetenekleri kontrol et
        tools_req = json.dumps({
            "jsonrpc": "2.0", "id": 2, "method": "tools/list"
        }) + "\n"

        try:
            proc2 = subprocess.Popen(
                [sys.executable, str(SERVE_PATH)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(ROOT),
                text=True,
            )
            stdout2, stderr2 = proc2.communicate(input=tools_req, timeout=timeout)
        except subprocess.TimeoutExpired:
            proc2.kill()
            proc2.communicate(timeout=2)
            # initialize başarılıydı en azından
            return HealthCheckResult(
                ad="mcp_serve.py",
                durum="uyari",
                mesaj="initialize OK ama tools/list zaman aşımı",
                sure_ms=round(sure, 1),
            )

        try:
            tools_yanit = json.loads(stdout2.strip())
        except json.JSONDecodeError:
            return HealthCheckResult(
                ad="mcp_serve.py",
                durum="uyari",
                mesaj="initialize OK ama tools/list yanıtı JSON değil",
                sure_ms=round(sure, 1),
            )

        if "error" in tools_yanit:
            return HealthCheckResult(
                ad="mcp_serve.py",
                durum="uyari",
                mesaj=f"initialize OK ama tools/list hatası: {tools_yanit['error'].get('message', '?')}",
                sure_ms=round(sure, 1),
            )

        tool_listesi = tools_yanit.get("result", {}).get("tools", [])
        tool_isimleri = [t.get("name", "?") for t in tool_listesi]

        return HealthCheckResult(
            ad="mcp_serve.py",
            durum="basarili",
            mesaj=f"Çalışıyor, {len(tool_listesi)} tool: {', '.join(tool_isimleri[:5])}"
                   + ("..." if len(tool_isimleri) > 5 else ""),
            sure_ms=round(sure, 1),
            detay={
                "tool_sayisi": len(tool_listesi),
                "tool_isimleri": tool_isimleri,
                "protocol_version": yanit.get("result", {}).get("protocolVersion", "?"),
                "server_info": yanit.get("result", {}).get("serverInfo", {}),
            },
        )

    except FileNotFoundError:
        sure = (time.perf_counter() - basla) * 1000
        return HealthCheckResult(
            ad="mcp_serve.py",
            durum="hata",
            mesaj=f"Python yorumlayıcısı bulunamadı: {sys.executable}",
            sure_ms=round(sure, 1),
        )
    except Exception as e:
        sure = (time.perf_counter() - basla) * 1000
        return HealthCheckResult(
            ad="mcp_serve.py",
            durum="hata",
            mesaj=str(e),
            sure_ms=round(sure, 1),
            detay={"hata_tipi": type(e).__name__},
        )


# ═══════════════════════════════════════════════════════════════════════
# MCP Sunucu Bağlantı Testi (mcp_manager.py üzerinden)
# ═══════════════════════════════════════════════════════════════════════

async def _test_sunucu_baglantisi(
    ad: str, cfg: dict, timeout: int
) -> HealthCheckResult:
    """Tek bir MCP sunucusuna bağlan ve tools/list çağır."""
    from tools.mcp_manager import MCPServerBaglantisi

    basla = time.perf_counter()
    baglanti = MCPServerBaglantisi(ad, cfg)

    try:
        tool_sayisi = await baglanti.tools_kesfet()
        sure = (time.perf_counter() - basla) * 1000

        if tool_sayisi == 0 and not baglanti.baglandi:
            return HealthCheckResult(
                ad=ad,
                durum="hata",
                mesaj="Bağlantı başarısız (tools/list yanıt vermedi)",
                sure_ms=round(sure, 1),
                detay={
                    "transport": cfg.get("transport", "tcp"),
                    "config": _cfg_ozet(cfg),
                },
            )

        durum = "basarili" if tool_sayisi > 0 else "uyari"
        mesaj = (
            f"{tool_sayisi} tool keşfedildi"
            if tool_sayisi > 0
            else "Bağlandı ama tool bulunamadı"
        )

        return HealthCheckResult(
            ad=ad,
            durum=durum,
            mesaj=mesaj,
            sure_ms=round(sure, 1),
            detay={
                "transport": cfg.get("transport", "tcp"),
                "tool_sayisi": tool_sayisi,
                "baglandi": baglanti.baglandi,
                "config": _cfg_ozet(cfg),
            },
        )

    except asyncio.TimeoutError:
        sure = (time.perf_counter() - basla) * 1000
        return HealthCheckResult(
            ad=ad,
            durum="hata",
            mesaj=f"Zaman aşımı ({timeout}s)",
            sure_ms=round(sure, 1),
            detay={"transport": cfg.get("transport", "tcp"), "timeout": timeout},
        )
    except Exception as e:
        sure = (time.perf_counter() - basla) * 1000
        return HealthCheckResult(
            ad=ad,
            durum="hata",
            mesaj=str(e),
            sure_ms=round(sure, 1),
            detay={
                "transport": cfg.get("transport", "tcp"),
                "hata_tipi": type(e).__name__,
            },
        )


async def _tum_sunuculari_test_et(
    servers_cfg: dict, timeout: int
) -> list[HealthCheckResult]:
    """Tüm MCP sunucularını paralel test et."""
    import asyncio

    tasks = [
        _test_sunucu_baglantisi(ad, cfg, timeout)
        for ad, cfg in servers_cfg.items()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    sonuclar = []
    for result in results:
        if isinstance(result, Exception):
            sonuclar.append(HealthCheckResult(
                ad="(bilinmeyen)",
                durum="hata",
                mesaj=f"Beklenmeyen hata: {result}",
            ))
        else:
            sonuclar.append(result)

    return sonuclar


# ═══════════════════════════════════════════════════════════════════════
# Zaman Aşımı Kontrolü
# ═══════════════════════════════════════════════════════════════════════

def timeout_kontrol(timeout: int = 5) -> HealthCheckResult:
    """Transport timeout değerlerinin geçerliliğini kontrol et.

    Her transport tipinin varsayılan timeout'larını ve config'de
    tanımlanan timeout değerlerini doğrular.
    """
    basla = time.perf_counter()

    # Varsayılan timeout standartları
    transport_timeouts = {
        "stdio": {"varsayilan": 30, "min": 5, "max": 120, "birim": "saniye"},
        "http": {"varsayilan": 15, "min": 3, "max": 60, "birim": "saniye"},
        "tcp": {"varsayilan": 10, "min": 2, "max": 30, "birim": "saniye"},
    }

    # Config'deki değerleri kontrol et
    import yaml
    servers = {}
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            servers = cfg.get("mcp_servers", {}) or {}
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")

    sorunlar = []
    for ad, srv_cfg in servers.items():
        if not isinstance(srv_cfg, dict):
            continue
        transport = srv_cfg.get("transport", "tcp")
        t_timeout = srv_cfg.get("timeout", transport_timeouts.get(transport, {}).get("varsayilan"))
        ref = transport_timeouts.get(transport, {})
        if ref:
            if isinstance(t_timeout, (int, float)):
                if t_timeout < ref["min"]:
                    sorunlar.append(f"{ad}: timeout {t_timeout}s < min {ref['min']}s ({transport})")
                elif t_timeout > ref["max"]:
                    sorunlar.append(f"{ad}: timeout {t_timeout}s > max {ref['max']}s ({transport})")

    sure = (time.perf_counter() - basla) * 1000
    ek_detay = {
        "standartlar": transport_timeouts,
        "test_timeout": timeout,
    }

    if sorunlar:
        return HealthCheckResult(
            ad="Timeout Kontrolü",
            durum="uyari",
            mesaj=f"{len(sorunlar)} sunucuda timeout uyarısı",
            sure_ms=round(sure, 1),
            detay={**ek_detay, "sorunlar": sorunlar},
        )

    return HealthCheckResult(
        ad="Timeout Kontrolü",
        durum="basarili",
        mesaj="Tüm timeout değerleri geçerli aralıkta",
        sure_ms=round(sure, 1),
        detay=ek_detay,
    )


# ═══════════════════════════════════════════════════════════════════════
# Yardımcılar
# ═══════════════════════════════════════════════════════════════════════

def _cfg_ozet(cfg: dict) -> dict:
    """Config dict'inin güvenli özetini çıkar (hassas bilgileri gizle)."""
    ozet = {}
    for k, v in cfg.items():
        if k in ("api_key", "token", "password", "secret"):
            ozet[k] = "***" if v else None
        elif isinstance(v, (str, int, float, bool)):
            ozet[k] = v
        elif isinstance(v, list):
            ozet[k] = [str(x)[:30] for x in v]
        else:
            ozet[k] = str(type(v).__name__)
    return ozet


def _config_yukle() -> dict:
    """config.yaml'dan mcp_servers anahtarını oku."""
    import yaml
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            return cfg.get("mcp_servers", {}) or {}
    except Exception as e:
        logger.warning(f"Config yükleme hatası: {e}")
    return {}


def _config_uyumluluk_sagla(servers: dict) -> dict:
    """Eski format (command str + args list) → yeni format (command list) dönüşümü."""
    for ad, cfg in servers.items():
        if isinstance(cfg, dict):
            if isinstance(cfg.get("command"), str) and "args" in cfg:
                cfg["command"] = [cfg["command"]] + cfg.get("args", [])
                cfg.pop("args", None)
            cfg.setdefault("transport", "stdio")
    return servers


# ═══════════════════════════════════════════════════════════════════════
# Ana Health Check Fonksiyonu
# ═══════════════════════════════════════════════════════════════════════

async def health_check(
    sunucu_adi: str = "",
    test_timeout: int = 10,
    detayli: bool = False,
) -> HealthReport:
    """Tam MCP health check çalıştır.

    Args:
        sunucu_adi: Sadece belirli bir sunucuyu kontrol et (boş = tümü).
        test_timeout: Bağlantı zaman aşımı saniye.
        detayli: Ayrıntılı detay ekle.

    Returns:
        HealthReport objesi.
    """
    import asyncio

    rapor = HealthReport()

    # 1. Config doğrulama
    config_sonuc = config_dogrula()
    rapor.config = config_sonuc
    if config_sonuc.durum == "hata":
        # Config yoksa veya bozuksa sunucu testi yapamayız
        rapor.serve = serve_saglik_kontrol(timeout=test_timeout)
        return rapor

    # 2. Sunucu bağlantı testleri
    servers = _config_yukle()
    servers = _config_uyumluluk_sagla(servers)

    if sunucu_adi:
        # Belirli bir sunucu
        if sunucu_adi in servers:
            sonuc = await _test_sunucu_baglantisi(
                sunucu_adi, servers[sunucu_adi], test_timeout
            )
            rapor.ekle(sonuc)
        else:
            rapor.ekle(HealthCheckResult(
                ad=sunucu_adi,
                durum="hata",
                mesaj=f"Sunucu '{sunucu_adi}' config'de tanımlı değil",
            ))
    else:
        # Tüm sunucular
        if servers:
            sonuclar = await _tum_sunuculari_test_et(servers, test_timeout)
            for s in sonuclar:
                rapor.ekle(s)
        else:
            logger.info("MCP sunucusu tanımlı değil, atlanıyor.")

    # 3. mcp_serve.py sağlık kontrolü
    rapor.serve = serve_saglik_kontrol(timeout=test_timeout)

    return rapor


# ═══════════════════════════════════════════════════════════════════════
# ToolRegistry / Motor uyumlu çağrılabilir fonksiyon
# ═══════════════════════════════════════════════════════════════════════

def run(
    sunucu: str = "",
    timeout: int = 10,
    detayli: bool = False,
) -> dict:
    """ReYMeN Motor / ToolRegistry uyumlu health check fonksiyonu.

    Kullanım:
        MCP_SAGLIK()
        MCP_SAGLIK(sunucu="github", timeout=5)
        MCP_SAGLIK(detayli=True)

    Returns:
        dict: Health check sonuçları.
    """
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        rapor = loop.run_until_complete(
            health_check(sunucu_adi=sunucu, test_timeout=timeout, detayli=detayli)
        )
        return rapor.to_dict()
    except Exception as e:
        logger.error(f"Health check hatası: {e}")
        return {
            "durum": "hata",
            "hata": str(e),
        }
    finally:
        loop.close()


# ═══════════════════════════════════════════════════════════════════════
# CLI Giriş Noktası
# ═══════════════════════════════════════════════════════════════════════

def main():
    """CLI'den çalıştırma."""
    import argparse

    parser = argparse.ArgumentParser(
        description="MCP Health Check — Sunucu bağlantı, config ve timeout testi",
    )
    parser.add_argument(
        "--sunucu", "-s", default="",
        help="Kontrol edilecek sunucu adı (boş = tümü)",
    )
    parser.add_argument(
        "--timeout", "-t", type=int, default=10,
        help="Bağlantı zaman aşımı saniye (varsayılan: 10)",
    )
    parser.add_argument(
        "--json", "-j", action="store_true",
        help="JSON formatında çıktı",
    )
    parser.add_argument(
        "--serve", action="store_true",
        help="Sadece mcp_serve.py'yi kontrol et",
    )
    parser.add_argument(
        "--config", action="store_true",
        help="Sadece config doğrulaması yap",
    )
    parser.add_argument(
        "--timeout-kontrol", action="store_true",
        help="Sadece timeout değerlerini kontrol et",
    )
    parser.add_argument(
        "--detayli", "-d", action="store_true",
        help="Ayrıntılı rapor",
    )

    args = parser.parse_args()

    if args.timeout_kontrol:
        sonuc = timeout_kontrol(timeout=args.timeout)
        if args.json:
            print(json.dumps(sonuc.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(sonuc.to_short_str())
        return

    if args.config:
        sonuc = config_dogrula()
        if args.json:
            print(json.dumps(sonuc.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"Config: {sonuc.to_short_str()}")
            if sonuc.detay.get("sunucular"):
                for s in sonuc.detay["sunucular"]:
                    print(f"  {s['ad']} ({s['transport']}): {s['durum']}")
                    if s.get("sorunlar"):
                        for sorun in s["sorunlar"]:
                            print(f"    ✗ {sorun}")
        return

    if args.serve:
        sonuc = serve_saglik_kontrol(timeout=args.timeout)
        if args.json:
            print(json.dumps(sonuc.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(sonuc.to_short_str())
            if args.detayli and sonuc.detay:
                for k, v in sonuc.detay.items():
                    print(f"  {k}: {v}")
        return

    # Tam health check
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        rapor = loop.run_until_complete(
            health_check(
                sunucu_adi=args.sunucu,
                test_timeout=args.timeout,
                detayli=args.detayli,
            )
        )
        print(rapor.raporla(json_cikti=args.json))
    finally:
        loop.close()


if __name__ == "__main__":
    main()
