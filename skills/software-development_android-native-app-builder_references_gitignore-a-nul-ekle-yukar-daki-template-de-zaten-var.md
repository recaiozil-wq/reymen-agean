---
name: software-development_android-native-app-builder_references_gitignore-a-nul-ekle-yukar-daki-template-de-zaten-var
description: .gitignore'a nul ekle (yukarıdaki template'de zaten var)
title: "Software Development Android Native App Builder References Gitignore A Nul Ekle Yukar Daki Template De Zaten Var"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | .gitignore'a nul ekle (yukarıdaki template'de zaten var) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

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
