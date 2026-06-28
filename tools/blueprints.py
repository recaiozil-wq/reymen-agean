# -*- coding: utf-8 -*-
"""blueprints.py — Blueprint Sablon Sistemi.

ReYMeN projesinde .ReYMeN/blueprints/ klasorunde YAML template
dosyalarini yonetir: listeleme, yukleme, kaydetme ve uygulama.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

BLUEPRINT_DIR = Path(__file__).parent.parent / ".ReYMeN" / "blueprints"


@dataclass
class BlueprintSpec:
    """Blueprint is tanim sablon verisi."""
    skill_name: str
    schedule: str
    deliver: str
    prompt: Optional[str] = None


def blueprint_to_job_spec(spec: "BlueprintSpec") -> dict:
    """BlueprintSpec'i cron is tanim sozlugune donustur."""
    return {
        "skills": [spec.skill_name],
        "schedule": spec.schedule,
        "deliver": spec.deliver,
        "prompt": spec.prompt or "",
        "name": spec.skill_name,
    }


def register_blueprint_suggestion(spec: "BlueprintSpec") -> Optional[dict]:
    """Blueprint'i cron oneri deposuna kaydet.

    Returns:
        Olusturulan oneri kaydi veya None (zaten var ya da kapasite doluysa)
    """
    import cron.suggestions as suggestions
    return suggestions.add_suggestion(
        title=spec.skill_name,
        description=f"Blueprint: {spec.skill_name} ({spec.schedule})",
        source="blueprint",
        job_spec=blueprint_to_job_spec(spec),
        dedup_key=f"blueprint:{spec.skill_name}:{spec.schedule}",
    )


