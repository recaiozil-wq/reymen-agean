---
skill_id: 3290ef91150d
usage_count: 1
last_used: 2026-06-16
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
