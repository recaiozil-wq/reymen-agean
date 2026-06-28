---
skill_id: 0c313ba67ea9
usage_count: 1
last_used: 2026-06-16
---
## ReYMeN CLI Invocation

### Problem

`hermes.exe` veya `hermes send --list telegram` çalıştırıldığında şu hata alınır:
```
ModuleNotFoundError: No module named 'hermes_cli'
```

**Nedeni:** `hermes_cli` paketi venv'deki site-packages'e düzgün kurulmamış. Dizin var ama içi boş:
```
/c/Users/marko/AppData/Local/hermes/hermes-agent/venv/Lib/site-packages/hermes_cli/  → boş
```

Asıl modül proje kökünde:
```
/c/Users/marko/AppData/Local/hermes/hermes-agent/hermes_cli/  → gerçek kod burada
```

### Çözüm

Her `hermes` komutunu **proje kökünden** `PYTHONPATH` + `REYMEN_HOME_PATH` ile çalıştır:

```bash
cd /c/Users/marko/AppData/Local/hermes/hermes-agent && \
REYMEN_HOME_PATH=/c/Users/marko/AppData/Local/hermes \
PYTHONPATH=/c/Users/marko/AppData/Local/hermes/hermes-agent \
/c/Users/marko/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe \
-m hermes_cli.main <subcommand> [args]
```

### Neden hermes.exe çalışmaz?

`hermes.exe` bir PyInstaller PE binary'sidir. Çalıştığında `hermes_cli` modülünü site-packages'te arar ama orası boş olduğu için `ModuleNotFoundError` alır. `python -m hermes_cli.main` ile doğrudan Python modülü olarak çağırmak bu sorunu bypass eder.

### Geçici çözüm mü kalıcı mı?

Bu **yeniden kurulum gerektiren** bir env sorunudur. `pip install -e .` ile editable kurulum yapılırsa `hermes.exe` tek başına çalışır hale gelir. Şu ana kadar yeniden kurulum yapılmadığı için PYTHONPATH workaround'u kullanılmaya devam edilmektedir.

### İlgili komutlar

| İşlem | Komut |
|-------|-------|
| Hedef listele | `... -m hermes_cli.main send --list telegram` |
| Test mesajı gönder | `... -m hermes_cli.main send --to "telegram:Q !" "mesaj"` |
| Gateway restart | `... -m hermes_cli.main gateway run --replace` |
