---
name: daily-briefing
description: Gunluk ozet botu - web'den haber topla, ozetle, Telegram'a gonder
version: 1.0.0
metadata:
  hermes:
    tags: [productivity, automation, news, briefing]
    category: productivity
    requires_toolsets: [web, cronjob]
    requires_tools: [web_search]
    config:
      - key: briefing.topics
        description: "Haber konulari (virgulle ayir)"
        default: "AI agents, open source LLMs, technology"
        prompt: "Hangi konulari takip edeyim?"
      - key: briefing.deliver_to
        description: "Hedef platform (telegram, local, discord)"
        default: "telegram"
        prompt: "Nereye gondereyim?"
    blueprint:
      schedule: "0 8 * * *"
      deliver: origin
      prompt: "Gunluk brifing hazirla - asagidaki gorev talimatina bak"
---

# Gunluk Brifing Botu

## Ne Zaman Kullanilir
- Her sabah guncel haberleri almak istediginde
- Belirledigin konularda otomatik ozet istedigin zaman
- /daily-briefing yazarak anlik calistirabilirsin

## Cron Job Talimati (BluePrint)
Asagidaki prompt'u cron job olarak kaydet:

```
/cron add "0 8 * * *" "Create a morning briefing covering BELIRLEDIGIN_KONULAR.

For each topic, search the web for recent news from the past 24 hours.
Summarize the top 2 stories with links. Use a professional but friendly tone.

Format:
## Gunluk Brifing — (tarih)

### 1. (konu basligi)
- (haber basligi): 2 cumle ozet + link
- (haber basligi): 2 cumle ozet + link

### 2. (konu basligi)
...

--- 
Hazirlayan: ReYMeN
"
```

## Manuel Kullanim
```
/daily-briefing
```
ya da
```
/daily-briefing AI agents, open source
```

## Ozellikler
- Web'den son 24 saat haber toplama
- Her konu icin en iyi 2 haberi secme
- Kaynak linklerle birlikte ozet
- Telegram/Discord/local teslimat
- Hata durumunda [SILENT] (sessiz mod)
