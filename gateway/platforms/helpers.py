# -*- coding: utf-8 -*-
"""gateway/platforms/helpers.py — Platform Yardimci Fonksiyonlar.

Mesaj formatlama, medya yukleme, retry mekanizmasi.
Tum platformlarin kullanabilecegi ortak fonksiyonlar.
"""

import os
import time
import logging
import functools

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. RETRY MEKANIZMASI
# ---------------------------------------------------------------------------

def retry(max_deneme: int = 3, bekle: float = 1.0, geri_cek: float = 2.0,
          hata_tipleri: tuple = (Exception,)):
    """Decorator: basarisiz islemleri belirli araliklarla tekrar dener.

    Args:
        max_deneme: Maksimum deneme sayisi (varsayilan: 3)
        bekle: Ilk deneme sonrasi bekleme suresi (saniye, varsayilan: 1.0)
        geri_cek: Her basarisiz denemede bekleme suresinin carpani (varsayilan: 2.0)
        hata_tipleri: Yakalanacak hata tipleri (varsayilan: (Exception,))

    Returns:
        Decorator ile sarilmis fonksiyon
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            son_hata = None
            bekleme = bekle
            for deneme in range(1, max_deneme + 1):
                try:
                    return func(*args, **kwargs)
                except hata_tipleri as e:
                    son_hata = e
                    if deneme < max_deneme:
                        logger.warning(
                            "%s basarisiz (deneme %d/%d): %s. %d sn bekleniyor...",
                            func.__name__, deneme, max_deneme, e, bekleme
                        )
                        time.sleep(bekleme)
                        bekleme *= geri_cek
                    else:
                        logger.error(
                            "%s tamamen basarisiz (%d deneme): %s",
                            func.__name__, max_deneme, e
                        )
            raise son_hata
        return wrapper
    return decorator


def retry_send_message(send_func, hedef: str, mesaj: str,
                       max_deneme: int = 3, **kwargs) -> dict:
    """send_message fonksiyonunu retry ile calistir.

    Args:
        send_func: send_message fonksiyonu
        hedef: Mesaj hedefi
        mesaj: Mesaj icerigi
        max_deneme: Maksimum deneme sayisi

    Returns:
        dict: {"durum": "basarili", ...} veya {"durum": "hata", ...}
    """
    sonuc = None
    for deneme in range(1, max_deneme + 1):
        sonuc = send_func(hedef, mesaj, **kwargs)
        if sonuc.get("durum") == "basarili":
            return sonuc
        if deneme < max_deneme:
            logger.warning(
                "retry_send_message: %s basarisiz (deneme %d/%d). Bekleniyor...",
                hedef, deneme, max_deneme
            )
            time.sleep(1.0 * deneme)
    return sonuc or {"durum": "hata", "hata": "retry_send_message: tum denemeler basarisiz."}


# ---------------------------------------------------------------------------
# 2. MESAJ FORMATLAMA
# ---------------------------------------------------------------------------

def mesaj_kisalt(mesaj: str, max_uzunluk: int = 4000) -> str:
    """Mesaji belirtilen maksimum uzunluga kisalt.

    Args:
        mesaj: Orijinal mesaj
        max_uzunluk: Maksimum karakter sayisi (varsayilan: 4000)

    Returns:
        str: Kisaltilmis mesaj
    """
    if len(mesaj) <= max_uzunluk:
        return mesaj
    return mesaj[:max_uzunluk - 3] + "..."


def mesaj_istege_cevir(mesaj: str, tur: str = "md") -> str:
    """Mesaji platforma uygun formata cevir.

    Args:
        mesaj: Ham mesaj
        tur: Format turu ("md" / "html" / "plain")

    Returns:
        str: Formatlanmis mesaj
    """
    if tur == "plain":
        # Markdown/isaretleme karakterlerini temizle
        import re
        temiz = re.sub(r'[*_~`#>|\[\]()!-]', '', mesaj)
        return temiz.strip()
    if tur == "html":
        # Basit HTML karsiligi (istege bagli)
        import re
        mesaj = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', mesaj)
        mesaj = re.sub(r'\*(.+?)\*', r'<i>\1</i>', mesaj)
        mesaj = re.sub(r'`(.+?)`', r'<code>\1</code>', mesaj)
        return mesaj
    # Varsayilan: markdown (dokunma)
    return mesaj


def mesaj_parcala(mesaj: str, max_parca: int = 4000) -> list:
    """Uzun mesaji platform sinirina uygun parcaciklara bol.

    Args:
        mesaj: Bolunecek mesaj
        max_parca: Her parcanin maksimum uzunlugu

    Returns:
        list: Mesaj parcaciklari
    """
    if len(mesaj) <= max_parca:
        return [mesaj]

    parcaciklar = []
    for i in range(0, len(mesaj), max_parca):
        parcaciklar.append(mesaj[i:i + max_parca])
    return parcaciklar


def mesaj_birlestir(mesajlar: list, ayrac: str = "\n\n") -> str:
    """Birden fazla mesaji birlestir.

    Args:
        mesajlar: Mesaj listesi
        ayrac: Mesajlar arasina eklenecek ayrac

    Returns:
        str: Birlestirilmis mesaj
    """
    return ayrac.join(str(m) for m in mesajlar if m)


# ---------------------------------------------------------------------------
# 3. MEDYA YUKLEME
# ---------------------------------------------------------------------------

def medya_yukle(url: str, hedef_klasor: str = None, timeout: int = 30) -> dict:
    """URL'den medya dosyasi indir.

    Args:
        url: Medya URL'si
        hedef_klasor: Kayit klasoru (None = gecici dizin)
        timeout: Istek zamanimasi (saniye)

    Returns:
        dict: {"durum": "basarili", "dosya": "...", "tur": "..."}
              veya {"durum": "hata", "hata": "..."}
    """
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    if not url:
        return {"durum": "hata", "hata": "URL gerekli."}

    try:
        r = requests.get(url, timeout=timeout, stream=True)
        r.raise_for_status()

        # Dosya turu
        content_type = r.headers.get("Content-Type", "").lower()
        if "image" in content_type:
            uzanti = content_type.split("/")[-1]
        elif "audio" in content_type:
            uzanti = content_type.split("/")[-1]
        elif "video" in content_type:
            uzanti = content_type.split("/")[-1]
        else:
            uzanti = "bin"

        # Hedef klasor
        if hedef_klasor:
            os.makedirs(hedef_klasor, exist_ok=True)
        else:
            import tempfile
            hedef_klasor = tempfile.gettempdir()

        dosya_adi = f"media_{int(time.time())}.{uzanti}"
        dosya_yolu = os.path.join(hedef_klasor, dosya_adi)

        with open(dosya_yolu, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        return {
            "durum": "basarili",
            "dosya": dosya_yolu,
            "tur": content_type,
            "boyut": os.path.getsize(dosya_yolu),
        }
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def medya_sil(dosya_yolu: str) -> bool:
    """Gecici medya dosyasini sil.

    Args:
        dosya_yolu: Silinecek dosya yolu

    Returns:
        bool: Basarili ise True
    """
    try:
        if os.path.isfile(dosya_yolu):
            os.remove(dosya_yolu)
            return True
        return False
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 4. MESAJ TEKRAR ÖNLEME (MessageDeduplicator)
# ---------------------------------------------------------------------------

import threading


class MessageDeduplicator:
    """Set tabanlı, thread-safe mesaj tekrar önleme sınıfı.

    Aynı mesaj ID'sinin veya içeriğinin kısa süre içinde birden fazla
    kez işlenmesini engeller. Varsayılan olarak 300 saniye (5 dakika)
    sonra girişleri otomatik temizler.
    """

    def __init__(self, timeout: float = 300.0):
        """
        Args:
            timeout: Bir mesaj ID'sinin hafızada tutulma süresi (saniye).
        """
        self._lock = threading.Lock()
        self._seen: dict[str, float] = {}
        self._timeout = timeout

    def seen(self, message_id: str) -> bool:
        """Belirtilen mesaj ID'si daha önce görüldü mü?

        Eğer görülmediyse kaydeder ve False döner.
        Eğer görüldüyse True döner (tekrar önleme).

        Args:
            message_id: Kontrol edilecek mesaj ID'si.

        Returns:
            bool: Daha önce görüldüyse True, yeni ise False.
        """
        with self._lock:
            now = time.time()
            self._temizle(now)
            if message_id in self._seen:
                return True
            self._seen[message_id] = now
            return False

    def check(self, message_id: str) -> bool:
        """Belirtilen mesaj ID'si daha önce görüldü mü? (salt okunur, kaydetmez)

        `seen()`'den farkı: mesajı kaydetmez, sadece kontrol eder.

        Args:
            message_id: Kontrol edilecek mesaj ID'si.

        Returns:
            bool: Daha önce görüldüyse True, yeni ise False.
        """
        with self._lock:
            now = time.time()
            self._temizle(now)
            return message_id in self._seen

    def forget(self, message_id: str) -> None:
        """Belirtilen mesaj ID'sini hafızadan sil.

        Args:
            message_id: Silinecek mesaj ID'si.
        """
        with self._lock:
            self._seen.pop(message_id, None)

    def clear(self) -> None:
        """Tüm görülen mesaj kayıtlarını temizle."""
        with self._lock:
            self._seen.clear()

    def _temizle(self, now: float) -> None:
        """Zaman aşımına uğramış girişleri temizle (iç kullanım, lock çağıranın elinde)."""
        sinir = now - self._timeout
        eski = [kid for kid, ktime in self._seen.items() if ktime < sinir]
        for kid in eski:
            del self._seen[kid]

    @property
    def count(self) -> int:
        """Hafızadaki toplam mesaj ID'si sayısı."""
        with self._lock:
            return len(self._seen)

    def __len__(self) -> int:
        return self.count

    def __contains__(self, message_id: str) -> bool:
        return self.check(message_id)

    def is_duplicate(self, message_id: str) -> bool:
        """Alias for seen() — compatible with test API."""
        return self.seen(message_id)

    def __repr__(self) -> str:
        return f"<MessageDeduplicator count={self.count} timeout={self._timeout}>"


