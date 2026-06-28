---
name: github-code-review
description: GitHub PR kod inceleme - hata, guvenlik, kalite denetimi
version: 1.0.0
metadata:
  hermes:
    tags: [github, code-review, pr, quality]
    category: software-development
    requires_toolsets: [terminal, web]
    requires_tools: [terminal]
    config:
      - key: code_review.repos
        description: "İzlenecek repo'lar (virgulle ayir)"
        default: "Watcher-Hermes/hermes-agent"
        prompt: "Hangi repolari takip edeyim?"
---

# GitHub Kod Inceleme

## Ne Zaman Kullanilir
- Yeni bir PR geldiginde otomatik inceleme
- /code-review <repo> <pr_no> ile manuel inceleme
- Cron ile periyodik PR taramasi

## Neleri Kontrol Et
1. **Hatalar** — Logic hatalari, off-by-one, null/undefined handling
2. **Guvenlik** — Injection, auth bypass, sirlar, SSRF
3. **Performans** — N+1 query, sinirsiz dongu, memory leak
4. **Kod Kalitesi** — Isimlendirme, olu kod, hata yonetimi
5. **Testler** — Degisiklikler test edilmis mi? Edge case'ler?

## Cikti Formati
Her bulgu icin:
- **Dosya:Satir** | **Onem** (Kritik/Uyari/Oneri) | **Sorun** | **Cozum**

## Cron Talimati
```
/cron add "0 */2 * * *" "Check for new open PRs in Watcher-Hermes/hermes-agent.
For each PR opened in the last 4 hours:
1. gh pr diff NUMBER --repo Watcher-Hermes/hermes-agent
2. Review for bugs, security, performance, code quality
3. Format: Dosya:Satir | Onem | Sorun | Cozum
Deliver to telegram."
```
