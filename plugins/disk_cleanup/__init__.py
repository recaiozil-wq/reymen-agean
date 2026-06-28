# -*- coding: utf-8 -*-
"""plugins/disk_cleanup/__init__.py — Disk Temizleme Plugin.

Gecici dosyalari, loglari, onbellegi temizler.
"""


__all__ = ['Path', 'disk_durum', 'disk_temizle', 'kaydet']
plugin_adi = "disk_cleanup"
plugin_aciklamasi = "Diskteki gecici dosyalari, loglari ve onbellegi temizleme"


def kaydet(motor):
    try:
        import shutil
        from pathlib import Path

        HEDEFLER = [
            Path.home() / "AppData" / "Local" / "Temp",
            Path.home() / ".cache",
            Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "INetCache",
        ]

        def disk_temizle(args):
            """Gecici dosyalari, loglari ve onbellekleri temizle."""
            toplam = 0
            sayac = 0
            for hedef in HEDEFLER:
                if hedef.exists():
                    for f in hedef.rglob("*"):
                        try:
                            if f.is_file():
                                toplam += f.stat().st_size
                                f.unlink()
                                sayac += 1
                        except Exception:
                            pass
            return f"[Disk] {sayac} dosya silindi ({toplam / 1024:.1f} KB)"

        def disk_durum(args):
            """Disk kullanim durumunu goster."""
            import shutil
            toplam, kullanilan, bos = shutil.disk_usage(Path.home())
            return (
                f"[Disk] Toplam: {toplam / (1024**3):.1f} GB | "
                f"Kullanilan: {kullanilan / (1024**3):.1f} GB | "
                f"Bos: {bos / (1024**3):.1f} GB"
            )

        if hasattr(motor, "_registry") and motor._registry:
            motor._registry.kaydet("DISK_TEMIZLE", disk_temizle)
            motor._registry.kaydet("DISK_DURUM", disk_durum)
    except Exception:
        pass
