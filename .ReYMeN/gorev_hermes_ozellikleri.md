# GÖREV: ReYMeN'e Hermes Özellikleri Ekleme

## NE
ReYMeN ajanına Hermes Agent'te olup eksik olan 3 temel özelliği ekle:
1. MCP client (mevcut MCP server'a client yeteneği)
2. Firecrawl web extract/search tool
3. OpenAI TTS/STT tool (mevcut araclar_ses.py'yi geliştir)

## NİYE
ReYMeN, Hermes'ten bu yönlerde geri. Ekleyince web bilgisi alabilir, ses çıktısı üretebilir ve harici MCP server'lara bağlanabilir.

## NASIL

### ADIM 1: MCP Client
- **Yer:** `reymen/arac/mcp_client_tool.py`
- **Ne yap:** config.yaml benzeri bir JSON'dan MCP server listesi oku (stdio/HTTP), her server'a bağlan, tool'larını keşfet, ReYMeN tool registry'sine kaydet
- **Kullanım:** `mcp_client_baglan("server_adi")` → tool'ları motor.py'ye kaydeder
- **Referans:** tools/mcp_tool.py (mevcut MCP server yapısı), reymen/arac/mcp_catalog.py
- **Kısıt:** aiohttp + asyncio kullan, threading ile ReYMeN loop'una entegre et

### ADIM 2: Firecrack Web Tool
- **Yer:** `reymen/arac/firecrawl_tool.py`
- **Ne yap:** Firecrawl API'sine bağlan (api.firecrawl.dev/v1), scrape ve search endpoint'lerini çağır
- **API:** 2 endpoint:
  - `POST /v1/scrape` → url ver, markdown içerik al
  - `POST /v1/search` → query ver, sonuçları al
- **API Key:** `FIRECRAWL_API_KEY` env var'dan oku (yoksa keyless mode dene)
- **Kullanım:** `firecrawl_web_extract(url)` → metin döndürür
- **Motor kayıt:** `motor_kaydet()` ile tool olarak ekle

### ADIM 3: TTS/STT Tool Geliştirme
- **Yer:** `reymen/arac/araclar_ses.py` (mevcut, pyttsx3 tabanlı)
- **Ne yap:** OpenAI TTS API + Whisper API desteği ekle
- **TTS:** `POST https://api.openai.com/v1/audio/speech` → ses dosyası oluştur
- **STT:** `POST https://api.openai.com/v1/audio/transcriptions` → sesi yazıya çevir
- **API Key:** `OPENAI_API_KEY` env var'dan oku
- **Mevcut pyttsx3 fonksiyonlarını koru, OpenAI'ı alternatif olarak ekle**
- **Motor kayıt:** mevcut kayıtlara ekle

## NE ZAMAN
Şu an. Cline Act modunda çalıştır.

## NEREDE
`C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan\`

## DOĞRULAMA
- Her 3 tool import edilebiliyor mu?
- motor.py'ye kaydedilebiliyor mu?
- Syntax hatası var mı? (compile kontrol)

## YASAKLAR
- Mevcut çalışan koda dokunma (enhancement, bug değil)
- Var olan tool'ların imzasını değiştirme
- .env dosyasına key yazma (kullanıcı kendi ekler)
- Test yazma (şimdilik, sadece tool'ları oluştur)