def _yaml_yukle(dosya_yolu: Path) -> dict:
    """Bir YAML dosyasini sozluge cevirir.

    Args:
        dosya_yolu: YAML dosya yolu

    Returns:
        dict: Cozulmus YAML icerigi
    """
    try:
        import yaml
        with open(dosya_yolu, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        # yaml yoksa basit bir metin ayristirici
        icerik = dosya_yolu.read_text(encoding="utf-8")
        return {"raw": icerik, "ad": dosya_yolu.stem}


def _yaml_kaydet(dosya_yolu: Path, icerik: dict) -> None:
    """Bir sozlugu YAML dosyasina yazar.

    Args:
        dosya_yolu: Hedef dosya yolu
        icerik: Kaydedilecek sozluk
    """
    try:
        import yaml
        with open(dosya_yolu, "w", encoding="utf-8") as f:
            yaml.dump(icerik, f, allow_unicode=True, default_flow_style=False)
    except ImportError:
        # yaml yoksa duz metin olarak kaydet
        with open(dosya_yolu, "w", encoding="utf-8") as f:
            f.write(str(icerik))


def blueprint_listele() -> str:
    """Blueprint klasorundeki tum sablonlari listeler.

    Returns:
        str: Blueprint listesi metni
    """
    try:
        if not BLUEPRINT_DIR.exists():
            return "[Blueprint]: Blueprint klasoru bulunamadi."

        dosyalar = sorted(BLUEPRINT_DIR.glob("*.yaml")) + sorted(BLUEPRINT_DIR.glob("*.yml"))
        if not dosyalar:
            return "[Blueprint]: Henuz hic blueprint yok."

        sonuc = [f"[Blueprint]: Toplam {len(dosyalar)} blueprint:"]
        for dosya in dosyalar:
            boyut = dosya.stat().st_size
            sonuc.append(f"  - {dosya.stem} ({boyut} bytes)")
        return "\n".join(sonuc)

    except Exception as e:
        return f"[Blueprint]: Listeleme hatasi - {e}"


def blueprint_yukle(ad: str) -> str:
    """Belirtilen blueprint sablonunu yukler.

    Args:
        ad: Blueprint adi (.yaml/.yml uzantisi olmadan)

    Returns:
        str: Blueprint icerigi metni
    """
    if not ad:
        return "[Blueprint]: Blueprint adi gerekli."

    try:
        # Once .yaml, sonra .yml dene
        dosya = BLUEPRINT_DIR / f"{ad}.yaml"
        if not dosya.exists():
            dosya = BLUEPRINT_DIR / f"{ad}.yml"
        if not dosya.exists():
            return f"[Blueprint]: '{ad}' blue print bulunamadi."

        veri = _yaml_yukle(dosya)

        import json
        return f"[Blueprint]: {ad} yuklendi.\n{json.dumps(veri, ensure_ascii=False, indent=2)}"

    except Exception as e:
        return f"[Blueprint]: Yukleme hatasi - {e}"


def blueprint_kaydet(ad: str, icerik: dict) -> str:
    """Yeni bir blueprint sablonu kaydeder.

    Args:
        ad: Blueprint adi (dosya adi)
        icerik: Kaydedilecek icerik (sozluk)

    Returns:
        str: Durum mesaji
    """
    if not ad:
        return "[Blueprint]: Blueprint adi gerekli."
    if not icerik:
        return "[Blueprint]: Icerik gerekli."

    try:
        BLUEPRINT_DIR.mkdir(parents=True, exist_ok=True)
        dosya = BLUEPRINT_DIR / f"{ad}.yaml"
        _yaml_kaydet(dosya, icerik)
        return f"[Blueprint]: '{ad}' kaydedildi ({dosya})."

    except Exception as e:
        return f"[Blueprint]: Kaydetme hatasi - {e}"


def blueprint_uygula(ad: str, parametreler: dict = None) -> str:
    """Bir blueprint sablonunu parametrelerle uygular.

    Args:
        ad: Blueprint adi
        parametreler: Uygulama parametreleri (opsiyonel sozluk)

    Returns:
        str: Uygulama sonucu
    """
    if not ad:
        return "[Blueprint]: Blueprint adi gerekli."

    try:
        # Blueprint'i yukle
        dosya = BLUEPRINT_DIR / f"{ad}.yaml"
        if not dosya.exists():
            dosya = BLUEPRINT_DIR / f"{ad}.yml"
        if not dosya.exists():
            return f"[Blueprint]: '{ad}' blue print bulunamadi."

        veri = _yaml_yukle(dosya)
        if parametreler:
            # Parametreleri birlestir
            if isinstance(veri, dict):
                veri.update(parametreler)

        import json
        return f"[Blueprint]: '{ad}' uygulandi.\n{json.dumps(veri, ensure_ascii=False, indent=2)}"

    except Exception as e:
        return f"[Blueprint]: Uygulama hatasi - {e}"


def run(**kwargs) -> str:
    """Blueprint sistemi ana yonlendirme fonksiyonu.

    Desteklenen islemler: blueprint_listele, blueprint_yukle, blueprint_kaydet, blueprint_uygula

    Args:
        islem (str): Yapilacak islem (zorunlu)
        ad (str): Blueprint adi (yukle, kaydet, uygula icin)
        icerik (dict): Blueprint icerigi (kaydet icin)
        parametreler (dict): Uygulama parametreleri (uygula icin)

    Returns:
        str: Islem sonucu
    """
    islem = kwargs.get("islem", "")
    if not islem:
        return "[Blueprint]: 'islem' parametresi zorunlu (blueprint_listele, blueprint_yukle, blueprint_kaydet, blueprint_uygula)."

    try:
        if islem == "blueprint_listele":
            return blueprint_listele()
        elif islem == "blueprint_yukle":
            return blueprint_yukle(kwargs.get("ad", ""))
        elif islem == "blueprint_kaydet":
            return blueprint_kaydet(
                kwargs.get("ad", ""),
                kwargs.get("icerik", {})
            )
        elif islem == "blueprint_uygula":
            return blueprint_uygula(
                kwargs.get("ad", ""),
                kwargs.get("parametreler", None)
            )
        else:
            return f"[Blueprint]: Bilinmeyen islem: {islem}"
    except Exception as e:
        return f"[Blueprint]: Hata - {e}"


def ping() -> bool:
    return True


if __name__ == "__main__":
    print(run(islem="blueprint_listele"))
    print(run(islem="blueprint_kaydet", ad="test", icerik={"adim": "ornek"}))
