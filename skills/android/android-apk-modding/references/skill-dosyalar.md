---
skill_id: 64ecb3a95da9
usage_count: 1
last_used: 2026-06-16
---
## Skill Dosyaları

| Dosya | Açıklama |
|-------|----------|
| `references/obfuscated-lifecycle-methods.md` | Obfuscated APK'lerde onPause/onStop bulma ve boşaltma |
| `references/rootless-patching-methods.md` | Root'suz runtime müdahale yöntemleri karşılaştırması |
| `scripts/patch.sh` | 7 adımlı pipeline scripti — tek komutla önbelge→doğrula |
| `references/smali-syntax.md` | Smali sözdizimi referansı (register, invoke, if/else, şablonlar) |
| `references/foreground-service-smali.md` | Foreground service smali şablonu |
| `references/google-cloud-auth-limitation.md` | Google apps cloud auth limitation — custom imza ile sunucu reddi, Frida non-root notları |
| `references/package-rename-bypass.md` | Sistem uygulaması bypass: package rename + smali/res patching — full workflow, real vaka |
| `references/session-20260613-live-transcribe-package-rename.md` | Live Transcribe package rename oturumu — crash döngüsü (5 hata), LauncherActivity fix, Samsung security bypass, Windows path separator uyarısı |
| `references/live-transcribe-xray-analysis.md` | Live Transcribe X-ray: Lgfq, Lgmw sınıf haritası, onPause/onResume kod akışı |
| `references/live-transcribe-lifecycle-analysis.md` | Live Transcribe lifecycle metod haritası (onPause/onResume/onStop satır satır) |
| `references/live-transcribe-community-research.md` | Dünya çapında topluluk araştırması — kimse modlamamış, neden mod yok, alternatifler |
| `references/observations.md` | Oturum notları (Split APK merge, binary rename, Telegram upload, Samsung uyarıları) |
| `references/session-20260613-live-transcribe-package-rename.md` | Live Transcribe package rename oturumu — crash döngüsü (5 hata), LauncherActivity fix, Samsung security bypass, Windows path separator uyarısı |\n| `references/audio-record-tcp-bridge.md` | SpeechRecognizer alternatifi — sesi PC'ye akit, orada isle (APK modding cozemediginde) |\n\n### patch.sh Kullanımı

```bash