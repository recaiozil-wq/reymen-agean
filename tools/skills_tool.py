"""
Skill arayüzü aracı.
Skill listeleme, yükleme, bilgi ve arama işlemleri.
"""
import os
import json

SKILL_DIZINI = os.path.expanduser("~/.ReYMeN/profiles/default/skills")


def _skill_listesi():
    """Yüklenmiş skill'leri listele."""
    if not os.path.isdir(SKILL_DIZINI):
        return []
    skilller = []
    for item in os.listdir(SKILL_DIZINI):
        item_path = os.path.join(SKILL_DIZINI, item)
        if os.path.isdir(item_path):
            skilller.append(item)
        elif item.endswith('.py') or item.endswith('.yaml') or item.endswith('.yml'):
            skilller.append(os.path.splitext(item)[0])
    return sorted(skilller)


def run(islem='listele', skill_adi=None, kategori=None, **kwargs):
    """
    Skill arayüzü.

    Parametreler:
        islem (str): 'listele', 'yukle', 'bilgi' veya 'ara'
        skill_adi (str): Skill adı
        kategori (str): Kategori filtresi

    Returns:
        str: İşlem sonucu.
    """
    try:
        if islem == 'listele':
            skilller = _skill_listesi()
            if not skilller:
                return "Yüklenmiş skill bulunamadı."
            if kategori:
                skilller = [s for s in skilller if kategori.lower() in s.lower()]
            liste = "\n".join([f"  - {s}" for s in skilller])
            return f"Skill'ler ({len(skilller)}):\n{liste}"

        elif islem == 'yukle':
            if not skill_adi:
                return "Hata: 'skill_adi' parametresi zorunludur."

            skill_yolu = os.path.join(SKILL_DIZINI, skill_adi)
            if os.path.exists(skill_yolu):
                return f"Skill '{skill_adi}' zaten mevcut: {skill_yolu}"
            if os.path.exists(skill_yolu + '.py'):
                return f"Skill '{skill_adi}' zaten mevcut: {skill_yolu + '.py'}"

            # Skill dizinini oluştur
            try:
                os.makedirs(skill_yolu, exist_ok=True)
                return f"Skill '{skill_adi}' yükleme için hazır: {skill_yolu}"
            except Exception as e:
                return f"Skill yükleme hatası: {str(e)}"

        elif islem == 'bilgi':
            if not skill_adi:
                return "Hata: 'skill_adi' parametresi zorunludur."

            skill_yolu = os.path.join(SKILL_DIZINI, skill_adi)
            py_yolu = skill_yolu + '.py'

            if os.path.isdir(skill_yolu):
                dosyalar = os.listdir(skill_yolu)
                return f"Skill: {skill_adi}\nTür: Dizin\nYol: {skill_yolu}\nDosyalar ({len(dosyalar)}): {', '.join(dosyalar)}"
            elif os.path.isfile(py_yolu):
                return f"Skill: {skill_adi}\nTür: Python dosyası\nYol: {py_yolu}"
            else:
                return f"Skill '{skill_adi}' bulunamadı."

        elif islem == 'ara':
            sorgu = skill_adi or ''
            if not sorgu and not kategori:
                return "Hata: Arama için 'skill_adi' veya 'kategori' parametrelerinden biri gerekli."

            skilller = _skill_listesi()
            sonuclar = []
            for s in skilller:
                eslesme = True
                if sorgu and sorgu.lower() not in s.lower():
                    eslesme = False
                if kategori and kategori.lower() not in s.lower():
                    eslesme = False
                if eslesme:
                    sonuclar.append(s)

            if not sonuclar:
                return f"'{sorgu}' için skill bulunamadı."
            return f"Arama sonuçları ({len(sonuclar)}):\n" + "\n".join([f"  - {s}" for s in sonuclar])

        else:
            return f"Hata: Geçersiz işlem '{islem}'. 'listele', 'yukle', 'bilgi' veya 'ara' kullanın."

    except Exception as e:
        return f"Skill aracı hatası: {str(e)}"
