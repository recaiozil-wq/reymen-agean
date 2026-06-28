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