---
name: data-science-powerbi-mcp
description: Power BI Desktop'taki semantic modelleri AI agent'ına bağlar. Doğal dil
  ile DAX formülleri yazdırabilir, tarih tabloları oluşturabilir, modelleme yapabilirsin.
title: Data Science Powerbi Mcp
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

AI agent''ı Power BI modellerine bağlama.'
# Power BI MCP

## Ne işe yarar
Power BI Desktop'taki semantic modelleri AI agent'ına bağlar. Doğal dil ile DAX formülleri yazdırabilir, tarih tabloları oluşturabilir, modelleme yapabilirsin.

## Ön koşullar
- **Power BI Desktop** — Microsoft Store'dan yüklenir (`winget install "Power BI Desktop"`)
- **VS Code** — `code` CLI çalışıyor olmalı
- **Power BI Modelling MCP extension** — VS Code marketplace'ten "Power BI Modelling MCP" (Microsoft, v0.4.0+)

## Kurulum

### 1. Extension'ın yolunu bul
```
# VS Code extensions altında
~/.vscode/extensions/analysis-services.powerbi-modeling-mcp-*/server/powerbi-modeling-mcp.exe
```

### 2. config.yaml'e MCP server'ı ekle
```yaml
mcp_servers:
  powerbi-modeling:
    command: "C:\\Users\\<kullanici>\\.vscode\\extensions\\analysis-services.powerbi-modeling-mcp-<version>-win32-x64\\server\\powerbi-modeling-mcp.exe"
    args: []
```

⚠️ **Yol formatı:** Ters slash'lar çift olmalı (`\\`). Tek slash çalışmaz.

### 3. Power BI Desktop'ı aç
MCP server bağlanmak için Power BI Desktop'ın çalışıyor ve bir dosyanın açık olması gerekir.

## Kullanım

Power BI Desktop açıkken:
```
# Bağlan
Agent: powerbi-modeling'e bağlan
Kullanıcı: "Satış dashboardu verilerime bağlan"

# DAX formülleri yazdır
Agent: "Bir tarih tablosu oluştur (yıl, ay, çeyrek, hafta günü ekle)"
Agent: "102 tane zaman zekası formülü oluştur (YTD, MTD, önceki dönem, kümülatif)"

# PDF rapor oluştur
Agent: "Satış performans analiz raporu oluştur ve PDF olarak ver"
```

## Örnek prompt'lar
| Prompt | Ne yapar |
|--------|----------|
| "Bir tarih tablosu oluştur ve modeller arası ilişki kur" | Tarih tablosu + ilişkilendirme |
| "Ölçü tabloları ve hesaplamaları oluştur" | 13+ ölçü (kar marjı, müşteri sayısı, ortalama sipariş) |
| "Her DAX fonksiyonuna satır satır açıklama ekle" | Yeni başlayanlar için dökümantasyon |
| "Zaman zekası formülleri oluştur" | 102 zaman zekası ölçüsü |

## Sorun giderme
- **"Failed to connect"**: Power BI Desktop açık mı kontrol et
- **"Extension not found"**: Extension versiyon numarasını kontrol et (`~/.vscode/extensions/` altında listele)
- **Yol çalışmıyor**: Ters slash'ları çiftlediğinden emin ol

## Kaynak
- [Power BI Modeling MCP (GitHub)](https://github.com/microsoft/powerbi-modeling-mcp)
- Oğuzhan ÇOLAK — "Claude'u Power BI'a Bağladım" (YouTube)
