
> **Kategori:** android

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Android_Android Apk Modding_References_3 Saniye Bekle Sonra Crash Kontrol |
| **Nerede?** | android/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# 3 saniye bekle, sonra crash kontrolü:
adb logcat -d -b crash | grep -i "com.package.name"
adb logcat -d | grep -i "FATAL\|ANR\|Exception\|deadObject" | grep "com.package.name"
```

**GATE 6b:**
```bash
CRASH_COUNT=$(adb logcat -d | grep -c -i "FATAL\|ANR\|Exception\|deadObject.*com.package.name")
[ "$CRASH_COUNT" = "0" ] && echo "DOGRULAMA_GECTI" || echo "DOGRULAMA_KALDI: $CRASH_COUNT crash"
```

Crush varsa logcat çıktısını oku:
- `ClassNotFoundException` → smali'de class reference yanlış
- `ResourceNotFoundException` → resource ID public.xml'de yok
- `UnsatisfiedLinkError` → native lib hizalanmamış veya eksik
- `SecurityException` → manifest'te eksik izin

**6c — Rapor:**
```
DURUM: GECTI / KALDI
targetSdk: 35
Split: hayır
Native lib: arm64-v8a (3 .so)
Obfuscation: R8 var
APK boyutu: 12.4 MB
İmza: v2+v3
Logcat: 0 crash
```

---