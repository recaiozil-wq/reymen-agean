#!/usr/bin/env python3
"""
Skill Shrink v1.0 — Şişkin Skill'leri Parçalama Aracı
======================================================
10KB+ veya 300+ satırlık skill'leri tespit eder,
bölümlerini references/ altına taşır.

Kullanım:
    python skill-shrink.py --scan              # sadece tara
    python skill-shrink.py --skill yol/adı     # tek skill
    python skill-shrink.py --all               # tümünü küçült
    python skill-shrink.py --csv rapor.csv     # CSV çıktı
"""

import re
import sys
import shutil
from pathlib import Path

SINIR_BYTE = 10 * 1024
SINIR_SATIR = 300

def parse_frontmatter(content):
    if not content.startswith("---"):
        return None, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content
    return parts[1], parts[2]

def bolumleri_bul(body):
    """## ve ### başlıklarını bul, her bölümün satır aralığını belirle."""
    lines = body.split("\n")
    bolumler = []
    baslangic = None
    baslik_adi = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## "):
            if baslangic is not None:
                bolumler.append((baslik_adi, baslangic, i))
            baslangic = i
            baslik_adi = stripped.replace("## ", "").strip()
        elif stripped.startswith("# ") and not stripped.startswith("##"):
            if baslangic is not None:
                bolumler.append((baslik_adi, baslangic, i))
            baslangic = i
            baslik_adi = stripped.replace("# ", "").strip()

    # Son bölüm
    if baslangic is not None:
        bolumler.append((baslik_adi, baslangic, len(lines)))

    return bolumler, lines

