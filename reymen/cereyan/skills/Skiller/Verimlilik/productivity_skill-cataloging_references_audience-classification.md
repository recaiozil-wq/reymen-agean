
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Productivity_Skill Cataloging_References_Audience Classification |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Skill Kütüphanesi — Audience Sınıflandırma Prosedürü

NemoClaw (NVIDIA/NemoClaw) referans stack'inden esinlenen 3'lü audience sistemi.
Her SKILL.md frontmatter'ına `audience: user | maintainer | contributor` alanı eklenir.

## Audience Tanımları

| Audience | Kim | Kapsam |
|----------|-----|--------|
| `user` | Günlük kullanıcı (%71.6) | AI/ML araçları, windows otomasyonu, media, creative, productivity, note-taking, gaming, araştırma, prompt mühendisliği, ML model yönetimi |
| `contributor` | Kod geliştiren (%24.2) | Software development, testing, git/PR, framework pattern'leri, kod review, CI/CD, reverse engineering, scaffold, build araçları |
| `maintainer` | Sistemi yöneten (%4.1) | Cron/backup, audit, vault maintenance, monitoring, cost optimization, cleanup, güvenlik izleme, devops |

## Sınıflandırma Hiyerarşisi (Öncelik Sırası)

```
1. KATEGORI BAZLI → skill bir kategori klasörü içindeyse (software-development/, ecc/, github/)
2. ECC OVERRIDE  → ecc/ içinde ama contributor olan spesifik skill'ler (pattern'ler)
3. ROOT LIST     → kök dizindeki skill'lerin manuel listesi
4. DEFAULT       → user
```

### 1. Kategori Bazlı (Toplu Atama)

| Kategori Klasörü | Audience | Gerekçe |
|-----------------|----------|---------|
| `software-development/` | **contributor** | Kod yazma, build, test, debug |
| `github/` | **contributor** | PR, code review, git workflow |
| `devops/` | **maintainer** | Backup, cron, migration, servis yönetimi |
| `automation/` | **maintainer** | n8n, otomasyon iş akışları |
| `windows-automation/` | user | Sistem otomasyonu kullanımı |
| `windows-shortcuts/` | user | Klavye kısayol referansı |
| `windows-system-automation/` | user | Windows araçları |
| `ecc/` (default) | user | AI/ML araç kullanım kılavuzları |
| `autonomous-ai-agents/` | user | Otonom ajan kullanımı |
| `creative/`, `media/`, `gaming/` | user | İçerik oluşturma araçları |
| `note-taking/` | user | Obsidian kullanımı |
| `research/` | user | Araştırma araçları |
| `security/` | user | Pentest/analiz araç kullanımı |
| `mlops/`, `data-science/` | user | ML model yönetimi |
| `productivity/` | user | Doküman, email, takvim |
| `user-preferences/` | user | Kişiselleştirme (hersona) |

### 2. ECC Override Listesi (contributor)

`ecc/` içinde olup contributor sayılan skill'ler:

**Dil/Framework Pattern'leri:**
`react-patterns`, `react-testing`, `react-performance`, `rust-patterns`, `rust-testing`,
`golang-patterns`, `golang-testing`, `python-patterns`, `python-testing`,
`django-patterns`, `django-tdd`, `django-security`, `django-celery`, `django-verification`,
`fastapi-patterns`, `springboot-patterns`, `springboot-security`, `springboot-tdd`, `springboot-verification`,
`nestjs-patterns`, `kotlin-patterns`, `kotlin-testing`, `kotlin-coroutines-flows`,
`kotlin-exposed-patterns`, `kotlin-ktor-patterns`, `dart-flutter-patterns`,
`swiftui-patterns`, `swift-concurrency-6-2`, `swift-actor-persistence`, `swift-protocol-di-testing`,
`backend-patterns`, `frontend-patterns`, `api-design`, `android-clean-architecture`,
`hexagonal-architecture`, `mysql-patterns`, `postgres-patterns`, `redis-patterns`, `prisma-patterns`,
`docker-patterns`, `kubernetes-patterns`, `cpp-coding-standards`, `cpp-testing`,
`csharp-testing`, `dotnet-patterns`, `fsharp-testing`, `perl-patterns`, `perl-security`, `perl-testing`,
`java-coding-standards`, `jpa-patterns`, `laravel-patterns`, `laravel-security`, `laravel-tdd`,
`laravel-verification`, `laravel-plugin-discovery`, `quarkus-patterns`, `quarkus-security`,
`quarkus-tdd`, `quarkus-verification`, `angular-developer`, `tinystruct-patterns`,
`bun-runtime`, `vite-patterns`, `nextjs-turbopack`, `nuxt4-patterns`,
`compose-multiplatform-patterns`, `nodejs-keccak256`

