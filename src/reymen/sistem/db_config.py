# -*- coding: utf-8 -*-
"""db_config.py â€” Merkezi VeritabanÄ± Yol Sabitleri.

DB_KONSOLIDASYON_RAPORU.md'de tespit edilen daÄŸÄ±nÄ±klÄ±ÄŸÄ±n (20+ DB dosyasÄ±,
7 kategori, ~230MB kopya) çözümü: tüm botlarÄ±n ve modüllerin tek bir
kaynaktan DB yolu okumasÄ±.

KullanÄ±m:
    from reymen.sistem.db_config import DB

    conn = sqlite3.connect(DB["analitik"])

Not: Bu dosya sadece YOL tanÄ±mlar, baÄŸlantÄ± açmaz. BaÄŸlantÄ± açma/kapama
sorumluluÄŸu çaÄŸÄ±ran modüldedir (özellikle thread/async ortamlarda
sqlite3 baÄŸlantÄ±larÄ±nÄ±n paylaÅŸÄ±lmamasÄ± gerekir).
"""

from pathlib import Path

# â”€â”€ Tek merkez kök dizin (rapordaki "Ã–nerilen YapÄ±" ile birebir) â”€â”€â”€â”€â”€â”€
PROJE_KOK = Path(__file__).resolve().parents[2]  # reymen/sistem/ -> proje kökü
DB_KOK = PROJE_KOK / ".ReYMeN" / "db"
DB_KOK.mkdir(parents=True, exist_ok=True)

# â”€â”€ Tüm botlarÄ±n (Pasa_38, Kiral38, ReYMeN_ReYMeNbot, DiscordBot) â”€â”€â”€â”€â”€
# â”€â”€ ortak kullandÄ±ÄŸÄ± tekil DB yollarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# NOT: DB dedupe (Item 6) sonrasÄ± 25â†’12 DB'ye düÅŸürüldü.
# Eski daÄŸÄ±nÄ±k DB'ler .old sonekiyle iÅŸaretlendi, kodda hala eski yolu
# kullanan bölümler varsa bu sözlükteki canonical yola yönlendirilmelidir.
DB = {
    "session": DB_KOK / "session.db",
    "ogrenmeler": DB_KOK / "ogrenme_merkezi.db",  # OnceHafiza â€” merged
    "skills_index": DB_KOK / "skills.db",          # merged with skill_library
    "hafiza": DB_KOK / "hafiza.db",
    "self_improve": DB_KOK / "analitik_merkezi.db",  # merged with analitik + execution_log
    "continuous_learning": DB_KOK / "cereyan.db",    # merged with nudge_model + steering
    "analitik": DB_KOK / "analitik_merkezi.db",      # merged with self_improve + execution_log
    "karar": DB_KOK / "karar.db",
    # â”€â”€ Yeni consolidated DB'ler â”€â”€
    "auth": DB_KOK / "auth.db",                      # auth + oauth + audit_log
    "cozum_merkezi": DB_KOK / "cozum_merkezi.db",    # hatalar + memory + cozum_hafizasi + hata_toplama
    "cereyan": DB_KOK / "cereyan.db",                # continuous_learning + nudge + steering
    "skills": DB_KOK / "skills.db",                  # skills_index + skill_library
}


def db_yolu(anahtar: str) -> str:
    """Verilen mantÄ±ksal isim için DB dosya yolunu str olarak döner.

    Bilinmeyen bir anahtar istenirse KeyError fÄ±rlatÄ±r â€” sessizce yeni bir
    dosya türetmek, raporun tespit ettiÄŸi "kopya DB" sorununu tekrar
    üretir, bu yüzden burada kasÄ±tlÄ± olarak izin verilmiyor.
    """
    if anahtar not in DB:
        raise KeyError(
            f"'{anahtar}' tanÄ±mlÄ± deÄŸil. Yeni bir DB kategorisi gerekiyorsa "
            f"önce DB_KONSOLIDASYON_RAPORU.md'yi ve bu dosyadaki DB sözlüÄŸünü "
            f"güncelle, koddan doÄŸrudan yol türetme."
        )
    return str(DB[anahtar])


__all__ = ["DB", "DB_KOK", "db_yolu"]
