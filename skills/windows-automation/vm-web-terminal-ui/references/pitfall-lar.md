---
skill_id: 8771facc17bb
usage_count: 1
last_used: 2026-06-16
---
## Pitfall'lar

1. **Guest Additions yok:** `guestproperty`'den IP alınamaz. Ağ taraması (nmap/arp), bridged subnet ping sweep veya VBoxManage NIC listesi ile IP bulunur.
2. **VM çalışıyor ama SSH zaman aşımı:** Kali'de NetworkManager vs interfaces çakışması olabilir. `systemctl mask networking` + `systemctl enable --now NetworkManager` çözümü dene. Ayrıca bridged IP değişmiş olabilir — host-only yerine bridged (192.168.0.x) subnet'te ara.
3. **Host-only bridged IP değişirse:** KALI_HOST sabit kodlu. DHCP bridged IP değişince kodu güncelle. IP bulmak için: Windows'ta `arp -a | grep 08-00-27` veya ping sweep yap; VBox arayüzsüz ise `for i in $(seq 1 254); do ping -n 1 -w 1 192.168.0.$i | grep -q TTL && echo 192.168.0.$i; done`.
4. **VBoxManage "already locked" hatası:** VM poweroff durumunda bile kilitli kalabilir. Çözüm: `taskkill.exe //F //IM VBoxSVC.exe && taskkill.exe //F //IM VirtualBox.exe`, 2sn bekle, sonra `VBoxManage startvm "kal" --type headless`. `discardstate` genelde aynı kilitten geçemediği için işe yaramaz.
4. **Flask restart gerekirse:** Arka planda çalışıyorsa önce process kill et, sonra yeniden başlat.
5. **Windows firewall:** localhost:5050'e erişim genelde açıktır. Bloklanırsa güvenlik duvarına `127.0.0.1:5050` için izin ekle.
6. **Paramiko exec_command** timeout parametresi alır ama session timeout değildir. Çok uzun süren komutlar için ayrı thread'de çalıştır.
7. **Her komut yeni bir shell açar** — `cd` gibi stateful komutlar çalışmaz. Tmux oturumu kullanarak kalıcı shell tutulabilir.
8. **zsh `===` reddeder:** Kali'de default shell zsh. `echo "=== metin ==="` çalışmaz — zsh `==` işaretini glob operatörü olarak algılar. `echo` ile basit süsleme: `echo "---- metin ----"` kullan.
9. **send-keys + bash/MSYS boşluk sorunu:** Tmux `send-keys`'e bash/MSYS üzerinden boşluklu string göndermek, boşlukları yutar. Sebebi: bash'ın komut ayrıştırması ile tmux `send-keys` argüman işlemesi arasındaki etkileşim. `-l` (literal) flag'i de çözemez. `C-m` (Enter) ayrı argüman olarak değil, literal string olarak gider. Çözüm: tmux kullanmadan `sshpass ssh -o StrictHostKeyChecking=no kali@IP 'komut'` ile doğrudan `exec_command()` tarzında tek tek komut çalıştır — her `terminal()` çağrısı Kali'de bir shell oturumu açar, boşluk sorunsuz çalışır.
10. **zsh'te `?` glob çakışması:** `echo "tararsam?"` gibi komutlar zsh'ta `no matches found` hatası verir. `?` karakteri glob wildcard'ıdır. Çözüm: `echo` içinde kullanma veya kaçış karakteri ekle (`\?`). Alternatif: `printf '%s\n' "..."` kullan.
11. **ssh ile interaktif komut gösterme yöntemi:** Terminalde her adımı ayrı `terminal()` çağrısı ile çalıştır. Kullanıcıya hangi komutların hangi sırayla çalıştırıldığını göstermek için önce açıklama echo'su, sonra asıl komut. Örnek:
    ```bash
    sshpass -p 'kali' ssh -o StrictHostKeyChecking=no kali@192.168.0.19 'echo "ADIM 1: arp-scan ile ag taramasi"'
    sshpass -p 'kali' ssh -o StrictHostKeyChecking=no kali@192.168.0.19 'sudo arp-scan --interface eth1 --localnet'
    ```
    Bu yöntem tmux'tan daha güvenilir çünkü her komut ayrı bir shell oturumunda çalışır ve boşluklar korunur.