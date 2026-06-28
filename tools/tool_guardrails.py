# -*- coding: utf-8 -*-
"""tools/tool_guardrails.py — Tool guvenlik filtresi.

Iki katmanli API:

Fonksiyonel (registry / run() uyumu):
  guard_check     — Butunlesik guvenlik degerlendirmesi
  path_safety     — Dosya yolu guvenlik kontrolu
  command_safety  — Shell komut guvenlik kontrolu
  run             — tool_registry uyumlu JSON arayuzu

Nesne yonelimli (test_guvenlik_kapsamli / dis kullanim):
  ToolGuardrails  — durum tutan (izinli/riskli arac, guvenlik seviyesi,
                    istatistik) guvenlik kapisi sinifi
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Set, Tuple
import logging
logger = logging.getLogger(__name__)

# ANSI renk kodlari
_Y = "\033[92m"   # yesil
_S = "\033[93m"   # sari
_K = "\033[91m"   # kirmizi
_M = "\033[94m"   # mavi
_R = "\033[0m"    # sifirla

# --- Tehlikeli komut kaliplari (regex) ---
_KOMUT_KARA_LISTE = [
    r"\brm\s+-[rRfF]{1,4}\b",               # rm -rf / rm -fr
    r"\brd\s+/[sS]\b",                       # Windows: rd /s
    r"\bdel\s+/[fFsS]\b",                    # Windows: del /f /s
    r"\bformat\s+[a-zA-Z]:",                 # format C:
    r"\bmkfs\b",                             # Linux disk formatlama
    r"\bshred\b",                            # guvenli silme
    r"\bdrop\s+(database|table)\b",          # SQL yikimi
    r"\btruncate\s+table\b",
    r":\s*\(\s*\)\s*\{[^}]*\|[^}]*\}",       # fork bomb
    r"\bsudo\s+rm\b",
    r"\bchmod\s+0?777\b",
    r"\beval\s*\(",                          # dinamik kod calistirma
    r"\bnc\s+.*-[eElLpP]",                  # netcat reverse shell
    r"\bbash\s+-i\b",                        # interaktif bash
    r"\bpython\d*\s+-c\s+['\"].*os\.",      # python -c os.system
    r"wget\s+\S+\s*\|\s*(ba)?sh\b",         # wget | sh
    r"curl\s+\S+\s*\|\s*(ba)?sh\b",         # curl | bash
    r"\bpowercat\b",                         # PowerShell reverse shell
    r"Invoke-Expression\s*\(",              # PS: IEX
    r"\bStart-Process\b.*-Verb\s+runAs",    # UAC bypass
]

# --- Yasakli yol kaliplari ---
_YOL_YASAK_KALIPLAR = [
    r"\.\.[\\/]",                            # path traversal
    r"[/\\]etc[/\\](passwd|shadow|sudoers)", # Linux kritik dosyalar
    r"[/\\]proc[/\\]",
    r"[/\\]sys[/\\]",
    r"~[/\\.ssh",
    r"C:[/\\]Windows[/\\]System32",
    r"C:[/\\]Windows[/\\]SysWOW64",
    r"C:[/\\]Windows[/\\]System",
    r"%SystemRoot%",
    r"%WINDIR%",
    r"\\\\.\\",                              # Windows raw device \\.\
]

_TEHLIKELI_YOL_PARCALARI = frozenset({
    "System32", "SysWOW64", "proc", "sys",
    "boot", "grub", "efi",
})

# Tool risk seviyeleri (modul-yolu adlari — guard_check icin)
_YUKSEK_RISK = frozenset({
    "code_execution_tool", "python_exec",
    "browser", "browser_camofox", "browser_cdp_tool",
    "mcp_tool", "delegate_tool", "mixture_of_agents_tool",
})

# Varsayilan riskli arac adlari (ToolGuardrails sinifi icin —
# buyuk harfli mantiksal tool adlari).
_VARSAYILAN_RISKLI_ARACLAR = frozenset({
    "KOMUT_CALISTIR", "PYTHON_CALISTIR", "PYTHON_EXEC",
    "SHELL", "CODE_EXECUTION", "CODE_EXECUTION_TOOL",
    "TARAYICI_AC", "BROWSER", "MCP_TOOL_CAGIR",
    "DELEGATE_TASK", "MIXTURE_OF_AGENTS_TOOL",
    "DOSYA_SIL", "WRITE_APPROVAL",
})


def path_safety(path: str) -> tuple:
    """Dosya yolu guvenlik kontrolu.

    Path traversal, sistem dizinleri ve tehlikeli semboller kontrol edilir.

    Args:
        path: Kontrol edilecek yol dizesi.

    Returns:
        (guvenli: bool, aciklama: str)
    """
    if not path or len(path.strip()) < 1:
        return True, "Bos yol"

    for kalip in _YOL_YASAK_KALIPLAR:
        if re.search(kalip, path, re.IGNORECASE):
            mesaj = f"Yasakli yol kalıbı: {kalip!r} icinde '{path[:80]}'"
            print(f"{_K}[GUARDRAIL] YOL ENGELLENDI: {mesaj}{_R}")
            return False, mesaj

    try:
        parcalar = Path(path).parts
        for parca in parcalar:
            if parca in _TEHLIKELI_YOL_PARCALARI:
                mesaj = f"Tehlikeli yol parcasi '{parca}' icinde: {path[:80]}"
                print(f"{_K}[GUARDRAIL] YOL ENGELLENDI: {mesaj}{_R}")
                return False, mesaj
    except (ValueError, OSError):
        logger.warning("[fix_01_sessiz_except] Exception")

    return True, "Yol guvenli"


def command_safety(cmd: str) -> tuple:
    """Shell komut guvenlik kontrolu.

    Kara listedeki pattern'lerle komut analiz edilir. Cok sayida
    pipe zinciri de suphelidir.

    Args:
        cmd: Kontrol edilecek komut dizesi.

    Returns:
        (guvenli: bool, aciklama: str)
    """
    if not cmd:
        return True, "Bos komut"

    for kalip in _KOMUT_KARA_LISTE:
        if re.search(kalip, cmd, re.IGNORECASE | re.DOTALL):
            mesaj = f"Tehlikeli komut kalıbı eslesti: '{cmd[:100]}'"
            print(f"{_K}[GUARDRAIL] KOMUT ENGELLENDI: {mesaj}{_R}")
            return False, mesaj

    pipe_sayisi = cmd.count("|")
    if pipe_sayisi > 5:
        mesaj = f"Asiri pipe zinciri ({pipe_sayisi}): '{cmd[:80]}'"
        print(f"{_S}[GUARDRAIL] KOMUT SUPHE: {mesaj}{_R}")
        return False, mesaj

    return True, "Komut guvenli"


def guard_check(tool_name: str, args: dict, context: dict | None = None) -> tuple:
    """Butunlesik guvenlik degerlendirmesi.

    Adimlar:
      1. Args icerisindeki her str degeri path_safety + command_safety'den gecirir.
      2. Yuksek riskli tool'lar icin context'teki 'yetki' seviyesini kontrol eder.

    Args:
        tool_name: Calistirilmak istenen tool modul adi.
        args: Tool parametreleri.
        context: {'yetki': 'admin' | 'normal', ...} gibi cagri baglami.

    Returns:
        (izin_var: bool, neden: str)
    """
    context = context or {}

    for deger in args.values():
        if not isinstance(deger, str):
            continue

        guvenli, aciklama = path_safety(deger)
        if not guvenli:
            print(f"{_K}[GUARDRAIL] ENGELLENDI — {tool_name}: {aciklama}{_R}")
            return False, f"Tehlikeli yol: {aciklama}"

        guvenli, aciklama = command_safety(deger)
        if not guvenli:
            print(f"{_K}[GUARDRAIL] ENGELLENDI — {tool_name}: {aciklama}{_R}")
            return False, f"Tehlikeli komut: {aciklama}"

    if tool_name in _YUKSEK_RISK and context.get("yetki") != "admin":
        mesaj = f"'{tool_name}' admin yetkisi gerektirir (mevcut: {context.get('yetki', 'normal')})"
        print(f"{_S}[GUARDRAIL] REDDEDILDI — {mesaj}{_R}")
        return False, mesaj

    print(f"{_Y}[GUARDRAIL] IZIN VERILDI — {tool_name}{_R}")
    return True, "Guvenli"


class ToolGuardrails:
    """Durum tutan tool guvenlik kapisi.

    Fonksiyonel guard_check/path_safety/command_safety katmaninin uzerine
    oturur; ek olarak izin listesi, riskli arac kumesi, guvenlik seviyesi
    ve istatistik tutar.

    Attributes:
        _riskli_araclar: Varsayilan olarak engellenen tool adlari.
        _izinli_araclar: Acikca izin verilmis (riskli olsa da gecen) adlar.
        _guvenlik_seviyesi: 1..5 arasi politika sertligi (varsayilan 3).
    """

    def __init__(
        self,
        riskli_araclar: Optional[Set[str]] = None,
        guvenlik_seviyesi: int = 3,
        izinli_araclar: Optional[Set[str]] = None,
    ):
        """ToolGuardrails baslatici.

        Args:
            riskli_araclar: Engellenecek tool adlari. None ise varsayilan kume.
            guvenlik_seviyesi: 1 (gevsek) .. 5 (siki). Varsayilan 3.
            izinli_araclar: Baslangicta izinli (whitelist) tool adlari.
        """
        self._riskli_araclar: Set[str] = set(
            riskli_araclar if riskli_araclar is not None else _VARSAYILAN_RISKLI_ARACLAR
        )
        self._izinli_araclar: Set[str] = set(izinli_araclar or set())
        # 1..5 araliginda kenetle
        self._guvenlik_seviyesi: int = max(1, min(5, int(guvenlik_seviyesi)))
        self._engellenen_islem: int = 0
        self._gecen_islem: int = 0

    # ── Politika sorgulari ────────────────────────────────────────────
    def guvenli_mi(self, arac_adi: str) -> bool:
        """Bir aracin (parametresiz) politika geregi guvenli olup olmadigi.

        Izinli listede ise her zaman guvenli; aksi halde riskli kumede
        olmamasi gerekir.

        Args:
            arac_adi: Mantiksal tool adi.

        Returns:
            bool: Guvenli ise True.
        """
        if arac_adi in self._izinli_araclar:
            return True
        return arac_adi not in self._riskli_araclar

    def kontrolet(self, arac_adi: str, **params: Any) -> Dict[str, Any]:
        """Bir arac cagrisini parametreleriyle birlikte degerlendir.

        Once parametre degerlerini (yol + komut guvenligi) tarar; ardindan
        aracin risk durumunu kontrol eder. Izinli araclar riskli olsa da
        gecer.

        Args:
            arac_adi: Mantiksal tool adi.
            **params: Arac parametreleri (str degerleri taranir).

        Returns:
            dict: {
                'guvenli': bool,
                'arac': str,
                'sebep': str,        # her zaman var
                'tespit': str|None,  # 'YOL' | 'KOMUT' | 'RISKLI_ARAC' | None
            }
        """
        # 1) Parametre degerlerini tara — izinli arac olsa bile tehlikeli
        #    bir yol/komut argumani gecmemeli.
        for deger in params.values():
            if not isinstance(deger, str):
                continue

            guvenli, aciklama = path_safety(deger)
            if not guvenli:
                return self._sonuc(False, arac_adi, f"Tehlikeli yol: {aciklama}", "YOL")

            guvenli, aciklama = command_safety(deger)
            if not guvenli:
                return self._sonuc(False, arac_adi, f"Tehlikeli komut: {aciklama}", "KOMUT")

        # 2) Arac risk durumu — izinli ise gec, degilse riskli kumeyi kontrol et.
        if arac_adi in self._izinli_araclar:
            return self._sonuc(True, arac_adi, "Izinli arac", None)

        if arac_adi in self._riskli_araclar:
            return self._sonuc(
                False, arac_adi,
                f"'{arac_adi}' riskli arac listesinde (seviye {self._guvenlik_seviyesi})",
                "RISKLI_ARAC",
            )

        return self._sonuc(True, arac_adi, "Guvenli", None)

    def _sonuc(self, guvenli: bool, arac: str, sebep: str, tespit: Optional[str]) -> Dict[str, Any]:
        """kontrolet() icin standart sonuc dict'i uret ve sayaci guncelle."""
        if guvenli:
            self._gecen_islem += 1
        else:
            self._engellenen_islem += 1
        return {"guvenli": guvenli, "arac": arac, "sebep": sebep, "tespit": tespit}

    # ── Izin yonetimi ─────────────────────────────────────────────────
    def izin_ver(self, arac_adi: str) -> None:
        """Bir araci izin listesine ekle (riskli olsa da gecer hale gelir)."""
        self._izinli_araclar.add(arac_adi)

    def izin_geri_al(self, arac_adi: str) -> None:
        """Bir aracin iznini kaldir."""
        self._izinli_araclar.discard(arac_adi)

    def izin_verilen_araclar(self) -> list:
        """Izin verilmis arac adlarinin listesi."""
        return sorted(self._izinli_araclar)

    # ── Raporlama ─────────────────────────────────────────────────────
    def istatistik(self) -> Dict[str, Any]:
        """Guardrails calisma istatistikleri."""
        return {
            "guvenlik_seviyesi": self._guvenlik_seviyesi,
            "engellenen_islem": self._engellenen_islem,
            "gecen_islem": self._gecen_islem,
            "riskli_arac_sayisi": len(self._riskli_araclar),
            "izinli_arac_sayisi": len(self._izinli_araclar),
        }


