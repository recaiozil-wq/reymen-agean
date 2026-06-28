---

name: kali-linux-remote
description: "Kali Linux VM'ye SSH ile bağlanıp komut çalıştırma workflow'u. sshpass ile şifresiz bağlantı, sudo komutları, arp-scan/nmap gibi ağ tarama araçları. HER ADIMDA kullanıcıdan klavyeden onay alınır — hangi araç, hangi hedef, hangi parametre. İzinsiz hiçbir şey çalıştırılmaz."
version: 3
license: MIT
metadata:
  hermes:
    tags: [kali, ssh, remote, linux, vm, network-scanning, kali-pentest]
audience: user
    platform: windows
    lang: turkish
---


> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Kali Linux VM'ye SSH ile bağlanıp komut çalıştırma workflow'u. sshpass ile şifresiz bağlantı, sudo komutları, arp-scan/nmap gibi ağ tarama araçları. HER ADIMDA kullanıcıdan klavyeden onay alınır — hangi araç, hangi hedef, hangi parametre. İzinsiz hiçbir şey çalıştırılmaz. |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Kali Linux Remote

Bu skill modüler bir yönlendiricidir. İhtiyacınız olan bölümü seçin ve ilgili reference dosyasını yükleyin.

## 📂 Bölümler

| Bölüm | Reference Dosyası |
|-------|------------------|
| ⚠️ KRİTİK KURAL — Şifre Sormadan Kullanma | `references/kri-ti-k-kural-ifre-sormadan-kullanma.md` |
| Bağlantı Bilgileri | `references/ba-lant-bilgileri.md` |
| Ön Koşullar | `references/n-ko-ullar.md` |
| Public Key Auth (Birincil, Tercih Edilen Yöntem) | `references/public-key-auth-birincil-tercih-edilen-y-ntem.md` |
| Sudo Önbellek Isıtma (HER OTURUMDA İLK ADIM) | `references/sudo-nbellek-is-tma-her-oturumda-i-lk-adim.md` |
| SSH Komut Çalıştırma (execute_code ile) | `references/ssh-komut-al-t-rma-execute_code-ile.md` |
| Sudo Komutları | `references/sudo-komutlar.md` |
| Ağ Tarama — Arp-scan vs Nmap Karşılaştırması | `references/a-tarama-arp-scan-vs-nmap-kar-la-t-rmas.md` |
| SSH ile Kali'ye Bağlanma (Kalıcı şifresiz sudo) | `references/ssh-ile-kali-ye-ba-lanma-kal-c-ifresiz-sudo.md` |
| Kullanıcı Çalışma Stili | `references/kullan-c-al-ma-stili.md` |
| SSH Akışı (Kullanıcı → Hermes → Kali → Rapor) | `references/ssh-ak-kullan-c-hermes-kali-rapor.md` |
| Git Credential Bypass (Git Popup'larını Kapatma) | `references/git-credential-bypass-git-popup-lar-n-kapatma.md` |
| Git credential manager'ı tamamen devre dışı bırakan alias | `references/git-credential-manager-tamamen-devre-d-b-rakan-alias.md` |
| SSH varsayılan olarak sshpass kullansın (Windows OpenSSH) | `references/ssh-varsay-lan-olarak-sshpass-kullans-n-windows-openssh.md` |
| Ağ Yapısı Sorgulama (VM NIC Tipi) | `references/a-yap-s-sorgulama-vm-nic-tipi.md` |
| Kali VM Ağ Kurtarma — Hızlı Reçete (En Sık Durum) | `references/kali-vm-a-kurtarma-h-zl-re-ete-en-s-k-durum.md` |
| SSH Bağlantı Sorunu — Tam Tanı ve Kurtarma | `references/ssh-ba-lant-sorunu-tam-tan-ve-kurtarma.md` |
| hata: VBOX_E_INVALID_OBJECT_STATE (0x80bb0007) | `references/hata-vbox_e_invalid_object_state-0x80bb0007.md` |
| 1. Çalışan VM'leri listele | `references/1-al-an-vm-leri-listele.md` |
| 2. Recovery VM'ini kapat | `references/2-recovery-vm-ini-kapat.md` |
| 3. Bekle (3 sn) | `references/3-bekle-3-sn.md` |
| 4. Doğrula — hiçbir VM çalışmıyor olmalı | `references/4-do-rula-hi-bir-vm-al-m-yor-olmal.md` |
| 5. Asıl VM'i başlat | `references/5-as-l-vm-i-ba-lat.md` |
| Calisma Akisi (Kullanici -> Hermes -> Onay -> Kali -> Rapor) | `references/calisma-akisi-kullanici-hermes-onay-kali-rapor.md` |
| 1. Önce managed moda geç | `references/1-nce-managed-moda-ge.md` |
| 2. Tara — tüm kanallar, otomatik tamamlanır | `references/2-tara-t-m-kanallar-otomatik-tamamlan-r.md` |
| 3. Belli bir SSID'yi ara (örn: S22 PLAS) | `references/3-belli-bir-ssid-yi-ara-rn-s22-plas.md` |
| Çıktı: BSSID 46:89:9e:xx:xx:xx, signal: -27.00 dBm, freq: 2437, SSID: S 22 PLAS | `references/kt-bssid-46-89-9e-xx-xx-xx-signal-27-00-dbm-freq-2437-ssid-s.md` |
| 1. Monitor moda geç | `references/1-monitor-moda-ge.md` |
| 2. Belli bir hedef BSSID'yi izle (arka planda, timeout ile) | `references/2-belli-bir-hedef-bssid-yi-izle-arka-planda-timeout-ile.md` |
| 3. Çıktıyı oku | `references/3-kt-y-oku.md` |
| 5. Temizlik | `references/5-temizlik.md` |
| managed → monitor | `references/managed-monitor.md` |
| monitor → managed (tekrar tarama için — iw scan için managed gerekir) | `references/monitor-managed-tekrar-tarama-i-in-iw-scan-i-in-managed-gere.md` |
| 1. ADIM — Help'i oku | `references/1-adim-help-i-oku.md` |
| 2. ADIM — Paket mevcut mu kontrol et | `references/2-adim-paket-mevcut-mu-kontrol-et.md` |
| Aynı aracın farklı parametrelerini dene (help'te gördüklerinle sınırlı kal) | `references/ayn-arac-n-farkl-parametrelerini-dene-help-te-g-rd-klerinle-.md` |
| phy0 var mı kontrol et | `references/phy0-var-m-kontrol-et.md` |
| Managed mode arayüz oluştur | `references/managed-mode-aray-z-olu-tur.md` |
| Doğrula | `references/do-rula.md` |
| Çıktı: type monitor olmalı | `references/kt-type-monitor-olmal.md` |
| airodumping ile tarama | `references/airodumping-ile-tarama.md` |
| 1. phy0 var mı kontrol et | `references/1-phy0-var-m-kontrol-et.md` |
| 2. Yeniden oluştur (managed veya monitor) | `references/2-yeniden-olu-tur-managed-veya-monitor.md` |
| 3. Monitor moda geç | `references/3-monitor-moda-ge.md` |
| NOT: airmon-ng start kullanma — interaktif prompt'ta çöker | `references/not-airmon-ng-start-kullanma-interaktif-prompt-ta-ker.md` |
| Yönetici PowerShell'de (Ctrl+Shift+Enter) | `references/y-netici-powershell-de-ctrl-shift-enter.md` |
| Pitfall'lar | `references/pitfall-lar.md` |

## Kullanım

1. İhtiyacın olan bölümü belirle
2. `skill_view(name="...", file_path="references/...")` ile yükle