# ---------------------------------------------------------------------------
# 5. PLATFORM DOGRULAMA
# ---------------------------------------------------------------------------

def platform_dogrula(env_anahtarlari: list, mesaj: bool = True) -> dict:
    """Platform icin gerekli ortam degiskenlerini kontrol et.

    Args:
        env_anahtarlari: Kontrol edilecek ortam degiskeni adlari
        mesaj: Eksik anahtarlari mesaj olarak ekle (varsayilan: True)

    Returns:
        dict: {"durum": "basarili"} veya {"durum": "hata", "eksikler": [...]}
    """
    eksikler = [k for k in env_anahtarlari if not os.environ.get(k, "")]
    if eksikler:
        sonuc = {"durum": "hata", "eksikler": eksikler}
        if mesaj:
            sonuc["hata"] = f"Eksik ortam degiskenleri: {', '.join(eksikler)}"
        return sonuc
    return {"durum": "basarili"}


def env_al(anahtar: str, varsayilan: str = "") -> str:
    """Ortam degiskenini guvenle al.

    Args:
        anahtar: Ortam degiskeni adi
        varsayilan: Varsayilan deger

    Returns:
        str: Deger veya varsayilan
    """
    return os.environ.get(anahtar, varsayilan)


def __ping_yardim() -> bool:
    """Helpers modulu icin ping — her zaman True (yardimci fonksiyonlar her zaman hazir)."""
    return True


