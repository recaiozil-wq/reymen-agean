
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Data Scraper Agent_References_Github Workflows Scraper Yml |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# .github/workflows/scraper.yml
name: Data Scraper Agent

on:
  schedule:
    - cron: "0 */3 * * *"  # every 3 hours — adjust to your needs
  workflow_dispatch:        # allow manual trigger

permissions:
  contents: write   # required for the feedback-history commit step

jobs:
  scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 20

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - run: pip install -r requirements.txt