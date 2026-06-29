---
name: software-development_re-hermes-v3_references_jadx-deep-analysis-workflow
description: Jadx Derin Analiz Workflow
title: "Software Development Re Hermes V3 References Jadx Deep Analysis Workflow"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Jadx Derin Analiz Workflow |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Jadx Derin Analiz Workflow

RE-Hermes triyajı tamamlandıktan sonra şüpheli token'ları doğrulamak için kullanılır.

## Adım 1 — jadx Kurulum (tek seferlik)

```bash
curl -sL "https://github.com/skylot/jadx/releases/download/v1.5.1/jadx-1.5.1.zip" -o /tmp/jadx.zip
unzip -qo /tmp/jadx.zip -d C:\Users\marko\jadx
# jadx.bat -> C:\Users\marko\jadx\bin\jadx.bat
```

## Adım 2 — APK'yı Decompile Et

```bash
/c/Users/marko/jadx/bin/jadx.bat -d output_dir hedef.apk
# output_dir/ altında *.java dosyalarına dönüşür
```

Obfuscated APK'larda Jadx 10-15 hata ile bitebilir — normaldir. Çoğu sınıf yine de decompile olur.

## Adım 3 — Token Doğrulama

### RE-Hermes'in bulduğu token'ları Java kodunda ara:

```bash
# Tam kelime arama (false positive riski az)
grep -rn "\bcurl\b" output_dir/ 2>/dev/null | head -20

# Regex ile
grep -rn "getDeviceId\|Runtime\.exec\|ProcessBuilder" output_dir/ 2>/dev/null | head -20

# Belirli API'ler
grep -rn "TelephonyManager\|getDeviceId\|getLastKnownLocation" output_dir/ 2>/dev/null
```

### Byte seviyesinde doğrulama (en kesin):

```python
with open("hedef.apk", "rb") as f:
    data = f.read()
count = data.count(b"curl")  # sadece tam "curl" kelimesi
```

## Adım 4 — Native Kod (.so) Sembol Kontrolü

```
cd workspace/static_analysis/unpacked/
for f in *.so; do
    nm -D "$f" 2>/dev/null | grep -i "ptrace\|curl\|chmod"
done
```

## False Positive Kategorileri

| Token | Muhtemel FP Kaynağı |
|-------|---------------------|
| `curl` | `left-curly-bracket` / `right-curly-bracket` |
| `ptrace` | C++ `perftools7tracing...` sembol adları |
| `GetProcAddress` | `eglGetProcAddress` (OpenGL) |
| `getDeviceId` | `getDeviceIds` (TensorFlow NNAPI logging) |

## Ne Zaman Ghidra/IDA Gerekir

Jadx Java bytecode'u decompile eder. Aşağıdaki durumlarda native .so analizi (Ghidra/IDA) gerekir:
- Token Jadx çıktısında bulunamadıysa
- Token sayısı .so parse ile eşleşiyorsa
- Şüpheli JNI çağrıları (`System.loadLibrary`) varsa
