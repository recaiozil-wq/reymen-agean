# -*- coding: utf-8 -*-
"""prompt_assembly.py â€” Sistem prompt'u tek noktadan topla.

Hedef yapi:
    system_prompt = config.yaml â†’ SOUL.md â†’ USER.md

conversation_loop ve diger moduller buradan okur, kendi icinde
sabit string tutmaz. SOUL.md ve USER.md diskten her defasinda
okunmaz â€” lru_cache ile bir kez yuklenir, bellekten servis edilir.

Yol bilgileri:
    SOUL.md  â†’ ~/.reymen/profiles/<profil>/SOUL.md (oncelikli)
              veya proje kokundeki SOUL.md (fallback)
    USER.md  â†’ reymen/hafiza/USER.md
    config   â†’ proje kokundeki config.yaml
"""

import functools
import logging
import os
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

# â”€â”€ Varsayilan yollar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_PROJE_KOKU = Path(__file__).resolve().parent.parent.parent  # ReYMeN-Ajan/
_VARSAYILAN_USER_MD = _PROJE_KOKU / "reymen" / "hafiza" / "USER.md"
_VARSAYILAN_SOUL_MD = _PROJE_KOKU / "SOUL.md"
_VARSAYILAN_CONFIG = _PROJE_KOKU / "config.yaml"

# ReYMeN profil SOUL.md (varsa oncelikli)
_REYMEN_PROFIL = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "hermes"
    / "profiles"
    / "reymen"
    / "SOUL.md"
)


def _profil_soul_yolu() -> Path:
    """Profil SOUL.md yolunu dondur; yoksa proje kokundekini dene."""
    yol = Path(str(_REYMEN_PROFIL))
    if yol.exists():
        return yol
    if _VARSAYILAN_SOUL_MD.exists():
        return _VARSAYILAN_SOUL_MD
    return yol  # yoksa bile dondur, cagiran handle etsin


@functools.lru_cache(maxsize=1)
def _dosya_oku(yol: Path) -> str:
    """Dosyayi oku, yoksa bos string dondur. lru_cache ile bellekte tut."""
    try:
        if yol.exists():
            icerik = yol.read_text(encoding="utf-8").strip()
            log.debug("PromptAssembly: %s okundu (%d chars)", yol.name, len(icerik))
            return icerik
        else:
            log.debug("PromptAssembly: %s bulunamadi, atlaniyor", yol)
            return ""
    except Exception as e:
        log.warning("PromptAssembly: %s okuma hatasi: %s", yol, e)
        return ""


