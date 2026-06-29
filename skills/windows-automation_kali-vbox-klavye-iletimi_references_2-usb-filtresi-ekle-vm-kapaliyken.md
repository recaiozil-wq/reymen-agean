
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Vbox Klavye Iletimi_References_2 Usb Filtresi Ekle Vm Kapaliyken |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# 2. USB filtresi ekle (VM KAPALIYKEN)
"C:\Program Files/Oracle/VirtualBox/VBoxManage.exe" usbfilter add 0 \
  --target "kal" \
  --name "Ralink WiFi" \
  --vendorid 148f \
  --productid 2573