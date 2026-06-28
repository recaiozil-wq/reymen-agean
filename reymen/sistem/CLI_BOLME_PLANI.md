# cli_main.py Bölme Planı (Adım 3)

## Mevcut Durum
`cli_main.py` 12,803 satır — KRİTİK boyut.

## Mevcut Mimari (Zaten Kısmen Bölünmüş)
Dosya zaten mixin pattern kullanıyor:
- `MixinDisplay` → `cli_mixin_display.py`
- `MixinStream` → `cli_mixin_stream.py`
- `MixinVoice` → `cli_mixin_voice.py`
- `MixinApproval` → `cli_mixin_approval.py`
- `MixinCommands` → `cli_mixin_commands.py` (3,639 satır)
- `MixinCore` → `cli_mixin_core.py`

Ek olarak:
- `cli_helpers.py` (wildcard import)
- `cli_display.py` (wildcard import)
- `cli_commands.py` (wildcard import)
- `cli_auth.py` (wildcard import)
- `cli_maintenance.py` (wildcard import)
- `cli_stream.py` (wildcard import)

## Sorun
`cli_main.py` hâlâ 12K+ satır çünkü:
1. `ReYMeNCLI` sınıfı çok büyük (__init__ + yüzlerce metod)
2. Wildcard import'lar (`from cli_helpers import *`) tüm fonksiyonları tek dosyada topluyor
3. `_run_cleanup()`, `_prepare_deferred_agent_startup()` gibi yardımcı fonksiyonlar çok büyük

## Önerilen Bölme Stratejisi (Kademeli)

### Faz 1: Wildcard import'ları kaldır (düşük risk)
```python
# ÖNCE:
from reymen.sistem.cli_helpers import *
# SONRA:
from reymen.sistem.cli_helpers import specific_func1, specific_func2
```

### Faz 2: ReYMeNCLI.__init__'i ayrı dosyaya taşı
```python
# cli_init.py
class ReYMeNCLIInit:
    def __init__(self, ...): ...
```

### Faz 3: Büyük metod gruplarını ayrı mixin'lere taşı
- `cli_mixin_session.py` — session yönetimi metodları
- `cli_mixin_background.py` — background task metodları
- `cli_mixin_config.py` — config yükleme/metodları

### Faz 4: Yardımcı fonksiyonları ayrı modüllere taşı
- `_run_cleanup()` → `cli_cleanup.py`
- `_prepare_deferred_agent_startup()` → `cli_startup.py`

## Risk Değerlendirmesi
- **Yüksek risk**: Import kırılmaları, sirküler import
- **Azaltma**: Kademeli refactor, her fazdan sonra test çalıştır
- **Öncelik**: Düşük — dosya büyük ama çalışıyor, mixin yapısı zaten var

## Sonuç
Tam bölme yüksek riskli ve uzun süreli bir iş. Mevcut mixin mimarisi korundu.
Bu plan dokümanı gelecekteki refactor çalışmaları için referans olarak saklandı.