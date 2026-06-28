# -*- coding: utf-8 -*-
"""gateway/slash_commands.py — Slash Komut Sistemi.

/komut tabanlı gateway işlemleri: /yardim, /durum, /kanallar.
"""

import shlex
from typing import Any, Callable, Optional


class SlashCommand:
    """Tek bir slash komut tanımı."""

    def __init__(self, komut: str, aciklama: str,
                 islev: Callable, kullanim: str = "",
                 yetki: Optional[str] = None):
        self.komut = komut.lower()
        self.aciklama = aciklama
        self.islev = islev
        self.kullanim = kullanim or f"/{komut}"
        self.yetki = yetki  # Gerekli yetki (None = herkese açık)

    def calistir(self, *args, **kwargs) -> str:
        """Komutu çalıştır."""
        try:
            sonuc = self.islev(*args, **kwargs)
            return str(sonuc)
        except Exception as e:
            return f"[{self.komut}]: Hata — {e}"


class SlashCommands:
    """Slash komut sistemi — /komut tabanlı işlemler."""

    def __init__(self):
        self._komutlar: dict[str, SlashCommand] = {}
        self._varsayilan_komutlari_kaydet()

    def _varsayilan_komutlari_kaydet(self):
        """Varsayılan gateway komutlarını kaydet."""
        self.kaydet("yardim", "Kullanılabilir komutları listeler",
                     self._cmd_yardim, "/yardim [komut]")
        self.kaydet("durum", "Gateway durumunu gösterir",
                     self._cmd_durum, "/durum")
        self.kaydet("kanallar", "Aktif kanalları listeler",
                     self._cmd_kanallar, "/kanallar")
        self.kaydet("ping", "Bağlantı testi",
                     self._cmd_ping, "/ping")
        self.kaydet("temizle", "Oturum verisini temizler",
                     self._cmd_temizle, "/temizle", yetki="admin")

    # ── Komut Kaydı ───────────────────────────────────────────────────

    def kaydet(self, komut: str, aciklama: str, islev: Callable,
               kullanim: str = "", yetki: Optional[str] = None) -> bool:
        """Yeni bir slash komut kaydet.

        Args:
            komut: Komut adı (/komut)
            aciklama: Komut açıklaması
            islev: Çalıştırılacak fonksiyon
            kullanim: Kullanım örneği
            yetki: Gerekli yetki (None = herkese açık)

        Returns:
            Başarılı mı
        """
        if komut in self._komutlar:
            return False
        self._komutlar[komut] = SlashCommand(komut, aciklama, islev, kullanim, yetki)
        return True

    def sil(self, komut: str) -> bool:
        """Komut sil."""
        return bool(self._komutlar.pop(komut, None))

    def komut_al(self, komut: str) -> Optional[SlashCommand]:
        """Komut tanımını döndür."""
        return self._komutlar.get(komut.lower())

    def komut_listesi(self, yetki: Optional[str] = None) -> list[dict]:
        """Tüm komutları listele.

        Args:
            yetki: Sadece bu yetkiye uygun komutları göster

        Returns:
            Komut listesi
        """
        komutlar = []
        for cmd in self._komutlar.values():
            if yetki and cmd.yetki and cmd.yetki != yetki:
                continue
            komutlar.append({
                "komut": f"/{cmd.komut}",
                "aciklama": cmd.aciklama,
                "kullanim": cmd.kullanim,
                "yetki": cmd.yetki,
            })
        return komutlar

    # ── Komut Ayrıştırma ve Çalıştırma ────────────────────────────────

    def ayristir(self, metin: str) -> Optional[dict]:
        """Metindeki slash komutunu ayristir.

        Args:
            metin: "/komut arg1 arg2" formatında metin

        Returns:
            {"komut": str, "args": list, "raw": str} veya None
        """
        metin = metin.strip()
        if not metin.startswith("/"):
            return None

        try:
            parcalar = shlex.split(metin)
        except ValueError:
            parcalar = metin.split()

        if not parcalar:
            return None

        komut = parcalar[0][1:].lower()  # "/" işaretini kaldır
        args = parcalar[1:]

        return {"komut": komut, "args": args, "raw": metin}

    def isle(self, metin: str, yetki: Optional[str] = None,
             **ctx) -> str:
        """Metni işle, slash komut varsa çalıştır.

        Args:
            metin: Gelen mesaj metni
            yetki: Kullanıcının yetkisi
            ctx: Komuta iletilecek ek bağlam

        Returns:
            Komut çıktısı veya boş string (komut değilse)
        """
        ayrik = self.ayristir(metin)
        if not ayrik:
            return ""

        cmd = self.komut_al(ayrik["komut"])
        if not cmd:
            return f"Bilinmeyen komut: /{ayrik['komut']}. /yardim yazın."

        # Yetki kontrolü
        if cmd.yetki and (not yetki or yetki != cmd.yetki):
            return f"Bu komutu kullanma yetkiniz yok. (Gerekli: {cmd.yetki})"

        return cmd.calistir(*ayrik["args"], **ctx)

    # ── Varsayılan Komutlar ───────────────────────────────────────────

    def _cmd_yardim(self, *args, **kwargs) -> str:
        """/yardim — komut listesi veya detay."""
        if args:
            cmd = self.komut_al(args[0])
            if cmd:
                return f"{cmd.kullanim} — {cmd.aciklama}" + \
                       (f" (Yetki: {cmd.yetki})" if cmd.yetki else "")
            return f"Bilinmeyen komut: {args[0]}"

        satirlar = ["**Kullanılabilir Komutlar:**", ""]
        for cmd in self._komutlar.values():
            satirlar.append(f"`{cmd.kullanim}` — {cmd.aciklama}")
        return "\n".join(satirlar)

    def _cmd_durum(self, *args, **kwargs) -> str:
        """/durum — gateway durumu."""
        return (f"**Gateway Durumu**\n"
                f"Komut sayısı: {len(self._komutlar)}\n"
                f"Durum: aktif")

    def _cmd_kanallar(self, *args, **kwargs) -> str:
        """/kanallar — aktif kanallar."""
        return "Aktif kanallar: (henüz bağlı kanal yok)"

    def _cmd_ping(self, *args, **kwargs) -> str:
        """/ping — bağlantı testi."""
        return "pong!"

    def _cmd_temizle(self, *args, **kwargs) -> str:
        """/temizle — oturum temizleme (admin)."""
        return "Oturum verileri temizlendi."

    # ── Ortak Gateway Metodları ───────────────────────────────────────

    def ping(self) -> dict:
        """Sağlık kontrolü."""
        return {
            "modul": "slash_commands",
            "durum": "hazir",
            "komut_sayisi": len(self._komutlar),
        }

    def send_message(self, mesaj: str, hedef: str, **kwargs) -> str:
        """Mesajı slash komut olarak işle."""
        sonuc = self.isle(mesaj, yetki=kwargs.get("yetki"))
        if sonuc:
            return f"[Slash]: {sonuc}"
        return f"[Slash]: '{mesaj}' bir komut değil."


# Global instance
komutlar = SlashCommands()


if __name__ == "__main__":
    sc = SlashCommands()
    print(sc.isle("/yardim"))
    print("---")
    print(sc.isle("/ping"))
    print("---")
    print(sc.isle("/durum"))
    print("---")
    print(sc.isle("/bilinmeyen"))
    print("---")
    print(sc.ping())
