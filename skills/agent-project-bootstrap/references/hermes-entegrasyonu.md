---
skill_id: cb6a87ed7826
usage_count: 1
last_used: 2026-06-16
---
# ReYMeN Agent Entegrasyon Deseni

ReYMeN Proje'de Nous Research ReYMeN Agent'ı entegre etmek için kullanılan desen.

## Mimari

```
C:\hermes\                         ← ReYMeN Agent (bağımsız repo)
  cli.py (731KB)                   ← Ana CLI
  agent/                           ← Agent runtime modülleri
  skills/                          ← 100+ skill
  apps/                            ← Uygulamalar
  cron/                            ← Zamanlanmış görevler
  .env                             ← ReYMeN config (ReYMeN'den senkronize)
  cli-config.yaml                  ← ReYMeN ayarları

ReYMeN Proje/
  hermes_cli.py                    ← Wrapper: env sync + ReYMeN CLI çağırma
  reyemen.bat                      ← "reyemen.bat hermes ..." ile erişim
```

## Wrapper (hermes_cli.py) İşleyişi

1. **Env senkronizasyonu**: ReYMeN .env'deki anahtarları ReYMeN .env'ye kopyala (boş/*** olanları doldur)
2. **Subprocess çağrısı**: `python C:\hermes\cli.py <args>` çalıştır
3. **Çıktı yönlendirme**: stdout/stderr kullanıcıya göster

```python
def env_aktar():
    ReYMeN = {}  # ReYMeN .env'den oku
    hermes = []  # ReYMeN .env'yi güncelle
    # ... senkronizasyon mantığı

def hermes_cagir(args):
    subprocess.run([sys.executable, HERMES_CLI, *args])
```

## .bat Entegrasyonu

```
reyemen.bat hermes doctor         # ReYMeN sağlık kontrolü
reyemen.bat hermes gateway start  # Gateway başlat
reyemen.bat hermes skills list    # Skill listele
```

## Önemli

- ReYMeN Agent kendi reposunda kalır (taşınmaz)
- Yalnızca wrapper (hermes_cli.py) ve .bat referansı ReYMeN Proje'de
- Çift yönlü env senkronizasyonu: ReYMeN'de değişiklik → ReYMeN'e yansır
- ReYMeN .git (280MB) korunur — kendi git geçmişi bozulmaz
