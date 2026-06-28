
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Windows Python Cli Installer_References_Re Hermes Setup |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# RE-Hermes v2 Kurulumu

## Yer
```
C:\Users\marko\re-hermes\
```

## Yapılan Değişiklikler

### 1. Model Güncelleme
`config.json` varsayılan modeli: `deepseek-chat` → `deepseek-v4-flash`

### 2. Non-Interactive Workspace
`main()` fonksiyonundaki `input()` satırı kaldırıldı, yerine:
```python
for i, a in enumerate(sys.argv[1:], 1):
    if a in ("-w", "--workspace") and i < len(sys.argv):
        workspace = sys.argv[i + 1]
        break
if not workspace:
    workspace = os.path.join(os.getcwd(), f"workspace_{filename.replace('.', '_')}")
```

### 3. API Anahtarı
DeepSeek API key config'e kaydedildi.

### 4. PATH
- Git Bash: alias `re-hermes="python /c/Users/marko/re-hermes/re-hermes.py"`
- Windows PATH: `C:\Users\marko\re-hermes` eklendi
- `.bat` launcher oluşturuldu

## Kullanım
```bash
re-hermes hedef.exe
re-hermes hedef.exe -w ozel_klasor
```

## AI False Positive Notları
- `WS2_32.dll` importu → AI "gereksiz ağ" der, ama `gethostname()` için normaldir
- `wget` string'i → AI "indirme aracı" der, ama log/error mesajı olabilir
- IP `5.1.0.0` → AI IP sanar, aslında `version="5.1.0.0"` manifest satırı
- Yüksek entropy → APK/ZIP dosyalarında normaldir (sıkıştırma)
- AES/RC4/XOR token'ları → Android/Java kripto API'leri, normal
- Domain listeleri → DEX class referansları, C2 değil

## Analiz Katmanları
1. Hash (MD5/SHA1/SHA256)
2. Entropy (Shannon)
3. Format (magic, PE/ELF header, sections, imports)
4. Strings (ASCII + UTF-16LE)
5. IOC (IP/URL/domain/email/registry)
6. Suspicious tokens (VirtualAlloc, CreateRemoteThread, CryptEncrypt...)
7. AI yorumu (opsiyonel, DeepSeek v4-flash)
