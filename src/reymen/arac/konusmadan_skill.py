# -*- coding: utf-8 -*-
"""
konusmadan_skill.py â€” KonuÅŸma geÃ§miÅŸinden otomatik skill Ã§Ä±karma.

Bir gÃ¶rev baÅŸarÄ±yla tamamlandÄ±ÄŸÄ±nda:
  1. KonuÅŸma mesajlarÄ±nÄ± analiz et
  2. LLM ile Ã§Ã¶zÃ¼m pattern'ini Ã§Ä±kar
  3. SKILL.md formatÄ±nda kaydet
  4. FTS5 index'e ekle

KullanÄ±m:
  from reymen.arac.konusmadan_skill import konusmadan_skill_cikar

  # Otomatik (conversation_loop sonunda)
  konusmadan_skill_cikar(messages, basari=True)

  # Manuel (kullanÄ±cÄ± komutu)
  konusmadan_skill_cikar(messages, basari=True, zorla=True)
"""

import json
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ROOT = Path(__file__).resolve().parent.parent  # reymen/
SKILLS_DIR = ROOT / "cereyan" / ".ReYMeN" / "skills"
INDEX_DB = ROOT.parent / ".ReYMeN" / "db" / "skills.db"  # consolidated: skills_index.db + skill_library.db
_MAKS_ACIKLAMA = 300
_MAKS_ADIM = 2000
_MIN_MESAJ_SAYISI = 3  # En az 3 mesaj varsa skill Ã§Ä±kar
_BASARI_ESIÄI = 0.4  # BaÅŸarÄ± puanÄ± eÅŸiÄŸi (0.0-1.0)

# â”€â”€ LLM SaÄŸlayÄ±cÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.cereyan.beyin import Beyin as _Beyin

    _LLM_HAZIR = True
except ImportError:
    _LLM_HAZIR = False

try:
    from reymen.arac.skill_utils import skill_olustur, skill_index_yenile

    _SKILL_UTILS_HAZIR = True
except ImportError:
    _SKILL_UTILS_HAZIR = False


def _mesajlari_ozetle(messages: List[Dict[str, Any]]) -> str:
    """KonuÅŸma mesajlarÄ±nÄ± LLM'e gÃ¶nderilebilir metne Ã§evir."""
    parcalar = []
    for m in messages[-20:]:  # Son 20 mesaj
        rol = m.get("role", "bilinmeyen")
        icerik = m.get("content", "")
        if isinstance(icerik, list):
            for p in icerik:
                if isinstance(p, dict):
                    if p.get("type") == "text":
                        icerik = p["text"][:500]
                    elif p.get("type") == "tool_use":
                        icerik = f"[ARAÃ‡: {p.get('name', '?')}(...)]"
                    elif p.get("type") == "tool_result":
                        icerik = f"[SONUÃ‡: {str(p.get('content', ''))[:200]}]"
        elif isinstance(icerik, str):
            icerik = icerik[:500]
        parcalar.append(f"[{rol.upper()}] {icerik}")
    return "\n".join(parcalar)


def _skill_adi_ureti(ozet: str, konu: str = "") -> str:
    """KonuÅŸma Ã¶zetinden skill adÄ± Ã¼ret."""
    ad = (konu or ozet)[:60].lower()
    ad = re.sub(r"[^a-z0-9\s-]", "", ad)
    ad = re.sub(r"\s+", "-", ad.strip())
    ad = re.sub(r"-+", "-", ad)
    return ad[:50] or f"konusma_skill_{int(time.time())}"