def _config_prompt_al() -> str:
    """config.yaml'dan agent.system_prompt veya general.default_system_prompt
    degerini oku. Yoksa bos string doner."""
    try:
        import yaml

        yol = _VARSAYILAN_CONFIG
        if yol.exists():
            with open(yol, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            if not cfg:
                return ""
            aranacak = [
                cfg.get("agent", {}).get("default_system_prompt"),
                cfg.get("general", {}).get("default_system_prompt"),
                cfg.get("personality", None),
            ]
            for val in aranacak:
                if val and isinstance(val, str) and val.strip():
                    return val.strip()
            # agent.personalities altinda 'default' key'i varsa
            personalities = cfg.get("agent", {}).get("personalities", {})
            if isinstance(personalities, dict):
                default_p = personalities.get("default", {})
                if isinstance(default_p, dict) and default_p.get("system_prompt"):
                    return default_p["system_prompt"].strip()
        return ""
    except ImportError:
        log.debug("PromptAssembly: yaml modulu yok, config atlandi")
        return ""
    except Exception as e:
        log.debug("PromptAssembly: config okuma hatasi (goz ardi): %s", e)
        return ""


def sistem_prompt_al(tema: Optional[str] = None, ek_bilgi: str = "") -> str:
    """Sistem prompt'unu configâ†’SOUL.mdâ†’USER.md sirasiyla birlestir.

    Args:
        tema:    Opsiyonel tema/task bilgisi (en alta eklenir).
        ek_bilgi: Opsiyonel ek baglam metni.

    Returns:
        Birlestirilmis sistem prompt metni.
    """
    bolumler: list[str] = []

    # 1. Config prompt (varsa)
    config_prompt = _config_prompt_al()
    if config_prompt:
        bolumler.append(config_prompt)

    # 2. SOUL.md â€” kisilik/identity
    soul_yol = _profil_soul_yolu()
    soul = _dosya_oku(soul_yol)
    if soul:
        bolumler.append(soul)

    # 3. USER.md â€” kullanici profili
    user = _dosya_oku(_VARSAYILAN_USER_MD)
    if user:
        bolumler.append(f"## Kullanici Profili\n{user}")

    # 4. Tema (opsiyonel)
    if tema:
        bolumler.append(f"## Mevcut Gorev\n{tema}")

    # 5. Ek bilgi (opsiyonel)
    if ek_bilgi:
        bolumler.append(f"## Ek Baglam\n{ek_bilgi}")

    if not bolumler:
        # Hicbiri yoksa minimum fallback
        return "Sen ReYMeN, otonom bir yazilim ajanisin. Hedefe odaklan, araclari kullan, Turkce yaz."

    sonuc = "\n\n".join(bolumler)
    log.debug("PromptAssembly: sistem prompt olusturuldu (%d chars)", len(sonuc))
    return sonuc


class PromptAssemblyEngine:
    """PromptAssemblyEngine â€” `sistem_prompt_al` fonksiyonlarini class arayuzuyle saran katman.

    Kullanim:
        engine = PromptAssemblyEngine(bounded_memory=..., learning_loop=...)
        prompt = engine.sistem_prompt_al(tema="...")
        engine.cache_tazele()
    """

    def __init__(self, bounded_memory=None, learning_loop=None):
        self.bounded_memory = bounded_memory
        self.learning_loop = learning_loop
        log.debug(
            "PromptAssemblyEngine baslatildi (bounded_memory=%s, learning_loop=%s)",
            bounded_memory is not None,
            learning_loop is not None,
        )

    def sistem_prompt_al(self, tema: Optional[str] = None, ek_bilgi: str = "") -> str:
        """sistem_prompt_al fonksiyonuna yonlendir."""
        return sistem_prompt_al(tema=tema, ek_bilgi=ek_bilgi)

    def cache_tazele(self) -> None:
        """Onbellekleri temizle."""
        cache_tazele()

    def kaynak_dosyalari(self) -> dict:
        """Debug icin kaynak dosya yollari."""
        return _kaynak_dosyalari()

    def insa_et(
        self,
        hedef: str,
        son_gozlem: str = "",
        tur: int = 1,
        toplam_tur: int = 15,
        ic_gozlem_modu: bool = False,
    ) -> str:
        """_sistem_promptu_insa_et fallback'i â€” prompt_assembly'den sistem prompt'u al.

        Bu fonksiyon `AIAgentOrchestrator._sistem_promptu_insa_et()` tarafindan
        PromptBuilder ve _sistem_talimati_fn yoksa cagrilir.
        """
        tema = hedef
        if son_gozlem:
            tema += f"\n\n[Son Gozlem]\n{son_gozlem[:500]}"
        ek = f"Tur {tur}/{toplam_tur}"
        if ic_gozlem_modu:
            ek += "\n[Ic Gozlem Modu]"
        return sistem_prompt_al(tema=tema, ek_bilgi=ek)


def cache_tazele() -> None:
    """SOUL.md/USER.md onbelleklerini sifirla (disk'ten tekrar okunur)."""
    _dosya_oku.cache_clear()
    log.info("PromptAssembly onbellekleri temizlendi")


def _kaynak_dosyalari() -> dict:
    """Debug icin: hangi dosyalardan okundugunu goster."""
    return {
        "config": str(_VARSAYILAN_CONFIG),
        "soul": str(_profil_soul_yolu()),
        "user": str(_VARSAYILAN_USER_MD),
    }


# ── Harici dosya cache (mtime kontrollü) ─────────────────────────────
_prompt_dosya_cache: dict[str, tuple[float, str]] = {}


def cache_dosya_oku(dosya_yolu: str | Path, max_len: int = 0) -> str | None:
    """Dosyayi mtime kontroluyle cache'le. Degismemisse cache'den don."""
    p = Path(dosya_yolu) if not isinstance(dosya_yolu, Path) else dosya_yolu
    if not p.exists():
        return None
    try:
        mtime = p.stat().st_mtime
        cache_key = f"{str(p.resolve())}_max{max_len}"
        if cache_key in _prompt_dosya_cache:
            cached_mtime, cached_content = _prompt_dosya_cache[cache_key]
            if cached_mtime == mtime:
                return cached_content
        icerik = p.read_text(encoding="utf-8", errors="replace")
        if max_len and len(icerik) > max_len:
            icerik = icerik[:max_len]
        _prompt_dosya_cache[cache_key] = (mtime, icerik)
        return icerik
    except (OSError, PermissionError):
        return None


# ── Profil bilgisi (MEMORY.md + USER.md) ───────────────────────────

def profil_bilgisi_al() -> str:
    """MEMORY.md + USER.md icerigini oku, profil bilgisi olarak don."""
    try:
        proje_kok = _PROJE_KOKU
        localappdata = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~/.hermes")))
        hermes_profiles = localappdata / "hermes" / "profiles"
        aday_yollar = [
            proje_kok / ".ReYMeN" / "memories",
            proje_kok / ".ReYMeN",
            proje_kok / "reymen" / "hafiza",
            hermes_profiles / "default" / "memories",
            hermes_profiles / "reymen" / "memories",
            hermes_profiles / "kiral38" / "memories",
            Path(sys.path[0]) / ".ReYMeN" / "memories" if sys.path[0] else None,
            Path.cwd() / ".ReYMeN" / "memories",
        ]
        parcalar = []
        for dosya_adi, etiket in [("MEMORY.md", "Hafiza Notlari"), ("USER.md", "Kullanici Profili")]:
            for aday in aday_yollar:
                if aday is None:
                    continue
                yol = aday / dosya_adi
                if yol.exists():
                    icerik = cache_dosya_oku(yol, max_len=2000)
                    if icerik:
                        parcalar.append(f"[{etiket}]\n{icerik}")
                    break
        return "\n" + "\n\n".join(parcalar) if parcalar else ""
    except Exception:
        return ""


def soul_bilgisi_al() -> str:
    """SOUL.md icerigini oku, kimlik + kural + platform bilgisi olarak don."""
    try:
        proje_kok = _PROJE_KOKU
        localappdata = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~/.hermes")))
        hermes_profiles = localappdata / "hermes" / "profiles"
        aday_yollar = [
            proje_kok / "SOUL.md",
            proje_kok / "SOUL" / "SOUL.md",
            proje_kok / ".ReYMeN" / "SOUL.md",
            hermes_profiles / "default" / "SOUL.md",
            hermes_profiles / "reymen" / "SOUL.md",
            hermes_profiles / "kiral38" / "SOUL.md",
            Path(sys.path[0]) / "SOUL.md" if sys.path[0] else None,
        ]
        for aday in aday_yollar:
            if aday is None:
                continue
            yol = aday if isinstance(aday, Path) else Path(aday)
            if yol.exists():
                icerik = cache_dosya_oku(yol, max_len=4000)
                if icerik:
                    return f"\n[SOUL.md — Kimlik & Kurallar]\n{icerik}\n"
        return ""
    except Exception:
        return ""


def agents_bilgisi_al() -> str:
    """AGENTS.md icerigini oku, entry point + yapi bilgisi olarak don."""
    try:
        proje_kok = _PROJE_KOKU
        aday_yollar = [
            proje_kok / "AGENTS.md",
            proje_kok / ".ReYMeN" / "AGENTS.md",
            Path(os.path.expanduser("~")) / "AppData" / "Local" / "reymen" / "profiles" / "reymen" / "AGENTS.md",
            Path(sys.path[0]) / "AGENTS.md" if sys.path[0] else None,
        ]
        for aday in aday_yollar:
            if aday is None:
                continue
            yol = aday if isinstance(aday, Path) else Path(aday)
            if yol.exists():
                icerik = cache_dosya_oku(yol, max_len=2000)
                if icerik:
                    return f"\n[AGENTS.md — Entry Points & Mimari]\n{icerik}\n"
        return ""
    except Exception:
        return ""


def sistem_promptu_olustur(hedef: str, baglam: dict = None, motor=None) -> str:
    """PromptBuilder ile sistem promptu insa et."""
    try:
        from reymen.arac.prompt_builder import PromptBuilder
        import json as _json
        import logging as _log
        _logg = _log.getLogger("conversation_loop")
        pb = PromptBuilder()
        if motor and hasattr(motor, "arac_listesi"):
            try:
                pb.araclar_kaydet(motor.arac_listesi())
            except Exception:
                pass
        ek_bilgi = _json.dumps(baglam, ensure_ascii=False) if baglam else ""

        try:
            from reymen.cereyan.continuous_learning import ogrenme_baglani_al as _cl_baglam
            cl_ctx = _cl_baglam()
            if cl_ctx:
                ek_bilgi += "\\n\\n" + cl_ctx
        except Exception:
            pass
        try:
            from reymen.cereyan.active_skill_tracker import aktif_skill_context_ekle
            skill_ctx = aktif_skill_context_ekle()
            if skill_ctx:
                ek_bilgi += "\\n\\n" + skill_ctx
        except Exception:
            pass
        try:
            from reymen.sistem.ortak_komut import guncelle as _ortak_guncelle
            _ortak_guncelle()
        except Exception:
            pass
        try:
            from reymen.sistem.durum import _yukle
            _ham_veri = _yukle()
            _ham_json = _json.dumps(_ham_veri, indent=2, ensure_ascii=False)
            ek_bilgi += "\\n\\n" + "=" * 50 + "\\n[ZORUNLU KURAL - ASAGIDAKI JSON TEK KAYNAKTIR]\\n"
            ek_bilgi += "ReYMeN durumu hakkinda soru gelince kendi training bilgini KULLANMA.\\n"
            ek_bilgi += "Bu JSON TEK KAYNAK.\\n" + "=" * 50 + "\\n"
            ek_bilgi += _ham_json[:8000]
            if len(_ham_json) > 8000:
                ek_bilgi += "\\n... (JSON kesildi)"
            ek_bilgi += "\\n" + "=" * 50 + "\\n"
        except Exception:
            pass

        try:
            p = profil_bilgisi_al()
            if p: ek_bilgi += p
        except Exception:
            pass
        try:
            s = soul_bilgisi_al()
            if s: ek_bilgi += "\\n" + s
        except Exception:
            pass
        try:
            a = agents_bilgisi_al()
            if a: ek_bilgi += "\\n" + a
        except Exception:
            pass

        return pb.sistem_prompt(hedef=hedef, ek_bilgi=ek_bilgi)
    except Exception as e:
        _logg = _log.getLogger("conversation_loop")
        _logg.warning("PromptBuilder yok: %s", e)

    skill_context = ""
    try:
        from reymen.cereyan.active_skill_tracker import aktif_skill_context_ekle
        skill_context = aktif_skill_context_ekle() or ""
    except Exception:
        pass
    return (
        "Sen ReYMeN, otonom bir yazilim ajanisin. "
        "Hedefe odaklan, araclari kullan, Turkce yaz. "
        f"{profil_bilgisi_al()}"
        f"{soul_bilgisi_al()}"
        f"{agents_bilgisi_al()}"
        f"{skill_context}"
    )
