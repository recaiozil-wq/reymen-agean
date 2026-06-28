# GÖREV: ReYMeN .md Dosyalarını Türkçeleştir

## NE
ReYMeN projesindeki tüm önemli .md dosyalarını **Hermes referanslarından temizle, ReYMeN'e özgü içerikle yeniden yaz, Türkçeleştir**.

## HEDEF DOSYALAR

| # | Dosya | Ne Yap |
|---|---|---|
| 1 | README.md | Türkçe baştan yaz, detaylı, kapsamlı |
| 2 | CONTRIBUTING.md | Türkçe'ye çevir, "Katkıda Bulunma Rehberi" |
| 3 | CHANGELOG.md | Türkçe'ye çevir, "Değişiklik Günlüğü" |
| 4 | AGENTS.md | Türkçe'ye çevir |

## İÇERİK

### README.md
Türkçe, sade, anlaşılır. GitHub'da gören hemen anlasın. Şunlar olsun:

1. **ReYMeN Nedir?**
   - "ReYMeN, yapay zeka asistanlarını yönetmek için geliştirilmiş açık kaynak bir platformdur."
   - "Hermes Agent tabanlıdır, Türkçe dil desteği ile Windows odaklı çalışır."
   - "Telegram botları, CLI, web arayüzü ve daha fazlasını tek merkezden yönetir."

2. **Özellikler** (emoji + kısa açıklama):
   - 🤖 Çoklu bot yönetimi (3 Telegram botu aynı anda)
   - 🧠 Çoklu yapay zeka desteği (DeepSeek, OpenAI, Groq, OpenRouter...)
   - 🛠️ 100+ araç (dosya, web, ses, görsel, kod, terminal)
   - 🧩 Otonom görev çözücü (hata al → öğren → çöz)
   - 💾 Akıllı hafıza (OnceHafiza ile hatalardan öğrenme)
   - 📊 Kanban görev takibi
   - 💰 API harcama takibi
   - 🔄 Kendini geliştirme döngüsü
   - 🌐 Platform desteği (Windows, WSL, Kali Linux)
   - 🧩 MCP istemci/sunucu desteği
   - 🔍 FTS5 sesion arama

3. **Kurulum** (adım adım, baştan sona):
   ```
   git clone https://github.com/İzleyici-Hermes/ReYMeN-Ajan-v2.git
   cd ReYMeN-Ajan-v2
   python -m venv venv
   source venv/bin/activate  (Windows: venv\Scripts\activate)
   pip install -r requirements.txt
   ```

4. **Kullanım** (örnekler):
   ```bash
   python reymen_launcher.py
   ```
   Veya modül olarak:
   ```bash
   python -m reymen
   ```

5. **Proje Yapısı**:
   ```
   reymen/
   ├── arac/       # Araçlar (web, dosya, ses...)
   ├── cereyan/    # Ana işlem döngüsü
   ├── core/       # Çekirdek (model, öğrenme, a2a)
   ├── sistem/     # Sistem yönetimi (CLI, gateway)
   ├── guvenlik/   # Güvenlik
   ├── hafiza/     # Hafıza sistemleri
   └── scripts/    # Yardımcı script'ler
   ```

6. **Lisans**: MIT - Nous Research (Hermes) + ReYMeN

### CONTRIBUTING.md
- "Katkıda Bulunma Rehberi" başlığı
- Nasıl katkıda bulunulur (fork, branch, PR)
- Kod standartları
- Test nasıl çalıştırılır
- İletişim

### CHANGELOG.md
- "Değişiklik Günlüğü" başlığı
- Mevcut İngilizce içeriği Türkçe'ye çevir
- Versiyonları koru

### AGENTS.md
- "ReYMeN Ajan Kılavuzu" başlığı
- Yetenekler
- Kullanım
- MCP sunucu
- Session arama

## DOĞRULAMA
- Dosyalar geçerli markdown mı?
- 3 farklı kişi okusa anlar mı?
- Kod blokları çalışıyor mu?
- Hermes referansları temizlenmiş mi?

## YASAKLAR
- **Hermes referansını olduğu gibi bırakma**
- Kod mantığını değiştirme
- .py dosyalarına dokunma
- .git, __pycache__, venv içinde değişiklik
