#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_otonom_fix.py — Otonom Sessiz Except Düzeltici v1

Tüm .py dosyalarını tarar, sessiz `except ... : pass` bloklarını bulur,
otomatik olarak `logger.warning(...)` ekler.

Çalışma modları:
    python _otonom_fix.py              # Tarama + düzeltme (varsayılan)
    python _otonom_fix.py --dry-run    # Sadece rapor, hiçbir şey değiştirme
    python _otonom_fix.py --cron       # Cron modu (sessiz, sadece değişiklik varsa rapor)

Güvenlik:
    - Her değişiklik öncesi dosyanın yedeğini alır
    - Syntax kontrolü başarısız olursa geri alır
    - İzinli/kara liste desteği
    - İnsan onayı gerektiren dosyaları atlar (opsiyonel)
"""
from __future__ import annotations

import ast
import difflib
import logging
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import textwrap
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Yapılandırma ──────────────────────────────────────────────────────────

# Varsayılan çalışma dizini (proje kökü)
# --proje argümanı ile override edilebilir
PROJE_KOK = Path(__file__).parent.resolve()
if PROJE_KOK.name == "scripts":
    # Cron'dan çalışıyorsa, proje kökünü manuel ayarla
    PROJE_KOK = Path(r"C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan")

# --proje argümanını işle
import sys as _sys
for i, arg in enumerate(_sys.argv):
    if arg == "--proje" and i + 1 < len(_sys.argv):
        PROJE_KOK = Path(_sys.argv[i + 1]).resolve()
        break

# Yedek dizini
YEDEK_DIZINI = PROJE_KOK / ".ReYMeN" / "fix_yedekleri"
YEDEK_DIZINI.mkdir(parents=True, exist_ok=True)

# Log
LOG_DIZINI = PROJE_KOK / ".ReYMeN" / "logs"
LOG_DIZINI.mkdir(parents=True, exist_ok=True)
LOG_DOSYASI = LOG_DIZINI / "otonom_fix.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_DOSYASI), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("otonom_fix")

# Atlanacak dizinler (regex desenleri)
ATLANACAK_DIZIN = [
    r"__pycache__",
    r"\.git",
    r"venv",
    r"\.venv",
    r"hermes-memory",
    r"hermes_backup",
    r"node_modules",
    r"\.ReYMeN",
    r"dist",
    r"build",
    r"\.eggs",
    r"\.pytest_cache",
]

# Atlanacak dosya isimleri (regex desenleri)
ATLANACAK_DOSYA = [
    r"^_",        # _ ile başlayan (internal)
    r"^test_",    # test_ ile başlayan (test dosyaları)
    r"^conftest",
    r"^setup\.py$",
]

# Kara liste — bu dosyalara asla dokunma (göreceli yol, proje kökünden)
KARA_LISTE: list[str] = [
    # 3. parti / vendor kodları
    "reymen/core/",  # Hermes vendor kopyası
]

# Beyaz liste — boşsa tüm dosyalar taranır
BEYAZ_LISTE: list[str] = []  # örn: ["reymen/arac/", "reymen/cereyan/"]

# Maksimum dosya boyutu (byte) — 500KB üstü atlanır
MAX_DOSYA_BOYUT = 500 * 1024

# Minimum güven skoru (0-1): 1 = kesin sessiz, 0.5 = şüpheli
MIN_GUVEN = 0.8


# ── Yardımcı Fonksiyonlar ────────────────────────────────────────────────

def _dizini_atla(yol: Path) -> bool:
    """Dizin atlanacak mı?"""
    yol_str = str(yol.as_posix())
    for desen in ATLANACAK_DIZIN:
        if re.search(desen, yol_str):
            return True
    return False


def _dosyayi_atla(yol: Path, rel: str) -> bool:
    """Dosya atlanacak mı?"""
    # Kara liste
    for kara in KARA_LISTE:
        if kara in rel:
            return True

    # İsim deseni
    for desen in ATLANACAK_DOSYA:
        if re.match(desen, yol.name):
            return True

    # Boyut
    try:
        if yol.stat().st_size > MAX_DOSYA_BOYUT:
            return True
    except OSError:
        return True

    # Beyaz liste (aktifse)
    if BEYAZ_LISTE:
        for beyaz in BEYAZ_LISTE:
            if beyaz in rel:
                return False
        return True  # beyaz listede değilse atla

    return False


def _logger_var_mi(icerik: str) -> bool:
    """Dosyada logger tanımı var mı?"""
    return bool(re.search(
        r'logger\s*=\s*logging\.(getLogger|get_logger)\s*\(',
        icerik
    ))


def _logging_import_var_mi(icerik: str) -> bool:
    """Dosyada import logging var mı?"""
    return bool(re.search(
        r'^\s*import\s+logging\s*$',
        icerik,
        re.MULTILINE
    ))


def _log_cagrisi_var_mi(icerik: str, satir_no: int, aralik: int = 5) -> bool:
    """Verilen satır civarında logger.warning/error/exception çağrısı var mı?"""
    satirlar = icerik.split('\n')
    bas = max(0, satir_no - 1 - aralik)
    son = min(len(satirlar), satir_no - 1 + aralik)
    for i in range(bas, son):
        if re.search(
            r'(logger|log)\.(warning|error|exception|info|debug)\s*\(',
            satirlar[i]
        ):
            return True
    return False


def _print_cagrisi_var_mi(icerik: str, satir_no: int, aralik: int = 5) -> bool:
    """print, return veya raise var mı (sessiz olmayan kod)?"""
    satirlar = icerik.split('\n')
    bas = max(0, satir_no - 1 - aralik)
    son = min(len(satirlar), satir_no - 1 + aralik)
    for i in range(bas, son):
        satir = satirlar[i].strip()
        if satir.startswith(('print(', 'return ', 'raise ')):
            return True
    return False


def _hata_mesaji_olustur(dosya_adi: str, exc_tipi: str, satir_no: int) -> str:
    """
    except bloğunun bağlamına göre anlamlı bir hata mesajı oluştur.
    
    Args:
        dosya_adi: Dosya adı (kısa)
        exc_tipi: 'Exception', 'KeyError', ':' (bare) vb.
        satir_no: Except satır numarası
    
    Returns:
        logger.warning için format string (ilk argüman)
    """
    # Dosya adından kısa bir modül etiketi çıkar
    # Örn: "reymen/cereyan/motor.py" → "[Motor]"
    kisalt = dosya_adi.replace('reymen/', '').replace('/', '.').replace('.py', '')
    kisalt = kisalt.split('.')[-1]  # son parça
    kisalt = kisalt.replace('_', ' ').title().replace(' ', '')
    
    # Exception tipine göre varsayılan mesaj
    if exc_tipi == 'Exception' or exc_tipi.startswith('except:'):
        return f"[{kisalt}] Bilinmeyen hata (L{satir_no}): %s"
    elif 'ImportError' in exc_tipi or 'ModuleNotFoundError' in exc_tipi:
        return f"[{kisalt}] Modul yuklenemedi (L{satir_no}): %s"
    elif 'KeyError' in exc_tipi:
        return f"[{kisalt}] Anahtar bulunamadi (L{satir_no}): %s"
    elif 'IndexError' in exc_tipi:
        return f"[{kisalt}] Indeks disi (L{satir_no}): %s"
    elif 'OSError' in exc_tipi or 'FileNotFoundError' in exc_tipi:
        return f"[{kisalt}] Dosya/klasor hatasi (L{satir_no}): %s"
    elif 'ValueError' in exc_tipi:
        return f"[{kisalt}] Gecersiz deger (L{satir_no}): %s"
    elif 'TypeError' in exc_tipi:
        return f"[{kisalt}] Tip hatasi (L{satir_no}): %s"
    elif 'sqlite3' in exc_tipi:
        return f"[{kisalt}] Veritabani hatasi (L{satir_no}): %s"
    elif 'AttributeError' in exc_tipi:
        return f"[{kisalt}] Nitelik hatasi (L{satir_no}): %s"
    elif 'json' in exc_tipi or 'JSONDecodeError' in exc_tipi:
        return f"[{kisalt}] JSON parse hatasi (L{satir_no}): %s"
    else:
        return f"[{kisalt}] {exc_tipi.strip(':')} (L{satir_no}): %s"


def _python_syntax_kontrol(path: Path) -> tuple[bool, str]:
    """Python dosyasının syntax'ını kontrol et."""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            ast.parse(f.read(), str(path))
        return True, ""
    except SyntaxError as e:
        return False, str(e)


