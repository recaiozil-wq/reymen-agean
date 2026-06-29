## Karar #36: TUI Hermes Seviyesine Yükseltme

**Ne yapıldı:** `tui.py` sade metin → prompt_toolkit + Rich tabanlı etkileşimli TUI

**Neden:** Mevcut tui.py (314 satır) sadece statik renkli çıktı fonksiyonlarıydı. Gerçek bir Terminal UI (komut girişi, geçmiş, otomatik tamamlama, panel sistemi) yoktu.

**Alternatifler:**
1. Sadece Rich fonksiyonları bırakmak → etkileşimsiz
2. Ayrı cli_tui.py modülü → dağınıklık
3. Mevcut tui.py'yi komple yeniden yazmak → Seçilen yol

**Eklenenler:**
- ReYMeNTUI class: prompt_toolkit tabanlı REPL (otomatik tamamlama, geçmiş, klavye kısayolları)
- Rich çıktı fonksiyonları korundu (info, success, warning, error, panel, table)
- Motor tool'u: TUI_BASLAT
- Fallback: prompt_toolkit yoksa basit input() REPL
## Karar #31 — Bot Çince cevap fix + Ensemble akışı

**Ne yapıldı?**
1. Hermes reymen profili SOUL.md'sine Türkçe talimatı eklendi (başa)
2. telegram_bot/__init__.py AIAgentOrchestrator → ConversationLoop ensemble akışına çevrildi
3. conversation_loop.py'ye .env yükleme eklendi (API key okunamıyordu)
4. OnceHafiza'daki eski Çince kayıt (dunyada guncel haberler) temizlendi
5. Gateway restart yapıldı

**Neden?**
- SOUL.md'de Türkçe talimatı yoktu → DeepSeek Çince cevap veriyordu
- Bot main.py'deki ağır ReAct döngüsü yerine ensemble akışı kullanmalı (DeepSeek önce toolsuz cevaplasın, sonra puanla karşılaştır)
- conversation_loop.py'de load_dotenv yoktu → API key bulunamıyordu

**Alternatif?**
- conversation_loop.py'deki ensemble zaten yazılıydı, sadece bot yönlendirilmedi
- SOUL.md'yi proje köküne koymak da çözümdü ama profil override ediyor
