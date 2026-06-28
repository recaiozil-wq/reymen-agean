---
name: kali-help-explorer
hermes_skill: true
category: windows-automation
audience: user
tags: [automation, windows]
description: Kali Linux araçlarının yardım/ man/ info sayfalarını analiz eder, parametre matrisi çıkarır, senaryo bazlı örnekler üretir. Kali VM'e SSH bağlantısı ile çalışır.
title: "Kali Help Explorer"
created: 2026-06-07
---

# Kali Linux Yardım ve Parametre Analizi (kali_help_explorer)

## Amaç
Kali Linux üzerindeki araçların karmaşık yardım (`--help`), kılavuz (`man`) ve bilgi (`info`) sayfalarını analiz ederek, kullanıcının siber güvenlik senaryolarına uygun parametreleri hızla bulmasını ve güvenli örnekler üretmesini sağlamak.

## Ön Koşullar
- Kali VM çalışıyor olmalı (`ssh kali@192.168.56.103`)
- Hedef araç Kali'de yüklü olmalı
- `sshpass` veya anahtar tabanlı SSH erişimi gerekli

## Kali VM Yapılandırması
- Host: 192.168.56.103
- User: kali
- Şifre: 1234
- Bağlantı: `sshpass -p 'kali' ssh -o StrictHostKeyChecking=no kali@192.168.56.103`

## Çalışma Protokolü

### 1. Komut Keşfi (Discovery)
Kullanıcı bir araç veya siber güvenlik görevi belirttiğinde, ilgili aracın yardım dokümanını şu hiyerarşiye göre analiz et:
1. Kısa Yardım: `[komut] -h` veya `[komut] --help`
2. Kılavuz Sayfası: `man [komut]`
3. Gelişmiş Bilgi: `info [komut]`

### 2. SSH Üzerinden Yardım Çekme
```bash
# Kısa yardım
sshpass -p 'kali' ssh -o StrictHostKeyChecking=no kali@192.168.56.103 "nmap -h" 2>/dev/null

# Man sayfası (düz metin)
sshpass -p 'kali' ssh -o StrictHostKeyChecking=no kali@192.168.56.103 "man nmap | col -b" 2>/dev/null

# info sayfası
sshpass -p 'kali' ssh -o StrictHostKeyChecking=no kali@192.168.56.103 "info nmap" 2>/dev/null
```

### 3. Çıktı Analiz ve Filtreleme
- Uzun yardım çıktılarını `grep`, `head`, `tail` ile filtrele
- İlgili bölümleri ayırmak için `grep -A N` (after) veya `grep -B N` (before) kullan
- Parametre satırlarını ayırmak için: `grep -E '^\s+-[a-zA-Z]'`

## 3. Çıktı Yapılandırma Şablonu
Analiz sonuçlarını her zaman aşağıdaki standart Markdown şablonuyla kullanıcıya sun. Otomatik olarak Obsidian vault'una kaydet:

Kayıt yolu: `C:\Users\marko\OneDrive\Belgeler\Obsidian Vault\Kali Araç Analizi\[araç-adi].md`

Klasör yoksa otomatik oluştur:
```bash
mkdir -p "C:\Users\marko\OneDrive\Belgeler\Obsidian Vault\Kali Araç Analizi"
```

### Şablon