def run(islem: str = "guard", tool_name: str = "", args=None,
        context=None, yol: str = "", cmd: str = "") -> str:
    """Guardrails harici arayuzu (tool_registry uyumu icin).

    Args:
        islem: 'guard' | 'path' | 'cmd'
        tool_name: guard islemi icin tool adi.
        args: guard islemi icin parametreler (dict veya JSON string).
        context: guard islemi icin baglam (dict veya JSON string).
        yol: path islemi icin yol dizesi.
        cmd: cmd islemi icin komut dizesi.

    Returns:
        str: JSON formatinda sonuc.
    """
    def _parse(x, varsayilan):
        if x is None:
            return varsayilan
        if isinstance(x, str):
            try:
                return json.loads(x)
            except json.JSONDecodeError:
                return varsayilan
        return x

    args = _parse(args, {})
    context = _parse(context, {})

    try:
        if islem == "guard":
            izin, neden = guard_check(tool_name, args, context)
            return json.dumps({"izin": izin, "neden": neden}, ensure_ascii=False)

        elif islem == "path":
            guvenli, mesaj = path_safety(yol)
            return json.dumps({"guvenli": guvenli, "mesaj": mesaj}, ensure_ascii=False)

        elif islem == "cmd":
            guvenli, mesaj = command_safety(cmd)
            return json.dumps({"guvenli": guvenli, "mesaj": mesaj}, ensure_ascii=False)

        return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen islem: {islem}"}, ensure_ascii=False)

    except Exception as exc:
        return json.dumps({"durum": "hata", "mesaj": str(exc)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("path", yol="../../etc/passwd"))
    print(run("cmd", cmd="rm -rf /"))
    print(run("guard", tool_name="shell", args={"komut": "echo test"}))
    print(run("guard", tool_name="code_execution_tool", args={}, context={"yetki": "admin"}))
