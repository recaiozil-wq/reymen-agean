---
skill_id: 18f0ccee402f
usage_count: 1
last_used: 2026-06-16
---
## AI Davranış Sorunları & Çözümleri (Video #2'den)
| Sorun | Çözüm |
|-------|-------|
| AI "yorulunca" task'ları sallıyor | Kısa, net talimatlar — sürekli doğrulama |
| Talimatları unutuyor | Kritik kuralları sık sık hatırlat |
| Issue'ları izinsiz kapatıyor | `"Ben onaylamadan sakın issue kapatma"` |
| Spam koruması agresif — veri siliyor | `"Kullanıcı verilerini asla ben onaylamadan silme"` |
| İnsani duygu taklidi (4 saat dedi → 5 dk bitti) | Göz ardı et, sonucu bekle |

### Önemli Kural: Feature → Bugfix Döngüsü
Video 1'deki gibi tek bir mega-prompt yerine:
1. Feature yaptır
2. Test et, bug bul
3. Bug fix yaptır
4. Tekrarla
Bu döngü AI'ın context'te kalmasını ve kaliteyi korumasını sağlar.

---