# ── Ana Tarama Motoru ────────────────────────────────────────────────────

class SessizExceptBulucu:
    """
    AST tabanlı sessiz except tarayıcı.
    
    Kullanım:
        bulucu = SessizExceptBulucu()
        sonuclar = bulucu.tara("reymen/")
    """
    
    def __init__(self, min_guven: float = MIN_GUVEN):
        self.min_guven = min_guven
        self.istatistik = defaultdict(int)
    
    def tara(self, dizin: str | Path) -> list[dict]:
        """
        Belirtilen dizindeki tüm .py dosyalarını tara.
        
        Returns:
            [{
                "dosya": Path,
                "rel_yol": str,
                "satir_no": int,
                "exc_tipi": str,
                "exc_metni": str,        # Orijinal except satırı
                "context": str,           # Bağlam satırları
                "guven": float,           # 0-1 arası güven skoru
                "log_varmi": bool,
                "logger_tanimli": bool,
                "logging_import_var": bool,
            }, ...]
        """
        sonuclar = []
        dizin = Path(dizin)
        
        for py_dosya in sorted(dizin.rglob("*.py")):
            # Atlama kontrolleri
            if _dizini_atla(py_dosya):
                continue
            
            rel = str(py_dosya.relative_to(PROJE_KOK).as_posix())
            if _dosyayi_atla(py_dosya, rel):
                continue
            
            try:
                icerik = py_dosya.read_text(encoding="utf-8", errors="replace")
            except (OSError, UnicodeDecodeError):
                continue
            
            # Dosya bazlı istatistik
            logger_tanimli = _logger_var_mi(icerik)
            logging_import_var = _logging_import_var_mi(icerik)
            
            try:
                tree = ast.parse(icerik, str(py_dosya))
            except SyntaxError:
                self.istatistik["syntax_hatasi"] += 1
                continue
            
            satirlar = icerik.split('\n')
            
            for node in ast.walk(tree):
                if not isinstance(node, ast.Try):
                    continue
                
                for handler in node.handlers:
                    self._is_except_sessiz(
                        handler, py_dosya, rel, satirlar,
                        logger_tanimli, logging_import_var, icerik, sonuclar
                    )
        
        return sonuclar
    
    def _is_except_sessiz(
        self, handler: ast.ExceptHandler,
        py_dosya: Path, rel: str, satirlar: list[str],
        logger_tanimli: bool, logging_import_var: bool,
        icerik: str, sonuclar: list[dict]
    ):
        """Bir except handler'ının sessiz olup olmadığını kontrol et."""
        lineno = handler.lineno
        
        # Exception tipini belirle
        if handler.type is None:
            exc_tipi = "except:"
            exc_metni = "except:"
        elif isinstance(handler.type, ast.Name):
            exc_tipi = f"except {handler.type.id}:"
            exc_metni = f"except {handler.type.id}:"
        elif isinstance(handler.type, ast.Tuple):
            isimler = []
            for e in handler.type.elts:
                if isinstance(e, ast.Name):
                    isimler.append(e.id)
                elif isinstance(e, ast.Attribute):
                    isimler.append(f"{e.value.id}.{e.attr}" if isinstance(e.value, ast.Name) else "?")
                else:
                    isimler.append("?")
            exc_tipi = f"except ({', '.join(isimler)}):"
            exc_metni = exc_tipi
        elif isinstance(handler.type, ast.Attribute):
            base = handler.type.value.id if isinstance(handler.type.value, ast.Name) else "?"
            exc_tipi = f"except {base}.{handler.type.attr}:"
            exc_metni = exc_tipi
        else:
            exc_tipi = f"except ({type(handler.type).__name__}):"
            exc_metni = exc_tipi
        
        # Handler body'sini analiz et
        body_satirlari = []
        sadece_pass = True
        ek_kod_var = False
        log_var = False
        print_var = False
        return_var = False
        raise_var = False
        
        for stmt in handler.body:
            # Satır numarasını al
            if hasattr(stmt, 'lineno'):
                for i in range(stmt.lineno - 1, (getattr(stmt, 'end_lineno', stmt.lineno) or stmt.lineno)):
                    if 0 <= i < len(satirlar):
                        body_satirlari.append(satirlar[i].strip())
            
            if isinstance(stmt, ast.Pass):
                pass  # pass normal
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call = stmt.value
                if isinstance(call.func, ast.Attribute):
                    func_name = f"{call.func.value.id}.{call.func.attr}" if isinstance(call.func.value, ast.Name) else call.func.attr
                    if 'logger' in func_name or 'log' in func_name:
                        if call.func.attr in ('warning', 'error', 'exception', 'info', 'debug'):
                            log_var = True
            elif isinstance(stmt, ast.Raise):
                raise_var = True
            elif isinstance(stmt, ast.Return):
                return_var = True
            else:
                ek_kod_var = True  # pass dışında kod var
        
        # pass var mı kontrol et (son satırda)
        pass_var_mi = any(isinstance(stmt, ast.Pass) for stmt in handler.body)
        
        # Güven skoru hesapla
        guven = 1.0
        if ek_kod_var:
            guven -= 0.5  # pass dışında kod varsa şüpheli
        if log_var:
            guven -= 0.5  # zaten log varsa sessiz değil
        if print_var or return_var or raise_var:
            guven -= 0.3
        if not pass_var_mi:
            guven -= 0.5  # pass yoksa bu bir silent except değil
        
        # Sadece pass ve log yoksa ilgilen
        if not pass_var_mi:
            return
        
        # Zaten log var mı kontrol et (AST dışında, string olarak da kontrol)
        log_var_str = _log_cagrisi_var_mi(icerik, lineno)
        print_var_str = _print_cagrisi_var_mi(icerik, lineno)
        
        if log_var or log_var_str:
            self.istatistik["zaten_log_var"] += 1
            return
        
        # Bağlam satırlarını topla
        context_satirlar = []
        for i in range(lineno - 1, min(lineno + 3, len(satirlar))):
            context_satirlar.append(satirlar[i].strip())
        context = '\n'.join(context_satirlar)
        
        guven_final = max(0.0, min(1.0, guven))
        
        if guven_final >= self.min_guven:
            sonuclar.append({
                "dosya": py_dosya,
                "rel_yol": rel,
                "satir_no": lineno,
                "exc_tipi": exc_tipi,
                "exc_metni": exc_metni,
                "context": context,
                "guven": guven_final,
                "log_varmi": log_var or log_var_str,
                "logger_tanimli": logger_tanimli,
                "logging_import_var": logging_import_var,
                "print_varmi": print_var or print_var_str,
                "ek_kod_var": ek_kod_var,
            })
            self.istatistik["bulunan"] += 1
        else:
            self.istatistik["dusuk_guven"] += 1


