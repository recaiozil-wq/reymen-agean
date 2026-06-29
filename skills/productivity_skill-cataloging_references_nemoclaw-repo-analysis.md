
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Productivity_Skill Cataloging_References_Nemoclaw Repo Analysis |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# NVIDIA NemoClaw Repo Analizi

Repo: https://github.com/NVIDIA/NemoClaw
Tarih: 14 Haziran 2026
Lisans: Apache 2.0
Durum: Alpha (aktif geliştirme)

## Ne İşe Yarar

NemoClaw, OpenClaw ve Hermes agent'larını NVIDIA OpenShell sandbox'ları içinde güvenle çalıştırmak için referans stack.
Linux Docker container bazlı — Windows'ta direkt çalışmaz.

## Bizim İçin Değerli Olan Parçalar

### 1. Skill Organizasyon Pattern'i (KULLANILDI)

NemoClaw'ın `.agents/skills/` dizini 3 audience bucket'a ayrılmış:
- `nemoclaw-user-*` (10 adet) — kullanıcı skill'leri
- `nemoclaw-maintainer-*` (12 adet) — bakım skill'leri
- `nemoclaw-contributor-*` (2 adet) — geliştirici skill'leri

Bu pattern Hermes'in 1.184 skill'ine uygulandı. Detay: `references/audience-classification.md`

### 2. AGENTS.md Formatı (KULLANILDI)

NemoClaw'ın AGENTS.md'si çok kapsamlı:
- Mimari tablosu (path → language → purpose)
- CLI quick reference
- Testing strategy (3 Vitest project)
- Security model (4 katman)
- Code style + commit conventions
- Git hooks (prek)
- PR requirements
- Gotchas bölümü

**Hermes için AGENTS.md oluşturuldu:**
`Watcher-Hermes/hermes-skills/blob/main/AGENTS.md`

İçerik: repo yapısı, skill formatı (frontmatter şeması), audience kategorizasyonu tablosu,
CLI quick reference, commit konvansiyonları (Conventional Commits), güvenlik kuralları.

### 3. Hermes Manifest Yapısı

`agents/hermes/manifest.yaml` — Hermes'in NemoClaw içindeki resmi konfigürasyon haritası:
- Health probe: port 8642 (GET /health)
- Config: `.hermes/config.yaml` + `.env`
- State dirs: memories, sessions, skills, plugins, cron, logs
- Dashboard: port 18789
- Inference: custom provider + model.base_url
- Messaging: telegram, discord, slack, wechat, whatsapp

### 4. validate-env-secret-boundary.py

`agents/hermes/validate-env-secret-boundary.py` (6.7 KB) — Hermes .env'sinde secret sızıntısını kontrol eden Python scripti. Direkt alınıp kullanılabilir.

### 5. Model-Specific Setup Schema

`nemoclaw-blueprint/model-specific-setup/schema.json` — model/provider compat registry için JSON schema. Hermes'e yeni model eklerken kullanılabilecek standart format.

## Kullanılmayan Parçalar (Windows'ta Çalışmaz)

- OpenShell Docker sandbox (Linux container)
- Container hardening (capability drops, process limits)
- Network policy engine (egress kontrolü)
- SSRF validation
- OpenClaw plugin sistemi
- Docker build (Dockerfile, start.sh)

## CLI Komutları

| Komut | Açıklama |
|-------|----------|
| `nemoclaw` | Ana CLI (OpenClaw için) |
| `nemohermes` | Hermes alias |
| `nemoclaw onboard` | İlk kurulum |
| `nemoclaw blueprint` | Sandbox yönetimi |
| `nemoclaw policies` | Network policy yönetimi |

## Agent Skill'leri (24 adet)

**Kullanıcı (10):** overview, get-started, configure-inference, configure-security, deploy-remote, manage-policy, manage-sandboxes, monitor-sandbox, reference, agent-skills

**Maintainer (12):** morning/evening/day, triage, PR review/find, security-code-review, cut-release-tag, release-notes, cross-issue-sweep, normalize-title-tags, verify-stale, policies

**Contributor (2):** create-pr, update-docs

## İlgili Ekosistem

| Repo | Açıklama |
|------|----------|
| NVIDIA/OpenShell | Alttaki sandbox runtime |
| VoltAgent/awesome-nemoclaw | NemoClaw preset/recipe koleksiyonu |
| vivekchand/clawmetry | 12 agent runtime için real-time observability |
| TheAiSingularity/hermesclaw | Hermes + OpenShell sandbox |
| Hmbown/NemoHermes | NVIDIA capability registry + Spark routing |
| jetsonhacks/NemoClaw-Orin | Jetson Orin kurulumu |
| LazaUK/AIFoundry-NemoClaw-AKS | Azure Kubernetes deployment |
