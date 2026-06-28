---
skill_id: 8771facc17bb
usage_count: 2
last_used: 2026-06-20
---
## PITFALL'LAR

- **Context sıfırlanması**: AI ajanı 1M token'da context kaybeder. Memory.md ile çöz.
- **Railway credential'ları**: Environment variable'ları Railway dashboard'dan ayarla, `.env`'e yazma.
- **R2 CORS**: Frontend'den direkt yükleme yapacaksan CORS ayarlarını unutma.
- **Test coverage düşüklüğü**: AI bazen test yazmayı atlar. "Test yaz" diye zorla.
- **Deployment hataları**: Railway CLI login'inin hala aktif olduğunu kontrol et.
- **Rate limiting**: Free tier AI modelleri (OpenRouter free) 429 dönebilir. Fallback chain kullan.

---
## Ek Adimlar / Varyasyon (2026-06-20T19:43:54Z)

DOSYA_OKU: "skills/"
PYTHON_CALISTIR: "import os; print(os.listdir('skills/'))"
HAFIZA_ARA: "skıller kontrol et"
PYTHON_CALISTIR: """
import os, json

# Son görev loglarını kontrol et
log_dir = 'logs'
if os.path.exists(log_dir):
    logs = os.listdir(log_dir)
    print(f"Log sayısı: {len(logs)}")
    for l in sorted(logs)[-5:]:
        print(l)
else:
    print("Log dizini yok")

# Ayrıca .reymen/ dizinini kontrol et
for d in ['.reymen', '.hermes', 'memory', 'state']:
    if os.path.exists(d):
        print(f"{d} mevcut, içindekiler: {os.listdir(d)[:10]}")
    else:
        print(f"{d} yok")
"""
KOMUT_CALISTIR: "ls -la logs/ 2>/dev/null; ls -la .reymen/ 2>/dev/null; ls -la memory/ 2>/dev/null"
PYTHON_CALISTIR: """
import os

# logs dizini
if os.path.exists('logs'):
    print('logs:', os.listdir('logs')[-5:])
else:
    print('logs yok')

# .reymen
if os.path.exists('.reymen'):
    print('.reymen:', os.listdir('.reymen'))
else:
    print('.reymen yok')

# memory
if os.path.exists('memory'):
    print('memory:', os.listdir('memory')[:5])
else:
    print('memory yok')

# state
if os.path.exists('state'):
    print('state:', os.listdir('state')[:5])
else:
    print('state yok')

# task durumu
if os.path.exists('task_state.json'):
    with open('task_state.json') as f:
        print('task:', f.read()[:200])
"""
DOSYA_OKU: "task_state.json"
WEB_ARA: "yetkilendirme zafiyeti çözümü"
PYTHON_CALISTIR: "import os; print([f for f in os.listdir('.') if not f.startswith('.')][:30])"
PYTHON_CALISTIR: """
import os
# 'coz' veya 'çöz' içeren dosyaları ara
coz_dosyalari = [f for f in os.listdir('.') if 'coz' in f.lower() or 'çöz' in f.lower()]
print("Çöz ile ilgili dosyalar:", coz_dosyalari)

# .py uzantılı ve 'coz' içeren dosyalar
py_coz = [f for f in os.listdir('.') if f.endswith('.py') and ('coz' in f.lower() or 'çöz' in f.lower())]
print("Python çöz dosyaları:", py_coz)

# Son değiştirilen 5 dosya
files = [(f, os.path.getmtime(f)) for f in os.listdir('.') if os.path.isfile(f)]
files.sort(key=lambda x: x[1], reverse=True)
print("Son 5 dosya:", [f[0] for f in files[:5]])
"""
PYTHON_CALISTIR: "import os; print('\\n'.join(os.listdir('.')))"
PYTHON_CALISTIR: """
import os, fnmatch
coz = []
for f in os.listdir('.'):
    if 'coz' in f.lower() or 'çöz' in f.lower():
        coz.append(f)
print(coz)
"""
DOSYA_OKU: "agent_init.py"
PYTHON_CALISTIR: """
with open('agent_init.py', 'r') as f:
    lines = f.readlines()
print(f'Toplam satır: {len(lines)}')
print('İlk 20 satır:')
for i, l in enumerate(lines[:20]):
    print(f'{i+1}: {l.rstrip()}')
"""
PYTHON_CALISTIR: "print('test')"
PYTHON_CALISTIR: "print(open('agent_init.py').read()[:500])"
PYTHON_CALISTIR: "print(open('agent_init.py').read()[500:1000])"
PYTHON_CALISTIR: "print(open('agent_init.py').read()[1000:1500])"
PYTHON_CALISTIR: "print(open('alt_ajan.py').read()[:500])"
PYTHON_CALISTIR: "import os; print([f for f in os.listdir('.') if f.lower().startswith('coz') or f.lower().startswith('çöz')])"
PYTHON_CALISTIR: "import os; print([f for f in os.listdir('.') if 'log' in f.lower()])"
PYTHON_CALISTIR: "print(open('bot_errors.log', 'r').read()[:1000])"
PYTHON_CALISTIR: "print(open('bot_err.log', 'r').read()[:1000])"
PYTHON_CALISTIR: "import os; pyfiles=[f for f in os.listdir('.') if f.endswith('.py')]; print(len(pyfiles), 'python dosyasi var'); print(pyfiles[:10])"
YARDIM_ISTE: "'çöz' hedefi çok genel. Ne çözülmesi gerekiyor? Bir hata mı, bir dosya mı, bir problem mi? Lütfen daha spesifik olun."
PYTHON_CALISTIR: "print(open('agent_init.py').read()[1500:2000])"
