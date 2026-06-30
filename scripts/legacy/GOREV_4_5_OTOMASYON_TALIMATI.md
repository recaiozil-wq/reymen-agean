# ReYMeN Test Otomasyonu + AGENTS.md Temizlik

## Ne Yapılacak?

Kalan 2 eksik otomatik olarak tamamlansın:

| # | Eksik | Çözüm |
|---|-------|-------|
| 4 | CLI dışı 59 modülde test yok | `reymen_test_otomasyonu.py` ile otomatik test üret + coverage ölç |
| 5 | AGENTS.md gereksiz bölümler | Script otomatik temizler (392 → ~50 satır) |

---

## Script: `reymen/scripts/reymen_test_otomasyonu.py`

### Yaptıkları (sırayla)

| Adım | Ne Yapar? | Detay |
|------|-----------|-------|
| **1** | Modülleri tara | `reymen/sistem/` altında CLI dışı (`cli_*` olmayan) tüm .py dosyalarını AST ile parse et |
| **2** | Public fonksiyon bul | Her modülde `_` ile başlamayan fonksiyonları tespit et |
| **3** | Test üret | Her fonksiyon için try/except'li pytest testi yaz → `reymen/test/test_sistem/` |
| **4** | Coverage ölç | `pytest --cov=reymen.sistem` çalıştır, modül bazlı yüzdeleri çıkar |
| **5** | AGENTS.md temizle | Gereksiz bölümleri kırp, sadece kritik talimatları bırak |
| **6** | Rapor | `test_otomasyon_raporu.json` yaz |

### Kod Yapısı (özet)

```
reymen_test_otomasyonu.py
├── adim1_tara_moduller()       → AST parse, public fonk bul
├── adim2_test_uret(modul)      → pytest kodu üret
├── adim3_test_yaz(moduller)    → dosyaya yaz + compile doğrula
├── adim4_coverage_olc()        → subprocess pytest --cov
├── adim5_agents_temizle()      → AGENTS.md kırp
└── main()                      → sırayla çalıştır
```

### Güvenlik Önlemleri

- `compile()` ile her test dosyası yazılmadan önce doğrulanır
- SyntaxError varsa o dosya atlanır, diğerleri devam eder
- Her test fonksiyonu **try/except** içinde çağrılır — crash durumunda bile pytest devam eder
- Mevcut testlere (`reymen/test/test_cli/`) dokunulmaz
- `main.py`, `run_agent.py` gibi ağır modüller hariç tutulur

### Çıktı Örneği

```
📦 ADIM 1: 59 modül bulundu
📝 ADIM 2-3: 45 test dosyası yazıldı
📊 ADIM 4: 320 passed, 0 failed, toplam coverage %35
📄 ADIM 5: AGENTS.md 392 → 48 satır
```

---

## Claude Code'a Verilecek Talimat

```
1. python reymen/scripts/reymen_test_otomasyonu.py çalıştır
2. Çıktıyı göster (coverage yüzdeleri + test geçme sayısı)
3. test_otomasyon_raporu.json dosyasını oku, toplam_coverage değerini söyle
4. Eğer fail varsa, hangi testler ve nedenini raporla
5. reymen/test/test_sistem/ altındaki test dosyalarına elle müdahale etme
```

---

## Beklenen Sonuç

| Metrik | Önce | Sonra |
|--------|------|-------|
| Test sayısı | 181 | 300+ |
| Coverage (CLI modülleri) | %43 | %35-45* |
| AGENTS.md | 392 satır | ~50 satır |
| Test fail | 0 | 0 |

*Toplam coverage düşebilir çünkü 59 yeni modül eklendi ama her biri sadece import+call seviyesinde testli. Gerçek coverage artışı için her modüle özel test yazmak gerekir.