def _beceri_puani_hesapla(messages: List[Dict]) -> float:
    """KonuÅŸmanÄ±n skill olmaya deÄŸer olup olmadÄ±ÄŸÄ±nÄ± hesapla."""
    if len(messages) < _MIN_MESAJ_SAYISI:
        return 0.0

    puan = 0.0

    # Kriter 1: AraÃ§ kullanÄ±mÄ± var mÄ±?
    arac_sayisi = 0
    for m in messages:
        if m.get("role") == "assistant":
            icerik = m.get("content") or []
            if isinstance(icerik, list):
                for p in icerik:
                    if isinstance(p, dict) and p.get("type") == "tool_use":
                        arac_sayisi += 1
    if arac_sayisi > 0:
        puan += 0.3

    # Kriter 2: KullanÄ±cÄ± mesajÄ± yeterince uzun mu?
    kullanici_mesajlari = [m for m in messages if m.get("role") == "user"]
    uzun_mesaj = sum(
        1 for m in kullanici_mesajlari if len(str(m.get("content", ""))) > 100
    )
    if uzun_mesaj > 0:
        puan += 0.2

    # Kriter 3: Tool sonuÃ§larÄ± var mÄ±?
    sonuc_sayisi = sum(1 for m in messages if m.get("role") == "tool")
    if sonuc_sayisi > 0:
        puan += 0.2

    # Kriter 4: Asistan yanÄ±tÄ± uzun mu?
    asistan_mesajlari = [m for m in messages if m.get("role") == "assistant"]
    uzun_yanit = 0
    for m in asistan_mesajlari:
        icerik = m.get("content", "")
        if isinstance(icerik, str) and len(icerik) > 200:
            uzun_yanit += 1
        elif isinstance(icerik, list):
            for p in icerik:
                if (
                    isinstance(p, dict)
                    and p.get("type") == "text"
                    and len(p.get("text", "")) > 200
                ):
                    uzun_yanit += 1
    if uzun_yanit > 0:
        puan += 0.3

    return min(puan, 1.0)


def _llm_ile_skill_cikar(mesaj_ozeti: str, konu: str = "") -> Optional[Dict[str, str]]:
    """LLM kullanarak konuÅŸmadan skill Ã§Ä±kar."""
    if not _LLM_HAZIR:
        logger.warning("[KonusmadanSkill] LLM hazir degil, skill cikarilamadi")
        return None

    try:
        beyin = _Beyin()
        prompt = f"""Bir kullanÄ±cÄ± ile AI asistan arasÄ±ndaki konuÅŸmayÄ± analiz et ve bir SKILL.md olarak kaydetmek iÃ§in JSON Ã§Ä±ktÄ±sÄ± ver.

KONUÅMA Ã–ZETÄ°:
{mesaj_ozeti[:3000]}

AÅŸaÄŸÄ±daki JSON formatÄ±nda Ã§Ä±ktÄ± ver (sadece JSON, baÅŸka metin yok):
{{
  "ad": "skill_adi (kucuk harf, tire-ile-ayrilmis)",
  "baslik": "KÄ±sa aÃ§Ä±klayÄ±cÄ± baÅŸlÄ±k",
  "aciklama": "Ne iÅŸe yarar, ne zaman kullanÄ±lÄ±r (max 300 karakter)",
  "etiketler": ["etiket1", "etiket2", "etiket3"],
  "kategori": "kategori_adi",
  "adimlar": "AdÄ±m adÄ±m Ã§Ã¶zÃ¼m talimatlarÄ± (Markdown, max 2000 karakter)",
  "trigger_kelimeler": ["kelime1", "kelime2"],
  "guven_skoru": 0.85
}}

Kurallar:
- adimlar: somut, adÄ±m adÄ±m, tekrarlanabilir olmalÄ±
- guven_skoru: 0.0-1.0 arasÄ±, konuÅŸmanÄ±n skill olmaya ne kadar uygun olduÄŸu
- EÄŸer konuÅŸma basit bir selamlaÅŸma veya anlamlÄ± bir Ã§Ã¶zÃ¼m iÃ§ermiyorsa guven_skoru dÃ¼ÅŸÃ¼k ver
"""

        yanit = beyin.soru(prompt)
        if not yanit:
            return None

        # JSON Ã§Ä±ktÄ±sÄ±nÄ± ayÄ±kla
        json_match = re.search(r"\{.*\}", yanit, re.DOTALL)
        if not json_match:
            return None

        data = json.loads(json_match.group())
        return data

    except Exception as e:
        logger.warning("[KonusmadanSkill] LLM hatasi: %s", e)
        return None


