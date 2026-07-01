# Karar Kaydı — 11 Proaktif Öneri (20-30) Uygulama

**Tarih:** 2026-07-01 23:20

## Ne yapıldı?
Sub-agent tarafından tespit edilen 30 öneriden 20-30 arası (🔵 NİCEL) uygulandı.

## Neden?
Proje kalitesi, güvenlik ve GitHub'dan indiren kişinin sorun yaşamaması için.

## Yapılanlar

| # | Öneri | Çözüm | Durum |
|---|-------|-------|-------|
| 20 | Ruff ANN/D kuralları aç | ruff.toml select'e ANN+D eklendi, target-version py312 yapıldı | ✅ |
| 21 | Versiyon tutarsızlığı | pyproject.toml → 1.0.2, classifiers 3.11→3.13 | ✅ |
| 22 | pyproject.toml URL | Zaten doğruydu (reymen-agean) | ✅ |
| 23 | SUPPORT.md e-posta | `marko [at] reymen [dot] dev` olarak obfuscate | ✅ |
| 24 | KARSILASTIRMA.md güncellik | Dipnot eklendi (2026-06-30 tarihli) | ✅ |
| 25 | install.ps1 referans | docs/kurulum.md'ye PowerShell kurulum bölümü eklendi | ✅ |
| 26 | mkdocs.yml repo_url | Watcher-ReYMeN → recaiozil-wq/reymen-agean | ✅ |
| 27 | requirements.txt senkron | pyproject.toml ile uyumlu hale getirildi (core+full+dev) | ✅ |
| 28 | ZIP arşivleri | arsiv/ klasörüne taşındı (~360MB) | ✅ |
| 29 | PULL_REQUEST_TEMPLATE | Boş checkbox'lar dolduruldu | ✅ |
| 30 | AGENTS.md.bak + ZIP disk | AGENTS.md.bak git rm ile temizlendi | ✅ |
