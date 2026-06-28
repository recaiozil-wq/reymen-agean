---
skill_id: e00417fb9b30
usage_count: 1
last_used: 2026-06-16
---
# Test Durumu ve Yaygın Tuzaklar

## Test Durumu

109 test, 108 başarılı, 1 hata (move --fast TypeError → düzeltildi)
Tüm komutlar gerçek Windows'ta test edildi.

## Test Protokolü (X-RAY)

Bu kullanıcı için test raporlamada X-RAY modu zorunludur:

1. **Her testi ayrı terminal çağrısıyla çalıştır** — her komut ayrı çağrılmalı
2. **Ham çıktıyı göster** — filtresiz, yorumsuz, olduğu gibi
3. **Her test numaralandırılır** — `[TEST 1]`, `[TEST 2]`, ...
4. **Hata + çözüm birlikte gösterilir** — hata oluştuysa hemen çözümü uygula, aynı testi tekrar çalıştır
5. **Son sayım** — `X/Y TEST GECTI, Z HATA` formatında kapat
6. **Tekrar eden test varsa belirt** — hata+düzeltme aynı komutun iki kez çalışması
7. **Eksik senaryoları işaretle** — gerçek Windows'ta test edilmemiş kod, mock-only doğrulama
8. **FORENSIC çapraz-kontrol** — her satırı ham veriyle sun

---

## Yaygın Tuzaklar

| Hata | Çözüm |
|------|-------|
| `element "X" list` action algılanmıyor | args[2] action keyword kontrolü |
| PowerShell çıktısı cp1254/UTF-8 | `[Console]::OutputEncoding = UTF8` + utf-8-sig öncelikli |
| `dwExtraInfo=None` → TypeError | ULONG_PTR `None` kabul etmez, `0` kullan |
| `--by ClassName coord` action kaçıyor | Flag'leri atlayan parser (`_parse_action`) |
| Tek elemanlı JSON dizi → nesne | `ConvertTo-Json @($results)` (@() sarması) |
| Türkçe Q Klavye URL/Sembol Sorunu | ctypes `keybd_event` ile `:`, `/`, `?`, `&` gibi özel karakterler Türkçe Q klavyede yanlış gider. **URL yazmak için asla ctypes kullanma** — `hermestor.py navigate <URL>` kullan |
| pyautogui asılıyor | hermesmouse.py kullan, ctypes hiç takılmaz |
| PowerShell Forms exit 1/127 | hermesmouse.py tek satır terminal komutuyla çalışır |
| Hareket oldu ama görünmedi | `sweep` komutunu kullan, daire çizerek gösterir |
| Path boşluk hatası | Script `C:\Users\marko\hermesmouse.py` (boşluksuz kök) |
| Ekran çözünürlüğü farklı | Önce `pos` ile gerçek koordinatları al |