# ---------------------------------------------------------------------------
# 6. THREAD KATILIM TAKİBİ (Discord vb. için)
# ---------------------------------------------------------------------------

class ThreadParticipationTracker:
    """Thread bazlı katılım takibi — discord gibi thread destekli platformlar için.

    Bir kullanıcının belirli bir thread'de daha önce konuşup konuşmadığını
    takip eder; ilk katılımda welcome mesajı göndermek gibi senaryolar için.
    """

    def __init__(self, platform_ad: str = "", platform: str = "", **kwargs):
        self._platform = platform or platform_ad
        self._lock = threading.Lock()
        self._katilimlar: dict[str, set] = {}  # thread_id → {user_id, ...}
        self._marked: set = set()

    def ilk_kez_mi(self, thread_id: str, user_id: str) -> bool:
        """Kullanıcı bu thread'e ilk kez mi katılıyor?

        True dönerse kaydeder; sonraki çağrılarda False döner.
        """
        with self._lock:
            katilimcilar = self._katilimlar.setdefault(thread_id, set())
            if user_id in katilimcilar:
                return False
            katilimcilar.add(user_id)
            return True

    def temizle(self, thread_id: str | None = None) -> None:
        """Thread katılım kayıtlarını temizle."""
        with self._lock:
            if thread_id:
                self._katilimlar.pop(thread_id, None)
            else:
                self._katilimlar.clear()

    def mark(self, thread_id: str) -> None:
        with self._lock:
            self._marked.add(thread_id)

    def __contains__(self, thread_id: str) -> bool:
        with self._lock:
            return thread_id in self._marked

    def __len__(self) -> int:
        with self._lock:
            return len(self._marked)

    def _state_path(self):
        import pathlib
        base = os.environ.get("HERMES_HOME") or os.environ.get("HOME", "/tmp")
        return pathlib.Path(base) / f"{self._platform}_threads.json"

    def __repr__(self) -> str:
        return (f"<ThreadParticipationTracker platform={self._platform!r} "
                f"threads={len(self._katilimlar)}>")


# ---------------------------------------------------------------------------
# 7. MARKDOWN TEMİZLEYİCİ
# ---------------------------------------------------------------------------

def strip_markdown(text: str) -> str:
    """Markdown biçimlendirmesini metinden kaldır.

    Kalın, italik, kod blokları, başlıklar, bağlantılar ve liste
    işaretlerini temizler; düz metin döndürür.

    Args:
        text: Temizlenecek metin.

    Returns:
        str: Düz metin (markdown işaretleri kaldırılmış).
    """
    import re
    # Kod blokları (fence kaldır, içeriği koru)
    text = re.sub(r'```\w*\n?([\s\S]*?)```', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Kalın / italik / strikethrough
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}(.*?)_{1,3}', r'\1', text)
    text = re.sub(r'~~(.*?)~~', r'\1', text)
    # Başlıklar
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Bağlantılar ve görseller
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Liste işaretleri
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # Alıntı blokları
    text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)
    return text.strip()


# Modul seviyesinde ping (helpers her zaman calisir)
def ping() -> bool:
    """Helpers modulu kullanilabilirlik kontrolu.

    Returns:
        bool: Her zaman True (yardimci fonksiyonlar bagimsiz calisir)
    """
    return True
