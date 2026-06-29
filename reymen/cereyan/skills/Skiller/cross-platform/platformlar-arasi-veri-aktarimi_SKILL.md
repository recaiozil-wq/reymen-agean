--- 
title: Platformlar Arası Veri Aktarımı
name: platformlar-arasi-veri-aktarimi
description: Windows, Linux (Kali) ve diğer platformlar arasında güvenli dosya ve veri aktarımı
tags: [cross-platform, dosya, aktarim, scp, rsync, network]
---

# Platformlar Arası Veri Aktarımı

| 5N1K | Açıklama |
|------|----------|
| Kim | ReYMeN bot kullanıcıları |
| Ne | Windows, Kali Linux ve diğer sistemler arasında güvenli dosya ve veri aktarımı yapar |
| Nerede | reymen/cereyan/skills/Skiller/cross-platform/ |
| Ne Zaman | İki farklı işletim sistemi arasında dosya paylaşımı gerektiğinde |
| Neden | Kali'de tespit edilen veriler Windows'a, Windows'ta hazırlanan script'ler Kali'ye gitmelidir |
| Nasıl | SCP, rsync, netcat veya paylaşılan ağ klasörü ile aktarım sağlanır |

## Yöntemler

| Yöntem | Yön | Hız | Güvenlik | Kullanım |
|--------|-----|-----|----------|----------|
| SCP | Çift yön | Orta | Yüksek (SSH) | `scp dosya.txt kullanici@hedef:/path/` |
| rsync | Çift yön | Hızlı | Yüksek (SSH) | `rsync -avz /kaynak/ kullanici@hedef:/hedef/` |
| netcat | Tek yön | Çok hızlı | Düşük (şifresiz) | `nc -lvp 4444 > gelen.zip` |
| SMB Paylaşım | Çift yön | Orta | Orta | `net use Z: \\HEDEF\paylasim` |

## Önerilen Akış

1. Küçük dosyalar (<100MB) → SCP
2. Büyük dosyalar / klasörler (>100MB) → rsync (--progress ile)
3. Aynı LAN'de hızlı transfer → netcat (sonrasında temizle)
4. Sürekli erişim gerekli → SMB paylaşımı kur

## Hafıza Kaydı

Her başarılı transfer `cross-platform/transfer/` kategorisine kaydedilir:
`kaynak → hedef | dosya: adı | boyut: X MB | yöntem: scp | süre: X sn`
