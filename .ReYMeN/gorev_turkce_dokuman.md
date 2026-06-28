# GÖREV: ReYMeN Projesine Türkçe Dokümantasyon Ekle

## NE
ReYMeN-Ajan projesinin tamamına Türkçe açıklamalar ekle. GitHub'da yüklendiğinde herkes (özellikle Türk çocuklar/geliştiriciler) ne olduğunu anlayabilsin.

## YAPILACAKLAR

### 1. README.md — Türkçe, Detaylı, Kapsamlı
**Yer:** proje kökünde `README.md` (varsa güncelle, yoksa oluştur)
**İçerik:**
- Proje adı ve logosu (varsa)
- **ReYMeN nedir?** — 2-3 paragraf Türkçe açıklama
  - "ReYMeN, yapay zeka asistanlarını tek bir merkezden yönetmek için geliştirilmiş açık kaynak bir platformdur."
  - "Hermes Agent tabanlıdır, Türkçe dil desteği ile Windows odaklı çalışır."
- **Özellikler** (maddeler halinde):
  - 🧠 Çoklu yapay zeka sağlayıcı desteği (DeepSeek, OpenAI, Groq, OpenRouter...)
  - 🤖 Telegram bot yönetimi (3 bot aynı anda)
  - 🛠️ 100+ araç (dosya, web, ses, görsel, video, kod)
  - 🧩 Otonom görev çözücü (hata al → öğren → çöz)
  - 💾 Akıllı hafıza (OnceHafiza ile hatalardan öğrenme)
  - 📊 Kanban görev takibi
  - 💰 API harcama takibi
  - 🔄 Kendini geliştirme döngüsü
  - 🌐 Platform desteği (Windows, WSL, Kali Linux)
- **Kurulum** (adım adım):
  1. Gereksinimler (Python 3.11+, Git)
  2. Repo'yu klonla
  3. Sanal ortam oluştur
  4. Bağımlılıkları yükle
  5. .env dosyasını yapılandır
  6. Çalıştır
- **Kullanım** (örneklerle):
  ```bash
  python reymen_launcher.py
  python -m reymen
  ```
- **Proje Yapısı** (klasörleri açıkla):
  ```
  reymen/          # Ana kod
    arac/          # Araçlar (web, dosya, ses...)
    cereyan/       # Ana işlem döngüsü
    core/          # Çekirdek (model adapter, öğrenme, a2a)
    sistem/        # Sistem yönetimi (CLI, gateway, config)
    ...
  ```
- **Katkıda Bulunma** (nasıl yardım edebilirsin)
- **Lisans** (MIT - Nous Research + ReYMeN)
- **İletişim** (Telegram bot bağlantıları)

### 2. Her Modülün Başına Türkçe Docstring

**Kapsam:** `reymen/` altındaki TÜM .py dosyaları

**Format:** Her .py dosyasının en üstüne Türkçe docstring ekle:

```python
# -*- coding: utf-8 -*-
"""
[modül_adı].py — ReYMeN [açıklama].

Ne işe yarar:
  - [madde 1]
  - [madde 2]

Nasıl kullanılır:
  >>> from reymen.[modül] import [fonksiyon]
  >>> [örnek]
"""
```

**Örnek docstring'ler:**
- `cost_tracker.py`: "API harcama takibi. Hangi modele ne kadar ödendiğini gösterir."
- `platform_adapter.py`: "Windows/WSL/Kali arasında köprü. Her platformda aynı kod çalışır."
- `kanban.py`: "Görev tahtası. Yapılacak işleri kartlarla takip eder."
- `a2a.py`: "Ajanlar arası mesajlaşma. Botlar birbirine mesaj atabilir."
- `motor.py`: "Ana motor. Tüm araçları yönetir ve çalıştırır."
- `conversation_loop.py`: "Sohbet döngüsü. Kullanıcı ile ajan arasındaki konuşmayı yönetir."

HEDEF: Her .py dosyasının ilk 10 satırında dosyanın ne işe yaradığı anlaşılsın.

### 3. Klasörler İçin Türkçe Açıklama
**Format:** Her önemli klasörde `__init__.py` yoksa ekle veya güncelle. Docstring olarak yaz.

```python
# -*- coding: utf-8 -*-
"""reymen/arac/ — ReYMeN araçları. Dosya, web, ses, görsel işleme, terminal ve daha fazlası."""
```

**Klasörler:**
- `reymen/arac/` — Araç modülleri
- `reymen/cereyan/` — Ana işlem döngüsü ve öğrenme
- `reymen/core/` — Çekirdek bileşenler
- `reymen/sistem/` — Sistem yönetimi
- `reymen/guvenlik/` — Güvenlik
- `reymen/hafiza/` — Hafıza sistemleri
- `reymen/scripts/` — Yardımcı script'ler
- `reymen/test/` — Testler
- `tests/` — Birim testler
- `dashboard/` — Web arayüzü
- `gateway/` — Mesajlaşma platformları

### 4. .github/workflows/ci.yml Varsa Açıklama Ekle
Yoksa sorun değil.

### 5. CONTRIBUTING.md Varsa Türkçe Güncelle
"Katkıda Bulunma Rehberi" olarak çevir.

## DOĞRULAMA
- README.md Türkçe mi?
- 3 farklı kişi okusa anlar mı?
- GitHub proje sayfasında göze hoş görünüyor mu?
- Her dosyanın ilk 10 satırında Türkçe açıklama var mı?

## ÖNCELİK
1. `README.md` — MUTLAKA yap (en önemlisi)
2. `reymen/core/*.py` — docstring ekle
3. `reymen/arac/*.py` — docstring ekle
4. `reymen/cereyan/*.py` — docstring ekle
5. `reymen/sistem/*.py` — docstring ekle
6. Klasör `__init__.py` — docstring ekle
7. Diğer dosyalar

## YASAKLAR
- Kod mantığını değiştirme (sadece yorum/docstring ekle)
- İngilizce docstring'leri silme (Türkçe'yi ÜSTÜNE ekle)
- .env, .git, __pycache__, venv içinde değişiklik yapma
- Testleri değiştirme
