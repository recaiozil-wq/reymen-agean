
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Linux Remote_References_A Tarama Arp Scan Vs Nmap Kar La T Rmas |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Ağ Tarama — Arp-scan vs Nmap Karşılaştırması

Aynı subnet'i tararken `arp-scan` ve `nmap -sn` farklı sonuçlar verebilir. İkisini birlikte kullanmak en iyisidir.

### Karşılaştırma Tablosu

| Özellik | arp-scan | nmap -sn |
|---------|----------|----------|
| Süre | ~1.8 sn (hızlı) | ~3.5 sn (orta) |
| Cihaz sayısı | Genelde daha fazla (7+) | Bazen eksik (6) |
| Vendor bilgisi | Yok (Unknown gösterir) | Var (üretici adıyla) |
| Kendi IP'sini listeler | Hayır | Evet |
| Protokol | ARP (L2) | ICMP + TCP (L3) |
| Çalışma şartı | Aynı broadcast domain | Genelde yeterli |
| Komut | `sudo arp-scan --interface eth1 --localnet` | `sudo nmap -sn 192.168.0.0/24` |

### Neden Farklı Sonuçlar?

- **arp-scan L2'de çalışır** → ARP isteği atar, aynı switch/bridge'deki tüm cihazlardan cevap alır. `.10` ve `.23` gibi cihazları ARP sayesinde bulur. **Kendini listelemez** çünkü kendi MAC'ini zaten biliyordur.
- **nmap -sn L3'te çalışır** → ICMP ping + TCP SYN (80, 443) dener. Kali'nin kendi IP'sini de listeler (`.19`). Bazen `.10` ve `.23`'ü kaçırabilir çünkü bu cihazlar ICMP'yi engelliyor olabilir.

### Önerilen Workflow

```
Adım 1: arp-scan (hızlı tarama) → tüm cihazları bul
Adım 2: nmap -sn (detaylı tarama) → vendor bilgilerini al
Adım 3: İkisini birleştir → eksiksiz liste + vendor bilgisi
```

### Kullanıcıya Rapor Formatı

Sonuç tablo olarak gösterilir:
```
IP              MAC              Vendor            Kaynak
192.168.0.1     98:f2:17:...     Castlenet Tech    arp-scan + nmap
192.168.0.10    00:00:00:...     Unknown           sadece arp-scan
192.168.0.17    00:00:00:...     Hikvision         arp-scan + nmap
...
```



### Kali Ağ Arayüzleri
| Arayüz | MAC | IP | Açıklama |
|--------|-----|----|----------|
| lo | 00:00:00:00:00:00 | 127.0.0.1/8 | Loopback |
| eth0 | 08:00:27:e2:02:51 | DHCP (bridged) veya IP yok | Bridged/NAT ağ |
| eth1 | 08:00:27:bc:0e:ba | 192.168.0.19/24 | Host-Only ağ |

- Kali'nin **WiFi adaptörü YOK** (VirtualBox VM, sanal NIC'ler).
- Kali'nin **WiFi ağına erişimi yok** (192.168.0.x) host-only'den. Bridged NIC ile WiFi subnet'ine erişir.
- Kali bridged'deyse `192.168.0.x` subnet'inde olur, host-only'deyse `192.168.56.x`.

### Ağ Tarama (Windows üzerinden)

Kali'de WiFi yoksa, Windows ana makinede `nmap` ile taranır:
```cmd
nmap -sn 192.168.0.0/24
```
nmap Windows'ta: `C:\Program Files (x86)\Nmap\nmap.exe`
Çıktı: IP + MAC + vendor bilgisi + hostname.

### nc Reverse Shell — ÇALIŞMAZ
nc ile reverse shell bağlantısı **farklı ağ segmentleri** (WiFi vs host-only) nedeniyle çalışmaz. VirtualBox VM ile ana makine farklı subnet'lerde. SSH kullanılır.

### Komut Gönderme Yöntemleri (Öncelik Sırasına Göre)

**Yöntem 1 — Direct SSH (Tercih Edilen, En Güvenilir)**
```
sshpass -p 'kali' ssh -o StrictHostKeyChecking=no kali@<ip> 'komut'
```
- Çıktı doğrudan döner, görülebilir, loglanabilir.
- sudo komutları için `sudo -S` ile şifre gönderme gerekebilir (bkz: Sudo Önbellek Isıtma)
- Pipe, redirect, grep, awk hepsi çalışır.

**Yöntem 2 — VirtualBox keyboardputstring (Kullanıcı Terminalde Görmek İsterse)**
```bash
VBOX="C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
"$VBOX" controlvm "kal" keyboardputstring "komut"
"$VBOX" controlvm "kal" keyboardputstring $'\n'
```
- Kullanıcı VM'in kendi terminalinde komutların yazıldığını görür.
- **Kısıtlamalar:** Çıktı yakalanamaz (görsel olarak VM ekranında kalır), pipe/redirect çalışmaz, `$()` ve `>` gibi shell operatörleri yollanamaz.
- Uzun zincirleme komutlar (`echo '...' && echo '...'`) buffer sorunu nedeniyle çalışmayabilir — her komut ayrı keyboardputstring çağrısı + sleep ile yazılmalı.
- Sleep süreleri: basit komutlar için 1-2 sn, nmap gibi uzun taramalar için 3-8 sn.

**Yöntem 3 — Tmux send-keys (ÖNERİLMEZ — git-bash/MSYS ortamında boşluk kırpma sorunu)**
```
sshpass -p 'kali' ssh kali@<ip> 'tmux send-keys -t hermes "komut" Enter'
sshpass -p 'kali' ssh kali@<ip> 'tmux capture-pane -t hermes -p -S -50'
```
- **Bilinen sorun:** git-bash/MSYS üzerinden `send-keys` çağrıldığında, çift tırnak içindeki boşluklar yutulur (`"echo hello"` → `echohello`).
- `send-keys -l` (literal mode) C-m (Enter) göndermeyi karmaşıklaştırır, zsh shell'de de ek sorun çıkarır.
- **Ne zaman kullanılır:** Sadece VM terminal çıktısının loglanması gerekiyorsa ve keyboardputstring yetersiz kalıyorsa. Bunun dışında doğrudan SSH kullan.