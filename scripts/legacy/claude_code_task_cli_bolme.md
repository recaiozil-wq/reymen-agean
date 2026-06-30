# Claude Code Task: cli.py Bölme (15,762 → 7 Modül)

## Hedef
`reymen/sistem/cli.py` dosyasını (15,762 satır) 7 ayrı Python dosyasına böl.
Her alt dosya <2,500 satır olacak. `cli_main.py` sadece yönlendirme (dispatch) yapacak.

## Mevcut Durum
cli.py içinde 7 ana sorumluluk alanı var (yorum bloklarıyla ayrılmış):
1. Display utilities (renk, terminal genişliği, markdown, çıktı formatlama)
2. CLI commands (argument parsing, alt komutlar)
3. Stream (streaming çıktı, progress)
4. Voice (ses/konuşma)
5. Maintenance (bakım, checkpoint, state)
6. Auth (yetkilendirme, API key yönetimi)
7. Helpers (genel yardımcı fonksiyonlar)

## Çıktı Dosyaları
```
reymen/sistem/
├── cli_main.py       # dispatch only (~200 satır)
├── cli_display.py    # display utilities
├── cli_commands.py   # CLI commands
├── cli_stream.py     # streaming
├── cli_voice.py      # voice
├── cli_maintenance.py # bakım
├── cli_auth.py       # auth
└── cli_helpers.py    # helpers
```

## Kurallar
1. Mevcut public API'yi koru: `run()`, `main()`, `AIAgent()`, `get_tool_definitions()` cli_main.py'den import edilebilir olmalı
2. Her modül kendi import'larını içersin
3. `from reymen.sistem.cli_X import ...` formatı
4. `__init__.py`'ye gerek yok (mevcut package yapısını bozma)
5. Her adımda `python -c "ast.parse(open('reymen/sistem/cli_main.py').read())"` ile syntax kontrol et

## Sıra
1. cli_helpers.py → en bağımsız
2. cli_display.py
3. cli_commands.py
4. cli_stream.py
5. cli_voice.py
6. cli_maintenance.py
7. cli_auth.py
8. cli_main.py → dispatch

## Doğrulama
```bash
python -c "from reymen.sistem.cli_main import run; print('OK')"
python -c "import ast; ast.parse(open('reymen/sistem/cli.py').read()); print('Syntax OK')"
```