# ── Düzeltme Motoru ──────────────────────────────────────────────────────

class OtonomDuzenleyici:
    """
    Sessiz except bloklarını otomatik düzeltir.
    
    Her değişiklik öncesi:
    1. Orijinal dosyanın yedeğini alır
    2. logger.warning ekler
    3. Syntax kontrolü yapar
    4. Başarısız olursa geri alır
    """
    
    def __init__(self, yedek_dizini: Path = YEDEK_DIZINI):
        self.yedek_dizini = yedek_dizini
        self.yedek_dizini.mkdir(parents=True, exist_ok=True)
        self.istatistik = {
            "duzeltilen": 0,
            "atlanan": 0,
            "hata": 0,
            "geri_alindi": 0,
        }
        self.degisiklikler: list[dict] = []
    
    def duzelt(self, bulgular: list[dict], dry_run: bool = False) -> list[dict]:
        """
        Bulguları düzelt.
        
        Args:
            bulgular: SessizExceptBulucu.tara() çıktısı
            dry_run: True ise hiçbir şey değiştirme, sadece raporla
        
        Returns:
            Değişiklik log'ları
        """
        self.degisiklikler = []
        
        # Dosya bazında grupla
        dosya_bazli: dict[str, list[dict]] = defaultdict(list)
        for b in bulgular:
            dosya_bazli[b["rel_yol"]].append(b)
        
        for rel_yol, noktalar in sorted(dosya_bazli.items()):
            if dry_run:
                for n in noktalar:
                    self.degisiklikler.append({
                        "durum": "dry_run",
                        "rel_yol": rel_yol,
                        "satir_no": n["satir_no"],
                        "exc_tipi": n["exc_tipi"],
                        "mesaj": f"[DRY-RUN] {rel_yol}:L{n['satir_no']} — {n['exc_tipi']}",
                    })
                continue
            
            try:
                self._duzelt_dosya(rel_yol, noktalar)
            except Exception as e:
                self.istatistik["hata"] += 1
                logger.error("[Fix] %s basarisiz: %s", rel_yol, e)
                self.degisiklikler.append({
                    "durum": "hata",
                    "rel_yol": rel_yol,
                    "hata": str(e),
                })
        
        return self.degisiklikler
    
    def _duzelt_dosya(self, rel_yol: str, noktalar: list[dict]):
        """Tek dosyadaki tüm sessiz except'leri düzelt."""
        dosya_yol = PROJE_KOK / rel_yol
        
        if not dosya_yol.exists():
            logger.warning("[Fix] Dosya bulunamadi: %s", rel_yol)
            self.istatistik["atlanan"] += 1
            return
        
        # Yedek al
        zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
        sep_replacement = "_"
        yedek_ad = f"{rel_yol.replace('/', sep_replacement).replace(os.sep, sep_replacement)}_{zaman}.bak"
        yedek_yol = self.yedek_dizini / yedek_ad
        yedek_yol.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(dosya_yol, yedek_yol)
        except OSError as e:
            logger.error("[Fix] Yedek alinamadi %s: %s", rel_yol, e)
            self.istatistik["hata"] += 1
            return
        
        # İçeriği oku
        icerik = dosya_yol.read_text(encoding="utf-8", errors="replace")
        orijinal = icerik
        satirlar = icerik.split('\n')
        
        # Değişiklikleri ters sırada uygula (satır numaraları kaymasın)
        degisen_satirlar = []
        logger_tanimli = _logger_var_mi(icerik)
        logging_import_var = _logging_import_var_mi(icerik)
        
        for n in sorted(noktalar, key=lambda x: x["satir_no"], reverse=True):
            lineno = n["satir_no"]
            exc_tipi = n["exc_tipi"]
            
            # Exception adını çıkar
            exc_ad = "Exception"
            if exc_tipi.startswith("except ") and exc_tipi.endswith(":"):
                exc_ad = exc_tipi[7:-1].strip()
                # Birden çok exception varsa ilkini al
                if '(' in exc_ad:
                    exc_ad = exc_ad.strip('()').split(',')[0].strip()
            
            # Hata mesajı
            mesaj = _hata_mesaji_olustur(rel_yol, exc_tipi, lineno)
            
            # logger.warning satırını oluştur
            if exc_ad.startswith('('):
                log_satiri = f"            logger.warning(\"{mesaj}\", {exc_ad[1:-1].split(',')[0].strip()})"
            else:
                log_satiri = f"            logger.warning(\"{mesaj}\", {exc_ad})"
            
            # "as e" kısmını kontrol et - yoksa ekle
            exc_satir = satirlar[lineno - 1]
            
            if " as " not in exc_satir:
                # as _e ekle
                if exc_tipi == "except:":
                    exc_satir_yeni = "except Exception as _e:"
                    log_satiri = f"            logger.warning(\"{mesaj}\", _e)"
                else:
                    # Son ":" dan önce " as _e" ekle
                    colon_pos = exc_satir.rfind(':')
                    if colon_pos != -1:
                        exc_satir_yeni = exc_satir[:colon_pos] + " as _e:"
                        # Boşlukları temizle
                        exc_satir_yeni = re.sub(r'\s+as\s+_e', ' as _e', exc_satir_yeni)
                    else:
                        continue
                
                satirlar[lineno - 1] = exc_satir_yeni
                degisen_satirlar.append(lineno)
            
            # logger.warning satırını pass'ten önce ekle
            # pass'ten önceki satırı bul
            for i in range(lineno, min(lineno + 5, len(satirlar))):
                if satirlar[i].strip() == 'pass' or satirlar[i].strip().startswith('pass #'):
                    # logger.warning satırını pass'ten önce yerleştir
                    # Aynı girintiyi kullan
                    girinti = re.match(r'^(\s*)', satirlar[i]).group(1)
                    log_satiri_indent = girinti + "logger.warning(" + log_satiri.split("logger.warning(")[1]
                    satirlar.insert(i, log_satiri_indent)
                    degisen_satirlar.append(i + 1)
                    break
        
        # import logging yoksa ekle
        if not logging_import_var and degisen_satirlar:
            # İlk import'dan sonra veya dosya başına ekle
            import_satiri = 0
            for i, satir in enumerate(satirlar):
                if satir.startswith('import ') or satir.startswith('from '):
                    import_satiri = i + 1
            
            # logger = logging.getLogger(__name__) ekle
            if not logger_tanimli:
                logger_def = "logger = logging.getLogger(__name__)"
                # import logging var mı kontrol et
                has_logging_import = any(
                    re.match(r'^\s*import\s+logging\s*$', s) for s in satirlar
                )
                if not has_logging_import:
                    satirlar.insert(import_satiri, "import logging")
                    import_satiri += 1
                    degisen_satirlar.append(import_satiri)
                
                # logger tanımını import'lardan sonra ekle
                satirlar.insert(import_satiri, "")
                satirlar.insert(import_satiri + 1, logger_def)
                degisen_satirlar.append(import_satiri + 1)
        
        if not degisen_satirlar:
            # Hiçbir değişiklik yapılmadı
            return
        
        # Yeni içerik
        yeni_icerik = '\n'.join(satirlar)
        
        # Syntax kontrolü
        gecici = Path(tempfile.mktemp(suffix=".py"))
        try:
            gecici.write_text(yeni_icerik, encoding="utf-8")
            syntax_ok, syntax_hata = _python_syntax_kontrol(gecici)
            if not syntax_ok:
                logger.error(
                    "[Fix] Syntax hatasi %s: %s — Geri aliniyor",
                    rel_yol, syntax_hata
                )
                # Geri al
                orijinal_dosya = dosya_yol  # zaten değişmedi, yedekten geri yüklemeye gerek yok
                self.istatistik["geri_alindi"] += 1
                self.degisiklikler.append({
                    "durum": "geri_alindi",
                    "rel_yol": rel_yol,
                    "hata": syntax_hata,
                })
                return
        finally:
            if gecici.exists():
                gecici.unlink()
        
        # Değişikliği uygula
        dosya_yol.write_text(yeni_icerik, encoding="utf-8")
        
        # Diff oluştur
        diff = list(difflib.unified_diff(
            orijinal.splitlines(keepends=True),
            yeni_icerik.splitlines(keepends=True),
            fromfile=f"a/{rel_yol}",
            tofile=f"b/{rel_yol}",
            n=2,
        ))
        
        self.istatistik["duzeltilen"] += len(noktalar)
        
        logger.info(
            "[Fix] ✅ %s — %d nokta duzeltildi",
            rel_yol, len(noktalar)
        )
        
        self.degisiklikler.append({
            "durum": "duzeltildi",
            "rel_yol": rel_yol,
            "satir_sayisi": len(noktalar),
            "satirlar": degisen_satirlar,
            "diff": ''.join(diff),
            "yedek": str(yedek_yol),
        })


