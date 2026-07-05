# -*- coding: utf-8 -*-
"""
reymen_agent.py â€” ReYMeN ana agent modülü.
DeepSoek API, agent orchestrator, beceri baÄŸlamÄ± ve format temizleme.
"""

import json
import logging
import os
import sys
import traceback
from typing import Any, Optional

import requests


# â”€â”€ Global state â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_agent = None
_logger = None

# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"
MAX_YANIT_UZUNLUK = 4000
MAX_BECERI_UZUNLUK = 1500
MAX_MESAJ_UZUNLUK = 500


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# _get_logger
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _get_logger(name: str = "reymen_agent") -> logging.Logger:
    """Singleton logger oluÅŸturur/döndürür."""
    global _logger
    if _logger is None:
        _logger = logging.getLogger(name)
        if not _logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            )
            handler.setFormatter(formatter)
            _logger.addHandler(handler)
            _logger.setLevel(logging.INFO)
    return _logger


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# _agent_instance
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _agent_instance(config: Optional[dict] = None) -> Any:
    """Agent singleton â€” AIAgentOrchestrator instance'Ä± döndürür."""
    global _agent
    if _agent is not None:
        return _agent
    try:
        from main import AIAgentOrchestrator

        _agent = AIAgentOrchestrator()
        return _agent
    except Exception as e:
        _get_logger().error(f"Agent baslatilamadi: {e}")
        return None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# _beceri_baglami_al
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _beceri_baglami_al(hedef: str) -> str:
    """closed_learning_loop._beceri_ara üzerinden beceri baÄŸlamÄ± alÄ±r."""
    try:
        from closed_learning_loop import _beceri_ara

        # MesajÄ± 500 karaktere kÄ±salt
        sorgu = hedef[:MAX_MESAJ_UZUNLUK] if hedef else ""

        sonuc = _beceri_ara(sorgu)

        # Beceri bulunamadi / toplam kontrolü
        if not sonuc or "beceri bulunamadi" in sonuc.lower():
            return ""
        if "toplam" in sonuc.lower():
            return ""

        # Uzun metni kÄ±salt
        if len(sonuc) > MAX_BECERI_UZUNLUK:
            sonuc = sonuc[:MAX_BECERI_UZUNLUK] + "..."

        return f"\n\n## Ä°LGÄ°LÄ° BECERÄ°LER:\n{sonuc}\n"
    except Exception:
        return ""


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# _deepseek_sohbet
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _deepseek_sohbet(messages: Any, config: Optional[dict] = None) -> str:
    """DeepSeek API'ye sohbet isteÄŸi gönderir."""
    logger = _get_logger()

    # API anahtarÄ± kontrolü
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        logger.warning("DeepSeek API anahtarÄ± bulunamadÄ±")
        return "API anahtarÄ± bulunamadÄ±"

    # MesajÄ± string'den listeye çevir
    if isinstance(messages, str):
        user_message = messages
    elif isinstance(messages, list):
        # EÄŸer messages bir liste ise son user mesajÄ±nÄ± bul
        user_texts = [
            m["content"]
            for m in messages
            if isinstance(m, dict) and m.get("role") == "user"
        ]
        user_message = user_texts[-1] if user_texts else str(messages)
    else:
        user_message = str(messages)

    # Beceri baÄŸlamÄ±nÄ± al
    beceri_baglama = _beceri_baglami_al(user_message)

    # System mesajÄ± oluÅŸtur
    system_content = (
        "Sen yardÄ±msever bir ReYMeN asistansÄ±n. "
        "KullanÄ±cÄ±ya net ve doÄŸrudan yanÄ±tlar ver."
    )
    if beceri_baglama:
        system_content += beceri_baglama

    # API isteÄŸi
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message},
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        logger.info("DeepSeek API çaÄŸrÄ±sÄ± yapÄ±lÄ±yor...")
        resp = requests.post(
            DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        yanit = data["choices"][0]["message"]["content"]
        logger.info("DeepSeek API yanÄ±tÄ± baÅŸarÄ±lÄ±")
        return yanit
    except Exception as e:
        logger.error(f"DeepSeek API hatasÄ±: {e}")
        return f"API hatasÄ±: {e}"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# _agent_loop
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _agent_loop(hedef: str, config: Optional[dict] = None) -> str:
    """Agent loop â€” orchestrator üzerinden konuÅŸma çalÄ±ÅŸtÄ±rÄ±r."""
    logger = _get_logger()
    logger.info(f"Agent loop baÅŸlatÄ±lÄ±yor: {hedef[:50]}...")

    try:
        agent = _agent_instance(config)
        if agent is None:
            logger.warning("Agent yok, fallback kullanÄ±lÄ±yor")
            return _deepseek_fallback(hedef)

        # Agent ile konuÅŸmayÄ± çalÄ±ÅŸtÄ±r
        agent.run_conversation(hedef)

        # YanÄ±tÄ± conversation_history'den al
        yanit = None
        if hasattr(agent, "conversation_history") and agent.conversation_history:
            for msg in reversed(agent.conversation_history):
                if isinstance(msg, dict) and msg.get("role") == "assistant":
                    yanit = msg.get("content", "")
                    break

        # Fallback: last_response
        if not yanit and hasattr(agent, "last_response") and agent.last_response:
            yanit = agent.last_response

        # Fallback: _yanit_ayikla
        if not yanit:
            raw = str(getattr(agent, "conversation_history", ""))
            yanit = _yanit_ayikla(raw)

        # 4000 karakter sÄ±nÄ±rÄ±
        if yanit and len(yanit) > MAX_YANIT_UZUNLUK:
            yanit = yanit[:MAX_YANIT_UZUNLUK]

        return yanit or ""
    except Exception as e:
        logger.error(f"Agent loop hatasÄ±: {e}")
        return _deepseek_fallback(str(e))


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# _yanit_ayikla
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _yanit_ayikla(raw: str) -> str:
    """Ham çÄ±ktÄ±dan yanÄ±t metnini ayÄ±klar."""
    if not raw:
        return ""

    satirlar = raw.split("\n")

    # Markör öncelik sÄ±rasÄ± (en yüksek â†’ düÅŸük)
    markorler = [
        ("[TAMAMLANDI]", 3),
        ("[SONUC]", 2),
        ("[YANIT]", 1),
    ]

    for markor, oncelik in markorler:
        for satir in satirlar:
            if markor in satir:
                icerik = satir.split(markor, 1)[1].strip()
                if len(icerik) >= 3:
                    return icerik

    # Markör bulunamadÄ± â€” son 5 satÄ±rdan en uzun içerikli satÄ±r
    son_satirlar = satirlar[-5:]

    # Filtrele: kÄ±sa/kalÄ±p satÄ±rlarÄ± atla
    filtrelenmis = []
    for satir in son_satirlar:
        satir_stripped = satir.strip()
        if not satir_stripped:
            continue
        if satir_stripped == "---":
            continue
        if satir_stripped == "===":
            continue
        if "[Budget]" in satir_stripped or "[Bütçe]" in satir_stripped:
            continue
        if "--- TUR" in satir_stripped:
            continue
        filtrelenmis.append(satir_stripped)

    if not filtrelenmis:
        # Hepsi filtrelendiyse son satÄ±rÄ± al
        return son_satirlar[-1].strip() if son_satirlar else ""

    # En uzun içerikli satÄ±rÄ± seç
    return max(filtrelenmis, key=len)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# _deepseek_fallback
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _deepseek_fallback(
    error: str, messages: Any = None, config: Optional[dict] = None
) -> str:
    """Fallback â€” agent baÅŸarÄ±sÄ±z olursa direkt DeepSeek API çaÄŸrÄ±sÄ±."""
    logger = _get_logger()
    logger.warning(f"Fallback kullanÄ±lÄ±yor: {error}")

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return "API anahtarÄ± bulunamadÄ±"

    # KullanÄ±lacak mesaj
    if messages is None:
        mesaj = f"Hata oluÅŸtu: {error}. Lütfen kullanÄ±cÄ±ya yardÄ±mcÄ± ol."
    elif isinstance(messages, str):
        mesaj = messages
    else:
        mesaj = str(messages)

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Sen bir fallback asistansÄ±n. Ana sistem hatasÄ± nedeniyle "
                    "devreye girdin. KullanÄ±cÄ±ya yardÄ±mcÄ± ol."
                ),
            },
            {"role": "user", "content": mesaj},
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Fallback API hatasÄ±: {e}")
        return f"API hatasÄ±: {e}"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# _format_temizle
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _format_temizle(text: str) -> str:
    """Metin formatÄ±nÄ± temizler â€” backtick ve kod bloklarÄ±nÄ± düzeltir."""
    if not text:
        return text

    # Kod bloÄŸu içinde olup olmadÄ±ÄŸÄ±mÄ±zÄ± takip et
    def _kod_ici_indexler(satirlar):
        """Kod bloÄŸu içindeki satÄ±rlarÄ±n index setini döndürür."""
        kod_ici = set()
        acik = False
        for i, satir in enumerate(satirlar):
            if satir.startswith("```"):
                acik = not acik
            elif acik:
                kod_ici.add(i)
        return kod_ici

    satirlar = text.split("\n")
    kod_ici = _kod_ici_indexler(satirlar)

    yeni_satirlar = []
    for i, satir in enumerate(satirlar):
        if i in kod_ici:
            # Kod bloÄŸu içindeki satÄ±rlarÄ± deÄŸiÅŸtirme
            yeni_satirlar.append(satir)
            continue

        yeni_satir = satir

        # 4+ backtick â†’ 3 backtick
        if yeni_satir.startswith("````"):
            # Kaç backtick var?
            count = 0
            for ch in yeni_satir:
                if ch == "`":
                    count += 1
                else:
                    break
            if count >= 4:
                gerisi = yeni_satir[count:]
                yeni_satir = "```" + gerisi

        # Ã‡ift backtick + dil â†’ üçlü backtick + dil (açÄ±lÄ±ÅŸ)
        if yeni_satir.startswith("``") and not yeni_satir.startswith("```"):
            gerisi = yeni_satir[2:]
            if gerisi and not gerisi.startswith("`"):
                yeni_satir = "```" + gerisi

        # SatÄ±r baÅŸÄ± tek backtick â†’ üçlü backtick
        if yeni_satir.startswith("`") and not yeni_satir.startswith("``"):
            # Kod bloÄŸu açma mÄ± yoksa inline kod mu?
            gerisi = yeni_satir[1:]
            if gerisi.strip():
                yeni_satir = "```" + gerisi

        yeni_satirlar.append(yeni_satir)

    # Kod bloÄŸu kapanÄ±ÅŸÄ±nÄ± düzelt: tek backtick â†’ üçlü
    metin = "\n".join(yeni_satirlar)
    if metin.rstrip().endswith("`") and not metin.rstrip().endswith("```"):
        # Son satÄ±r tek backtick ile bitiyor
        # ``` ile baÅŸlayan bir bloÄŸun kapanÄ±ÅŸÄ± mÄ±?
        satirlar_yeni = metin.split("\n")
        acik_blok_sayisi = 0
        for s in satirlar_yeni:
            if s.startswith("```") and s.strip() == "```":
                acik_blok_sayisi += 1
            elif s.startswith("```"):
                acik_blok_sayisi += 1

        if acik_blok_sayisi % 2 != 0:
            # AçÄ±k blok var, kapat
            for j in range(len(satirlar_yeni) - 1, -1, -1):
                s = satirlar_yeni[j]
                if s.rstrip().endswith("`") and not s.rstrip().endswith("```"):
                    # Tek backtick ile biten satÄ±r
                    if s.rstrip().endswith("`"):
                        # Son backtick(ler)i say
                        sondaki_backtick = 0
                        for ch in reversed(s.rstrip()):
                            if ch == "`":
                                sondaki_backtick += 1
                            else:
                                break
                        if sondaki_backtick == 1:
                            satirlar_yeni[j] = s.rstrip()[:-1].rstrip() + "```"
                            break
            metin = "\n".join(satirlar_yeni)

    # 2+ ardÄ±ÅŸÄ±k Python kodu satÄ±rÄ±nÄ± blokla (kod bloÄŸu dÄ±ÅŸÄ±nda)
    satirlar_son = metin.split("\n")
    kod_ici2 = _kod_ici_indexler(satirlar_son)
    yeni_satirlar2 = []
    i = 0
    while i < len(satirlar_son):
        if i in kod_ici2:
            yeni_satirlar2.append(satirlar_son[i])
            i += 1
            continue

        # 2+ ardÄ±ÅŸÄ±k Python kodu satÄ±rÄ± ara
        python_satirlari = []
        j = i
        while j < len(satirlar_son) and j not in kod_ici2:
            s = satirlar_son[j]
            # Python kodu: indent (4 boÅŸluk) veya def/class/if/for/with ile baÅŸlayan
            if (
                s.startswith("    ")
                or s.startswith("\t")
                or s.startswith("def ")
                or s.startswith("class ")
                or s.startswith("if ")
                or s.startswith("for ")
                or s.startswith("while ")
                or s.startswith("with ")
                or s.startswith("try:")
                or s.startswith("except")
                or s.startswith("elif ")
                or s.startswith("else:")
                or s.startswith("return ")
                or s.startswith("import ")
                or s.startswith("from ")
                or s.startswith("async ")
                or s.startswith("@")
            ):
                python_satirlari.append(s)
                j += 1
            else:
                break

        if len(python_satirlari) >= 2:
            yeni_satirlar2.append("```python")
            yeni_satirlar2.extend(python_satirlari)
            yeni_satirlar2.append("```")
            i = j
        else:
            yeni_satirlar2.append(satirlar_son[i])
            i += 1

    return "\n".join(yeni_satirlar2).strip()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# isleyen_gorev
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def isleyen_gorev(
    task: str, use_agent: bool = False, chat_id: Optional[str] = None
) -> str:
    """Ana iÅŸlev â€” görevi iÅŸler ve yanÄ±t döndürür."""
    logger = _get_logger()
    logger.info(
        f"Görev iÅŸleniyor: {task[:50]}... (use_agent={use_agent}, chat_id={chat_id})"
    )

    if use_agent:
        return _agent_loop(task)
    else:
        return _deepseek_sohbet(task)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# kopru_deepseek_istek
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def kopru_deepseek_istek(messages: Any, config: Optional[dict] = None) -> str:
    """Köprü entegrasyonu â€” isleyen_gorev'e yönlendirir."""
    logger = _get_logger()
    logger.info("Köprü isteÄŸi alÄ±ndÄ±, isleyen_gorev'e yönlendiriliyor...")

    if isinstance(messages, str):
        return isleyen_gorev(messages, chat_id="kopru")
    elif isinstance(messages, list):
        # Liste ise son user mesajÄ±nÄ± çÄ±kar
        user_texts = [
            m["content"]
            for m in messages
            if isinstance(m, dict) and m.get("role") == "user"
        ]
        mesaj = user_texts[-1] if user_texts else str(messages)
        return isleyen_gorev(mesaj, chat_id="kopru")
    else:
        return isleyen_gorev(str(messages), chat_id="kopru")
