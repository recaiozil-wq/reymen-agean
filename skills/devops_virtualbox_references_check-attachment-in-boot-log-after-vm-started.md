
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Virtualbox_References_Check Attachment In Boot Log After Vm Started |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Check attachment in boot log (after VM started)
grep -i "USB\|<vendorid>\|<productid>\|attach" "C:/Users/<user>/VirtualBox VMs/<vm>/Logs/VBox.log"
```

**Known good config for RT73 (Ralink) USB WiFi:**
- VID 148F, PID 2573
- HighSpeed on RootHub (OHCI/EHCI controller)
- xHCI (USB 3.0) controller NOT needed — RT73 is USB 2.0 HighSpeed
- Works with VirtualBox default OHCI+EHCI controllers

**⚠️ WiFi passthrough danger**: USB WiFi passthrough can destabilize the VM's own networking (see Pitfalls). Best practice: set up USB filter while VM is off, start VM, expect it to take slightly longer on first boot as the new USB device is detected. If the VM becomes unreachable, the fix is removing the filter + console recovery.