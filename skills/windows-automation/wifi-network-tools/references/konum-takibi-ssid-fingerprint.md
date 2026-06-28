---
skill_id: 367fca6e59a7
usage_count: 1
last_used: 2026-06-16
---
# Wi-Fi Konum Takibi — SSID Fingerprinting ile MAC Rastgeleleştirme Bypass

## Problem

Modern telefonlar (Android 10+, iOS 14+) Wi-Fi taramalarında rastgele MAC adresleri kullanır. Bu nedenle BSSID (MAC) üzerinden cihaz takibi güvenilir değildir.

## Çözüm: SSID + Sinyal Profili + Çevre AP Parmak İzi

Bir cihazın BSSID'si her taramada değişse bile şu alanlar **sabit kalır**:

| Alan | Sabitlik | Güvenilirlik |
|------|----------|--------------|
| SSID | ✅ Sabit (kullanıcı değiştirmedikçe) | Yüksek |
| Sinyal gücü (RSSI) | ⚠️ ±5-10 dBm toleransla benzer | Orta |
| Kanal/frekans | ✅ Sabit (AP ile aynı kanalda) | Yüksek |
| Çevre AP BSSID'leri | ✅ Sabit (erişim noktalarının MAC'leri değişmez) | Çok Yüksek |
| Çevre AP sinyal oranları | ⚠️ Kısmen (cihaz konumuna bağlı) | Orta |

## Fingerprinting Akışı

### Adım 1 — Çevre AP Profili Oluştur

```bash
# Hedef SSID'yi bul, etrafındaki sabit BSSID'leri kaydet
sudo iw dev wlan0 scan 2>&1 | grep -A 10 "<hedef_SSID>" | grep "BSSID"

# Tüm çevre ağları kaydet
sudo iw dev wlan0 scan 2>&1 | awk '/^BSS/{b=$2} /SSID:/{print b, $0}'
```

### Adım 2 — SSID Filtreleme

```bash
# Hedef SSID'ye göre filtrele — MAC değişse bile SSID sabit
sudo iw dev wlan0 scan 2>&1 | grep -A 5 "S 22 PLAS"
```

### Adım 3 — Çevre AP Karşılaştırması

İki farklı taramada aynı çevre AP'ler + aynı sinyal sıralaması + aynı kanal varsa → cihaz AYNI cihazdır, MAC değişmiş olsa bile.

```bash
# 1. tarama profilini kaydet
t1=$(sudo iw dev wlan0 scan 2>&1 | grep "SSID:" | sort | md5sum)

# 2. taramayı yap (30 sn sonra)
sleep 30
t2=$(sudo iw dev wlan0 scan 2>&1 | grep "SSID:" | sort | md5sum)

# Profiller farklıysa ortak SSID'leri bul
comm -12 <(sort <t1_liste) <(sort <t2_liste)
```

## Python Script — SSID Fingerprint ile Cihaz Tespiti

```python
#!/usr/bin/env python3
"""
SSID tabanlı hedef cihaz tespiti.
MAC rastgeleleştirmeye rağmen SSID + çevre AP profili ile çalışır.
"""
import subprocess, json, re

def scan_wifi(interface="wlan0"):
    """Wi-Fi tara ve yapılandırılmış çıktı döndür."""
    result = subprocess.run(
        ["sudo", "iw", "dev", interface, "scan"],
        capture_output=True, text=True, timeout=30
    )
    return parse_iw_scan(result.stdout)

def parse_iw_scan(raw):
    """iw scan çıktısını listeye çevir."""
    networks = []
    blocks = raw.split("BSS ")
    for block in blocks[1:]:
        lines = block.split("\n")
        bssid = lines[0].split("(")[0].strip()
        net = {"bssid": bssid}
        for line in lines:
            if "SSID:" in line:
                net["ssid"] = line.split("SSID:")[-1].strip()
            elif "signal:" in line:
                net["signal"] = float(re.search(r"[-.\d]+", line).group())
            elif "freq:" in line:
                net["channel"] = int(re.search(r"\d+", line).group())
        if "ssid" in net and net["ssid"]:
            networks.append(net)
    return networks

def find_target(networks, target_ssid="S 22 PLAS"):
    """SSID'ye göre hedef cihazı bul."""
    for net in networks:
        if target_ssid in net.get("ssid", ""):
            return net
    return None

def get_environment_fingerprint(networks, exclude_ssid=None):
    """Çevre AP profilini çıkar (BSSID sabit, SSID değişebilir)."""
    env = []
    for net in networks:
        if exclude_ssid and exclude_ssid in net.get("ssid", ""):
            continue
        env.append({
            "ssid": net.get("ssid", "?"),
            "signal": net.get("signal", 0),
            "bssid": net.get("bssid", "?")
        })
    return sorted(env, key=lambda x: x["signal"], reverse=True)[:5]

# Kullanım:
# nets = scan_wifi()
# target = find_target(nets, "S 22 PLAS")
# env = get_environment_fingerprint(nets, exclude_ssid="S 22 PLAS")
```

## Alternatif: Telefonda Random MAC'i Kapatma

**Samsung One UI 6+:**
Ayarlar → Wi-Fi → [Ağ adı] → Gelişmiş → MAC Adresi Türü → **Telefon MAC'i**

Kapatılınca cihaz her zaman aynı MAC ile taramalarda görünür.

## Canlı Takip İçin Önerilen Yöntem

| Yöntem | MAC Bypass | Gizlilik | Kurulum |
|--------|-----------|----------|---------|
| SSID fingerprint | ✅ Otomatik | Düşük | Yok (sadece tarama) |
| Termux + Reverse SSH | ✅ (bağımsız) | Yüksek | Telefonda kurulum gerek |
| ICMP tunnel (ping) | ✅ (bağımsız) | Orta | Telefonda + sunucuda |
| Telegram bot (telefonda) | ✅ (bağımsız) | Yüksek | Telefonda Termux + bot |

En stabil çözüm: **SSID fingerprint** (hiçbir şey kurmadan, sadece dinleyerek)
En gizli çözüm: **Termux + Reverse SSH** (telefona kurulum gerek)