**Test/QA Pattern'leri:**
`tdd-workflow`, `e2e-testing`, `browser-qa`, `eval-harness`, `benchmark`,
`benchmark-optimization-loop`, `windows-desktop-e2e`

**Mimari/Standartlar:**
`design-system`, `motion-patterns`, `motion-foundations`, `motion-advanced`, `motion-ui`,
`architecture-decision-records`, `security-review`, `security-bounty-hunter`, `security-scan`,
`coding-standards`, `error-handling`, `database-migrations`, `deployment-patterns`,
`git-workflow`, `github-ops`, `mcp-server-patterns`, `ci-cd`

**Kod Geliştirme Süreçleri:**
`issue-to-pr`, `migration-agent`, `code-tour`, `verification-loop`, `production-audit`,
`repo-scan`, `codehealth-mcp`, `agentic-engineering`, `ai-first-engineering`,
`continuous-agent-loop`, `autonomous-loops`, `autonomous-agent-harness`,
`subagent-driven-development`, `intent-driven-development`,
`orch-add-feature`, `orch-build-mvp`, `orch-change-feature`, `orch-fix-defect`,
`orch-refine-code`, `orch-pipeline`, `plan-orchestrate`,
`nanoclaw-repl`, `santa-method`, `recursive-decision-ledger`,
`deep-research`, `search-first`, `flox-environments`,
`dmux-workflows`, `dynamic-workflow-mode`,
`ata-throughput-accelerator`, `parallel-execution-optimizer`,
`latency-critical-systems`, `context-budget`, `config-gc`,
`product-capability`, `product-lens`, `team-builder`, `team-agent-orchestration`,
`ui-to-vue`, `documentation-lookup`, `skill-comply`, `skill-scout`, `skill-stocktake`,
`hookify-rules`, `inherit-legacy-style`, `ecc-tools-cost-audit`,
`opensource-pipeline`, `hermes-imports`, `nutrient-document-processing`,
`enterprise-agent-ops`, `uncloud`, `project-flow-ops`, `ralphinho-rfc-pipeline`,
`token-budget-advisor`, `strategic-compact`, `workspace-surface-audit`,
`terminal-ops`, `research-ops`, `email-ops`, `messages-ops`, `knowledge-ops`,
`canary-watch`, `click-path-audit`, `cost-aware-llm-pipeline`, `cost-tracking`,
`agent-harness-construction`, `agent-introspection-debugging`, `agent-eval`,
`agent-payment-x402`, `agent-sort`, `api-connector-builder`, `blueprint`,
`brand-voice`, `automation-audit-ops`, `cisco-ios-patterns`, `ck`,
`claude-devfleet`, `clickhouse-io`, `codebase-onboarding`, `crosspost`,
`content-engine`, `dashboard-builder`, `data-scraper-agent`,
`defi-amm-security`, `exa-search`, `fal-ai-media`,
`foundation-models-on-device`, `frontend-a11y`, `frontend-design-direction`,
`frontend-slides`, `gget`, `google-workspace-ops`,
`healthcare-cdss-patterns`, `healthcare-emr-patterns`, `healthcare-eval-harness`,
`healthcare-phi-compliance`, `hipaa-compliance`,
`homelab-pihole-dns`, `homelab-network-readiness`, `homelab-network-setup`,
`homelab-vlan-segmentation`, `homelab-wireguard-vpn`,
`ios-icon-gen`, `iterative-retrieval`,
`ito-basket-compare`, `ito-data-atlas-agent`, `ito-market-intelligence`, `ito-trade-planner`,
`jira-integration`, `lead-intelligence`, `liquid-glass-design`,
`literature-review`, `llm-trading-agent-security`,
`make-interfaces-feel-better`, `manim-video`, `market-research`,
`marketing-campaign`, `mle-workflow`,
`netmiko-ssh-automation`, `network-bgp-diagnostics`, `network-config-validation`,
`network-interface-health`, `prediction-market-oracle-research`,
`prediction-market-risk-review`, `prompt-optimizer`,
`pubmed-database`, `recsys-pipeline-architect`,
`regex-vs-llm-structured-text`, `remotion-video-creation`,
`rules-distill`, `scholar-evaluation`, `seo`,
`social-graph-ranker`, `social-publisher`, `videodb`,
`visa-doc-translate`, `x-api`,
`connections-optimizer`, `carrier-relationship-management`,
`customer-billing-ops`, `customs-trade-compliance`,
`energy-procurement`, `finance-billing-ops`, `inventory-demand-planning`,
`logistics-exception-management`, `production-scheduling`,
`quality-nonconformance`, `returns-reverse-logistics`,
`article-writing`, `investor-materials`, `investor-outreach`

