---
skill_id: f0484a7f2de6
usage_count: 1
last_used: 2026-06-16
---
# .gitignore'a nul ekle (yukarıdaki template'de zaten var)
```

Eğer `nul` dosyası git add sırasında hataya sebep olursa:
1. `rm -f nul` ile sil
2. `.git` klasörünü silip (`rm -rf .git`) baştan init et
3. `.gitignore`'da `nul` satırı olduğundan emin ol
4. `git add -A` ile tekrar dene

### `.gitignore`'a İlk Eklenmesi Gerekenler (Android Özel)

| Pattern | Neden |
|---------|-------|
| `**/build` | Tüm `build/` alt klasörleri (`app/build/`, `build/`) |
| `release.keystore` | İmza anahtarı — sızdırılırsa başkası APK imzalayabilir |
| `nul` | Windows phantom dosya |
| `.idea/` | Android Studio kişisel ayarları |
| `local.properties` | SDK yolu (kullanıcıya özel) |
| `.gradle` | Gradle cache |