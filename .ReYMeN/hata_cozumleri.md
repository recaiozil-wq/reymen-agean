# Hata Çözümleri — ReYMeN

_Otomatik kaydedilen hata-çözüm eşleşmeleri._

## diger
- **Tum kaynaklar basarisiz** (2026-06-29 23:07)
  - Hata: `2+2 nedir?`
  - Cozum: Manuel analiz gerekli

- **hedef** (2026-06-26 00:13)
  - Hata: `[KALICI DURDURMA] 3/3 ardisik hata. 3 deneme hakkiniz doldu.`
  - Cozum: Manuel analiz gerekli

## hermes-core
- **_REYMEN_TAM profil tespiti** (2026-07-04)
  - Hata: `@Kiral38bot ve @ReYMeN_ReYMeNbot su an kullanilamiyor. ReYMeN agent kapali.`
  - Sebep: `run_agent.py:5533` `"profiles/reymen" in _HERMES_HOME` kontrolu yapiyordu ama `_HERMES_HOME = "C:/.../hermes"` bu substring'i asla icermez. Sonuc: `_REYMEN_TAM` tum profillerde False.
  - Cozum: `os.environ.get("HERMES_PROFILE")` ile dogrudan profil adina bak. `reymen`/`kiral38` ise True.
  - Dosya: `run_agent.py:5532-5534` (Hermes core)
  - Dogrulama: 3 profil test edildi ✅
