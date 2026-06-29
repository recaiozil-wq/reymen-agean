
> **Kategori:** Medya

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Media_Talimat Uygulama_References_Powerbi Mcp Setup |
| **Nerede?** | Medya/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Power BI MCP — Kurulum Notları

## Bileşenler

| Bileşen | Yol / Not |
|---------|-----------|
| Power BI Desktop | Microsoft Store (msstore: `winget list "Power BI Desktop"`) |
| VS Code | `code --version` ile doğrula |
| PBI Modelling MCP Extension | `analysis-services.powerbi-modeling-mcp-0.4.0-win32-x64` |
| Extension yolu | `C:\Users\{kullanici}\.vscode\extensions\analysis-services.powerbi-modeling-mcp-{version}-win32-x64\server\powerbi-modeling-mcp.exe` |
| MCP Sunucu | `powerbi-modeling-mcp.exe` |

## ReYMeN Config (config.yaml)

```yaml
mcp_servers:
  powerbi-modeling:
    command: "C:\\Users\\{kullanici}\\.vscode\\extensions\\analysis-services.powerbi-modeling-mcp-{version}-win32-x64\\server\\powerbi-modeling-mcp.exe"
    args: []
```

## Kullanım

1. Power BI Desktop'ı aç ve bir .pbix dosyası yükle
2. ReYMeN'e şu promptu ver:
   ```
   powerbi-modeling'e bağlan ve [istek] yap
   ```
3. Örnek istekler:
   - "tarih tablosu oluştur ve yıl/ay/çeyrek sütunları ekle"
   - "satış dashboardu için 13 DAX ölçüsü yaz (toplam satış, kar marjı, YTD, vs)"
   - "102 zaman zekası fonksiyonu oluştur"
   - "her DAX ölçüsüne satır satır açıklama ekle"
   - "PDF raporu oluştur"

## Önemli Uyarılar

- YAML'de Windows yolunda **çift ters slash** (`\\`) kullan
- Extension sürüm numarası değişebilir — `ls ~/.vscode/extensions/ | grep powerbi` ile kontrol et
- Power BI Modelling MCP **Public Preview** — tool'lar değişebilir
- LLM yanlış DAX üretebilir — her değişiklikten önce model yedeği al
