# DeepSeek Ajan

Guvenli, full yetkili, ogrenen AI agent for **DeepSeek-v4-flash**.

## Ozellikler

| Ozellik | Aciklama |
|---------|----------|
| AI Sohbet | DeepSeek-v4-flash ile dogal dil iletisimi |
| Python Calistirma | `/py` ile kod calistir |
| Shell Erisimi | `/sys` ile terminal komutlari |
| Dosya Yonetimi | `/read`, `/write`, `/ls` ile dosya islemleri |
| Ogrenme Hafizasi | SQLite tabanli OnceHafiza (cozumleri kaydeder) |
| Session Yonetimi | Konusma gecmisi kaydet/yukle |
| Guvenlik Katmani | approvals mode, kullanici izin kontrolu |

## Hizli Baslangic

```bash
# 1. OpenAI kutuphanesini yukle
pip install openai

# 2. .env dosyasina API key ekle
echo DEEPSEEK_API_KEY=*** > .env

# 3. Calistir
python -m deepseek_ajan
```

## Pip Paketi

```bash
pip install deepseek-ajan
deepseek-ajan
```

## Guvenlik

Varsayilan ayarlar **GUVENLI** modda gelir:

| Ayar | Varsayilan | Aciklama |
|------|-----------|----------|
| approvals_mode | strict | Her kritik komut onay ister |
| allow_all_users | false | Sadece yerel kullanici |
| max_py_execution_time | 30sn | Python kodu timeout |
| max_sys_execution_time | 30sn | Shell komutu timeout |

Guvenligi kapatmak icin: `/approve-off` (DIKKAT: tum komutlar direkt calisir)
Herkesin erisimine acmak icin: `/allow`

## Komutlar

| Komut | Islev |
|-------|-------|
| `/help` | Yardim |
| `/new` | Yeni session |
| `/save <ad>` | Session kaydet |
| `/load <ad>` | Session yukle |
| `/list` | Session listele |
| `/py <kod>` | Python calistir (onayli) |
| `/sys <komut>` | Shell calistir (onayli) |
| `/read <yol>` | Dosya oku (onayli) |
| `/write <yol>` | Dosya yaz (onayli) |
| `/ls <yol>` | Klasor listele (onayli) |
| `/guvenlik` | Guvenlik durumu |
| `/allow` | Herkes icin ac (DIKKAT) |
| `/strict` | Onaylari aktif et |
| `/approve-off` | Onaylari kapa (DIKKAT) |
| `/hafiza` | Hafiza istatistik |
| `/model <ad>` | Model degistir |

## Lisans

MIT
