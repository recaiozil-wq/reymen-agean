---
skill_id: 58b192791918
usage_count: 1
last_used: 2026-06-16
---
## Kali VM Ağ Kurtarma — Hızlı Reçete (En Sık Durum)

Kali çalışıyor (VMState=running) ama SSH bağlanamıyorsa, en olası neden: **`/etc/network/interfaces`'e `auto eth0` eklenmesi**, bu NetworkManager'ın eth0'ı "unmanaged" yapmasına ve boot'ta `networking.service`'in takılıp ağın hiç gelmemesine yol açar.

**Tanı (Windows'tan):**
- `VBoxManage list runningvms` → VM "kal" çalışıyor
- `sshpass -p 'kali' ssh -o ConnectTimeout=5 kali@192.168.0.19 "whoami"` → timeout
- `nmap -sn 192.168.56.0/24` → Kali'nin IP'si (192.168.0.19) yanıt vermiyor
- `arp -a | grep 08-00-27` → Kali MAC host-only subnet'te görünmüyor

**Hızlı çözüm (VirtualBox GUI ile):**
1. VirtualBox'ı aç → Kali'yi seç → Show
2. Kali'de root/1234 ile oturum aç
3. Terminal'de şunu çalıştır:
   ```bash
   sudo systemctl mask networking
   sudo systemctl unmask NetworkManager
   sudo systemctl enable --now NetworkManager
   sudo dhclient eth0
   ```
4. `ip addr show` ile IP'yi kontrol et
5. `sudo systemctl restart sshd`
6. Windows'tan SSH test et

**Reçetenin nedeni:**
- `systemctl mask networking` → ifupdown'ı tamamen devre dışı bırakır
- `NetworkManager enable --now` → NM'yi başlatır ve otomatik başlatır
- `dhclient eth0` → hemen DHCP lease alır
- interfaces'de `auto eth0` varsa bile maskelendiği için sorun çıkarmaz

**Alternatif — interfaces dosyasını temizleme:**
Eğer GUI'ye erişim yoksa ama recovery SSH varsa (NAT + port forwarding):
```bash
cat > /etc/network/interfaces << 'EOF'
source /etc/network/interfaces.d/*
auto lo
iface lo inet loopback
EOF
systemctl mask networking
systemctl enable --now NetworkManager
```