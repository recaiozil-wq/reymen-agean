# ReYMeN — Son İyileştirmeler

## NE
Tüm kalan eksikleri sırayla tamamla. Her adımda hata alırsan düzeltip tekrar dene (max 3). Act modunda çalıştır.

---

## 1. shell=True Kalan 2 Nokta

### Hedef
reymen/ dizininde hala shell=True kullanan 2 dosyayı temizle.

### Yapılacaklar

**a) reymen/sistem/terminal_backends.py:37**
```python
# Mevcut:
def calistir(self, komut, timeout=None, ortam=None, shell=True):

# Olması gereken:
def calistir(self, komut, timeout=None, ortam=None, shell=False):
```
- shell=True varsayılandan kaldır
- string komut alan yerlerde shlex.split() kullan
- `nosec B603` comment ekle

**b) reymen/sistem/cli_mixin_commands.py:3639**
```python
# Mevcut: exec_cmd, shell=True, capture_output=True

# Olması gereken:
import shlex
args = shlex.split(exec_cmd)
subprocess.run(args, capture_output=True, ...)
```

### Doğrulama
```bash
grep -rn "shell=True" reymen/ --include="*.py" | grep -v __pycache__ | grep -v "yorum\|#"
# Çıktı: 0 satır (yorumlar hariç)
```

---

## 2. .pre-commit-config.yaml

### Hedef
Her commit öncesi otomatik lint + test + güvenlik taraması.

### Yapılacaklar

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.7
    hooks:
      - id: bandit
        args: [-ll, --skip, B101,B603]
        exclude: tests/

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        args: [tests/, --ignore=tests/ReYMeN_reference, -x, -q]
        language: system
        pass_filenames: false
```

### Doğrulama
```bash
pre-commit run --all-files
```

---

## 3. Adım Script'leri (Öğrenme Testi)

### Hedef
Öğrenme döngüsünün gerçekten çalıştığını test et. Bir script bilerek hata içersin, motor hata alınca kendi çözsün.

### Yapılacaklar

**a) reymen/scripts/step_01_merhaba.py**
```python
# Basit script — hata yok, öğrenme gerektirmez
print("Merhaba ReYMeN!")
```

**b) reymen/scripts/step_02_hata.py**
```python
# Bilerek hata içeren script — öğrenme döngüsü testi
# Bu script NameError fırlatır
print(merhaba)  # NameError: name 'merhaba' is not defined
```

**c) Test et**
```python
from reymen.cereyan.motor import Motor
m = Motor()
m.script_calistir("reymen/scripts/step_01_merhaba.py")  # ✅ direkt geçer
m.script_calistir("reymen/scripts/step_02_hata.py")     # ❌ hata → öğrenme döngüsü
```

### Doğrulama
```python
from reymen.core.ogrenme import istatistik
s = istatistik()
assert s["toplam"] == 1  # 1 çözüm öğrenmiş olmalı
```

---

## 4. Test Coverage

### Hedef
Hangi modüllerin test kapsamı düşük, raporla ve eksik testleri ekle.

### Yapılacaklar

```bash
# Coverage raporu al
pytest --cov=reymen.core --cov=reymen.cereyan.motor \
       --cov=reymen.cereyan --cov-report=term-missing \
       --ignore=tests/ReYMeN_reference 2>&1 | tail -30
```

- %50 altındaki modülleri tespit et
- Her modül için en az 1 test dosyası ekle:
  - `tests/test_core/test_ogrenme.py`
  - `tests/test_core/test_model_adapter.py`
  - `tests/test_core/test_mcp_server.py`
  - `tests/test_core/test_session_search.py`

### Doğrulama
```bash
pytest tests/test_core/ -v --tb=short
# Tüm testler PASS
```

---

## 5. CHANGELOG.md

### Hedef
Proje değişikliklerini düzenli tut.

### Yapılacaklar

```markdown
# Changelog

## [2.1.0] - 2026-06-28
### Added
- Öğrenme döngüsü (reymen/core/ogrenme.py) — SQLite hafıza, TTL, soyut imza
- Model Adapter (reymen/core/model_adapter.py) — 7 provider, auto-detect
- Orchestrator (reymen/core/orchestrator.py) — solve_step, coz_hata
- MCP Server Host (reymen/core/mcp_server.py)
- Session Search FTS5 (reymen/core/session_search.py)
- Dockerfile + docker-compose.yml
- Skill import script (reymen/scripts/skill_import.py)
- .github/workflows/ci.yml

### Fixed
- shell=True 37→0 nokta temizlendi
- 12 sessiz except düzeltildi
- Cron dağınıklığı tek noktada toplandı
- 13 yeni __init__.py

## [2.0.0] - 2026-06-27
- İlk sürüm
```

---

## 6. CONTRIBUTING.md

### Hedef
GitHub'da açık kaynak katkısı için yönergeler.

### Yapılacaklar

```markdown
# Katkı Rehberi

## Başlarken
1. Fork et
2. `pip install -e ".[dev]"`
3. `pre-commit install`

## Branch Stratejisi
- `main` — kararlı sürüm
- `feature/xyz` — yeni özellik
- `fix/xyz` — hata düzeltme

## Test
```bash
pytest tests/ --ignore=tests/ReYMeN_reference -v
```

## Kod Standartları
- Ruff lint + format (pre-commit otomatik)
- Bandit güvenlik taraması
- shell=True KULLANMA
- Her yeni özellik için test ekle

## PR Süreci
1. feature branch aç
2. Kodla + test ekle
3. pre-commit çalıştır
4. PR aç, açıklama yaz
5. Review bekle
```

---

## ÖNCELİK
1 → shell=True kalanlar → 2 → pre-commit → 3 → adım script'leri → 4 → test coverage → 5 → CHANGELOG → 6 → CONTRIBUTING

## KRİTİK — Büyük Dosyaları Böl (Öncelik 0)
Cline önceki task'ta bölmeyi erteledi. ŞİMDİ YAP. 5 dosya, hepsi max 2.000 satır altına.

### 1. gateway/run.py (19.683 satır)
- `gateway/runner.py` — ana döngü
- `gateway/handlers.py` — mesaj işleyiciler
- `gateway/config.py` — yapılandırma
- `gateway/plugins.py` — plugin yükleme
- `gateway/health.py` — sağlık kontrolü

### 2. reymen/reymen_cli/main.py (14.988 satır)
- `reymen/reymen_cli/commands.py` — komutlar
- `reymen/reymen_cli/config.py` — yapılandırma
- `reymen/reymen_cli/display.py` — çıktı

### 3. reymen/sistem/cli_main.py (12.803 satır)
- `cli/display.py` — ekran çıktıları
- `cli/commands.py` — komut işleyiciler
- `cli/stream.py` — stream yönetimi
- `cli/voice.py` — ses işlemleri
- `cli/auth.py` — kimlik doğrulama

### 4. reymen/sistem/cli_mixin_commands.py (8.693 satır)
- Var olan mixin yapısını koru
- Her mixin kendi dosyasına (max 2.000 satır)

### 5. tests/test_bulk_5000.py (20.003 satır)
- Konusuna göre ayır: test_cron.py, test_gateway.py, test_agent.py vb.

### Kural
- Her dosya max 2.000 satır
- Mevcut public API değişmez (import'lar aynı kalır)
- Bölme sonrası `pytest` geçmeli
- Bot'ların çalışması etkilenmemeli

## KISITLAMALAR
- shell=True KULLANMA
- Her adımda pytest ile doğrula
- Hata alırsan düzeltip tekrar dene (max 3)
- Act modunda çalıştır