### 3. Root (Kök Dizin) Contributor Listesi

```python
ROOT_CONTRIBUTOR = {
    "android-apk-modding", "android-apk-repackaging", "android-native-app-builder",
    "spring-boot-scaffold", "spring-boot-microservice-scaffold",
    "writing-plans", "test-driven-development", "systematic-debugging",
    "vscode-python-dongusu", "vscode-otomasyon", "vscode-agent-control", "vscode-control",
    "hermes-agent-skill-authoring", "debugging-hermes-tui-commands",
    "node-inspect-debugger", "playwright",
    "subagent-driven-development", "spike", "plan", "requesting-code-review",
    "dogfood", "ai-fullstack-kodlamiyoruz",
    "re-hermes-triage", "re-hermes-v3", "tersine-muhendislik",
    "html-report-dashboard", "self-contained-report-dashboard",
    "money-printer-turbo", "money-printer-turbo-kurulum",
    "mobile-expo-dev", "streamlit-setup", "odysseus",
    "agent-loop", "init-script", "issue-to-pr", "kali-pentest",
    "codebase-rag", "mcp-server-scaffolder",
    "claude-agent-scaffold", "agents-sdk-scaffold",
    "security-best-practices",
}
```

### 4. Root Maintainer Listesi

```python
ROOT_MAINTAINER = {
    # Bakım
    "__cleanup_deprecated_obsidian_vault_path_fix",
    "self-improvement", "obsidian-vault-maintenance", "obsidian-vault-analysis",
    "vault-fix-and-tag", "obsidian-vault-kurallari",
    "gece-3-github-yedek", "hermes-backup-otomasyonu",
    "hermes-migration-restore", "hermes-kurulacak-repolar",
    "hafiza-temizligi-hard-reset", "memory-compaction",
    "guvenlik-izleme-sistemi", "wifi-network-tools",
    "port-firewall-taramasi", "network-camera-discovery",
    "localhost-servis-yonetimi", "windows-guvenlik-izleme",
    "env-kayit-kurallari", "odysseus-sifre-sifirlama",
    "usb-driver-kontrol", "adb-sdk-path-fix",
    "project-startup-check", "repos-ve-mcp-koprusu",
    # Audit
    "agent-budget-audit", "attack-audit", "cache-auditor", "card-audit",
    "classifier-stack-audit", "control-protocol-audit", "dp-audit",
    "encoding-audit", "evaluator-rigor-audit",
    "ipi-audit", "mast-auditor", "memory-auditor", "msj-audit",
    "native-vs-posthoc-auditor", "provenance-audit", "provider-portability-audit",
    "reward-hack-auditor", "self-improvement-auditor",
    "sleeper-audit", "tom-auditor", "workbench-audit",
    "compliance-gap", "compliance-matrix",
    # Monitoring
    "skill-cmer-monitor", "skill-cost-patterns", "skill-inference-optimization",
    "skill-quantization", "skill-pipeline-budget-planner",
    "gateway-bootstrap", "load-test-plan", "gpu-autoscaler-plan",
    "llm-pipeline-reviewer", "finops-plan",
    # Otomasyon
    "n8n-claude-telegram-workflow", "n8n-claude-telegram-automation",
    "kanban-orchestrator", "kanban-worker", "kanban-codex-lane",
    "nightly-self-improvement", "otonom-gece-gelistirme",
    "takili-kalma",
}
```

## Uygulama Scripti

