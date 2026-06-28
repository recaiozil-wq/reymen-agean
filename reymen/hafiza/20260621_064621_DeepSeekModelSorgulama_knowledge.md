# Teknik Bilgi — DeepSeek Model Sorgulama (kiral38)
**Tarih:** 2026-06-21
**Kaynak:** gecmis_konusmalar/kiral38_20260621_064621__DeepSeek Model Sorgulama.md

## Proje Yapısı
- **Çalışma dizini:** `C:\Users\marko\Desktop\Reymen Proje\hermes_projesi`
- **Kök dizin:** 158 .py dosyası (27 özel + 27 override + 104 diğer)
- **agent/ klasörü:** 102 .py dosyası (27 override yedek + 75 saf Hermes)
- **Ölü dosyalar:** `ReYMeN_ölü_dosyalar/` (101 dosya + 56 duplicate)

## Provider Yapılandırması
| Provider | Model | Rol |
|----------|-------|-----|
| deepseek | deepseek-v4-flash | Birincil |
| groq | llama-3.1-8b-instant | Yedek |
| openai | gpt-4o-mini | Yedek |
| lmstudio | cognitivecomputations.dolphin3.0-llama3.1-8b | Local |

## Protected Dosyalar (27 adet)
main.py, beyin.py, motor.py, guardrails.py, hata_cozucu.py, tor_otomasyonu.py, araclar_nisan.py, nisan_yakala.py, otonom_nisan_olusturucu.py, akilli_yonlendirici.py, cokus_raporlayici.py, closed_learning_loop.py, vektorel_hafiza.py, insan_arayuzu.py, planlayici.py, robust_execution.py, provider_router.py + 10 dosya (tam liste .ReYMeN_sync.sh içinde `REYMEN_OVERRIDES` değişkeninde)

## Paket Yapısı (Kod Konsolidasyonu Sonrası)
| Paket | İçerik | Dosya Sayısı |
|-------|--------|:------------:|
| `reymen/guvenlik/` | Güvenlik modülleri | 12 |
| `reymen/hafiza/` | Bellek sistemleri | ~15 |
| `reymen/cereyan/` | AI motor, beyin, planlama | ~12 |
| `reymen/arac/` | Araçlar (araclar_*) | ~12 |
| `reymen/windows/` | Windows otomasyon | ~8 |
| `reymen/ag/` | Ağ/API/gateway | ~15 |
| `reymen/sistem/` | Sistem yönetimi | ~15 |
| Kök SHIM'ler | Yönlendirme dosyaları | ~89 |

## Windows Event Bus Sistemi
- **Sınıf:** `WindowsEventBus` (thread-safe)
- **Konsept:** Publisher-subscriber pattern
- **Event tipleri:** OLAY_TOR_HATA, OLAY_TOR_BASARILI, OLAY_NISAN, OLAY_COZUM_UYGULANDI, OLAY_HATA, OLAY_COKUS
- **Metotlar:** `dinle()`, `dinleme_kes()`, `yayinla()`, `event_bus_al()` (singleton)
- **Thread güvenliği:** `threading.Lock()` ile korumalı
- **Geçmiş:** Son 100 olay tutulur

## Browser Tool API
- **Komutlar:** navigate, click, snapshot, type, scroll, vision, back, status
- **Türkçe alias:** ac→navigate, kapat→back, git→navigate, tikla→click, yaz→type, kaydir→scroll, goruntu→snapshot, gorsel→vision, durum→status
- **Test:** 243 test geçiyor

## Test Yapısı
| Klasör | Açıklama | Dosya Sayısı |
|--------|----------|:------------:|
| `tests/ReYMeN_reference/` | Hermes orijinal testleri | 1,755 |
| `tests/tools/` | ReYMeN araç testleri | 28 |
| Diğer `tests/` | ReYMeN çekirdek testleri | 150+ |

## ReYMeN __init__.py Export'ları
Motor, AIAgentOrchestrator, ClosedLearningLoop, YetenekFabrikasi, SignalHandler, InsanArayuzu, Planlayici, UygulamaHafizasi, vektorel_hafiza_sistemini_kur, tecrube_kaydet, anlamsal_hafiza_ara, izole_python_calistir, AdvancedSessionStorage, RuntimeProviderEngine, AdvancedContextCompressor, PromptAssemblyEngine, BoundedMemory, registry, tool_error

## Hermes → ReYMeN Referans Değişiklikleri
| Eski | Yeni |
|------|------|
| `tests/hermes_reference/` | `tests/ReYMeN_reference/` |
| `reymen/hermes/` | `reymen/ReYMeN_mirror/` |
| `tools/hermes_ajan.py` | `tools/reymen_ajan.py` |
| `.hermes_sync.sh` | `.ReYMeN_sync.sh` |
| `hermes-full-backup/` | `ReYMeN-full-backup/` |
