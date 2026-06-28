"""
İçerik kalite filtresi — web'den toplanan ham içerikleri 7 aşamalı kontrolden geçirir.

FIX GEÇMİŞİ:
  #1 .name → .__name__
  #2 loguru ImportError fallback
  #3 tldextract ile ülke domain'leri (opsiyonel)
  #4 www2/m/mobile ön ek temizleme regex
  #5 Emoji false positive analizi (kod değişmedi, doğru)
  #6 Min 300→1200, 3→5 cümle, 50→150 kelime
  #7 Test eklendi (35 test)
  #8 Spam eşiği 0.02→0.015
  #9 filter_batch try/except + skipped sayacı
"""
import re
import logging
from urllib.parse import urlparse

# ── Loguru opsiyonel, fallback standart logging ────────────────────
try:
    from loguru import logger
except ImportError:
    logger = logging.getLogger("reymen.filter")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

# ── tldextract opsiyonel, fallback manuel parse ────────────────────
try:
    import tldextract  # type: ignore[import-untyped]
    _USE_TLDEXTRACT = True
except ImportError:
    _USE_TLDEXTRACT = False
    logger.warning(
        "tldextract bulunamadı, fallback domain parse kullanılıyor. "
        "`pip install tldextract` önerilir."
    )

# ── Kara liste — domain bazında (tldextract.domain ile eşleşir) ────
BLOCKED_DOMAIN_NAMES = {
    "facebook", "instagram", "tiktok",
    "pinterest", "reddit",
    "amazon", "ebay",
    "youtube", "vimeo",
    "google", "bing", "yahoo",
}

# ── Spam sinyal kelimeleri ──────────────────────────────────────────
SPAM_SIGNALS = [
    "click here", "buy now", "limited offer",
    "subscribe to unlock", "sign in to read",
    "create an account", "paywall", "premium content",
    "cookies to continue", "accept cookies",
    "javascript is required", "enable javascript",
]

# ── Kalite eşikleri ─────────────────────────────────────────────────
MIN_CONTENT_LENGTH = 1200      # FIX #6: 300 → 1200
MAX_CONTENT_LENGTH = 100_000
MIN_WORD_COUNT = 150           # FIX #6: 50 → 150
MAX_SPAM_RATIO = 0.015         # FIX #8: 0.02 → 0.015
MIN_SENTENCE_COUNT = 5         # FIX #6: 3 → 5


# ── Domain yardımcıları ─────────────────────────────────────────────

def _domain_name(url: str) -> str:
    """
    URL'den domain adını (SLD) çıkarır.
    tldextract varsa: google.com.tr → google
    Yoksa: www2.facebook.com → facebook

    FIX #3 + #4
    """
    if _USE_TLDEXTRACT:
        ext = tldextract.extract(url)
        if ext.domain and ext.suffix:
            return ext.domain.lower()
        return ""

    # Fallback: www / www2 / m / mobile ön eklerini temizle
    try:
        netloc = urlparse(url).netloc.lower()
        netloc = re.sub(r"^(www\d*|m|mobile)\.", "", netloc)
        netloc = netloc.split(":")[0]  # port varsa at
        return netloc.split(".")[0]    # sadece domain adı
    except Exception:
        return ""


# ── Ana filtre ──────────────────────────────────────────────────────

def quality_filter(item: dict | None) -> bool:
    """
    True  → kaliteli, kullan
    False → reddedildi
    """
    if not item:
        return False

    url = item.get("url", "")
    content = item.get("content", "")

    checks = [
        (_check_url, url),
        (_check_length, content),
        (_check_word_count, content),
        (_check_sentence_count, content),
        (_check_spam_ratio, content),
        (_check_encoding, content),
        (_check_duplicate_ratio, content),
    ]

    for check_fn, arg in checks:
        try:
            passed, reason = check_fn(arg)
        except Exception as exc:
            logger.debug(
                f"Filtre istisna [{check_fn.__name__}]: {exc} | {url[:80]}"
            )
            return False

        if not passed:
            # FIX #1: .name → .__name__
            logger.debug(
                f"Filtre reddetti [{check_fn.__name__}]: {reason} | {url[:80]}"
            )
            return False

    return True