def slugify(text):
    """Dosya adı için güvenli hale getir."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9_]', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    return text[:60] or "bolum"

def shrink_skill(skill_path, dry_run=False):
    """Tek bir skill'i küçült."""
    skill_adi = skill_path.parent.name if skill_path.name == "SKILL.md" else skill_path.name
    skill_dir = skill_path.parent
    ref_dir = skill_dir / "references"

    content = skill_path.read_text(encoding="utf-8", errors="replace")
    byte = len(content)
    satir = len(content.splitlines())

    if byte < SINIR_BYTE and satir < SINIR_SATIR:
        return None  # şişkin değil

    fm_text, body = parse_frontmatter(content)
    if fm_text is None:
        return {"skill": skill_adi, "durum": "ATLANDI", "sebep": "frontmatter yok"}

    bolumler, lines = bolumleri_bul(body)

    if len(bolumler) <= 1:
        return {"skill": skill_adi, "durum": "ATLANDI", "sebep": "tek bölüm, bölünemez"}

    if dry_run:
        return {
            "skill": skill_adi,
            "durum": "HAZIR",
            "byte": byte,
            "satir": satir,
            "bolum": len(bolumler)
        }

    # Reference klasörünü oluştur
    if ref_dir.exists():
        try:
            shutil.rmtree(ref_dir)
        except PermissionError:
            # Windows kilitli dosya sorunu - geçici isimle taşı
            import tempfile
            temp_dir = ref_dir.parent / f".trash_{ref_dir.name}"
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            ref_dir.rename(temp_dir)
            shutil.rmtree(temp_dir, ignore_errors=True)
    ref_dir.mkdir(parents=True, exist_ok=True)

    # Her bölümü reference dosyasına yaz
    taşınan = []
    for baslik, start, end in bolumler:
        if end - start <= 2:  # sadece başlık, içerik yok
            continue
        bolum_icerik = "\n".join(lines[start:end]).strip()
        dosya_adi = f"{slugify(baslik)}.md"
        (ref_dir / dosya_adi).write_text(bolum_icerik, encoding="utf-8")
        taşınan.append((dosya_adi, baslik))

    # Yeni SKILL.md oluştur (router)
    router = f"""---
{fm_text}---

# {skill_adi.replace('-', ' ').title()}

Bu skill modüler bir yönlendiricidir. İhtiyacınız olan bölümü seçin ve ilgili reference dosyasını yükleyin.

## 📂 Bölümler

| Bölüm | Reference Dosyası |
|-------|------------------|
"""
    for dosya_adi, baslik in taşınan:
        router += f"| {baslik} | `references/{dosya_adi}` |\n"

    router += "\n## Kullanım\n\n"
    router += "1. İhtiyacın olan bölümü belirle\n"
    router += "2. `skill_view(name=\"...\", file_path=\"references/...\")` ile yükle\n"

    skill_path.write_text(router, encoding="utf-8")

    return {
        "skill": skill_adi,
        "durum": "KÜÇÜLTÜLDÜ",
        "once": f"{byte/1024:.0f}KB/{satir}satir",
        "sonra": f"{len(router)/1024:.0f}KB/{len(router.splitlines())}satir",
        "bolum": len(taşınan)
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Skill Shrink")
    parser.add_argument("--scan", action="store_true", help="Sadece tara")
    parser.add_argument("--skill", help="Tek bir skill (skills/ altındaki yolu)")
    parser.add_argument("--all", action="store_true", help="Tüm şişkin skill'leri küçült")
    parser.add_argument("--dry-run", action="store_true", help="Kuru çalıştırma (değişiklik yapma)")
    parser.add_argument("--csv", help="CSV çıktı dosyası")
    args = parser.parse_args()

    skills_dir = Path.home() / "AppData/Local/ReYMeN/skills"

    if args.skill:
        skill_path = skills_dir / args.skill
        if not skill_path.exists():
            skill_path = skills_dir / args.skill / "SKILL.md"
        if not skill_path.exists():
            print(f"❌ Skill bulunamadı: {args.skill}")
            return

        result = shrink_skill(skill_path, dry_run=args.dry_run)
        if result:
            print(f"{result['durum']}: {result['skill']}")
            for k, v in result.items():
                if k != "skill" and k != "durum":
                    print(f"  {k}: {v}")
        else:
            print("✅ Skill zaten ideal boyutta")
        return

    # Tara
    siskinler = []
    for p in sorted(skills_dir.rglob("SKILL.md")):
        content = p.read_text(encoding="utf-8", errors="replace")
        byte = len(content)
        satir = len(content.splitlines())
        if byte >= SINIR_BYTE or satir >= SINIR_SATIR:
            siskinler.append((p, byte, satir))

    siskinler.sort(key=lambda x: -x[1])  # en büyükten küçüğe

    print(f"\n🔍 Şişkin skill: {len(siskinler)} adet")
    print(f"{'Boyut':>8} {'Satır':>6}  {'Dosya'}")
    print("-" * 60)

    for p, byte, satir in siskinler:
        rel = p.relative_to(skills_dir.parent)
        print(f"{byte/1024:>7.1f}KB {satir:>5}  {rel}")

    if not args.all:
        print(f"\n💡 Tümünü küçültmek için: --all ekleyin")
        return

    # Tümünü küçült
    print(f"\n🔧 Küçültülüyor...")
    sonuclar = []
    for p, byte, satir in siskinler:
        result = shrink_skill(p, dry_run=False)
        if result:
            sonuclar.append(result)
            print(f"  {result['durum']}: {result['skill']} ({result.get('bolum', 0)} bölüm)")

    # Özet
    kucultulen = [r for r in sonuclar if r['durum'] == 'KÜÇÜLTÜLDÜ']
    atlanan = [r for r in sonuclar if r['durum'] == 'ATLANDI']
    print(f"\n✅ Küçültülen: {len(kucultulen)}")
    print(f"⏭️  Atlanan: {len(atlanan)}")

    if args.csv:
        import csv
        with open(args.csv, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=["skill", "durum", "once", "sonra", "bolum", "sebep"])
            w.writeheader()
            for r in sonuclar:
                w.writerow(r)
        print(f"📄 CSV: {args.csv}")


if __name__ == "__main__":
    main()