def konusmadan_skill_cikar(
    messages: List[Dict[str, Any]],
    basari: bool = True,
    zorla: bool = False,
    konu: str = "",
) -> str:
    """KonuÅŸma mesajlarÄ±ndan skill Ã§Ä±kar ve kaydet.

    Args:
        messages: KonuÅŸma mesaj listesi.
        basari: GÃ¶rev baÅŸarÄ±lÄ± mÄ±?
        zorla: Zorla skill Ã§Ä±kar (puan kontrolÃ¼nÃ¼ atla).
        konu: Ä°steÄŸe baÄŸlÄ± konu baÅŸlÄ±ÄŸÄ±.

    Returns:
        Durum mesajÄ±.
    """
    if not _SKILL_UTILS_HAZIR:
        return "[KonusmadanSkill] skill_utils hazir degil"

    if not messages:
        return "[KonusmadanSkill] Mesaj yok"

    if not basari and not zorla:
        return "[KonusmadanSkill] Gorev basarisiz, skill cikarilmadi"

    # Beceri puanÄ± hesapla
    puan = _beceri_puani_hesapla(messages)
    if puan < _BASARI_ESIÄI and not zorla:
        return f"[KonusmadanSkill] Dusuk puan ({puan:.2f} < {_BASARI_ESIÄI}), skill cikarilmadi"

    # MesajlarÄ± Ã¶zetle
    ozet = _mesajlari_ozetle(messages)

    # LLM ile skill Ã§Ä±kar
    skill_data = _llm_ile_skill_cikar(ozet, konu)
    if not skill_data:
        # LLM yoksa basit ÅŸablonla skill oluÅŸtur
        return _basit_skill_kaydet(ozet, konu)

    guven = skill_data.get("guven_skoru", 0.0)
    if guven < 0.3 and not zorla:
        return (
            f"[KonusmadanSkill] LLM guven skoru dusuk ({guven:.2f}), skill cikarilmadi"
        )

    ad = skill_data.get("ad", _skill_adi_ureti(ozet, konu))
    baslik = skill_data.get("baslik", ad)
    aciklama = skill_data.get("aciklama", "")[:_MAKS_ACIKLAMA]
    etiketler = skill_data.get("etiketler", [])
    kategori = skill_data.get("kategori", "konusma")
    adimlar = skill_data.get("adimlar", "")[:_MAKS_ADIM]
    trigger_kelimeler = skill_data.get("trigger_kelimeler", [])

    if not aciklama:
        return "[KonusmadanSkill] Aciklama bos, skill cikarilmadi"

    # SKILL.md dosyasina yaz
    try:
        etiket_str = ", ".join(f'"{e}"' for e in etiketler)
        trigger_str = ", ".join(f'"{t}"' for t in trigger_kelimeler)

        skill_md = f"""---
name: {ad}
title: "{baslik}"
description: "{aciklama}"
tags: [{etiket_str}]
category: {kategori}
audience: user
triggers: [{trigger_str}]
created_from: conversation
confidence: {guven:.2f}
created_at: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

| 5N1K | AÃ§Ä±klama |
|:----:|:---------|
| **Kim** | AI kullanÄ±cÄ±sÄ± |
| **Ne** | {baslik} |
| **Nerede** | `{kategori}/{ad}.md` |
| **Ne Zaman** | Ä°lgili gÃ¶rev gerektiÄŸinde |
| **Neden** | {aciklama} |

{adimlar}
"""
        hedef_klasor = SKILLS_DIR / kategori / ad
        hedef_klasor.mkdir(parents=True, exist_ok=True)
        hedef_dosya = hedef_klasor / "SKILL.md"
        hedef_dosya.write_text(skill_md, encoding="utf-8")

        skill_index_yenile(zorla=True)

        logger.info(
            "[KonusmadanSkill] âœ… Skill olusturuldu: %s (guven=%.2f) -> %s",
            ad,
            guven,
            hedef_dosya,
        )
        return f"[KonusmadanSkill] âœ… '{ad}' skill'i olusturuldu (guven: {guven:.0%})"

    except Exception as e:
        logger.error("[KonusmadanSkill] Skill kayit hatasi: %s", e)
        return f"[KonusmadanSkill] Hata: {e}"