```python
from pathlib import Path
import re

skills_dir = Path("C:/Users/marko/AppData/Local/hermes/skills")

CATEGORY_AUDIENCE = {
    "software-development": "contributor",
    "github": "contributor",
    "devops": "maintainer",
    "automation": "maintainer",
    # Diğer tüm kategoriler default "user"
}

def get_audience(skill_dir_name, category):
    # 1. Kategori bazlı
    if category and category in CATEGORY_AUDIENCE:
        base = CATEGORY_AUDIENCE[category]
        # ECC override
        if category == "ecc" and skill_dir_name in ECC_CONTRIBUTOR:
            return "contributor"
        return base
    # 2. Root listeler
    if skill_dir_name in ROOT_CONTRIBUTOR:
        return "contributor"
    if skill_dir_name in ROOT_MAINTAINER:
        return "maintainer"
    # 3. Default
    return "user"

# Frontmatter'a audience ekle (mevcut alan varsa atla)
for p in skills_dir.rglob("SKILL.md"):
    content = p.read_text(encoding="utf-8", errors="replace")
    if not content.startswith("---"):
        continue
    parts = content.split("---", 2)
    if len(parts) < 3:
        continue

    fm_text = parts[1]
    if re.search(r'^audience:\s*', fm_text, re.MULTILINE):
        continue  # zaten var

    # Skill adı ve kategori
    rel = p.relative_to(skills_dir)
    parts_path = rel.parts
    if len(parts_path) >= 3:
        category = parts_path[0]
        skill_name = parts_path[1]
    elif len(parts_path) == 2:
        category = None
        skill_name = parts_path[0]
    else:
        continue

    audience = get_audience(skill_name, category)

    # category veya tags'dan sonra ekle
    lines = fm_text.split("\n")
    insert_pos = len(lines)
    for i, line in enumerate(lines):
        if line.strip().startswith("category:") or line.strip().startswith("tags:"):
            insert_pos = i + 1

    lines.insert(insert_pos, f"audience: {audience}")
    new_fm = "\n".join(lines)
    new_content = f"---{new_fm}---{parts[2]}"
    p.write_text(new_content, encoding="utf-8")
```

## Güvenlik Önlemleri (Toplu Değişiklik Öncesi)

**ZORUNLU:** 500+ dosyada değişiklik yapmadan önce yedek al:

```python
from pathlib import Path
import hashlib, json, shutil
from datetime import datetime

skills_dir = Path("C:/Users/marko/AppData/Local/hermes/skills")
backup_dir = Path("C:/Users/marko/AppData/Local/hermes/.audience-backup")
backup_dir.mkdir(parents=True, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

manifest = []
for p in skills_dir.rglob("SKILL.md"):
    content = p.read_bytes()
    rel = p.relative_to(skills_dir)
    file_hash = hashlib.sha256(content).hexdigest()
    backup_path = backup_dir / str(rel).replace("/", "_").replace("\\", "_")
    backup_path.write_bytes(content)
    manifest.append({"path": str(rel), "hash": file_hash, "size": len(content)})

manifest_path = backup_dir / f"manifest_{timestamp}.json"
manifest_path.write_text(json.dumps(manifest, indent=2))
```

**Geri yükleme:**
```python
m = json.loads(manifest_path.read_text())
src = backup_dir
dst = skills_dir
for f in m['files']:
    src_file = src / f['path'].replace('/', '_').replace(chr(92), '_')
    dst_file = dst / f['path']
    dst_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dst_file)
```

## Doğrulama

```bash
python3 -c "
from pathlib import Path, yaml
from collections import Counter

audiences = []
for p in Path('/c/Users/marko/AppData/Local/hermes/skills').rglob('SKILL.md'):
    content = p.read_text(encoding='utf-8', errors='replace')
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            if fm and 'audience' in fm:
                audiences.append(fm['audience'])

counts = Counter(audiences)
for aud in ['user', 'contributor', 'maintainer']:
    print(f'{aud}: {counts[aud]}')
print(f'Toplam: {sum(counts.values())}')
"
```

## Dağılım (Son Güncelleme: 14 Haziran 2026)

```
USER:         848 (%71.6)
CONTRIBUTOR:  287 (%24.2)
MAINTAINER:    49  (%4.1)
TOPLAM:     1.184
```

## İlgili

- Kaynak: NVIDIA/NemoClaw → `.agents/skills/` → 3 audience bucket yapısı
- Obsidian notu: `Hermes/Skills/audience-kategorizasyonu.md`
- Bu prosedür `skill-cataloging` skill'inin parçasıdır
