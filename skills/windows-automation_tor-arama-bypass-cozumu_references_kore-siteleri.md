
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Tor Arama Bypass Cozumu_References_Kore Siteleri |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Kore Siteleri — Tor Erişim Durumu

## Çalışan

### Bing KR
```
GET https://www.bing.com/search?q={urllib.parse.quote('블루투스 스니핑 공격')}&cc=KR
```
- 10 sonuç ✅
- HTTP 200, ~119KB

### Naver
```
GET https://search.naver.com/search.naver?query={urllib.parse.quote('블루투스 보안 취약점')}
```
- HTTP 200, ~530KB ✅
- Korece arama sonuçları

## Bloklu (SOCKSHTTPSConnectionPool)
- `www.boannews.com` ❌
- `dailysec.kr` ❌

**Sebep:** Kore CDN/firewall'ları Tor çıkış düğümlerini engelliyor.
