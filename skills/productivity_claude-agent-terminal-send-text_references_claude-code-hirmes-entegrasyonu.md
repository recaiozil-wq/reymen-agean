
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Productivity_Claude Agent Terminal Send Text_References_Claude Code Hirmes Entegrasyonu |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Claude Code ↔ Hermes Entegrasyonu

> Kaynak: Claude Opus 4.8'in 11.06.2026 oturumunda verdiği cevap.
> Soru: "Claude Code, Hermes'in skill ve Obsidian notlarını nasıl kullanabilir?"

## 3 Yöntem (Claude Önerisi)

### 1. `.instructions.md` (en basit, tek seferlik)

VS Code workspace'inde `.vscode/.instructions.md` oluştur. Claude Code otomatik okur.

```
project/
└── .vscode/
    └── .instructions.md   <- Hermes skill'lerini buraya ekle
```

**Ne yap:** Hermes skill'lerinin özetini/ilgili kısımlarını bu dosyaya kopyala.
**Artı:** Sıfır kurulum, Claude Code doğrudan okur.
**Eksi:** Manuel güncelleme gerekir, dinamik değil.

### 2. Symlink + `.instructions.md` (sürekli kullanım)

```powershell
# Hermes skill'lerini projeye bağla
New-Item -ItemType SymbolicLink -Path ".\docs\hermes-skills" `
  -Target "C:\Users\marko\AppData\Local\hermes\skills"

# Obsidian vault'u projeye bağla
New-Item -ItemType SymbolicLink -Path ".\docs\obsidian-vault" `
  -Target "C:\Users\marko\OneDrive\Belgeler\Obsidian Vault"
```

**Artı:** Canlı bağlantı — güncelleme gerektirmez.
**Eksi:** Workspace dosya ağacı kalabalıklaşır.

### 3. MCP Server (ileri seviye, dinamik)

Obsidian vault'unu Model Context Protocol sunucusu olarak expose et. Claude Code MCP üzerinden canlı okuyabilir.

**Artı:** Gerçek zamanlı, dinamik.
**Eksi:** Kurulum karmaşık, bakım gerektirir.

## Claude'ın Tavsiyesi

| Durum | Yöntem |
|-------|--------|
| Tek seferlik çalıştırma | Yöntem 1 (pre-prompt / .instructions.md) |
| Sürekli kullanım | Yöntem 2 (symlink + .instructions.md) |
| Obsidian'ı canlı tutmak | Yöntem 3 (MCP) |

## Pratik Uygulama: Soru Gönderme Akışı

Hermes, Claude Code'a soru göndermek için şu sırayı dene:

1. **Clipboard paste** (önerilen) — PowerShell `Get-Content | Set-Clipboard` ile panoya kopyala, `pyautogui.hotkey('ctrl', 'v')` ile yapıştır
2. **pyautogui.write()** — kısa metinlerde, bot algılaması riski var
3. **Doğal yazma** — bot algılaması durumunda, random gecikmeli harf harf yazma
4. **Tam başarısızlık protokolü** — kullanıcıya "manuel yapıştır" de

## Hermes Çalışma Dizini Referansları

| Kaynak | Yol |
|--------|-----|
| Hermes skills | `C:\Users\marko\AppData\Local\hermes\skills\` |
| Obsidian vault | `C:\Users\marko\OneDrive\Belgeler\Obsidian Vault` |
| VS Code workspace | `C:\Users\marko\OneDrive\Desktop\hermes_v7\tests` (veya mevcut proje) |
| Claude input koordinatı | Değişken — her seferinde kullanıcıya tıklat |

## Test Edilenler (11.06.2026)

- PowerShell `Get-Content | Set-Clipboard` ✓ çalıştı
- `pyautogui.click(568, 818)` → `ctrl+v` → `enter` ✓ Claude'a ulaştı
- `vision_analyze` ile cevap okuma ✓ Claude'ın cevabı okundu
- ctypes clipboard API'si ✗ access violation (hata 0x20)
- `pyautogui.write()` ✗ karakter bozulması
