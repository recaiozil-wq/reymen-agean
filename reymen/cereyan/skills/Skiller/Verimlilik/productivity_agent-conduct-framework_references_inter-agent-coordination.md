
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Productivity_Agent Conduct Framework_References_Inter Agent Coordination |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Inter-Agent Koordinasyon Protokolü

İki veya daha fazla uzman ajan (Kali, Windows, Video, vs.) birlikte çalıştığında kullanılır.

## Mesaj Formatı (JSON)

```json
{
  "from": "kali_agent|windows_agent|video_agent",
  "to": "kali_agent|windows_agent|orkestrator",
  "protocol": "ReYMeN_InterAgent_v1",
  "payload": {
    "type": "security_alert|scan_result|verify|block|error",
    "severity": "low|medium|high|critical",
    "data": {},
    "action": "verify_and_block|scan_only|report_only"
  },
  "timestamp": "2026-06-21T19:03:00Z",
  "requires_ack": true
}
```

## Orkestratör

- **conversation_loop** (ana thread) — ajanlar arası köprü
- Ajanlar **OnceHafiza** üzerinden ortak hafıza kullanır

## Hata Yönetimi

| Hata Senaryosu | Ne olur? |
|:---------------|:---------|
| Kali hata yaparsa | Windows kendi netstat'ini çalıştırır, portu kendisi tespit eder |
| Windows hata yaparsa | Kali alternatif blok yöntemi dener (sc stop, wmic) |
| İkisi de hata | Orkestratör escalate eder, kullanıcıya sorar |
| Timeout | max 120sn, budget 30 tur, circuit breaker 3 hata |

## Hafıza

| Ajan | Kategori |
|:-----|:---------|
| Kali | kali/network/nmap |
| Windows | windows/terminal/network |
| Video | video/python/nmap, video/learning |
| Ortak | cross-platform/* |

- Tüm ajanlar aynı DB: reymen/cereyan/.ReYMeN/ogrenmeler.db
- kaydet(): ayni hedef+kategori bulursa UPDATE (yeni kayıt açmaz)

## Gerçek Senaryo: Kali + Windows Koordinasyonu

1. Kali: nmap -sS -sV -p 1-1000 127.0.0.1
2. Kali -> Windows: Port 135 (msrpc) acik, dogrula + blokla
3. Windows: netstat -an ile port 135 dogrula
4. Windows: netsh advfirewall firewall add rule name="Block_Port_135"
5. Windows -> Kali: Port 135 bloklandi
6. Kali: nmap ile tekrar tara -> port kapali mi?
