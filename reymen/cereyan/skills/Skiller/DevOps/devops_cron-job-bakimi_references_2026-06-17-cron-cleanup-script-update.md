
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Cron Job Bakimi_References_2026 06 17 Cron Cleanup Script Update |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# `_cron_cleanup.py` Güncellemesi — 17 Haziran 2026 16:54

## Ne Değişti

`_cron_cleanup.py`'a **isim-bazlı anlık placeholder tespiti** eklendi.

### Önceki mantık (yetersiz):
```python
if enabled and status == 'error' and completed >= 10:
    # ... disable et
```

Bu, yeni oluşturulmuş placeholder'ları yakalamıyordu çünkü onların `last_status=None` ve `completed=0`.

### Sonraki mantık:
```python
is_named_placeholder = name in ('do a thing', 'say hi', 'w.sh', 'alert.sh',
                                'watchdog.sh', 'quiet.sh', 'gated.sh', 'broken.sh')
if enabled and (status == 'error' and completed >= 10) or is_named_placeholder:
    # ... disable et
```

Artık yeni placeholder job'ları **ilk tick'te** disable edilir.

## Keşif: Cron Job Silme Tetikleyebilir

Bu oturumda fark edildi: `hermes cron delete` ile teker teker silme yaparken, aynı anda 36 yeni placeholder job oluştu. Bunun sebebi:

1. Batch loop'taki `hermes cron delete` çağrıları jobs.json'ı her seferinde okuyup yazıyor
2. Scheduler aynı anda tick yapıp yeni job'lar create ediyor (race condition)
3. Veya cron delete işleminin kendisi bir bug nedeniyle yeniden oluşturmaya sebep oluyor

**Çözüm:** Tek seferlik JSON purge (tek okuma, toplu silme, tek yazma) atomic olduğu için race condition oluşturmaz.

## Yeni Sağlıklı Cron: `hermes-sync`

ID: `659609b4799e`
Schedule: haftalık Pazartesi 03:00
Mode: agent (LLM kullanır)
Durum: yeni, henüz hiç çalışmadı (completed=0)
Koruma: Önemli job listesine eklendi
