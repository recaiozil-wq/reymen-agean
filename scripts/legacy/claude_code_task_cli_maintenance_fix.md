# Görev: cli_maintenance.py indentation hatası düzeltme

## NE
`reymen/sistem/cli_maintenance.py` dosyasında Claude Code bölme işlemi sırasında indentation bozuldu.

## HATA
```
SyntaxError: 'try' without 'except' or 'finally' on line 40-ish
```
Kök neden: `try/except` bloklarının girinti seviyeleri karıştı — `try` indentation'ı `except` ile eşleşmiyor, bazı bloklar ortada kalmış.

## YAPILACAKLAR (sırayla)
1. `reymen/sistem/cli_maintenance.py` dosyasını oku
2. Tüm `try/except/finally` bloklarını tara
3. **add_package_task**, **pip_list**, **check_ollama**, **check_python** fonksiyonlarındaki girintileri düzelt
   - `try:` → doğru seviye (fonksiyon içinde 1 indent)
   - `except X:` → `try` ile aynı seviye
   - `finally:` → `try` ile aynı seviye
4. Şu doğrulamayı yap:
```
python -c "compile(open('reymen/sistem/cli_maintenance.py').read(),'cli_maintenance.py','exec')"
```

## ONAY KRİTERİ
- `compile()` hata vermezse ✅
- Sadece indentation düzelt — fonksiyon mantığını değiştirme
- İç içe try/except'lerde hiyerarşiyi koru

## YEDEK
Dosyanın mevcut hali `reymen/sistem/cli_maintenance_fix.zip` içinde.
