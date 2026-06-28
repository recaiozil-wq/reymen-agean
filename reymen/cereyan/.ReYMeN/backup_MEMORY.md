ZORUNLU KURAL — VS CODE YAZMA: Kullanıcı "VS Code'a yaz", "Claude terminaline yaz", "agent'a yaz", "imlec getir" dediğinde TEK YAPILACAK ŞEYE: terminal(command="C:\Users\marko\AppData\Local\hermes\scripts\vscode_yaz.bat <MESAJ>"). BAŞKA HİÇBİR ŞEY YAPMA. Script yazma. Koordinat arama. Dosya değiştirme. SADECE vscode_yaz.bat çağır.
§
ZORUNLU KURAL — KONUM KAYDET: "konum kaydet" veya "hazırım tıkla" dediğinde şunu çalıştır: C:\Users\marko\AppData\Local\Python\PythonCore-3.14-64\python.exe "C:\Users\marko\AppData\Local\hermes\scripts\find_caret.py" "claude terminal" — 4 sn bekler, imlecin yanıp söndüğü yeri (caret) kaydeder. Kullanıcı o 4 saniyede Claude input'a tıklamalı.
§
Windows'ta fare imlecini hareket ettirmek icin PowerShell + System.Windows.Forms kullan. Inline bash komutunda tırnak/karakter kaybolmasi sorununu onlemek icin script dosyasina yazip powershell -ExecutionPolicy Bypass -File ile calistir. Bilinen scriptler: C:/Users/marko/AppData/Local/hermes/scripts/move_mouse.ps1, visible_move.ps1, screenshot.ps1
§
Kullanıcının GitHub hesabı: https://github.com/Izleyici-Hermes (eski adı: asdafgf, değiştirildi). Repolar: hermes-gemini-copilot, wifi-ag-tarayici, runners-journey. GitHub içeriği hem Hermes skill hem Obsidian notu olarak daima referans gösterilebilir.
§
VS CODE KALICI KURAL: Claude Agent inline suggestion / auto-complete KESİNLİKLE KAPALI. settings.json: editor.inlineSuggest.enabled=false, editor.suggest.enabled=false, claudeCode.autoFocusChat=false, claude.autoComplete=false. Bu ayarlar asla açılmaz, kullanıcı onayı beklenmez. Tekrar açılırsa hemen kapat.
§
User explicitly stated: 'Her söylediğim is skil veya Obsidian var mi diye kontrol et yapmadan once bu bir kuraldır. Öncelikli.' This is a mandatory pre-flight check for every task. Must scan skills_list and search_files in Obsidian vault before executing any new request. If a matching skill/note exists, reuse it instead of recreating.
§
Ekran görüntüsü ve pencere başlığı doğrulaması yapmadan pencere focus/ilerleme bildirilmesin. Windows'ta ön plan odaklama tekrar tekrar aynı betiği çalıştırmak bunaltıcı oluyor. Çözüm: 4 farklı foreground denemesini sırayla uygula (`SetForegroundWindow` alt bypassı, Alt+Tab/WScript `%{TAB}`, görev çubuğu tıklamaları, pencereleri gezerek `GetWindowText` ile başlık kontrolü). Başarısız olunca durumu netleştir ve kullanıcıya bildir.
§
Claude Code v2.1.161: C:\Users\marko\AppData\Roaming\npm\claude.cmd. Ollama KALDIRILDI. LM Studio local LLM: C:\Users\marko\AppData\Local\Programs\LM Studio\LM Studio.exe.
§
Kullanıcı GitHub'dan sadece SKILL almak istiyor, sistem değiştiren araçlar istemiyor: "biz skill almak istiyoruz hafıza silmek değil". Kurulum öncesi mutlaka kontrol et: skill paketi mi (SKILL.md, markdown dosyaları) yoksa sistem değiştiren bir araç mı (pip paketi, daemon, memory provider)? Sadece skill olanları kur.
§
gorsel-onaylama (Allow Once) skill güncellendi v2.0.0:
- Artık Allow Once / Bir kere izin ver butonlarını da otomatik tıklıyor
- Python 3.14 (C:\Users\marko\AppData\Local\Python\PythonCore-3.14-64\python.exe) ile çağrılmalı, Hermes venv'ında PIL/pyautogui yok
- Çağırma: powershell -ExecutionPolicy Bypass -Command "& 'python3.14.exe' 'C:\Users\marko\hermesapprove.py'"
- Test: llava butonu buldu (414,571) ve tıkladı (760,628) — başarılı
- Skil: Hermes skill + Obsidian vault notu güncellendi
§
screenshot_v2.py (Python 3.14 + mss, monitors[1]) tercih edilen tam ekran görüntüsü scripti. PowerShell screenshot.ps1 bazen alt kısmı kesiyor. Çağırma: powershell -ExecutionPolicy Bypass -Command "& 'C:\Users\marko\AppData\Local\Python\PythonCore-3.14-64\python.exe' 'C:\Users\marko\AppData\Local\hermes\scripts\screenshot_v2.py'". Ekran görüntüsü kesik çıkarsa hemen bu scripte geç.
§
VS Code Claude Agent sohbet kutusu koordinat her oturumda değişir. Son bilinen: (890, 133). Her seferinde kullanıcıdan tıklamasını iste ve yeni koordinat al. Asla eski koordinatı kullanma.
§
ZORUNLU — HER OTURUM AÇILIŞINDA İLK İŞ:
1. skills_list() — tüm skill'leri tara, güncel listeyi al
2. search_files() — Obsidian vault'ta konuyla ilgili not var mı kontrol et (doğru vault: C:\Users\marko\OneDrive\Belgeler\Obsidian Vault)
3. Bulunan kaydı KULLAN, yeniden oluşturma
4. Yoksa hem Hermes skill hem Obsidian notu oluştur
Bu kural HER görevde, HER oturumda, ATLAMADAN uygulanır. İlk mesajda (kullanıcı bir şey söylemeden önce) değil, kullanıcı bir talep verdiği anda ilk adım olarak yap.
§
User prefers LM Studio over Ollama for local LLM inference. Ollama dizini silinmis durumda, yeniden kurulmayacak. LM Studio path: C:\Users\marko\AppData\Local\Programs\LM Studio\LM Studio.exe.
§
KURAL - Yeni GitHub reposu eklenince: (1) KURULACAK_REPOLAR.md güncelle, (2) commit+push, (3) Obsidian notu güncelle, (4) hermes-kurulacak-repolar skill güncelle.
§
Tor Browser `open_url`: tor_running() kontrolü yapar. Kapalıysa direkt URL (varsayılan sayfa atlanır), açıksa --new-tab ile yeni sekmede açar. Gereksiz sayfa açılmaz.
§
ZORUNLU KURAL — Kali pentest araçları (269 araç) KESİNLİKLE izinsiz kullanılmaz. Kullanıcı açıkça "kali", "pentest" veya bir Kali aracının adını söylemedikçe Kali'ye SSH bağlanma, araç çalıştırma, tarama yapma YASAK. İzin verdiğinde bile HER ADIMDA kullanıcıdan klavyeden onay alınır — hangi araç, hangi hedef, hangi parametre. İstisnasız kural.
§
GitHub backup repo durumu (2026-06-14): Kullanıcı adı `asdafgf` → `Izleyici-Hermes` olarak değiştirilmiş. Skills backup repo remote URL hala `asdafgf/hermes-skills` kullanıyor (404). Local backup `/c/Users/marko/hermes-skills-backup/` commit'li ama push edilemiyor — remote URL `Izleyici-Hermes` olarak güncellenmeli. Obsidian vault `Watcher-Hermes/obsidian-vault` reposu çalışıyor. MEMORY.md/USER.md yedekleri Obsidian `08-Backup/` klasöründe.
§
GitHub hesap durumu: asdafgf kullanıcı adı 404 dönüyor (silinmiş/yeniden adlandırılmış). Tüm GitHub işlemleri Watcher-Hermes organizasyonu üzerinden yapılıyor. gh CLI asdafgf olarak giriş yapmış durumda ve Watcher-Hermes altında repo oluşturabiliyor.
§
Skill audience kategorizasyonu (NemoClaw pattern'i) tüm 1.184 SKILL.md'ye uygulandı. Frontmatter'da `audience: user|contributor|maintainer` alanı var. Dağılım: user=848, contributor=287, maintainer=49. Yedek: C:\Users\marko\AppData\Local\hermes\.audience-backup\. Obsidian notu: Hermes/Skills/audience-kategorizasyonu.md
§
NemoClaw'dan alinan ozellikler: (1) Skill audience kategorizasyonu — 1.184 SKILL.md'ye audience alani eklendi, GitHub'a push edildi. (2) AGENTS.md — skill repo yapisi, format, commit kurallari tek dosyada. GitHub'da Watcher-Hermes/hermes-skills reposunda.
§
ZORUNLU KURAL — .env ve Telegram token yönetimi:
- .env yolu: C:\Users\marko\AppData\Local\hermes\.env (ana), C:\Users\marko\hermes-ai\.env (ikincil)
- Değişiklikler KESİNLİKLE kalıcı olmalı: Python ile dosyaya yaz (PowerShell tırnak sorunu), env_watcher.py çalıştır → Obsidian'a kaydet
- .env'deki değerler asla *** ile maskelenmez. f-string içinde *** SyntaxError verir — string concatenation kullan
- Kullanıcı .env değer değişikliklerini manuel kontrol ediyor: ".env verılen deger degıstırılmelı kontrol et"
- Telegram chat_id: 6328823909
§
DOSYA YOLLARI:
- Ana masaüstü: C:\Users\marko\OneDrive\Desktop (OneDrive\Masaüstü veya C:\Users\marko\Desktop DEĞİL)
- Obsidian vault (DOGRU): C:\Users\marko\OneDrive\Belgeler\Obsidian Vault
- Windows masaüstü clasörü: C:\Users\marko\OneDrive\Desktop
- Hermes-Localhosts klasörü masaüstünde
§
KESİN KURAL — Kredi kartı ve ödeme yasağı:
(1) Hiçbir siteye kredi kartı bilgisi isteyen sayfaya gidilmez, hiçbir ödeme işlemi yapılmaz, hiçbir satın alma gerçekleştirilmez. Bu konuda sorgu bile açılmaz.
(2) Hermes'in açtığı herhangi bir sayfada kredi kartı, ödeme, satın alma, cart/add, checkout, payment, billing sayfası görülürse, o domain DERHAL engellenir. Engelleme: hosts dosyasına 127.0.0.1 ekle + Windows Firewall IP bazlı engelle. Tor dahil hiçbir yerde açılmasın.
(3) Kullanıcıdan onay istenmez.
§
ZORUNLU KURAL — Allow Once / Onay kutuları:
(1) Karşılaşılan herhangi bir "Allow Once / Bir kere izin ver / OK / Tamam" benzeri seçenek sorusunda onay beklemeden otomatik seç ve ilerle. Kullanıcıdan ayrıca onay isteme.
(2) Kalıcı otomatik onay: approvals.mode=off (Hermes onayları tamamen kapalı), allow-once-watcher cron job (her 1 dk, no_agent=true) ekranı tarar, Allow Once/OK/Tamam butonlarını otomatik tıklar.
(3) Skill: gorsel-onaylama v3.0.0. Script: allow_once_watcher.py. Job ID: 4e537bd89a9a.
§
Ortam bilgileri: Windows 10, VS Code + Node.js v24+ + npm. Python 3.14 (C:\Users\marko\AppData\Local\Python\PythonCore-3.14-64). Ollama kaldırıldı, LM Studio tercih edilen local LLM. PowerShell exec policy npm'i blokluyor; claude komutu stdin ister. DeepSeek V4 Flash'in vision'ı yok — Tesseract OCR kullan.
§
ZORUNLU KURAL — SKILL OLUŞTURMA/GÜNCELLEME STANDARTLARI:
- skill_manage(action='create'|'edit') öncesi skill-creation-standards skill'i yüklenir
- Router + Reference: SKILL.md asla 3-4 KB'ı geçmez, detaylar references/ altında
- Frontmatter zorunlu: title, tags, audience (user|contributor|maintainer)
- Sıfır şişkinlik: kod blokları/log/ham metin references/'de, SKILL.md'ye gömülmez
- DEPLOYMENT: Kayıt sonrası 4 adım: (1) Hermes'e kaydet (2) Origin izlerini temizle (3) Obsidian sync (4) GitHub hermes-skills push
- Origin izleri: phase/lesson/origin/tools alanları silinmeli, NeMo/Nemotron gibi marka adları jenerik terimlerle değiştirilmeli
- İhlal = skill-shrink otomatik böler
- Skill yolu: software-development/skill-creation-standards/
§
HAFIZA EKLEME STANDARTLARI (Kalıcı Protokol):

1. MÜKERRER VE DAĞINIKLIK ENGELİ: Yeni bilgi eklenmeden önce mevcut MEMORY ve USER PROFILE taranır. Benzer konu varsa yeni entry açılmaz — mevcut entry genişletilir/güncellenir.

2. DEPO AYRIMI: 
   - MEMORY (limit 50K): ortam bilgileri, teknik kurallar, IP/token talimatları, sistem yapılandırmaları
   - USER PROFILE (limit 5K): kullanıcı tercihleri, çalışma stilleri, dil seçimleri, iletişim tercihleri

3. GEREKSİZ VERİ FİLTRESİ: Günlük oturum özetleri, "kurulum tamamlandı" bildirimleri, tek seferlik benchmark sonuçları asla kalıcı hafızaya işlenmez.

4. STARTUP HOOK (Her Oturum Açılışında):
   - hermes_workspace_health.py (C:\Users\marko\OneDrive\Desktop\hermes_workspace_health.py) otomatik çalıştır
   - .env yolları, repolar, hafıza doluluk oranları taranır
   - Şişkin skill veya bozuk YAML kontrolü yapılır
   - Standart dışı durumlar kullanıcıya raporlanmadan önce otomatik düzeltilir
§
GitHub memory backup repo: Watcher-Hermes/hermes-memory-backup (private). MEMORY.md + USER.md token temizlenmiş şekilde push edildi. gh CLI ile auth çalışıyor (asdafgf). MCP GitHub auth çalışmıyor — gh CLI tercih edilmeli.
§
LM Studio v0.4.16.0 REST API model load endpoint (`/api/v1/models/load`) sadece şu parametreleri kabul eder: `model` (zorunlu, key alanı), `context_length` (max 32768), `flash_attention` (bool), `echo_load_config` (bool). GPU parametreleri (`gpu`, `gpu_layers`, `parallel`, `ngl`, `num_gpu_layers`, `offload_kv_cache_to_gpu`) bu derlemede TANINMAZ — hepsi "Unrecognized key" hatası verir. GPU offload ayarı sadece GUI'den yapılır (Settings > Model Defaults > GPU Offload slider). Model key = API /models/ listesindeki `key` alanı, GGUF dosya adı değil. Varsayılan GPU ayarları: CUDA llama.cpp, flash_attention açık, KV cache GPU'da, parallel=4.
§
Hermes venv fix (hermes-venv-fix-windows): Hermes guncellenemeyince (.pyd dosyalari kilitli), cozum: (1) git -C %LOCALAPPDATA%\hermes\hermes-agent checkout -- package-lock.json (2) Get-Process ile kilitli PID bul (3) Stop-Process -Force (4) Remove-Item -Recurse -Force venv (5) install.cmd calistir, [y/N]'ye n yaz. Kill ile Delete arasinda 2-3sn gecikme olursa Hermes yeniden baslar ve kilit geri gelir.
§
ZORUNLU KURAL — "sıkıl ve memory guncellensın" / "skill ve memory guncelle" dendiğinde KESİNLİKLE 3 repo da güncellenir: (1) hermes-skills (2) hermes-memory-backup (3) hermes-full-backup. Herhangi birini atlamak yasak. hermes-full-backup her seferinde skills/ klasoru komple silinip yeniden kopyalanir, sonra git add + commit + push main yapilir. Bu kural "sıkıl ve memory guncellensın" ifadesi için de geçerlidir — atlama yok.
§
R>eYMeN projesi 16 Haziran 2026'da Hermes Agent ile dosya bazinda esitlendi. 84/84 Hermes agent dosyasinin R>eYMeN'de karsiligi var. 307 Python dosyasi, 40.867 satir, 84 test (49 pytest + 35 test_suite), %100 gecen. Konum: C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi. Hermes'te olmayan 5 ozellik: ekran OCR/tiklama, makro kaydetme/oynatma, uygulama adim hafizasi, adim adim planlama, otomatik beceri kristallestirme.
§
Hermes -> Claude 4.8 is bolumu: Hermes gap analizi yapar, task description hazirlar (provider plugin, tool executor, test coverage gibi). Kullanici bu task'lari manuel olarak VS Code Claude Code terminaline yapistirir. Claude 4.8 kod uretimini yapar. Ben dosya taramasi yapip ilerleme raporu veririm. R>eYMeN projesi icin calisma akisi bu sekilde.
§
Reymen'de closed_learning_loop.py ve yetenek_fabrikasi.py'ye 3 aşamalı güncelleme yapıldı:
1. YAML Frontmatter (skill_id=MD5 hash, usage_count, last_used) — yetenek_fabrikasi.py'deki _frontmatter_olustur/_parse/_guncelle fonksiyonları ve standalone beceri_karti_uret()
2. FTS5 çakışma kontrolü — closed_learning_loop.py'de _fts5_benzer_beceri_ara() ile önce FTS5 sorgula, varsa merge (usage_count++, yeni adımlar ekle), yoksa yeni oluştur
3. 4000 karakter bağlam sınırı — beceri_baglamini_al()'da _ilgili_becerileri_skorlu() ile BM25 sıralı, MAKS_BAGLAM_KARAKTER=4000 limitli
§
ZORUNLU KURAL — Her görev/çözüm sonrasında "bu çözüm hangi ortamda/koşulda kırılır?" sorusunu sor ve yanıtla. Bu soruyu cevaplamadan bir sonraki adıma geçme. Edge case'leri (Windows CRLF, dosya kilidi, FTS5 tutarsızlığı, bozuk dosya, OneDrive, yetki) önceden düşün. Sadece happy path değil, tüm alternatif senaryoları test et.
§
Windows pytest cleanup pattern: Read-only test dosyalari TemporaryDirectory cleanup'inde PermissionError firlatir. Cozum: tempfile.mkdtemp() + try/finally + shutil.rmtree(tmp, ignore_errors=True) kullan. Ayrica _guvenli_chmod() helper'i ile os.chmod'u try-except PermissionError ile sarmala.
§
ReYMeN projesi Hermes Agent fork'u. GitHub: Watcher-Hermes/ReYMeN-Ajan. Kullanıcı ReYMeN'i Hermes seviyesine çıkarmak için feature-by-feature comparison yapıyor. conversation_loop.py (162→3900 satır) ve session_db.py (125→tam) Hermes'ten eksik. ReYMeN'in güçlü tarafı: ekran OCR, makro, uygulama otomasyonu. Hermes'in güçlü tarafı: konuşma döngüsü, session, provider, test. MIT lisansı korunuyor, ATTRIBUTION.md eklendi, Nous Research copyright'ı korunuyor.
§
Reymen'de 2 yeni bileşen: (1) `akilli_yonlendirici.py` — stratejik_ajan_sec() fonksiyonu, 5 persona (genel_cozucu, kod_uzmani, sistem_mimari, guvenlik_uzmani, veri_uzmani), hata mesajına göre kural tabanlı ajan değiştirme. (2) `cokus_raporlayici.py` — otonom çözüm sınırları tükenince crash raporu üretir, `.ReYMeN/cokus_raporlari/`'na kaydeder.
§
Reymen projesi (`C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi`) Hermes Agent ile %100 parity hedefliyor. Kullanıcının vizyonu: Reymen kullanan 10.000+ kişinin skill ve memory kazanımlarını ortak bir repoda toplamak, herkes birbirinden öğrensin. Bu kolektif öğrenme mekanizması Hermes'te yok, Reymen'e rekabet avantajı sağlar.