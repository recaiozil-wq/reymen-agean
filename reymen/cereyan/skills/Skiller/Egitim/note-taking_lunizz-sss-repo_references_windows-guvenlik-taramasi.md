
> **Kategori:** Egitim

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Note Taking_Lunizz Sss Repo_References_Windows Guvenlik Taramasi |
| **Nerede?** | Egitim/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Windows Güvenlik Taraması — Hızlı Kontrol

Kullanıcı "bilgisayarımda açık var mı", "güvenlik açığı ara" dediğinde şu sırayı izle:

## 1. Açık Portlar (netstat)
```
powershell -NoProfile -Command "netstat -ano | Select-String LISTENING"
```
**Dikkat edilecek portlar:**
- 135 (RPC) — 0.0.0.0'da dinliyorsa 🟡 orta risk
- 445 (SMB) — 0.0.0.0'da dinliyorsa 🟡 orta risk (EternalBlue vektörü)
- 139 (NetBIOS) — LAN'a açıksa 🟢 düşük
- 11434 (Ollama) — sadece localhost'ta 🟢 güvenli
- 3389 (RDP) — dışarı açıksa 🔴 yüksek risk
- 22 (SSH) — dışarı açıksa 🔴 yüksek risk

## 2. Güvenlik Duvarı Durumu
```
powershell -NoProfile -Command "Get-NetFirewallProfile | Format-Table Name,Enabled,DefaultInboundAction"
```
- `Enabled=True` + `DefaultInboundAction=NotConfigured` (=Block) ✅ güvenli
- `Enabled=False` ❌ güvenlik duvarı kapalı

## 3. Şüpheli Processler
```
powershell -NoProfile -Command "Get-Process | Where-Object {$_.ProcessName -match 'python|powershell|cmd|wscript|cscript'} | Format-Table Id,ProcessName,StartTime"
```

## 4. Risk Değerlendirmesi

| Durum | Değerlendirme |
|-------|---------------|
| NAT arkası (192.168.x) | Portlar dışarı kapalı, firewall yeterli |
| Public IP (doğrudan modem) | 135/445/3389 açıksa 🔴 acil kapat |
| Firewall Block | 135/445 dinlese bile dışarı kapalı, 🟢 güvenli |

## 5. Rapor Formatı
Portları şu şekilde kategorize ederek raporla:
```
🔴 YÜKSEK RİSK — dışarı açık ve kritik servis
🟡 ORTA RİSK — dinliyor ama firewall koruyor
🟢 DÜŞÜK RİSK — localhost veya güvenli servis
```

## Not
- Kali VM kapalıysa bu taramayı Windows host'ta yap.
- Kali açıksa `nmap -sV <hedef>` ile doğrulatılabilir.