# ── Raporlama ────────────────────────────────────────────────────────────

def rapor_olustur(
    bulgular: list[dict],
    degisiklikler: list[dict],
    istatistik: dict,
    dry_run: bool = False,
) -> str:
    """İnsan tarafından okunabilir rapor oluştur."""
    
    satirlar = []
    satirlar.append("# 🤖 Otonom Fix Raporu")
    satirlar.append(f"**Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    satirlar.append(f"**Mod:** {'DRY-RUN (sadece tarama)' if dry_run else 'DUZELTME'}")
    satirlar.append("")
    
    # Özet
    satirlar.append("## 📊 Özet")
    satirlar.append("")
    
    if dry_run:
        satirlar.append(f"| Metrik | Değer |")
        satirlar.append(f"|--------|------:|")
        satirlar.append(f"| Taranan dosya | {istatistik.get('bulunan', 0)} |")
        satirlar.append(f"| Sessiz except | {len(bulgular)} |")
        satirlar.append(f"| Düşük güven (atlandı) | {istatistik.get('dusuk_guven', 0)} |")
    else:
        satirlar.append(f"| Metrik | Değer |")
        satirlar.append(f"|--------|------:|")
        satirlar.append(f"| Bulunan sessiz except | {len(bulgular)} |")
        satirlar.append(f"| Düzeltilen | {istatistik.get('duzeltilen', 0)} |")
        satirlar.append(f"| Atlanan | {istatistik.get('atlanan', 0)} |")
        satirlar.append(f"| Hata | {istatistik.get('hata', 0)} |")
        satirlar.append(f"| Geri alınan | {istatistik.get('geri_alindi', 0)} |")
    
    satirlar.append("")
    
    # Dosya bazında detay
    satirlar.append("## 📁 Dosya Bazında Detay")
    satirlar.append("")
    
    # Grupla
    dosya_grup: dict[str, list[dict]] = defaultdict(list)
    for b in bulgular:
        dosya_grup[b["rel_yol"]].append(b)
    
    for rel_yol, noktalar in sorted(dosya_grup.items()):
        durum_ikon = "✅" if any(
            d["durum"] == "duzeltildi" and d["rel_yol"] == rel_yol
            for d in degisiklikler
        ) else "📋"
        
        satirlar.append(f"### {durum_ikon} `{rel_yol}` ({len(noktalar)} nokta)")
        satirlar.append("")
        satirlar.append("| Satır | Tür | Güven |")
        satirlar.append("|:----:|:----|:----:|")
        
        for n in noktalar:
            guven_yuzde = f"%{n['guven']*100:.0f}"
            satirlar.append(f"| {n['satir_no']} | `{n['exc_tipi']}` | {guven_yuzde} |")
        
        satirlar.append("")
    
    # Hatalar
    hatalar = [d for d in degisiklikler if d.get("durum") in ("hata", "geri_alindi")]
    if hatalar:
        satirlar.append("## ❌ Hatalar")
        satirlar.append("")
        for h in hatalar:
            satirlar.append(f"- `{h['rel_yol']}`: {h.get('hata', 'bilinmiyor')}")
        satirlar.append("")
    
    return '\n'.join(satirlar)


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    """Ana CLI giriş noktası."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Otonom Sessiz Except Düzeltici",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Örnekler:
              python _otonom_fix.py                    # Tarama + düzeltme
              python _otonom_fix.py --dry-run          # Sadece rapor
              python _otonom_fix.py --cron             # Cron modu
              python _otonom_fix.py --dizin reymen/arac  # Belirli dizin
        """),
    )
    
    parser.add_argument(
        "--dizin", "-d",
        default="reymen",
        help="Taranacak dizin (varsayılan: reymen)",
    )
    
    parser.add_argument(
        "--proje", "-p",
        default=None,
        help="Proje kok dizini (varsayilan: scriptin bulundugu klasor)",
    )
    
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Sadece tara, hiçbir şey değiştirme",
    )
    
    parser.add_argument(
        "--cron",
        action="store_true",
        help="Cron modu (sessiz, sadece değişiklik varsa rapor)",
    )
    
    parser.add_argument(
        "--min-guven",
        type=float,
        default=MIN_GUVEN,
        help=f"Minimum güven skoru (varsayılan: {MIN_GUVEN})",
    )
    
    parser.add_argument(
        "--cikti",
        choices=["terminal", "dosya", "hermes"],
        default="terminal",
        help="Rapor çıktısı hedefi",
    )
    
    args = parser.parse_args()
    
    # Cron modu: logging seviyesini artır
    if args.cron:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Proje kokunu guncelle
    global PROJE_KOK
    if args.proje:
        PROJE_KOK = Path(args.proje).resolve()
    
    baslangic = time.time()
    
    # 1. TARA
    logger.info("🔍 Tarama basliyor: %s/", args.dizin)
    tarama_dizini = PROJE_KOK / args.dizin
    bulucu = SessizExceptBulucu(min_guven=args.min_guven)
    bulgular = bulucu.tara(str(tarama_dizini))
    
    sure_tara = time.time() - baslangic
    
    logger.info(
        "📋 Tarama tamam: %d nokta (%.1fs), %d zaten log'lu atlandi, %d dusuk guven",
        len(bulgular),
        sure_tara,
        bulucu.istatistik.get("zaten_log_var", 0),
        bulucu.istatistik.get("dusuk_guven", 0),
    )
    
    if not bulgular:
        if args.cron:
            # Cron modu: hiçbir şey yapma, sessiz çık
            return
        
        logger.info("✅ Tüm except bloklari temiz! Isleme gerek yok.")
        return
    
    # 2. DÜZELT
    duzenleyici = OtonomDuzenleyici()
    degisiklikler = duzenleyici.duzelt(bulgular, dry_run=args.dry_run)
    
    sure_toplam = time.time() - baslangic
    
    # Cron modu: sadece değişiklik varsa raporla
    if args.cron:
        if duzenleyici.istatistik["duzeltilen"] == 0:
            return  # sessiz çık
    
    # 3. RAPORLA
    rapor = rapor_olustur(
        bulgular,
        degisiklikler,
        duzenleyici.istatistik,
        dry_run=args.dry_run,
    )
    
    print(f"\n{rapor}")
    
    logger.info(
        "🏁 %s tamam: %d duzeltildi (%.1fs)",
        "DRY-RUN" if args.dry_run else "FIX",
        duzenleyici.istatistik["duzeltilen"],
        sure_toplam,
    )


if __name__ == "__main__":
    main()