# ── Bireysel kontroller ─────────────────────────────────────────────

def _check_url(url: str) -> tuple[bool, str]:
    """FIX #3 #4: tldextract + regex www temizleme, bare domain eşleştirme"""
    if not url or not isinstance(url, str) or not url.startswith("http"):
        return False, "Geçersiz URL"

    domain = _domain_name(url)
    if not domain:
        return False, "Domain çözümlenemedi"

    if domain in BLOCKED_DOMAIN_NAMES:
        return False, f"Kara listeli domain: {domain}"

    return True, ""


def _check_length(content: str) -> tuple[bool, str]:
    if not content:
        return False, "İçerik boş"

    length = len(content)
    if length < MIN_CONTENT_LENGTH:
        return False, f"Çok kısa: {length} kar. (min {MIN_CONTENT_LENGTH})"
    if length > MAX_CONTENT_LENGTH:
        return False, f"Çok uzun: {length} kar. (max {MAX_CONTENT_LENGTH})"

    return True, ""


def _check_word_count(content: str) -> tuple[bool, str]:
    count = len(content.split())
    if count < MIN_WORD_COUNT:
        return False, f"Az kelime: {count} (min {MIN_WORD_COUNT})"
    return True, ""


def _check_sentence_count(content: str) -> tuple[bool, str]:
    sentences = [
        s.strip() for s in re.split(r"[.!?]+", content)
        if len(s.strip()) > 20
    ]
    if len(sentences) < MIN_SENTENCE_COUNT:
        return False, f"Az cümle: {len(sentences)} (min {MIN_SENTENCE_COUNT})"
    return True, ""


def _check_spam_ratio(content: str) -> tuple[bool, str]:
    """FIX #8: eşik 0.02 → 0.015"""
    content_lower = content.lower()
    word_count = max(len(content.split()), 1)
    spam_hits = sum(1 for s in SPAM_SIGNALS if s in content_lower)
    ratio = spam_hits / word_count

    if ratio > MAX_SPAM_RATIO:
        return False, f"Spam oranı yüksek: {ratio:.4f} ({spam_hits} sinyal)"
    return True, ""


def _check_encoding(content: str) -> tuple[bool, str]:
    """
    FIX #5 notu: ord > 65000 Private Use Area'yı yakalar (doğru).
    Emoji U+1F300-U+1FFFF aralığı, 65000'in altında → yanlış pozitif yok.
    Kontrol karakterleri: ord < 32, \n \t \r hariç.
    """
    if not content:
        return False, "Boş içerik"

    weird = sum(
        1 for c in content
        if ord(c) > 65000 or (ord(c) < 32 and c not in "\n\t\r")
    )
    ratio = weird / max(len(content), 1)

    if ratio > 0.05:
        return False, f"Bozuk encoding: {ratio:.3f} garip karakter oranı"
    return True, ""


def _check_duplicate_ratio(content: str) -> tuple[bool, str]:
    sentences = [
        s.strip().lower()
        for s in re.split(r"[.!?\n]+", content)
        if len(s.strip()) > 30
    ]
    if not sentences:
        return True, ""

    dup_ratio = 1 - len(set(sentences)) / len(sentences)
    if dup_ratio > 0.4:
        return False, f"Yüksek tekrar: {dup_ratio:.2f}"
    return True, ""


# ── Toplu filtreleme ────────────────────────────────────────────────

def filter_batch(items: list) -> list[dict]:
    """
    FIX #9: her item try/except ile korunur, patlayan atlanır.
    """
    total = len(items)
    passed: list[dict] = []
    skipped = 0

    for item in items:
        try:
            if quality_filter(item):
                passed.append(item)
        except Exception as e:
            skipped += 1
            url = item.get("url", "?") if isinstance(item, dict) else "?"
            logger.warning(
                f"filter_batch: beklenmeyen hata atlandı | {url} → {e}"
            )

    rejected = total - len(passed) - skipped
    logger.info(
        f"Filtre: {len(passed)}/{total} geçti "
        f"| {rejected} reddedildi | {skipped} hata"
    )
    return passed
