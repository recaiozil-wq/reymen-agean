
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Tor Arama Bypass Cozumu_References_Cin Siteleri |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Çin Siteleri — Tor Erişim Durumu

## Çalışan

### Kaspersky CN Blog
```
GET https://www.kaspersky.com.cn/blog/?s={urllib.parse.quote('蓝牙 安全 攻击')}
```
- Direkt çalışır ✅
- 133KB, BT güvenlik içeriği mevcut
- HTTP 200, CAPTCHA yok

## Kısmen Çalışan

### Bing CN
```
GET https://cn.bing.com/search?q={q}&cc=CN
```
- 10 sonuç döndürür (genel BT sayfaları)
- Güvenlik spesifik sonuç az

## Bloklu (SOCKSHTTPSConnectionPool)
- `freebuf.com` ❌
- `so.csdn.net` ❌
- `www.anquanke.com` ❌
- `blog.netlab.360.com` ❌
- `segmentfault.com` ❌
- `security.alibaba.com` ❌
- `securelist.cn` ❌

**Sebep:** Çin CDN/firewall'ları Tor çıkış düğümü IP'lerini engelliyor.
Bu sitelere Tor üzerinden erişim şu an için mümkün değil.

## Alternatif
- Google Cache: `https://webcache.googleusercontent.com/search?q=cache:freebuf.com` (domain cache çalışır, search cache 429)
- Browser ile denenebilir (farklı proxy zinciri)
