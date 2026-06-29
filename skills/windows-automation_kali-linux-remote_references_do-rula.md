
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Linux Remote_References_Do Rula |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Doğrula
iw dev
ip link show wlan0
```

### Monitor Mode (airmon-ng YERİNE iw ile)

`airmon-ng start wlan0` **interaktif prompt sorar** (`Found phy0 with no interfaces assigned, would you like to assign one to it? [y/n]`) ve SSH üzerinden cevap verilemediği için recursion hatasıyla çöker (`Maximum function recursion depth (1000) reached`).

**Doğru yöntem — manuel iw:**
```bash
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up