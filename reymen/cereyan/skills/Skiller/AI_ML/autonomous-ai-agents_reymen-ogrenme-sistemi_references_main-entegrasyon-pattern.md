---
name: autonomous-ai-agents_reymen-ogrenme-sistemi_references_main-entegrasyon-pattern
description: main.py Entegrasyon Pattern
title: "Autonomous Ai Agents Reymen Ogrenme Sistemi References Main Entegrasyon Pattern"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | main.py Entegrasyon Pattern |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# main.py Entegrasyon Pattern

## Prompt'a Beceri Bağlamı Ekleme

main.py'de `sistem_prompt` oluşturulduktan SONRA, LLM'e gönderilmeden ÖNCE beceri bağlamı eklenir.

### Entegrasyon Noktası

```python
# 3 prompt builder zincirinden biri:
if self.prompt_builder:
    sistem_prompt, _ = self.prompt_builder.insa(...)
elif self._sistem_talimati_fn:
    sistem_prompt = self._sistem_talimati_fn(...)
else:
    sistem_prompt = self.prompt_engine.insa_et(...)

# --- ENTEGRASYON NOKTASI (hepsi icin calisir) ---
if hasattr(self, 'learning') and self.learning:
    try:
        beceri_baglam = self.learning.beceri_baglamini_al(hedef, adet=3)
        if beceri_baglam:
            sistem_prompt += beceri_baglam
    except Exception as e:
        print(f"[Beceri] Baglam ekleme uyarisi: {e}")
# --- ENTEGRASYON NOKTASI SONU ---

mesajlar = self.compressor.compress(mesajlar, context_length=8192)
```

### Özellikler

- `try-except` ile korunur — hata durumunda ReAct döngüsü etkilenmez
- `hasattr` kontrolü — `learning` yoksa sessizce geçer
- 3 prompt builder yönteminin tümünde çalışır
- `MAKS_BAGLAM_KARAKTER=4000` ile sınırlıdır (`closed_learning_loop.py`)
- `kategori=None` (default) ile tüm beceriler taranır

### Görev Sonu: Öğrenme Döngüsü

`main.py`'de `_ogren()` metodu, görev başarılı veya başarısız her durumda tetiklenir:

```python
def _ogren(self, hedef, adim_gecmisi, ozet):
    try:
        self.learning.beceri_kristallestir(
            hedef[:40], ozet, "\n".join(adim_gecmisi)
        )
        print("[Ogrenme] Tecrube ve beceri kaydedildi.")
    except Exception as e:
        print(f"[Ogrenme Hatasi] {e}")
```

Tetikleyiciler: adım tamam (402), iç gözlem (424), budget limit (461), tekrarlı hata (483/487), tur aşımı (496).

### Kategori Filtreleme

```python
# Tüm becerilerde ara (eski davranış)
loop.ilgili_becerileri_cagir("write_text")

# Sadece IO_Operations etiketlilerde ara
loop.ilgili_becerileri_cagir("write_text", kategori="IO_Operations")

# İkisi de ayni islev: _ilgili_becerileri_skorlu()
loop._ilgili_becerileri_skorlu("write_text", kategori="IO_Operations")
```

FTS5 sorgusu: `kategori=None` → `MATCH "sorgu"`, `kategori="IO_Operations"` → `MATCH "IO_Operations AND sorgu"`
