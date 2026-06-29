# 🛠️ CLI Referansı

`reymen` komut satırı arayüzü.

## Genel Kullanım

```
reymen [komut] [parametreler]
```

## Komutlar

### `reymen chat`

Etkileşimli veya tek sorguluk sohbet.

```
# Etkileşimli
reymen chat

# Tek sorgu
reymen chat -q "Türkiyenin başkenti neresi?"

# Model seçerek
reymen chat -m deepseek
```

### `reymen web`

Web UI (http://localhost:5000).

```
reymen web
reymen web --port 8080
```

### `reymen kanban`

Kanban board yönetimi.

```
reymen kanban boards
reymen kanban add "Yeni görev" --column backlog
reymen kanban move KART_ID in_progress
reymen kanban done KART_ID
```

### `reymen cron`

Zamanlanmış görevler.

```
reymen cron list
reymen cron add "30m" "Her 30 dakikada kontrol"
reymen cron pause JOB_ID
```

### `reymen plugin`

Plugin yönetimi.

```
reymen plugin list
reymen plugin install PLUGIN_ADI
reymen plugin remove PLUGIN_ADI
```

### `reymen model`

Model/provider yönetimi.

```
reymen model
reymen model deepseek
reymen model providers
```

### `reymen session`

Oturum yönetimi.

```
reymen session list
reymen session search "kelime"
reymen session delete SESSION_ID
```

### `reymen backup`

Yedekleme.

```
reymen backup create
reymen backup restore DOSYA.zip
reymen backup list
```

### `reymen gateway`

Gateway yönetimi.

```
reymen gateway start
reymen gateway stop
reymen gateway status
```

### `reymen skill`

Skill yönetimi.

```
reymen skill list
reymen skill search "kelime"
reymen skill install SKILL_ADI
```

### `reymen config`

Yapılandırma.

```
reymen config show
reymen config set anahtar.deger
reymen config edit
```

## Çıkış Kodları

| Kod | Anlamı |
|:---:|--------|
| 0 | Başarılı |
| 1 | Genel hata |
| 2 | Parametre hatası |
| 3 | Yetki hatası |
| 4 | Bağlantı hatası |
