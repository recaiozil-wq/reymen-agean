---
skill_id: 9964ac9762a7
usage_count: 1
last_used: 2026-06-16
---
# 5. Asıl VM'i başlat
VBoxManage startvm "kal" --type headless
```

**Not:** `poweroff` komutu çıktı olarak yüzde ilerlemesi (%0...%100) döndürür. Bu normaldir, başarılı çalıştığını gösterir.
**Not 2:** Eğer `VBoxManage list vms`'de kal-recovery zaten kayıtlı değilse, yanlış alarmdır — medya kilidi farklı bir nedenden olabilir (VM zaten çalışıyor olabilir).

### VM Açık Ama SSH Zaman Aşımı — Adım Adım

1. **VM durumunu kontrol et:** `VBoxManage showvminfo "vm-adı" --machinereadable | grep VMState=`
   - `running` değilse → VM kapalı, başlat.
2. **VM ağ arayüzlerini kontrol et:**
   - `VBoxManage showvminfo "vm-adı" --machinereadable | grep -E "^(nic|macaddress)"`
   - Hangi NIC'lerin tanımlı olduğunu, tiplerini (bridged/hostonly/nat) gör.
3. **NetworkManager ↔ ifupdown çakışması kontrolü (EN SIK NEDEN):**
   Kali/Ubuntu/Debian'da `/etc/network/interfaces`'e `auto eth0` eklemek, NetworkManager'ın eth0'ı "strictly unmanaged" yapmasına yol açar.
   - **Belirtiler:** Boot sonrası ağ tamamen kırık, VM çalışıyor ama SSH zaman aşımı, host-only DHCP lease dolu ama VM IP alamamış.
   - **Tanı:** Recovery VM ile SSH bağlanıp `nmcli device status` çalıştır — eth0 "yönetilmeyen" görünür.
   - **Kök neden:** `/etc/NetworkManager/NetworkManager.conf`'da `[ifupdown] managed=false`. interfaces'te tanımlı arayüzleri ifupdown yönetir, NetworkManager dokunmaz. Ama interfaces'e `auto eth0` eklenince ifupdown eth0'ı yönetmeye çalışır, boot'ta networking servisi dhclient ile takılır ve ağ asla gelmez.

   **Çözüm adımları (Kali'yi kurtarma):**
   a. **Recovery VM oluştur** — Aynı VDI'ı kullan, NAT + port forwarding (ör. 2224→22) ile başlat
   b. **GRUB'a müdahale et** — Boot'ta networking servisi takılmasın diye:
      - VBoxManage reset at → hemen `keyboardputstring "e"` (5-8 kere, 0.5 sn aralık)
      - Bekle 3sn → ok tuşu ile `linux` satırına git → `keyboardputstring " systemd.unit=multi-user.target"`
      - Ctrl+X ile boot et
   c. **SSH bağlan** (NAT DHCP 10.0.2.15, port forwarding ile)
   d. **Interfaces'i sıfırla** — Sadece loopback bırak:
      ```
      cat > /etc/network/interfaces << EOF
      source /etc/network/interfaces.d/*
      auto lo
      iface lo inet loopback
      EOF
      ```
   e. **networking servisini devre dışı bırak:**
      `systemctl disable networking`
   f. **NetworkManager managed=true yap:**
      `sed -i "s/managed=false/managed=true/" /etc/NetworkManager/NetworkManager.conf`
   g. **NetworkManager'ı restart et:**
      `systemctl restart NetworkManager`
   h. **Doğrula:** `nmcli device status` → eth0 "bağlandı" gösterir
   i. **Recovery VM'i kapat, orijinal VM'i başlat** — Kali artık DHCP ile otomatik IP alır.

- **GuestInfo'dan IP almayı dene (genelde çalışmaz):**
   ```
   VBoxManage guestproperty get "vm-adı" "/VirtualBox/GuestInfo/Net/0/V4/IP"
   ```
   `No value set!` dönerse GuestAdditions kurulu değil veya çalışmıyor — normal. Kali'de Guest Additions yoksa hiçbir IP bilgisi dönmez.
4. **Host-only IP'yi dene (bilinen IP varsa):**
   ```
   sshpass -p 'sifre' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 kullanici@<hostonly-ip> "ip addr show"
   ```
   Bu da timeout verirse → Kali'de sshd çalışmıyor olabilir.
5. **SSH başarısızsa alternatif tanı:**
   - Windows'ta `arp -a` ile Kali MAC'ini kontrol et — hangi subnet'te görünüyor?
   - Bridged NIC MAC'i WiFi subnet'inde (192.168.0.x) yoksa → Kali bridged'dan IP almamış.
   - Çözüm: VM'ye GUI'den bağlan (VirtualBox penceresi) veya VM'i yeniden başlat.

### IP Discovery Workflow — VM Çalışıyor Ama SSH Vermiyorsa

VM `VBoxManage list runningvms` ile çalışıyor görünüyor ama bilinen IP'den SSH zaman aşımı veriyorsa:

**Adım 1 — VM'in ağ yapısını kontrol et:**
```bash
"/c/Program Files/Oracle/VirtualBox/VBoxManage.exe" showvminfo "<vm-adi>" | grep -E "NIC|MAC"
```
Hangi NIC'lerin tanımlı olduğunu ve MAC adreslerini not et.

**Adım 2 — MAC'leri ARP tablosunda ara:**
```bash
arp -a | grep "08-00-27"
```
VirtualBox MAC'leri `08:00:27` ile başlar. Çıktıda hangi subnet'te göründüklerine bak:
- `192.168.56.x` -> host-only ağda
- `192.168.0.x` (veya başka) -> bridged ağda (WiFi/Ethernet)
- Hiç görünmüyorsa -> VM ağ servisi çalışmıyor

**Adım 3 — Bridged IP'yi dene:**
Eğer MAC bridged subnet'teyse (örn. 192.168.0.19), o IP'den SSH dene:
```bash
sshpass -p 'kali' /c/Windows/System32/OpenSSH/ssh.exe -o StrictHostKeyChecking=no -o ConnectTimeout=5 kali@<bridged-ip> "hostname"
```

**Adım 4 — Hala zaman asimi?** -> Ag Kurtarma recetesine gec (yukaridaki "Kali VM Ag Kurtarma" bolumu).

**Not:** Host-only DHCP kapali olabilir (`VBoxManage list hostonlyifs` ile kontrol et -> `DHCP: Disabled`). Kali bridged subnet'teyse host-only IP alamaz.
**Not 2:** `VBoxManage guestproperty get` ile IP alinamazsa (`No value set!`) bu NORMALDIR.

### SSH Backend Config (ReYMeN config.yaml)

Terminal tool'unu dogrudan Kali'ye SSH yapacak sekilde yapilandirmak icin:
```bash
"/c/Users/marko/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe" config set terminal.backend ssh
"/c/Users/marko/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe" config set terminal.ssh_host <ip>
"/c/Users/marko/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe" config set terminal.ssh_user kali
"/c/Users/marko/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe" config set terminal.ssh_password "1234"
"/c/Users/marko/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe" config set terminal.ssh_port 22
"/c/Users/marko/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe" config set terminal.ssh_strict_host_key_check false
```
**Uyari:** Config dosyasina `patch` ile dogrudan yazmak ENGELENIR -> `hermes config set` kullanilmali.
**Not:** Config degisiklikleri mevcut session'da etkili olmaz, yeni session gerektirir.

### Bridged Agdan IP Alip Almadigini Kontrol

```
nmap -sn <wifi-subnet> --exclude <host-ip>
```
Sonra cikti da VirtualBox MAC (08:00:27 ile baslar) ara. Yoksa bridged baglanti sorunlu.