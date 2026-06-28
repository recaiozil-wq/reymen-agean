# -*- coding: utf-8 -*-
"""tools/checkpoint_manager.py — Checkpoint yoneticisi sarmalayicisi.

Kok dizindeki checkpoint_manager.py modulunu import eder ve
checkpoint kaydetme, yukleme, listeleme islemlerini delegasyonla calistirir.
"""
import json


def run(islem='liste', **kwargs) -> str:
    """Checkpoint islemlerini yonetir.

    Parametreler:
        islem (str): 'kaydet', 'yukle', 'liste', 'temizle' veya 'devam'
        hedef (str): Gorev hedefi (islem=kaydet/devam icin)
        tur (int): Mevcut tur (islem=kaydet icin)
        durum (dict): Kaydedilecek durum (islem=kaydet icin)
        checkpoint_id (str): Yuklenecek checkpoint ID (islem=yukle icin)
        saat (int): Temizleme siniri saat (islem=temizle icin)

    Returns:
        str: Islem sonucu.
    """
    try:
        from checkpoint_manager import CheckpointManager

        c = CheckpointManager()

        if islem == 'kaydet':
            hedef = kwargs.get('hedef', '')
            tur = int(kwargs.get('tur', 0))
            durum = kwargs.get('durum', {})
            if not hedef:
                return "Hata: 'hedef' parametresi zorunludur."
            cid = c.kaydet(hedef, tur, durum)
            return f"Checkpoint kaydedildi: {cid} (tur {tur})"

        elif islem == 'yukle':
            cid = kwargs.get('checkpoint_id', '')
            if not cid:
                return "Hata: 'checkpoint_id' parametresi zorunludur."
            veri = c.yukle(cid)
            if veri:
                return json.dumps(veri, ensure_ascii=False, indent=2)
            return f"Checkpoint bulunamadi: {cid}"

        elif islem == 'liste':
            checkpointler = c.listele()
            if not checkpointler:
                return "Henuz checkpoint bulunmuyor."
            satirlar = [f"Checkpoint'ler ({len(checkpointler)}):"]
            for cp in checkpointler:
                satirlar.append(
                    f"  [{cp['id']}] {cp['hedef']} - tur {cp['tur']} ({cp['zaman']})"
                )
            return "\n".join(satirlar)

        elif islem == 'temizle':
            saat = int(kwargs.get('saat', 24))
            c.temizle(saat)
            return f"{saat} saatten eski checkpoint'ler temizlendi."

        elif islem == 'devam':
            hedef = kwargs.get('hedef', '')
            if not hedef:
                return "Hata: 'hedef' parametresi zorunludur."
            veri = c.devam_edebilir_mi(hedef)
            if veri:
                return json.dumps(veri, ensure_ascii=False, indent=2)
            return f"Devam edilebilecek checkpoint bulunamadi: {hedef}"

        else:
            return f"Hata: Gecersiz islem '{islem}'."

    except Exception as e:
        return f"Checkpoint hatasi: {e}"


def motor_kaydet(motor) -> None:
    """Motor'a checkpoint araçlarını kaydet."""
    motor._plugin_arac_kaydet(
        "CHECKPOINT_KAYDET",
        lambda hedef="", tur="0": run("kaydet", hedef=hedef, tur=int(tur) if tur else 0),
        "Görev durumunu checkpoint'e kaydet — CHECKPOINT_KAYDET(hedef, tur)"
    )
    motor._plugin_arac_kaydet(
        "CHECKPOINT_YUKLE",
        lambda checkpoint_id="": run("yukle", checkpoint_id=checkpoint_id),
        "Checkpoint yükle — CHECKPOINT_YUKLE(checkpoint_id)"
    )
    motor._plugin_arac_kaydet(
        "CHECKPOINT_LISTELE",
        lambda: run("liste"),
        "Tüm checkpoint'leri listele"
    )
    motor._plugin_arac_kaydet(
        "CHECKPOINT_TEMIZLE",
        lambda saat="24": run("temizle", saat=int(saat) if saat else 24),
        "Eski checkpoint'leri temizle — CHECKPOINT_TEMIZLE(saat)"
    )
    motor._plugin_arac_kaydet(
        "CHECKPOINT_DEVAM",
        lambda hedef="": run("devam", hedef=hedef),
        "Devam edilebilir checkpoint bul — CHECKPOINT_DEVAM(hedef)"
    )
