import os
import shutil
import re

# Sistem yolları tanımlaması
ENV_YOLU = r"C:\hermes\.env"
YEDEK_YOLU = r"C:\hermes\.env.backup"

def openrouter_guncelle():
    print("[SİSTEM] ReYMeN OpenRouter (DeepSeek) Konfigürasyon Aracı Başlatıldı.")

    # 1. Dosya Kontrolü ve Yedekleme
    if not os.path.exists(ENV_YOLU):
        print(f"[HATA] {ENV_YOLU} bulunamadı! Lütfen dizini kontrol edin.")
        return

    try:
        shutil.copy2(ENV_YOLU, YEDEK_YOLU)
        print(f"[ONAY] Mevcut ayarlar yedeklendi: {YEDEK_YOLU}")
    except Exception as e:
        print(f"[HATA] Yedekleme başarısız: {e}")
        return

    # 2. Kullanıcıdan OpenRouter API Anahtarı Alma
    print("\n[BİLGİ] https://openrouter.ai/workspaces/default/keys adresinden aldığınız")
    print("OpenRouter API anahtarınızı giriniz.")
    yeni_api_key = input("OpenRouter API Key (sk-or-...): ").strip()

    if not yeni_api_key.startswith("sk-or-"):
        print("[UYARI] Girilen anahtar standart OpenRouter formatına (sk-or-...) benzemiyor, yine de işleniyor.")

    # 3. OpenRouter Hedef Parametreleri
    yeni_ayarlar = {
        "OPENAI_API_BASE": "https://openrouter.ai/api/v1",
        "API_BASE": "https://openrouter.ai/api/v1",
        "BASE_URL": "https://openrouter.ai/api/v1",
        "MODEL_NAME": "deepseek/deepseek-chat",
        "MODEL": "deepseek/deepseek-chat",
        "OPENAI_API_KEY": yeni_api_key,
        "API_KEY": yeni_api_key,
        "ANTHROPIC_API_KEY": "", # Anthropic ile olası çakışmaları engelle
    }

    # 4. Dosyayı Okuma ve Değiştirme
    with open(ENV_YOLU, 'r', encoding='utf-8') as dosya:
        satirlar = dosya.readlines()

    yeni_satirlar = []
    degistirilen_anahtarlar = set()

    for satir in satirlar:
        satir_temiz = satir.strip()
        if not satir_temiz or satir_temiz.startswith('#'):
            yeni_satirlar.append(satir)
            continue

        # Anahtar=Değer eşleşmesini bul
        eslesme = re.match(r'^([A-Za-z0-9_]+)=(.*)$', satir_temiz)
        if eslesme:
            anahtar = eslesme.group(1)
            
            # Eğer anahtar güncellenecek listemizdeyse, yeni değeri yaz
            if anahtar in yeni_ayarlar:
                yeni_satirlar.append(f"{anahtar}={yeni_ayarlar[anahtar]}\n")
                degistirilen_anahtarlar.add(anahtar)
            else:
                yeni_satirlar.append(satir)
        else:
            yeni_satirlar.append(satir)

    # 5. Dosyada hiç olmayan ama gerekli olan OpenRouter anahtarlarını ekle
    eksik_anahtarlar = ["BASE_URL", "MODEL_NAME", "API_KEY"]
    for eksik in eksik_anahtarlar:
        if eksik not in degistirilen_anahtarlar:
            yeni_satirlar.append(f"{eksik}={yeni_ayarlar[eksik]}\n")

    # 6. Yeni Ayarları Kaydet
    with open(ENV_YOLU, 'w', encoding='utf-8') as dosya:
        dosya.writelines(yeni_satirlar)

    print("\n[BAŞARILI] Konfigürasyon OpenRouter ağına yönlendirildi ve DeepSeek modeli tanımlandı.")
    print("[SİSTEM] Terminalden ReYMeN ajanını yeniden başlatın.")

if __name__ == "__main__":
    openrouter_guncelle()
