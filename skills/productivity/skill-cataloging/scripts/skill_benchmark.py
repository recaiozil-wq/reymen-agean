#!/usr/bin/env python3
"""
Skill Benchmark v2 — Derinlemesine İçerik Analizi
==================================================
Tüm SKILL.md dosyalarını tarar ve CSV rapor + özet çıkarır.

Kullanım:
    python skill_benchmark.py                              # skills/ klasörünü tara
    python skill_benchmark.py --path ./skills              # özel yol
    python skill_benchmark.py --csv rapor.csv --min 300    # minimum 300 satır
"""

import csv
import re
import sys
import argparse
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

# ─── KONFİGÜRASYON ────────────────────────────────────────────────
SISKIN_SINIRI_BYTE = 10 * 1024       # 10 KB
SISKIN_SINIRI_SATIR = 300             # 300 satır
SISKIN_SINIRI_TOKEN_TAHMİN = 2500    # ~2500 token (4 char/token)

# Anahtar kelime grupları — potansiyel kopya tespiti için
KONU_KUMELERI = [
    ["yedek", "backup", "sync", "senkronizasyon"],
    ["arama", "search", "araştır", "research"],
    ["güvenlik", "security", "safety", "guvenlik"],
    ["test", "testing", "tdd", "test-driven"],
    ["deploy", "deployment", "yayınla", "release"],
    ["monitor", "monitoring", "izle", "watch", "gözlem"],
    ["cleanup", "temizlik", "clean", "sil"],
    ["git", "github", "pull", "push", "commit"],
    ["docker", "container", "image"],
    ["api", "rest", "endpoint", "graphql"],
    ["auth", "login", "kimlik", "token", "credential"],
    ["log", "logging", "kayıt", "logger"],
    ["config", "yapılandırma", "setting", "ayar"],
    ["error", "hata", "exception", "try", "catch"],
    ["veri", "data", "database", "db", "sql"],
    ["network", "ağ", "ag", "bağlantı", "connection"],
    ["email", "mail", "posta", "e-posta"],
    ["not", "note", "obsidian", "vault"],
    ["video", "mp4", "ekran", "screen", "capture"],
    ["audio", "ses", "sound", "mikrofon", "microphone"],
]


def parse_frontmatter(content):
    """Frontmatter'ı parse et, (dict, varsa) döndür."""
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None

    import yaml
    try:
        fm = yaml.safe_load(parts[1])
        return fm if isinstance(fm, dict) else None
    except Exception:
        return None


