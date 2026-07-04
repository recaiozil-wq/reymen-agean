# -*- coding: utf-8 -*-
"""db_config.py — Merkezi Veritabanı Yol Sabitleri.

DB_KONSOLIDASYON_RAPORU.md'de tespit edilen dağınıklığın (20+ DB dosyası,
7 kategori, ~230MB kopya) çözümü: tüm botların ve modüllerin tek bir
kaynaktan DB yolu okuması.

Kullanım:
    from reymen.sistem.db_config import DB

    conn = sqlite3.connect(DB["analitik"])

Not: Bu dosya sadece YOL tanımlar, bağlantı açmaz. Bağlantı açma/kapama
sorumluluğu çağıran modüldedir (özellikle thread/async ortamlarda
sqlite3 bağlantılarının paylaşılmaması gerekir).
"""

from pathlib import Path

# ── Tek merkez kök dizin (rapordaki "Önerilen Yapı" ile birebir) ──────
PROJE_KOK = Path(__file__).resolve().parents[2]  # reymen/sistem/ -> proje kökü
DB_KOK = PROJE_KOK / ".ReYMeN" / "db"
DB_KOK.mkdir(parents=True, exist_ok=True)

# ── Tüm botların (Pasa_38, Kiral38, ReYMeN_ReYMeNbot, DiscordBot) ─────
# ── ortak kullandığı tekil DB yolları ─────────────────────────────────
# NOT: DB dedupe (Item 6) sonrası 25→12 DB'ye düşürüldü.
# Eski dağınık DB'ler .old sonekiyle işaretlendi, kodda hala eski yolu
# kullanan bölümler varsa bu sözlükteki canonical yola yönlendirilmelidir.
DB = {
    "session": DB_KOK / "session.db",
    "ogrenmeler": DB_KOK / "ogrenme_merkezi.db",  # OnceHafiza — merged
    "skills_index": DB_KOK / "skills.db",          # merged with skill_library
    "hafiza": DB_KOK / "hafiza.db",
    "self_improve": DB_KOK / "analitik_merkezi.db",  # merged with analitik + execution_log
    "continuous_learning": DB_KOK / "cereyan.db",    # merged with nudge_model + steering
    "analitik": DB_KOK / "analitik_merkezi.db",      # merged with self_improve + execution_log
    "karar": DB_KOK / "karar.db",
    # ── Yeni consolidated DB'ler ──
    "auth": DB_KOK / "auth.db",                      # auth + oauth + audit_log
    "cozum_merkezi": DB_KOK / "cozum_merkezi.db",    # hatalar + memory + cozum_hafizasi + hata_toplama
    "cereyan": DB_KOK / "cereyan.db",                # continuous_learning + nudge + steering
    "skills": DB_KOK / "skills.db",                  # skills_index + skill_library
}


def db_yolu(anahtar: str) -> str:
    """Verilen mantıksal isim için DB dosya yolunu str olarak döner.

    Bilinmeyen bir anahtar istenirse KeyError fırlatır — sessizce yeni bir
    dosya türetmek, raporun tespit ettiği "kopya DB" sorununu tekrar
    üretir, bu yüzden burada kasıtlı olarak izin verilmiyor.
    """
    if anahtar not in DB:
        raise KeyError(
            f"'{anahtar}' tanımlı değil. Yeni bir DB kategorisi gerekiyorsa "
            f"önce DB_KONSOLIDASYON_RAPORU.md'yi ve bu dosyadaki DB sözlüğünü "
            f"güncelle, koddan doğrudan yol türetme."
        )
    return str(DB[anahtar])


__all__ = ["DB", "DB_KOK", "db_yolu"]
