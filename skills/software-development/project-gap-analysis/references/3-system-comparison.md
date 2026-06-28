---
skill_id: 82b58a523111
usage_count: 1
last_used: 2026-06-16
---
# 3-Sistem Karşılaştırma Şablonu

Bir projeyi analiz ederken bazen kullanıcının elinde **birden fazla sistem** vardır
ve bunların birbiriyle ilişkisini anlamak gerekir.

## Tipik Senaryo

| # | Sistem | Kaynak | Ne işe yarar |
|---|--------|--------|-------------|
| 1 | **Nous ReYMeN Agent** | Resmi kurulum (`AppData/Local/hermes/`) | Profesyonel AI ajan. CLI, 100+ skill, MCP, gateway, çoklu provider. **Zaten çalışıyor.** |
| 2 | **Kullanıcının projesi** | Masaüstü / C:\ | Sıfırdan yazılmış mini ajan. ReYMeN'ten ilham almış ama farklı kod. |
| 3 | **Yardımcı araçlar** | Ayrı klasör (örn: C:\hermes_output) | Dashboard, Telegram bot, Notion entegrasyonu gibi ReYMeN'in etrafına yazılmış modüller. |

## Sık Yapılan Hatalar

1. **Sistem 2'yi Sistem 1 sanmak** — Kullanıcının kendi projesi (ReYMeN gibi) ReYMeN Agent ile aynı değildir. Aynı seviyeye getirmek aylarca sürer.
2. **Sistem 3'ü Sistem 1'in alternatifi sanmak** — ReYMeN_output, ReYMeN Agent'ın **yerine geçmez**, **etrafına eklenen araçlardır**.
3. **En kısa yolu atlamak** — Bazen en mantıklısı Sistem 2'yi geliştirmek değil, Sistem 1'i kullanıp Sistem 3'ü ona bağlamaktır.

## Doğru Yaklaşım

1. Önce hangi sistemlerin var olduğunu netleştir
2. Her birinin ne işe yaradığını belirle
3. Kullanıcının asıl hedefini anla:
   - "Kendi ajanımı yapmak istiyorum" → Sistem 2'yi büyüt
   - "ReYMeN gibi çalışan bir sistem istiyorum" → Sistem 1'i kullan
   - "ReYMeN'i telefondan/web'den yönetmek istiyorum" → Sistem 3'ü Sistem 1'e bağla
4. En kısa yolu öner, alternatifi de belirt
