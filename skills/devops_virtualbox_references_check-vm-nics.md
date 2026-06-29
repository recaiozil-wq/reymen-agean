
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Virtualbox_References_Check Vm Nics |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Check VM NICs
VBoxManage showvminfo <name> | grep -E "NIC|Network"
```

Common configurations:
- **NAT only**: VM gets 10.0.2.15, host sees nothing. Requires port forwarding for inbound connections.
- **Host-Only**: Host and VM on same private subnet (e.g. 192.168.56.0/24). Easier SSH.
- **NAT + Host-Only**: Best of both.

### 4. Remote access options

| Method | Requires | Notes |
|--------|----------|-------|
| SSH | NAT port forwarding **OR** Host-Only adapter | Kali default user often `kali`/`kali` |
| VRDP (RDP) | `--vrde on` + port | VM must be **powered off** to modify |
| Shared clipboard | Guest Additions installed | One-way: Host→Guest or bidirectional |