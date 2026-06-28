---
skill_id: dd8c63c67c91
usage_count: 1
last_used: 2026-06-16
---
# Batch File Creation Pattern (Hızlı Seri Üretim)

Bu doküman, 20-80 dosyanın saatler içinde oluşturulması gereken
durumlar için kanıtlanmış batch stratejisini açıklar.

## Temel Kural

Her batch = bağımsız, birbirine referans vermeyen dosyalar.
Batch boyutu = 5-10 dosya (çok büyük olursa import testi zorlaşır).

## Batch Gruplama Stratejisi

```
Grup 1: Kok dizindeki bagimsiz dosyalar (5-6 dosya)
  context_references.py
  trajectory.py
  trajectory_compressor.py
  conversation_compression.py
  iteration_budget.py
  process_bootstrap.py

Grup 2: Ayni klasordeki dosyalar (8 dosya)
  tools/__init__.py
  tools/memory_tool.py
  tools/send_message_tool.py
  ...

Grup 3: Bagimli dosyalar (once base, sonra extend)
  providers/__init__.py  (once)
  providers/base.py      (base class)
  bedrock_adapter.py     (extends)

Grup 4: Gateway/platform eklemeleri
  gateway/platforms/discord.py
  gateway/platforms/signal.py
  ...
```

## Her Dosyada Zorunlu Yapı

```python
# -*- coding: utf-8 -*-
"""module_name.py — Kisa Aciklama.

Detayli aciklama (ne ise yarar, nasil kullanilir).

Kullanim:
    from module_name import SinifAdi
    nesne = SinifAdi()
    sonuc = nesne.metod()
"""

# import'lar


class SinifAdi:
    """Sinif aciklamasi."""
    def __init__(self):
        pass

    def metod(self, parametre: str) -> str:
        """Metod aciklamasi.

        Args:
            parametre: Ne ise yarar

        Returns:
            Ne dondurur
        """
        return parametre


if __name__ == "__main__":
    # Calistirilabilir test
    nesne = SinifAdi()
    print(nesne.metod("test"))
```

## Batch Akışı

```
1. write_file(path="dosya1.py", content=...)  # 1. dosya
2. write_file(path="dosya2.py", content=...)  # 2. dosya
3. write_file(path="dosyaN.py", content=...)  # N. dosya (paralel)
4. python -c "import dosya1, dosya2, ..."     # TOPLU IMPORT TESTI
5. HATA varsa → patch() ile düzelt, tekrar test et
6. OK → sonraki batch'e geç
7. 10 batch'de bir python reyment.py doctor  # sistem testi
```

## Hız İpuçları

- write_file() ile dosya oluştur (asla terminal echo/cat heredoc kullanma)
- Patch ile hata düzelt (dosyayı komple yeniden yazma)
- Tüm dosyaları aynı anda yaz (paralel write_file çağrıları)
- Import testini tek satırda yap: `python -c "import a, b, c"`
- Hata varsa sadece hatalı dosyayı düzelt, tüm batch'i tekrar test etme

## Uzun Çalışma Oturumu Disiplini

Kullanıcı "tum gun calisabilirsin" dediğinde:
- Ara vermeden batch üretmeye devam et
- Her batch sonu sadece kısa ✅/❌ raporu ver (uzun açıklama yapma)
- 5 batch'te bir toplu ilerleme bildir
- Kullanıcı "sorma" dediyse düşük riskli kararları (dosya adı, yeri, içerik) KENDİN VER
- Sadece geri dönüşü olmayan işlemlerde sor (credential değişikliği, dosya silme vb.)