def _basit_skill_kaydet(ozet: str, konu: str = "") -> str:
    """LLM yokken basit ÅŸablonla skill kaydet."""
    ad = _skill_adi_ureti(ozet, konu)
    baslik = konu or ad.replace("-", " ").title()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    skill_md = f"""---
name: {ad}
title: "{baslik}"
description: "Konusmadan cikarilmis cozum: {baslik}"
tags: ["konusma", "otomatik"]
category: konusma
audience: user
triggers: []
created_from: conversation
created_at: {timestamp}

---

| 5N1K | AÃ§Ä±klama |
|:----:|:---------|
| **Kim** | AI kullanÄ±cÄ±sÄ± |
| **Ne** | {baslik} |
| **Nerede** | `konusma/{ad}.md` |
| **Ne Zaman** | Ä°lgili gÃ¶rev gerektiÄŸinde |
| **Neden** | KonuÅŸmadan Ã§Ä±karÄ±lan Ã§Ã¶zÃ¼m |

## Ã‡Ã¶zÃ¼m AdÄ±mlarÄ±

1. **Problem:** {baslik}
2. **Ã‡Ã¶zÃ¼m:** KonuÅŸma iÃ§inde Ã§Ã¶zÃ¼lmÃ¼ÅŸtÃ¼r. Detaylar iÃ§in skill iÃ§eriÄŸine bakÄ±n.

## KullanÄ±m

Bu skill otomatik olarak bir konuÅŸmadan Ã§Ä±karÄ±lmÄ±ÅŸtÄ±r.
Ä°lgili bir gÃ¶rev geldiÄŸinde bu skill devreye girecektir.
"""

    try:
        # Direkt SKILLS_DIR'e yaz (skill_olustur yanlis ROOT kullaniyor)
        hedef_klasor = SKILLS_DIR / "konusma" / ad
        hedef_klasor.mkdir(parents=True, exist_ok=True)
        hedef_dosya = hedef_klasor / "SKILL.md"
        hedef_dosya.write_text(skill_md, encoding="utf-8")

        skill_index_yenile(zorla=True)
        logger.info(
            "[KonusmadanSkill] âœ… Basit skill olusturuldu: %s -> %s", ad, hedef_dosya
        )
        return f"[KonusmadanSkill] âœ… '{ad}' basit skill olusturuldu ({hedef_dosya})"
    except Exception as e:
        logger.error("[KonusmadanSkill] Basit kayit hatasi: %s", e)
        return f"[KonusmadanSkill] Hata: {e}"


# â”€â”€ Motor'a kayÄ±t â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def motor_kaydet(motor: object) -> None:
    """Motor'a konusmadan_skill_cikar aracini kaydet."""
    try:
        motor.kaydet(
            "KONUSMADAN_SKILL",
            konusmadan_skill_cikar,
            "Konusma gecmisinden skill cikar ve kaydet. "
            "Parametre: messages=[...], basari=True/False, zorla=True/False, konu='...'",
        )
        logger.info("[KonusmadanSkill] Motor'a kaydedildi")
    except Exception as e:
        logger.warning("[KonusmadanSkill] Motor kayit hatasi: %s", e)
