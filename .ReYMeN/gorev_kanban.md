# GÖREV: Kanban Geliştirme

## NE
Mevcut `reymen/arac/kanban_orchestrator.py` (454 satır) geliştir.

## MEVCUT ÖZELLİKLER (korunacak)
- SQLite + FTS5 depolama
- Kolonlar: todo → ready → running → done | blocked | archived
- Öncelik (1-yüksek, 2-orta, 3-düşük)
- CLI: ekle, liste, güncelle, sil, özet

## EKLENECEKLER

### 1. Kanban Dashboard HTML
- `dashboard/templates/kanban.html` — Kanban board görünümü
- Kolon bazlı kart görüntüleme (sürükle-bırak OLMADAN, basit)
- Koyu tema
- Her kolonda kart sayısı göster
- JSON API: `GET /api/kanban` — tüm kartlar
- Flask route'larını webui.py'ye ekle

### 2. Kullanıcı Atama
- `atanan` alanı ekle (string)
- CLI: `--atanan "username"`
- Filtre: `kanban_orchestrator.py liste --atanan "username"`

### 3. Deadline Takibi
- `deadline` alanı ekle (ISO datetime, optional)
- CLI: `--deadline "2026-07-01"`
- Geçmiş deadline'ları kırmızı göster
- Filtre: `liste --gecikmis` (deadline geçmiş + running/todo)

### 4. Etiket Geliştirme
- Mevcut etiket sistemini genişlet
- `liste --etiket "bug"` ile filtreleme
- Etiket renkleri (opsiyonel)

### 5. İstatistikler
- `ozet` komutunu genişlet:
  - Kolon bazlı kart sayısı
  - Gecikmiş kart sayısı
  - Kullanıcı başına kart dağılımı
  - Ortalama tamamlanma süresi

### 6. Motor Kaydı
- `motor_kaydet("kanban_ekle", ...)` 
- `motor_kaydet("kanban_liste", ...)`
- `motor_kaydet("kanban_guncelle", ...)`
- `motor_kaydet("kanban_ozet", ...)`

## DOĞRULAMA

```bash
python -c "compile(open('reymen/arac/kanban_orchestrator.py').read(), 'reymen/arac/kanban_orchestrator.py', 'exec'); print('OK')"
python reymen/arac/kanban_orchestrator.py ozet
```

## YASAKLAR
- Mevcut API'yi kırma (ekle/liste/guncelle/sil/ozet aynı kalsın)
- SQLite DB şemasını kırma
- Test dosyalarını düzenleme
