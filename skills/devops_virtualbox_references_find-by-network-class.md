
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Virtualbox_References_Find By Network Class |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Find by network class
Get-PnpDevice | Where-Object { $_.Class -eq 'Net' } | Select-Object FriendlyName,InstanceId | Format-List
```

Add USB filter (VM must be off or device not yet captured):
```bash
VBoxManage usbfilter add 0 --target "<vm-name>" \
  --name "RT73 USB Wireless" \
  --vendorid 148F \
  --productid 2573 \
  --revision 0001
```

Verify filter and attachment:
```bash