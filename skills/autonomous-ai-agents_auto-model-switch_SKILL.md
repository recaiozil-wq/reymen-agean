---
name: autonomous-ai-agents-auto-model-switch
description: Kullanıcıya onay sormadan, görev gerektirdiğinde otomatik model geçişi
  yapmak.
title: Autonomous Ai Agents Auto Model Switch
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

# Otonom Model Geçişi

## Amaç
Kullanıcıya onay sormadan, görev gerektirdiğinde otomatik model geçişi yapmak.

## Kullanım
- Ana akış: `stepfun/step-3.7-flash:free`
- Yedek görev modeli: `dolphin-llama3`
- Kural: Her görevde ilk olarak Hermes skill + Obsidian kontrolü yap. Kayıt varsa yeniden yazma, var olan akışa devam et.
- Görev tamamlandığında ana akışa geri dön.

## Otomatik Geçiş Yöntemleri

### 1. CLI agent'dan model değiştirme (ÖNERİLEN)
```bash
hermes config set model <alias>
```
Alias'lar (config.yaml'dan okunur): `deepseek`, `dolphin`, `dolphin-lmstudio`, `llama`
**NOT:** Bu değişiklik sadece **yeni oturumlarda** geçerlidir. Mevcut oturum eskisiyle devam eder.

### 2. Manuel interaktif model değiştirme
```bash
hermes model
```
Interaktif menü açar. CLI agent'dan çalıştırılamaz (PTY gerekir).

### 3. Config.yaml düzenleme
Dosya: `C:\\Users\\marko\\AppData\\Local\\hermes\\config.yaml`
```yaml
model:
  default: dolphin-lmstudio
  provider: custom
  base_url: http://localhost:1234/v1
  model: dolphin-8b
```

### 4. Görev sonrası geri dönüş — cron job
```bash
hermes cron create '30m' \
  'prompt: Ana akış modeline geri dön: stepfun/step-3.7-flash:free' \
  --model dolphin-llama3
```

## PITFALLS

- **`/model` slash komutu CLI agent'tan çalıştırılamaz** — gateway seviyesinde işlenir. Her zaman `hermes config set model <alias>` kullan.
- **Config değişikliği mevcut oturumu etkilemez** — bu oturum başlatıldığı config ile devam eder. Yeni oturum gerekir.
- **Kullanıcı fark eder** — "sen hala eski modeldesin" derse haklıdır. Açıkla ve yeni oturum öner.

## Kaynak
- Hermes Agent skill: `hermes-agent` (model seçimi bölümü)
