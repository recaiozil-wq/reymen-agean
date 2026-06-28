---
skill_id: dafcd9ff67b5
usage_count: 1
last_used: 2026-06-16
---
## Ağ Yapısı Sorgulama (VM NIC Tipi)

Kali'ye bağlanamıyorsam veya WiFi taraması istenmişse, önce VM'in ağ yapısını sorgula:

### Adım 1 — VM ağ arayüzlerini kontrol et
```bash
VBoxManage showvminfo "vm-adı" --machinereadable | grep -E "^(nic|macaddress)" | head -20
```

### Adım 2 — Çıktıyı yorumla
- `nic1="hostonly"` → Kali host-only ağda, WiFi'ye erişemez
- `nic1="nat"` → Kali NAT ağda, dışarı çıkabilir ama WiFi subnet'inde görünmez
- `nic1="bridged"` → Kali WiFi subnet'inde, tam erişim var
- `nic2` yoksa veya "none" → ikinci NIC yok, bridged eklenebilir

### Adım 3 — Çözüm üret
- **Sadece host-only** → Windows üzerinden nmap/ARP ile tara (Kali fayda etmez)
- **Bridged var** → Kali'de `arp-scan -l` ile tam MAC taraması yap
- **NAT var** → Port forwarding ile SSH bağlan, ama ağ taraması yapamaz