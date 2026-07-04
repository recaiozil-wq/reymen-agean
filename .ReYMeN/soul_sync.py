#!/usr/bin/env python3
"""Her profile'ın SOUL.md'sine durum.json özetini ekle/senkronize et.
Böylece tüm botlar aynı güncel veriyi context'inde görür."""

import json, shutil
from pathlib import Path

# Profil SOUL.md yolları
PROFILLER = {
    "default": Path.home() / "AppData/Local/hermes/profiles/default/SOUL.md",
    "kiral38": Path.home() / "AppData/Local/hermes/profiles/kiral38/SOUL.md",
    "reymen": Path.home() / "AppData/Local/hermes/profiles/reymen/SOUL.md",
}

# durum.json
DURUM_JSON = Path.home() / "Desktop/Reymen Proje/ReYMeN-Ajan/durum.json"


def durum_ozeti() -> str:
    """durum.json'dan kisa bir ozet metni olustur."""
    try:
        with open(DURUM_JSON, "r", encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        return "[durum.json okunamadi]"

    toplam = d.get("toplam_ozellik", 0)
    tamam = d.get("tamam", 0)
    isleniyor = d.get("isleniyor", 0)
    guncel = d.get("son_guncelleme", "?")
    bot = d.get("guncelleyen_bot", "?")

    satirlar = [
        "",
        "## 📋 REYMeN GUNCEL DURUM (otomatik)",
        f"Son guncelleme: {guncel} ({bot})",
        f"Toplam: {tamam}/{toplam} tamam, {isleniyor} isleniyor",
        "",
        "### Eksikler (ReYMeN'te var, ReYMeN'de yok):",
    ]

    # durum.json'daki eksikleri oku
    eksikler = d.get("pasa_38_karsilastirmasi", {}).get("maddeler", [])
    if eksikler:
        for e in eksikler:
            ad = e.get("eksik", "?")
            ReYMeN = e.get("ReYMeN", "?")
            cozuldu = e.get("cozuldu_mu", "hayir")
            ikon = "✅" if cozuldu == "evet" else ("⚠️" if cozuldu == "kismen" else "❌")
            satirlar.append(f"- {ikon} {ad}: ReYMeN'te {ReYMeN}")
    else:
        satirlar.append("- (eksik listesi bos)")

    satirlar.append("")
    satirlar.append(
        "(Bu bolum otomatik eklenir. Sorulunca BURADAKI veriye gore cevap ver.)"
    )
    satirlar.append("")

    return "\n".join(satirlar)


def senkronize_et():
    """Her SOUL.md'nin sonuna durum ozetini ekle/guncelle."""
    ozet = durum_ozeti()

    # Baslangic/bitis markeri
    BASLANGIC = "\n## 📋 REYMeN GUNCEL DURUM (otomatik)"
    BITIS = "(Bu bolum otomatik eklenir."

    for profil, yol in PROFILLER.items():
        if not yol.exists():
            print(f"⏭️  {profil}: SOUL.md yok ({yol})")
            continue

        with open(yol, "r", encoding="utf-8") as f:
            icerik = f.read()

        # Eski durum bolumunu cikar
        if BASLANGIC in icerik:
            bas = icerik.index(BASLANGIC)
            bitis = icerik.index(BITIS, bas) + len(BITIS) + 3  # ) + bosluk
            # Bitis'ten sonraki satirlari da temizle
            sonraki = icerik[bitis:].lstrip("\n")
            # Sonraki satir --- ile basliyorsa onu da sil
            if sonraki.startswith("---"):
                sonraki = sonraki.split("\n", 1)[1] if "\n" in sonraki else ""
            icerik = icerik[:bas] + sonraki
            print(f"🔄 {profil}: Eski durum bolumu cikarildi")

        # Yeni durum ozetini ekle (en sona)
        icerik = icerik.rstrip() + "\n" + ozet

        # Yedek al
        yedek = yol.with_suffix(".md.yedek")
        shutil.copy2(yol, yedek)

        with open(yol, "w", encoding="utf-8") as f:
            f.write(icerik)

        print(f"✅ {profil}: SOUL.md guncellendi ({len(ozet)} karakter)")


if __name__ == "__main__":
    senkronize_et()
    print("\n--- durum ozeti ---")
    print(durum_ozeti())
