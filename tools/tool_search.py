"""
Tool arama aracı.
ToolRegistry üzerinde isim, açıklama, etiket araması.
"""
import json

# Varsayılan tool kaydı
_TOOL_REGISTRY = {}


def run(islem='ara', sorgu=None, limit=10, **kwargs):
    """
    Tool arama.

    Parametreler:
        islem (str): 'ara', 'oner' veya 'tavsiye_et'
        sorgu (str): Aranacak sorgu
        limit (int): Maksimum sonuç sayısı (varsayılan: 10)

    Returns:
        str: Arama sonuçları.
    """
    global _TOOL_REGISTRY

    try:
        if not sorgu:
            sorgu = ''

        if islem in ('oner', 'tavsiye_et'):
            # Popüler/önerilen tool'ları döndür
            populer = [
                'anser_endpoint', 'browser_tool', 'web_search', 'read_extract',
                'file_operations', 'terminal_tool', 'code_executor', 'git_operations',
                'api_client', 'data_analyzer', 'patch_parser', 'skills_tool',
                'binary_extensions', 'ansi_strip', 'openrouter_client'
            ]
            if sorgu:
                eslesen = [t for t in populer if sorgu.lower() in t.lower()]
                if eslesen:
                    return f"Önerilen tool'lar:\n" + "\n".join([f"  - {t}" for t in eslesen[:limit]])
            return f"Popüler tool'lar:\n" + "\n".join([f"  - {t}" for t in populer[:limit]])

        elif islem == 'ara':
            if not sorgu:
                return "Hata: 'sorgu' parametresi zorunludur."

            # _TOOL_REGISTRY üzerinde ara
            yerel_sonuclar = []
            for ad, bilgi in _TOOL_REGISTRY.items():
                if sorgu.lower() in ad.lower():
                    yerel_sonuclar.append((ad, bilgi))

            # tools/ dizinindeki dosyaları tara
            import os
            tools_dizini = os.path.join(os.path.dirname(__file__))
            dosya_sonuclari = []
            if os.path.isdir(tools_dizini):
                for f in os.listdir(tools_dizini):
                    if f.endswith('.py') and f != '__init__.py':
                        ad = f[:-3]
                        if sorgu.lower() in ad.lower() and ad not in [r[0] for r in yerel_sonuclar]:
                            dosya_sonuclari.append((ad, {'kaynak': 'tools_dizini'}))

            tum_sonuclar = yerel_sonuclar + dosya_sonuclari

            if not tum_sonuclar:
                return f"'{sorgu}' için tool bulunamadı."

            sinirli = tum_sonuclar[:limit]
            return f"Arama: '{sorgu}' ({len(tum_sonuclar)} sonuç):\n" + "\n".join(
                [f"  - {ad}" for ad, _ in sinirli]
            )

        else:
            return f"Hata: Geçersiz işlem '{islem}'. 'ara', 'oner' veya 'tavsiye_et' kullanın."

    except Exception as e:
        return f"Tool arama hatası: {str(e)}"
