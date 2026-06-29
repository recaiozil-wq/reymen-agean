# ReYMeN Hafıza — MEMORY.md

## Kullanıcı Tercihleri
- Dil: Türkçe (kesinlikle Türkçe cevap ver)
- İletişim: Çok kısa direkt komutlar, fluff yok
- Cevap formatı: Başlık(emoji+konu) → kısa açıklama → tablo (sütun başlıklı) → altta yorum
- "ok" = onayla/devam et, "dur/stop" = anında kes
- Sessiz onay: 3dk bekle, cevap yoksa onay say ve devam et
- Açıklama istemez, direkt sonuç bekler
- Teknik konularda derinlemesine analiz ister, yüzeysel cevap kabul etmez

## Ortam Bilgileri
- İşletim Sistemi: Windows 10 (22H2)
- Çalışma Dizini: C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan
- Python: 3.11.15 (venv), 3.14.5 (python3)
- GitHub: Watcher-Hermes/ReYMeN-Ajan-v2
- GitHub hesabı: asdafgf@
- Provider: deepseek/deepseek-v4-flash (birincil), OpenRouter (fallback)
- Kali VM: 192.168.56.103
- E:\ sürücüsünde yedek: "reymen ajan versiyon 1" (4.4 GB)

## Öğrenilen Bilgiler
- Proje kökü: C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan
- .env dosyaları: AppData/Local/hermes/profiles/<profil>/.env (asla write_file ile yazma, terminal echo ile append yap)
- ReYMeN özel skill'leri: reymen/cereyan/skills/ altında (proje kökü skills/ Hermes kopyası)
- Cline: GLM 5.2, VS Code extension, Act moduna manuel geçirilir
- 3 bot profili: default (Pasa_38_bot), reymen (ReYMeN_ReYMeNbot), kiral38 (Kiral38bot)
- Cevap stili: Tablo + emoji + kısa öz

## Proje Durumu
- README.md ✅ Türkçe, profesyonel
- CONTRIBUTING.md ✅ Türkçe
- AGENTS.md ✅ Türkçe
- CHANGELOG.md ✅ Türkçe
- LICENSE ✅ MIT (Nous Research + ReYMeN)
- kurulum.bat ✅ Otomatik kurulum scripti
- 7 modül ✅ (cost_tracker, platform_adapter, self_improve, video_tools, a2a, kanban, tui)
- CLI split ✅ (cli_mixin_commands 9 satır, cli_main 4.857 satır)
- Hafıza sistemi ✅ (MEMORY.md + USER.md + MemoryManager)
- GitHub: https://github.com/Watcher-Hermes/ReYMeN-Ajan-v2
- Docstring'ler (.py): ⏳ Bekliyor (Cline kredisi bitince)