```markdown
---
tool_name: "[Araç Adı]"
category: "[Recon / Exploitation / Post-Exploitation / Privilege Escalation / Password / Wireless / Web / Forensics / Reporting / Stress Testing / Sniffing / Spoofing / Database / Vulnerability Analysis / Social Engineering / Hardware]"
last_verified: 2026-06
source: "kali-help-explorer"
---

# 🛠 Araç Analizi: [Araç Adı]

## 📌 Temel Amacı
[Aracın ne işe yaradığına dair 1-2 cümlelik net açıklama.]

## ⌨️ En Sık Kullanılan Temel Yardım Komutları
- `$ [komut] -h` → Hızlı parametre listesi.
- `$ man [komut]` → Detaylı sistem kılavuzu.
- `$ [komut] --help` → Genişletilmiş yardım (varsa).

## 🔍 Kritik Parametre Matrisi

| Parametre | Uzun Versiyon | Açıklama | Risk Seviyesi |
| :--- | :--- | :--- | :--- |
| `-sS` | `--syn-scan` | Yarı açık (SYN) tarama. Yakalanma riski düşük. | Orta |
| `-p-` | `--ports 1-65535` | Tüm portlar. Zaman alır ama kapsamlıdır. | Düşük |
| `-O` | `--os-detection` | İşletim sistemi tespiti. Root gerektirir. | Yüksek |

## 🎯 Senaryo Bazlı Örnek Kullanımlar

### Senaryo 1: [Senaryo Başlığı]
**Açıklama:** [Senaryonun amacı ve ne zaman kullanılacağı]
```bash
[örnek komut satırı]
```
**Çıktı:** [beklenen çıktı veya dikkat edilmesi gerekenler]

### Senaryo 2: [Senaryo Başlığı]
**Açıklama:** [Senaryonun amacı]
```bash
[örnek komut satırı]
```

## ⚠️ Uyarılar & İpuçları
- [Güvenlik uyarısı veya pratik ipucu]
- [Yaygın hatalar ve çözümleri]
```

## Kategori Ön Tanımları
| Kategori | Örnek Araçlar |
| :--- | :--- |
| Recon | nmap, gobuster, dirb, dirsearch, dnsrecon, sublist3r |
| Exploitation | metasploit, searchsploit, sqlmap, beef-xss |
| Post-Exploitation | mimikatz, bloodhound, powercat |
| Privilege Escalation | linpeas, winpeas, peass-ng |
| Password Attacks | hydra, john, hashcat, crunch |
| Wireless | aircrack-ng, reaver, kismet |
| Web Apps | burpsuite, owasp-zap, whatweb, wpscan |
| Sniffing | wireshark, tcpdump, bettercap |
| Forensics | autopsy, sleuthkit, volatility |

## Kritik Parametreler İçin Filtreleme Desenleri
```bash
# Sadece parametre satırlarını göster
ssh kali@192.168.56.103 "nmap --help | grep -E '^\s+-[a-zA-Z]'"

# Belirli bir anahtar kelime içeren parametreleri bul
ssh kali@192.168.56.103 "man nmap | col -b | grep -A 2 -i 'syn scan'"

# Örnek kullanım satırlarını bul
ssh kali@192.168.56.103 "man nmap | col -b | grep -A 1 'example\|örnek\|usage\|kullanım' -i"
```

## 5. Tam İş Akışı (Uçtan Uca)

### 5.1 Hiyerarşik Yardım Keşfi
Sırayla dene:

1. `[komut] --help 2>&1 | head -150` — en hızlı, en kısa
2. `[komut] -h 2>&1 | head -150` — alternatif kısa yardım
3. `man [komut] 2>&1 | col -b | head -300` — detaylı kılavuz
4. `info [komut] 2>&1 | head -200` — gelişmiş bilgi (varsa)

Bir seviye yeterli çıktı verirse sonrakine geçme.

### 5.2 Örnek Çağrı
```bash
# SSH ile Kali'ye bağlan, yardımı çek, parametreleri filtrele
sshpass -p 'kali' ssh -o StrictHostKeyChecking=no kali@192.168.56.103 "
  nmap --help 2>&1 | head -80
  echo '=== MAN ==='
  man nmap 2>&1 | col -b | grep -A 1 'example\|usage\|örnek' -i | head -20
"
- Uzun man sayfaları (500+ satır) terminal çıktısını doldurabilir — `head -100` ile sınırla
- Bazı araçlar `--help` yerine `-h` ile kısa yardım, `--usage` ile kullanım gösterir
- `info` komutu her araç için mevcut değildir; yoksa `man`'e düş
- `sshpass` yüklü değilse Kali VM'de `sudo apt install sshpass` gerekebilir
- araç ismi yanlışsa (örn. `nmap` doğru, `nmapx` yanlış) hata alınır — önce `which [komut]` ile doğrula