def count_code_blocks(content):
    """``` ile işaretlenmiş kod bloklarını say."""
    blocks = re.findall(r'```\w*\n.*?(?=```)```', content, re.DOTALL)
    opens = len(re.findall(r'^```', content, re.MULTILINE))
    return max(len(blocks), opens // 2)


def has_reference_links(content, skill_dir):
    """Skill içinde references/ klasörüne yönlendirme var mı kontrol et."""
    checks = {
        "ref_klasoru_var": (skill_dir / "references").exists(),
        "ref_link_var": bool(re.search(r'references/[\w.-]+', content)),
        "go_link_var": bool(re.search(r'→\s*(?:Bkz|See|Refer|references)', content, re.IGNORECASE)),
    }
    return checks


def token_tahmini(content):
    """Kabaca token sayısı tahmini (4 karakter ≈ 1 token)."""
    return len(content) // 4


def skor_hesapla(fm, satir_sayisi, kod_bloklari, ref_durum):
    """0-100 arası kalite skoru hesapla."""
    skor = 0

    # Frontmatter (max 40 puan)
    if fm:
        if fm.get("title"): skor += 10
        if fm.get("description") and len(fm["description"]) > 20: skor += 12
        elif fm.get("description"): skor += 6
        if fm.get("tags"): skor += 10
        if fm.get("category"): skor += 8

    # Kod bloğu (max 20 puan)
    if kod_bloklari >= 5: skor += 20
    elif kod_bloklari >= 3: skor += 15
    elif kod_bloklari >= 1: skor += 10

    # Boyut (max 20 puan) — ne çok şişkin ne çok kısa
    if 50 <= satir_sayisi <= 250:
        skor += 20
    elif satir_sayisi <= 400:
        skor += 15
    else:
        skor += 5

    # Referans (max 20 puan)
    if ref_durum.get("ref_klasoru_var"):
        skor += 20
    elif ref_durum.get("ref_link_var"):
        skor += 10

    return min(skor, 100)


def konu_benzerlik(skill_name, content, tum_isimler):
    """Aynı konudaki potansiyel kopya skill'leri bul."""
    uyarilar = []
    name_lower = skill_name.lower()

    for kume in KONU_KUMELERI:
        eslesen = [kw for kw in kume if kw in name_lower]
        if eslesen:
            for diger_isim in tum_isimler:
                if diger_isim == skill_name:
                    continue
                diger_lower = diger_isim.lower()
                diger_eslesen = [kw for kw in kume if kw in diger_lower]
                if diger_eslesen:
                    ortak = set(eslesen) & set(diger_eslesen)
                    if ortak:
                        uyarilar.append({
                            "benzer": diger_isim,
                            "ortak_kelimeler": ", ".join(ortak),
                            "kume": kume[0]
                        })

    return uyarilar


def main():
    parser = argparse.ArgumentParser(description="Skill Benchmark v2")
    parser.add_argument("--path", default=None,
                        help="Skill'lerin bulunduğu ana dizin (varsayılan: AppData/ReYMeN/skills)")
    parser.add_argument("--csv", default="skill_benchmark_raporu.csv",
                        help="CSV çıktı dosyası (varsayılan: skill_benchmark_raporu.csv)")
    parser.add_argument("--min", type=int, default=300,
                        help="Şişkinlik sınırı satır sayısı (varsayılan: 300)")
    parser.add_argument("--siskin-kb", type=int, default=10,
                        help="Şişkinlik sınırı KB (varsayılan: 10)")
    args = parser.parse_args()

    if args.path:
        kok = Path(args.path)
    else:
        kok = Path.home() / "AppData/Local/ReYMeN/skills"

    if not kok.exists():
        print(f"❌ HATA: {kok} bulunamadı!")
        sys.exit(1)

    print(f"📂 Taranıyor: {kok}")
    print(f"📊 Çıktı: {args.csv}")
    print(f"📏 Şişkinlik sınırı: {args.min} satır / {args.siskin_kb} KB")
    print()

    rows = []
    tum_isimler = []
    tum_icerikler = {}
    from collections import Counter as _Counter
    istatistik = _Counter()

    for p in sorted(kok.rglob("SKILL.md")):
        rel_path = p.relative_to(kok)
        skill_dir = p.parent
        skill_name = p.parent.name
        tum_isimler.append(skill_name)

        content = p.read_text(encoding="utf-8", errors="replace")
        tum_icerikler[skill_name] = content

        satir_sayisi = len(content.splitlines())
        byte_boyut = len(content)
        token_tahmini_deger = token_tahmini(content)

        fm = parse_frontmatter(content)
        fm_title = bool(fm and fm.get("title"))
        fm_desc = bool(fm and fm.get("description"))
        fm_tags = bool(fm and fm.get("tags"))
        fm_category = bool(fm and fm.get("category"))
        audience = (fm and fm.get("audience")) or "belirtilmemiş"

        siskin_nedeni = []
        if byte_boyut >= args.siskin_kb * 1024:
            siskin_nedeni.append(f"BOYUT({byte_boyut/1024:.0f}KB)")
        if satir_sayisi >= args.min:
            siskin_nedeni.append(f"SATIR({satir_sayisi})")
        if token_tahmini_deger >= SISKIN_SINIRI_TOKEN_TAHMİN:
            siskin_nedeni.append(f"TOKEN(~{token_tahmini_deger})")

        siskin_etiketi = "; ".join(siskin_nedeni) if siskin_nedeni else "HAYIR"

        kod_bloklari = count_code_blocks(content)
        ref_durum = has_reference_links(content, skill_dir)
        kalite_skoru = skor_hesapla(fm, satir_sayisi, kod_bloklari, ref_durum)

        rows.append({
            "skill_adi": skill_name,
            "klasor": str(rel_path.parent),
            "audience": audience,
            "satir_sayisi": satir_sayisi,
            "byte_boyut": byte_boyut,
            "kb": round(byte_boyut / 1024, 1),
            "token_tahmini": token_tahmini_deger,
            "siskin": siskin_etiketi,
            "kod_bloklari": kod_bloklari,
            "teorik": "EVET" if kod_bloklari == 0 else "HAYIR",
            "ref_klasoru_var": ref_durum["ref_klasoru_var"],
            "ref_link_var": ref_durum["ref_link_var"],
            "title_var": fm_title,
            "description_var": fm_desc,
            "tags_var": fm_tags,
            "category_var": fm_category,
            "kalite_skoru": kalite_skoru,
        })

        if siskin_nedeni: istatistik["şişkin"] += 1
        if kod_bloklari == 0: istatistik["teorik"] += 1
        if not fm_title: istatistik["eksik_title"] += 1
        if not fm_desc: istatistik["eksik_description"] += 1
        if not fm_tags: istatistik["eksik_tags"] += 1
        if not fm_category: istatistik["eksik_category"] += 1
        if ref_durum["ref_klasoru_var"]: istatistik["ref_klasoru_var"] += 1

    istatistik["toplam"] = len(rows)

    # İsim çakışması analizi
    name_count = _Counter()
    for r in rows:
        name_count[r["skill_adi"]] += 1

    cayisma_uyarilari = []
    for name, cnt in name_count.most_common():
        if cnt > 1:
            cayisma_uyarilari.append({"tip": "BIREBIR", "skill": name, "detay": f"{cnt} kopya"})

    gorulen = set()
    for r in rows:
        if r["skill_adi"] in gorulen:
            continue
        uyarilar = konu_benzerlik(r["skill_adi"], tum_icerikler.get(r["skill_adi"], ""), tum_isimler)
        for u in uyarilar:
            if u["benzer"] not in gorulen:
                cayisma_uyarilari.append({
                    "tip": "KONU",
                    "skill": f"{r['skill_adi']} ↔ {u['benzer']}",
                    "detay": f"Ortak: {u['ortak_kelimeler']}"
                })
        gorulen.add(r["skill_adi"])

    istatistik["potansiyel_kopya"] = len(cayisma_uyarilari)

    # CSV yaz
    csv_path = Path(args.csv)
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "skill_adi", "klasor", "audience", "satir_sayisi", "byte_boyut",
            "kb", "token_tahmini", "siskin", "kod_bloklari", "teorik",
            "ref_klasoru_var", "ref_link_var",
            "title_var", "description_var", "tags_var", "category_var",
            "kalite_skoru"
        ])
        writer.writeheader()
        for r in sorted(rows, key=lambda x: (-x["kalite_skoru"], x["skill_adi"])):
            writer.writerow(r)

    print(f"\n✅ CSV kaydedildi: {csv_path.resolve()}")

    # Özet rapor
    print(f"""
╔═══════════════════════════════════════════════════╗
║         SKILL BENCHMARK v2 — ÖZET RAPOR          ║
╚═══════════════════════════════════════════════════╝

📊 GENEL
   Toplam skill: {istatistik['toplam']}
   Ortalama satır: {sum(r['satir_sayisi'] for r in rows) // max(len(rows), 1)}
   Ortalama boyut: {sum(r['byte_boyut'] for r in rows) // max(len(rows), 1) // 1024} KB

🔴 ŞİŞKİN SKILL'LER (>={args.siskin_kb} KB veya >={args.min} satır)
   Toplam: {istatistik.get('şişkin', 0)}""")

    for r in rows:
        if r["siskin"] != "HAYIR":
            print(f"   - {r['skill_adi']}: {r['kb']}KB / {r['satir_sayisi']} satır")

    print(f"""
📘 TEORİK SKILL'LER (hiç kod bloğu yok)
   Toplam: {istatistik.get('teorik', 0)}""")

    for r in rows:
        if r["teorik"] == "EVET":
            print(f"   - {r['skill_adi']} ({r['audience']})")

    print(f"""
📋 FRONTMATTER EKSİKLERİ
   Eksik title: {istatistik.get('eksik_title', 0)}
   Eksik description: {istatistik.get('eksik_description', 0)}
   Eksik tags: {istatistik.get('eksik_tags', 0)}
   Eksik category: {istatistik.get('eksik_category', 0)}
   Referans kullanan: {istatistik.get('ref_klasoru_var', 0)}

⚠️  POTANSİYEL KOPYA SKILL'LER
   Toplam: {istatistik.get('potansiyel_kopya', 0)}""")

    for u in cayisma_uyarilari[:20]:
        print(f"   - [{u['tip']}] {u['skill']} ({u['detay']})")

    if len(cayisma_uyarilari) > 20:
        print(f"   ... ve {len(cayisma_uyarilari) - 20} uyarı daha (CSV'de tam liste)")

    print(f"""
👥 AUDIENCE DAĞILIMI""")
    audience_dagilim = _Counter(r["audience"] for r in rows)
    for aud, cnt in audience_dagilim.most_common():
        print(f"   {aud}: {cnt}")

    print(f"\n📄 Detaylı CSV: {csv_path.resolve()}")
    print()


if __name__ == "__main__":
    main()
