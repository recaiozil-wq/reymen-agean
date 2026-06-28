---
name: autonomous-ai-agents-telegram-approval-bridge
description: İki LLM arasında dönüşümlü problem çözme + her turda insan onayı (file-signal
  üzerinden). `bridge_tg.py` üzerinden çalışır.
title: Autonomous Ai Agents Telegram Approval Bridge
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

the user wants alternating Claude+Ollama reasoning with manual 'devam/dur' control
  between turns.
# Telegram-Onaylı LLM Köprü

İki LLM arasında dönüşümlü problem çözme + her turda insan onayı (file-signal üzerinden). `bridge_tg.py` üzerinden çalışır.

## Kullanım

### Gereksinimler
- `claude` CLI kurulu ve PATH'te
- `ollama` + hedef model çekirdekte (`ollama list` ile doğrula)
- Masaüstü yazma izinleri: `C:\Users\marko\Desktop\`

### Çalıştırma
```bash
python C:\Users\marko\Desktop\bridge_tg.py
```

### Akış
1. Script ilk turda `bridge_status.txt` yazar.
2. Hermes/Ollama cevaplarını okuyarıp Telegram ile paylaş.
3. Kullanıcı `devam` (devam) veya `dur` (durdur) der.
4. `C:\Users\marko\Desktop\bridge_signal.txt` dosyasına yaz (sadece `devam` veya `dur`, küçük harf).
5. Script sinyali okur, yükümlüyü siler, bir sonraki tura geçer.
6. Tüm loglar bittiğinde Hem Hermes skill klasörüne Hem Obsidian Vault'a yazılır.

### Güvenlik
- `MAX_TURN=5`, zaman aşımı `300sn` → otomatik `dur`.
- Yalnızca dosya tabanlı iletişim; ağ/port yok.

## Yapılandırma

`bridge_tg.py` içindeki sabitler:
- `OLLAMA_MODEL` → kullanılacak Ollama modeli (ör: `dolphin-llama3:latest`)
- `signal_file` / `status_file` → masaüstü yolları
- `MAX_TURN` → maksimum tur sayısı

## Çıktılar
- Skill: `C:\Users\marko\AppData\Local\hermes\skills\telegram-onayli-kopru.md`
- Obsidian: `C:\Users\marko\OneDrive\Belgeler\Obsidian Vault\Telegram Kopru.md`

## Pitfall
- `bridge_signal.txt` içine başka bir şey yazma; "devam"/"dur" dışında algılanmaz.
- Script çalışırken dosyaları elle silme; çakışma olur.
