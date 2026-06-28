---
skill_id: a9c06eaac2da
usage_count: 1
last_used: 2026-06-16
---
# state.db Yedekleme Tekniği

## Sorun

ReYMeN state.db ~240MB (tüm konuşma geçmişi + memory + session'lar).
GitHub dosya limiti: 100MB. Git LFS olmadan pushlanamaz.

## Çözüm: Zip + Parçalama

### Adım 1 — ReYMeN'i durdur

state.db SQLite WAL modunda çalışır. ReYMeN açıkken zip alınırsa:
- `.db-wal` dosyası checkpoint yapılmamış olur
- Kilitli dosya hatası alınabilir

```powershell
Stop-Process -Name "hermes" -Force
Start-Sleep -Seconds 2
```

### Adım 2 — Sıkıştır

```python
import zipfile, os

hermes_dir = r"C:\Users\marko\AppData\Local\hermes"
files = [
    os.path.join(hermes_dir, "state.db"),
    os.path.join(hermes_dir, "state.db-wal"),
    os.path.join(hermes_dir, "state.db-shm")
]

output = r"C:\Users\marko\Desktop\hermes-state-backup.zip"
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for f in files:
        if os.path.exists(f):
            zf.write(f, os.path.basename(f))
```

**compresslevel=9** (max) önemli — 240MB → ~105MB (level=5'te ~105.4MB, level=9'da ~104.6MB).

### Adım 3 — Parçalara böl

GitHub dosya limiti **100MB**. Güvenli tarafta kalmak için 55MB chunk:

```python
chunk_size = 55 * 1024 * 1024

with open(zip_path, 'rb') as f:
    data = f.read()

for i in range(0, len(data), chunk_size):
    part = i // chunk_size + 1
    part_file = f"hermes-state-part{part:03d}.zip"
    with open(part_file, 'wb') as pf:
        pf.write(data[i:i + chunk_size])
```

İsimlendirme: `part001.zip`, `part002.zip`, ... (sıralı sort için 3 digit)

### Adım 4 — Push

```bash
git add hermes-state-part001.zip hermes-state-part002.zip
git commit -m "state.db yedek"
git push origin main
```

GitHub 50MB üstü dosyalar için uyarı verir (`warning: File hermes-state-part001.zip is 55.00 MB; this is larger than GitHub's recommended maximum file size of 50.00 MB`) ama engellemez. 100MB limit aşılmadığı sürece geçer.

## Restore (Birleştirme)

PowerShell'de binary stream ile birleştir:

```powershell
$mergedZip = "$env:TEMP\hermes-state-merged.zip"
$part1 = "$BackupDir\hermes-state-part001.zip"
$part2 = "$BackupDir\hermes-state-part002.zip"

$stream = [System.IO.File]::OpenWrite($mergedZip)
foreach ($part in @($part1, $part2)) {
    $partData = [System.IO.File]::ReadAllBytes($part)
    $stream.Write($partData, 0, $partData.Length)
}
$stream.Close()

# Zip'i aç
$extractDir = "$env:TEMP\hermes-state-extract"
Expand-Archive -Path $mergedZip -DestinationPath $extractDir -Force

# state.db'yi kopyala
foreach ($file in @("state.db", "state.db-wal", "state.db-shm")) {
    Copy-Item -Path (Join-Path $extractDir $file) -Destination $ReYMeNHome -Force
}
```

**Kritik**: `[System.IO.File]::ReadAllBytes` ile binary mode'da okumak şart. `Get-Content -Encoding Byte` PowerShell'de farklı davranabilir.

## Güncelleme Stratejisi

Yeni state.db yedeklemesi yapılırken:

1. Eski `part001.zip` + `part002.zip`'i repodan sil
2. Yenilerini ekle
3. `git commit --amend` veya yeni commit
4. `git push --force`

Restore scriptinin `-Update` modu:
- `git pull` ile en son state.db'yi çeker
- Mevcut state.db'nin üzerine yazar
- Config ve .env'ye dokunmaz

## Alternatif: Git LFS

Eğer parçalama istenmiyorsa Git LFS kullanılabilir:

```bash
git lfs track "*.zip"
git add .gitattributes hermes-state-backup.zip
git commit -m "state.db LFS yedek"
git push origin main
```

Ancak:
- GitHub LFS kotası: 1GB ücretsiz (sonrası ücretli)
- LFS kurulumu her bilgisayarda gerekir
- Parçalama daha basit ve bağımlılıksız

## Neden state.db Yedeklenmeli?

state.db içinde:
- **Memory entries**: Kullanıcı profili, tercihler, kurallar
- **Session history**: Tüm konuşma geçmişi (session_search ile erişilebilir)
- **Channel state**: Telegram/Discord bağlantı durumu
- **Cron state**: Zamanlanmış görevlerin son çalışma durumu

Skills + config + state.db = **tam ReYMeN taşınabilirliği**.
