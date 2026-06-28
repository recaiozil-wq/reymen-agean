
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Linux Remote_References_A Yap S Sorgulama Vm Nic Tipi |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

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