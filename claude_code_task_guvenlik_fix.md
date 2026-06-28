# Claude Code Task: Güvenlik Fix'i (shell=True + Hardcoded Credential)

## Hedef
`fix_04_rapor.json` dosyasındaki güvenlik açıklarını kapat:
1. **67 adet shell=True** → güvenli alternatife çevir
2. **Hardcoded credential** → os.environ.get(...) ile değiştir

## 1. shell=True Düzeltme (67 adet)

**Mevcut (GÜVENLİKSİZ):**
```python
subprocess.run("komut arg1 arg2", shell=True)
subprocess.Popen("komut", shell=True)
os.system("komut")
```

**Hedef (GÜVENLİ):**
```python
subprocess.run(["komut", "arg1", "arg2"], shell=False)
# veya shlex.split() ile:
import shlex
subprocess.run(shlex.split("komut arg1 arg2"), shell=False)
```

**Kural:**
- `shell=True` → `shell=False` yap
- String komutları liste formatına çevir (`shlex.split()` kullan)
- `os.system()` → `subprocess.run()` ile değiştir
- Eğer liste formatına çevrilemiyorsa (değişken içeriyorsa), en azından `shell=False` yap ve `shlex.quote()` ile parametreleri koru

## 2. Hardcoded Credential Düzeltme

**Mevcut (GÜVENLİKSİZ):**
```python
API_KEY = "sk-1234567890abcdef"
TOKEN = "12345:abcdeffedcba"
```

**Hedef (GÜVENLİ):**
```python
API_KEY = os.environ.get("API_KEY", "")
TOKEN = os.environ.get("TOKEN", "")
```

**Kural:**
- Sadece **gerçek credential** içerenleri değiştir (test dummy verilerini değiştirme)
- Dosya başına `import os` ekle (yoksa)
- `.env` dosyasında karşılığı olmayanlar için yorum satırı ekle: `# TODO: .env'ye ekle`

## 3. SQL Injection Riskleri (63 adet)

**Mevcut:**
```python
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

**Hedef:**
```python
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

## Sıra
1. İlk `fix_04_rapor.json`'u oku ve hangi dosyalarda sorun olduğunu gör
2. shell=True olan dosyaları düzelt (öncelik sırası: reymen/ > gateway/ > tools/ > diğer)
3. Hardcoded credential dosyalarını düzelt (reymen/ altı öncelikli)
4. SQL risklerini düzelt

## Doğrulama
```bash
python -c "import ast; ast.parse(open('DOSYA').read()); print('OK')"
```
