"""🌐 ReYMeN Web UI — FastAPI + Jinja2 + HTMX + WebSocket yönetim paneli.

Kullanim:
    python -c "from reymen.web_ui import baslat; baslat()"
    # http://localhost:5000
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Response, Cookie, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# Web UI modülleri
from reymen.web_ui.auth import AuthConfig, UserManager, TokenManager, user_manager, token_manager
from reymen.web_ui.module_discovery import ModulTarayici, modul_kategorileri
from reymen.web_ui.process_manager import ProcessManager
from reymen.web_ui.log_stream import LogStreamer, log_kuyrugu_oku

logger = logging.getLogger(__name__)

PROJE_KOK = Path(__file__).resolve().parent.parent.parent
PLUGIN_DIZIN = PROJE_KOK / "reymen" / "sistem" / "plugins"
TEMPLATE_DIZIN = Path(__file__).parent / "templates"
STATIC_DIZIN = Path(__file__).parent / "static"
LOG_DOSYASI = PROJE_KOK / "reymen.log"

# ---------------------------------------------------------------------------
# Uygulama
# ---------------------------------------------------------------------------

app = FastAPI(title="ReYMeN Web UI", version="2.0.0")

# Jinja2 templates
templates = Jinja2Templates(directory=str(TEMPLATE_DIZIN))

# Static files
if STATIC_DIZIN.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIZIN)), name="static")

# Singleton servisler
modul_tarayici = ModulTarayici()
process_manager = ProcessManager()
log_streamer = LogStreamer(LOG_DOSYASI)

# ---------------------------------------------------------------------------
# Auth yardımcıları
# ---------------------------------------------------------------------------

def _get_user(token: Optional[str]) -> Optional[str]:
    """Cookie'den kullanıcı adını çöz."""
    if not token:
        return None
    return token_manager.verify(token)


def _require_auth(request: Request, token: Optional[str] = None) -> Optional[str]:
    """Auth kontrolü, yoksa None döndür."""
    user = _get_user(token)
    if not user:
        user = _get_user(request.cookies.get(token_manager.config.cookie_name))
    return user

# ---------------------------------------------------------------------------
# Middleware — auth kontrolü
# ---------------------------------------------------------------------------

AUTH_ATLANACAK = {"/login", "/static", "/ws/logs", "/api/health"}


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    if any(path.startswith(a) for a in AUTH_ATLANACAK):
        return await call_next(request)

    token = request.cookies.get(token_manager.config.cookie_name)
    user = _get_user(token)
    if not user:
        if path.startswith("/api/"):
            return JSONResponse({"hata": "Yetkisiz"}, status_code=401)
        return RedirectResponse(url="/login")
    
    request.state.user = user
    return await call_next(request)

# ---------------------------------------------------------------------------
# Routes — Sayfalar
# ---------------------------------------------------------------------------


@app.get("/login", response_class=HTMLResponse)
async def login_sayfasi(request: Request, hata: str = ""):
    return templates.TemplateResponse(
        request, "login.html", {"hata": hata}
    )


@app.post("/login")
async def login_post(request: Request):
    form = await request.form()
    username = form.get("username", "")
    password = form.get("password", "")

    if user_manager.verify(username, password):
        token = token_manager.create(username)
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(
            key=token_manager.config.cookie_name,
            value=token,
            max_age=token_manager.config.token_expiry,
            httponly=True,
            samesite="lax",
        )
        return response

    return templates.TemplateResponse(
        request, "login.html",
        {"hata": "Hatalı kullanıcı adı veya şifre"},
    )


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie(token_manager.config.cookie_name)
    return response


@app.get("/", response_class=HTMLResponse)
async def ana_sayfa(request: Request):
    return templates.TemplateResponse(
        request, "dashboard.html", {}
    )


@app.get("/plugins", response_class=HTMLResponse)
async def plugins_sayfasi(request: Request):
    return templates.TemplateResponse(
        request, "plugins.html", {}
    )


@app.get("/gateway", response_class=HTMLResponse)
async def gateway_sayfasi(request: Request):
    return templates.TemplateResponse(
        request, "gateway.html", {}
    )


@app.get("/logs", response_class=HTMLResponse)
async def logs_sayfasi(request: Request):
    return templates.TemplateResponse(
        request, "logs.html", {}
    )


@app.get("/users", response_class=HTMLResponse)
async def users_sayfasi(request: Request):
    return templates.TemplateResponse(
        request, "users.html", {}
    )


@app.get("/kalite", response_class=HTMLResponse)
async def kalite_sayfasi(request: Request):
    return templates.TemplateResponse(
        request, "quality.html", {}
    )


@app.get("/maliyet", response_class=HTMLResponse)
async def maliyet_sayfasi(request: Request):
    return templates.TemplateResponse(
        request, "cost.html", {}
    )


@app.get("/kanban", response_class=HTMLResponse)
async def kanban_sayfasi(request: Request):
    return templates.TemplateResponse(
        request, "kanban.html", {}
    )


@app.get("/sistem", response_class=HTMLResponse)
async def sistem_sayfasi(request: Request):
    return templates.TemplateResponse(
        request, "sistem.html", {}
    )

# ---------------------------------------------------------------------------
# API — Dashboard
# ---------------------------------------------------------------------------


@app.get("/api/durum")
async def api_durum(request: Request):
    """Sistem durumu HTML snippet."""
    satirlar = []
    
    # Process durumları
    tumu = process_manager.tumu()
    for p in tumu:
        dot = "🟢" if p.get("durum") == "calisiyor" else "🔴"
        satirlar.append(f"<div class='flex'><span>{dot} <b>{p['ad']}</b> — {p['durum']}</span></div>")

    if not tumu:
        satirlar.append("<div class='flex gri'>Aktif process yok</div>")

    # Log son satır
    son = log_streamer.son_satir
    satirlar.append(f"<div class='flex gri' style='margin-top:8px;font-size:0.8rem'>📋 {son[:100]}</div>")
    
    satirlar.append(f"<div class='flex gri' style='font-size:0.75rem'>Son: {datetime.now().strftime('%H:%M:%S')}</div>")
    
    return HTMLResponse(content="\n".join(satirlar))


@app.get("/api/moduller/ozet")
async def api_moduller_ozet():
    """Modül özet bilgisi."""
    try:
        moduller = modul_tarayici.tara()
        kategoriler = modul_kategorileri(moduller)
        toplam = len(moduller)
        yuklu = sum(1 for m in moduller if m.yuklu)
        kat_sayisi = len(kategoriler)
        return HTMLResponse(
            content=f"<div><b>{toplam}</b> modül (<b>{yuklu}</b> yüklü, <b>{kat_sayisi}</b> kategori)</div>"
        )
    except Exception as e:
        return HTMLResponse(content=f"<div class='tag-no'>Hata: {e}</div>")


@app.get("/api/log/son")
async def api_log_son():
    """Son log satırı."""
    son = log_streamer.son_satir
    if len(son) > 150:
        son = son[:150] + "..."
    return HTMLResponse(content=f"<pre class='gri' style='font-size:0.8rem'>{son}</pre>")


@app.get("/api/log/tail")
async def api_log_tail(n: int = 50):
    """Son N log satırı."""
    satirlar = log_streamer.tail(n)
    return HTMLResponse(
        content="<pre>" + "\n".join(satirlar) + "</pre>"
    )

# ---------------------------------------------------------------------------
# API — Pluginler
# ---------------------------------------------------------------------------


@app.get("/api/plugins")
async def api_plugins():
    """Plugin listesi HTML tablosu."""
    try:
        sys.path.insert(0, str(PROJE_KOK))
        from reymen.sistem.plugin_manager import PluginYoneticisi
        yonetici = PluginYoneticisi(str(PLUGIN_DIZIN))
        pluginler = yonetici.list_plugins()
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>Plugin sistemi yüklenemedi: {e}</div>")

    if not pluginler:
        return HTMLResponse(content="<div class='gri'>Henüz plugin yok</div>")

    satirlar = ["<table><tr><th>Plugin</th><th>Açıklama</th><th>Durum</th><th>İşlem</th></tr>"]
    for p in pluginler:
        ad = p.get("ad", p.get("name", "?"))
        aciklama = p.get("aciklama", p.get("description", ""))[:60]
        aktif = p.get("aktif", p.get("enabled", False))
        tag = "tag-yes" if aktif else "tag-no"
        durum_text = "Aktif" if aktif else "Pasif"
        toggle_action = "devre_disina_al" if aktif else "aktif_et"
        toggle_text = "🔴 Devre Dışı" if aktif else "🟢 Aktif Et"
        satirlar.append(
            f"<tr>"
            f"<td>{ad}</td>"
            f"<td class='gri'>{aciklama}</td>"
            f"<td><span class='tag {tag}'>{durum_text}</span></td>"
            f"<td><button class='btn btn-sm' hx-post='/api/plugins/{toggle_action}/{ad}' "
            f"hx-target='#plugin-sonuc'>{toggle_text}</button></td>"
            f"</tr>"
        )
    satirlar.append("</table>")
    return HTMLResponse(content="\n".join(satirlar))


@app.get("/api/plugins/ozet")
async def api_plugins_ozet():
    """Plugin özet bilgisi."""
    try:
        sys.path.insert(0, str(PROJE_KOK))
        from reymen.sistem.plugin_manager import PluginYoneticisi
        yonetici = PluginYoneticisi(str(PLUGIN_DIZIN))
        pluginler = yonetici.list_plugins()
        toplam = len(pluginler)
        aktif = sum(1 for p in pluginler if p.get("aktif", p.get("enabled", False)))
        return HTMLResponse(
            content=f"<div><b>{toplam}</b> plugin, <b>{aktif}</b> aktif</div>"
        )
    except Exception as e:
        return HTMLResponse(content=f"<div class='gri'>Plugin sistemi: {e}</div>")


@app.post("/api/plugins/aktif_et/{ad}")
async def api_plugin_aktif_et(ad: str):
    """Plugin'i aktif et."""
    try:
        sys.path.insert(0, str(PROJE_KOK))
        from reymen.sistem.plugin_manager import PluginYoneticisi
        yonetici = PluginYoneticisi(str(PLUGIN_DIZIN))
        yonetici.enable_plugin(ad)
        return HTMLResponse(content=f"<div class='alert alert-success'>✅ {ad} aktif edildi</div>")
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ {e}</div>")


@app.post("/api/plugins/devre_disina_al/{ad}")
async def api_plugin_devre_disina_al(ad: str):
    """Plugin'i devre dışı bırak."""
    try:
        sys.path.insert(0, str(PROJE_KOK))
        from reymen.sistem.plugin_manager import PluginYoneticisi
        yonetici = PluginYoneticisi(str(PLUGIN_DIZIN))
        yonetici.disable_plugin(ad)
        return HTMLResponse(content=f"<div class='alert alert-success'>✅ {ad} devre dışı</div>")
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ {e}</div>")


@app.get("/api/plugins/tazele")
async def api_plugins_tazele():
    """Plugin listesini yenile."""
    return await api_plugins()

# ---------------------------------------------------------------------------
# API — Kullanıcı Yönetimi
# ---------------------------------------------------------------------------


@app.get("/api/users")
async def api_users():
    """Kullanıcı listesi HTML tablosu."""
    kullanicilar = user_manager.list_users()
    satirlar = ["<table><tr><th>#</th><th>Kullanıcı</th><th>İşlem</th></tr>"]
    for i, k in enumerate(kullanicilar, 1):
        satirlar.append(
            f"<tr><td>{i}</td><td>{k}</td>"
            f"<td><button class='btn btn-sm btn-danger' "
            f"hx-post='/api/users/sil/{k}' hx-target='#sonuc' "
            f"hx-confirm='{k} silinsin mi?'>🗑 Sil</button></td></tr>"
        )
    satirlar.append("</table>")
    return HTMLResponse(content="\n".join(satirlar))


@app.post("/api/users/ekle")
async def api_users_ekle(request: Request):
    """Yeni kullanıcı ekle."""
    form = await request.form()
    username = form.get("username", "").strip()
    password = form.get("password", "").strip()
    if not username or not password:
        return HTMLResponse(content="<div class='alert alert-error'>❌ Boş alan bırakma</div>")
    if len(password) < 4:
        return HTMLResponse(content="<div class='alert alert-error'>❌ Şifre en az 4 karakter</div>")
    try:
        user_manager.set_password(username, password)
        return HTMLResponse(content=f"<div class='alert alert-success'>✅ {username} eklendi</div>")
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ {e}</div>")


@app.post("/api/users/sifre")
async def api_users_sifre(request: Request):
    """Şifre değiştir."""
    form = await request.form()
    username = form.get("username", "").strip()
    password = form.get("password", "").strip()
    if not username or not password:
        return HTMLResponse(content="<div class='alert alert-error'>❌ Boş alan bırakma</div>")
    if username not in user_manager.list_users():
        return HTMLResponse(content="<div class='alert alert-error'>❌ Kullanıcı bulunamadı</div>")
    try:
        user_manager.set_password(username, password)
        return HTMLResponse(content=f"<div class='alert alert-success'>✅ {username} şifresi güncellendi</div>")
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ {e}</div>")


@app.post("/api/users/sil/{username}")
async def api_users_sil(username: str):
    """Kullanıcı sil."""
    try:
        dosya = user_manager.config.users_file
        if not dosya.exists():
            return HTMLResponse(content="<div class='alert alert-error'>❌ users.json yok</div>")
        import json
        users = json.loads(dosya.read_text(encoding="utf-8"))
        if username in users:
            del users[username]
            dosya.write_text(json.dumps(users, indent=2, ensure_ascii=False), encoding="utf-8")
            user_manager._users = users
            return HTMLResponse(content=f"<div class='alert alert-success'>✅ {username} silindi</div>")
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ {username} bulunamadı</div>")
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ {e}</div>")

# ---------------------------------------------------------------------------
# API — Gateway
# ---------------------------------------------------------------------------


@app.get("/api/gateway")
async def api_gateway():
    """Gateway servis durumları."""
    tumu = process_manager.tumu()
    if not tumu:
        return HTMLResponse(content="<div class='gri'>Aktif gateway servisi yok</div>")

    satirlar = ["<table><tr><th>Servis</th><th>Durum</th><th>PID</th><th>Port</th></tr>"]
    for p in tumu:
        durum = p.get("durum", "?")
        dot = "🟢" if durum == "calisiyor" else "🔴"
        satirlar.append(
            f"<tr><td>{p.get('ad', '?')}</td>"
            f"<td>{dot} {durum}</td>"
            f"<td>{p.get('pid', '-') or '-'}</td>"
            f"<td>{p.get('port', '-')}</td></tr>"
        )
    satirlar.append("</table>")
    return HTMLResponse(content="\n".join(satirlar))


@app.get("/api/gateway/ozet")
async def api_gateway_ozet():
    """Gateway özet."""
    tumu = process_manager.tumu()
    calisan = sum(1 for p in tumu if p.get("durum") == "calisiyor")
    return HTMLResponse(
        content=f"<div><b>{calisan}</b>/<b>{len(tumu)}</b> servis çalışıyor</div>"
    )


@app.get("/api/gateway/ayarlar")
async def api_gateway_ayarlar():
    """Gateway ayarları."""
    env_yolu = PROJE_KOK / ".env"
    ayarlar = {}
    if env_yolu.exists():
        with open(str(env_yolu), encoding="utf-8") as f:
            for satir in f:
                satir = satir.strip()
                if satir and not satir.startswith("#") and "=" in satir:
                    k, v = satir.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "OPENAI_API_KEY", "DEEPSEEK_API_KEY"):
                        # Maskele
                        ayarlar[k] = v[:6] + "..." + v[-4:] if len(v) > 12 else "***"
                    elif k in ("WEB_UI_SECRET",):
                        ayarlar[k] = "***"
                    else:
                        ayarlar[k] = v

    if not ayarlar:
        return HTMLResponse(content="<div class='gri'>.env dosyası bulunamadı</div>")

    satirlar = ["<table><tr><th>Anahtar</th><th>Değer</th></tr>"]
    for k, v in ayarlar.items():
        satirlar.append(f"<tr><td>{k}</td><td class='gri'>{v}</td></tr>")
    satirlar.append("</table>")
    return HTMLResponse(content="\n".join(satirlar))


@app.post("/api/gateway/restart")
async def api_gateway_restart():
    """Gateway yeniden başlat."""
    try:
        process_manager.durdur("gateway")
        # Kısa bekle
        await asyncio.sleep(0.5)
        ok = process_manager.baslat(
            "gateway",
            [sys.executable, "-m", "reymen.web_ui"],
            port=5000,
        )
        if ok:
            return HTMLResponse(content="<div class='alert alert-success'>✅ Gateway yeniden başlatıldı</div>")
        return HTMLResponse(content="<div class='alert alert-error'>❌ Başlatılamadı</div>")
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ Hata: {e}</div>")


@app.post("/api/gateway/baslat")
async def api_gateway_baslat():
    """Gateway başlat."""
    try:
        durum = process_manager.durum("gateway")
        if durum.get("durum") == "calisiyor":
            return HTMLResponse(content="<div class='alert alert-success'>✅ Zaten çalışıyor</div>")
        ok = process_manager.baslat(
            "gateway",
            [sys.executable, "-m", "reymen.web_ui"],
            port=5000,
        )
        if ok:
            return HTMLResponse(content="<div class='alert alert-success'>✅ Gateway başlatıldı</div>")
        return HTMLResponse(content="<div class='alert alert-error'>❌ Başlatılamadı</div>")
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ Hata: {e}</div>")


@app.post("/api/gateway/durdur")
async def api_gateway_durdur():
    """Gateway durdur."""
    try:
        process_manager.durdur("gateway", force=True)
        return HTMLResponse(content="<div class='alert alert-success'>✅ Gateway durduruldu</div>")
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ Hata: {e}</div>")


@app.post("/api/bot/test")
async def api_bot_test():
    """Bot bağlantı testi."""
    try:
        import urllib.request
        import urllib.error
        env_yolu = PROJE_KOK / ".env"
        token = ""
        if env_yolu.exists():
            for satir in env_yolu.read_text(encoding="utf-8").splitlines():
                if satir.strip().startswith("TELEGRAM_BOT_TOKEN"):
                    token = satir.split("=", 1)[1].strip().strip('"').strip("'")

        if not token:
            return HTMLResponse(content="<div class='tag-no'>❌ TELEGRAM_BOT_TOKEN yok</div>")

        url = f"https://api.telegram.org/bot{token}/getMe"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get("ok"):
                bot_info = data.get("result", {})
                return HTMLResponse(
                    content=f"<div class='alert alert-success'>✅ @{bot_info.get('username', '?')} bağlantı başarılı</div>"
                )
        return HTMLResponse(content="<div class='alert alert-error'>❌ API hatası</div>")
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ Hata: {e}</div>")


# ---------------------------------------------------------------------------
# API — Telegram Özel
# ---------------------------------------------------------------------------


@app.get("/api/gateway/telegram")
async def api_gateway_telegram():
    """Telegram bot durumu + bilgisi."""
    # Token var mı?
    token = _env_oku("TELEGRAM_BOT_TOKEN", "")
    chat_id = _env_oku("TELEGRAM_CHAT_ID", "")

    if not token:
        return HTMLResponse(content="<div class='alert alert-error'>❌ TELEGRAM_BOT_TOKEN yok</div>")

    # Bot bilgisi al (getMe)
    bot_username = "?"
    bot_online = False
    try:
        req = urllib.request.Request(f"https://api.telegram.org/bot{token}/getMe")
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
            if data.get("ok"):
                bot_username = data["result"].get("username", "?")
                bot_online = True
    except Exception:
        bot_online = False

    # Process kontrol
    durum = process_manager.durum("telegram_bot")

    satirlar = [
        f"<div class='flex'><span>{'🟢' if bot_online else '🔴'} <b>@{bot_username}</b></span></div>",
        f"<div class='flex gri' style='font-size:0.85rem'>Token: {'✅' if token else '❌'} mevcut</div>",
    ]
    if chat_id:
        satirlar.append(f"<div class='flex gri' style='font-size:0.85rem'>Hedef Chat ID: {chat_id}</div>")
    else:
        satirlar.append("<div class='flex gri' style='font-size:0.85rem'>Hedef Chat ID: Herkese açık</div>")

    bot_durum = durum.get("durum", "durduruldu")
    dot = "🟢" if bot_durum == "calisiyor" else "🔴"
    satirlar.append(f"<div class='flex' style='margin-top:8px'><span>{dot} Bot process: {bot_durum}</span></div>")

    return HTMLResponse(content="\n".join(satirlar))


@app.post("/api/gateway/telegram/baslat")
async def api_gateway_telegram_baslat():
    """Telegram bot process'ini başlat."""
    tg_yolu = PROJE_KOK / "reymen" / "ag" / "telegram_bot.py"
    if not tg_yolu.exists():
        return HTMLResponse(content="<div class='alert alert-error'>❌ telegram_bot.py bulunamadı</div>")

    ok = process_manager.baslat(
        "telegram_bot",
        [sys.executable, str(tg_yolu)],
        port=0,  # Telegram botu için port gerekmez
        log_dosyasi=PROJE_KOK / "logs" / "telegram_bot.log",
    )
    if ok:
        return HTMLResponse(content="<div class='alert alert-success'>✅ Telegram bot başlatıldı</div>")
    return HTMLResponse(content="<div class='alert alert-error'>❌ Başlatılamadı</div>")


@app.post("/api/gateway/telegram/durdur")
async def api_gateway_telegram_durdur():
    """Telegram bot process'ini durdur."""
    process_manager.durdur("telegram_bot", force=True)
    return HTMLResponse(content="<div class='alert alert-success'>✅ Telegram bot durduruldu</div>")


@app.post("/api/gateway/telegram/mesaj")
async def api_gateway_telegram_mesaj(request: Request):
    """Telegram üzerinden mesaj gönder."""
    form = await request.form()
    metin = form.get("metin", "").strip()
    hedef = form.get("chat_id", "").strip()

    if not metin:
        return HTMLResponse(content="<div class='alert alert-error'>❌ Mesaj boş</div>")

    token = _env_oku("TELEGRAM_BOT_TOKEN", "")
    if not token:
        return HTMLResponse(content="<div class='alert alert-error'>❌ TELEGRAM_BOT_TOKEN yok</div>")

    chat_id = hedef or _env_oku("TELEGRAM_CHAT_ID", "")
    if not chat_id:
        return HTMLResponse(content="<div class='alert alert-error'>❌ Hedef Chat ID yok</div>")

    try:
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": metin}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data, method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            resp = json.loads(r.read())
            if resp.get("ok"):
                return HTMLResponse(content=f"<div class='alert alert-success'>✅ Mesaj gönderildi → {chat_id}</div>")
            return HTMLResponse(content=f"<div class='alert alert-error'>❌ Telegram hatası: {resp.get('description', '?')}</div>")
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ Hata: {e}</div>")


@app.post("/api/gateway/test-mesaj")
async def api_gateway_test_mesaj():
    """Varsayılan chat_id'e test mesajı gönder."""
    token = _env_oku("TELEGRAM_BOT_TOKEN", "")
    chat_id = _env_oku("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return HTMLResponse(content="<div class='alert alert-error'>❌ Token veya Chat ID yok</div>")

    try:
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": "🧪 Test mesajı — ReYMeN Web UI",
            "parse_mode": "HTML",
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data, method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return HTMLResponse(content="<div class='alert alert-success'>✅ Test mesajı gönderildi 📨</div>")
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ Hata: {e}</div>")


# _env_oku helper
def _env_oku(anahtar: str, varsayilan: str = "") -> str:
    """.env dosyasından değer oku."""
    env_yolu = PROJE_KOK / ".env"
    if not env_yolu.exists():
        return varsayilan
    for satir in env_yolu.read_text(encoding="utf-8").splitlines():
        satir = satir.strip()
        if satir.startswith("#") or "=" not in satir:
            continue
        k, v = satir.split("=", 1)
        if k.strip() == anahtar:
            return v.strip().strip('"').strip("'")
    # Hermes env'de de ara
    hermes_env = Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "kiral38" / ".env"
    if hermes_env.exists():
        for satir in hermes_env.read_text(encoding="utf-8").splitlines():
            satir = satir.strip()
            if satir.startswith("#") or "=" not in satir:
                continue
            k, v = satir.split("=", 1)
            if k.strip() == anahtar:
                return v.strip().strip('"').strip("'")
    return varsayilan


# ---------------------------------------------------------------------------
# API — Discord
# ---------------------------------------------------------------------------


@app.get("/api/gateway/discord")
async def api_gateway_discord():
    """Discord bot durumu + bilgisi."""
    token = _env_oku("DISCORD_BOT_TOKEN", "")

    if not token:
        return HTMLResponse(content="<div class='alert alert-error'>❌ DISCORD_BOT_TOKEN yok</div>")

    # Token doğrulama (Discord API /users/@me)
    bot_username = "?"
    bot_online = False
    try:
        req = urllib.request.Request(
            "https://discord.com/api/v10/users/@me",
            headers={"Authorization": f"Bot {token}"},
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
            bot_username = data.get("username", "?") + "#" + data.get("discriminator", "0")
            bot_online = True
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return HTMLResponse(content="<div class='alert alert-error'>❌ Token geçersiz (401)</div>")
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ Discord API: {e.code}</div>")
    except Exception:
        bot_online = False

    # Process kontrol
    durum = process_manager.durum("discord_bot")
    bot_durum = durum.get("durum", "durduruldu")

    satirlar = [
        f"<div class='flex'><span>{'🟢' if bot_online else '🔴'} <b>{bot_username}</b></span></div>",
        f"<div class='flex gri' style='font-size:0.85rem'>Token: {'✅' if token else '❌'} mevcut</div>",
    ]

    dot = "🟢" if bot_durum == "calisiyor" else "🔴"
    satirlar.append(f"<div class='flex' style='margin-top:8px'><span>{dot} Bot process: {bot_durum}</span></div>")

    return HTMLResponse(content="\n".join(satirlar))


@app.post("/api/gateway/discord/baslat")
async def api_gateway_discord_baslat():
    """Discord bot process'ini başlat."""
    bot_yolu = PROJE_KOK / "reymen" / "ag" / "discord_bot.py"
    if not bot_yolu.exists():
        return HTMLResponse(content="<div class='alert alert-error'>❌ discord_bot.py bulunamadı</div>")

    ok = process_manager.baslat(
        "discord_bot",
        [sys.executable, str(bot_yolu)],
        port=0,
        log_dosyasi=PROJE_KOK / "logs" / "discord_bot.log",
    )
    if ok:
        return HTMLResponse(content="<div class='alert alert-success'>✅ Discord bot başlatıldı</div>")
    return HTMLResponse(content="<div class='alert alert-error'>❌ Başlatılamadı</div>")


@app.post("/api/gateway/discord/durdur")
async def api_gateway_discord_durdur():
    """Discord bot process'ini durdur."""
    process_manager.durdur("discord_bot", force=True)
    return HTMLResponse(content="<div class='alert alert-success'>✅ Discord bot durduruldu</div>")


@app.post("/api/gateway/discord/mesaj")
async def api_gateway_discord_mesaj(request: Request):
    """Discord kanalına REST ile mesaj gönder."""
    form = await request.form()
    kanal_id = form.get("kanal_id", "").strip()
    metin = form.get("metin", "").strip()

    if not metin or not kanal_id:
        return HTMLResponse(content="<div class='alert alert-error'>❌ Kanal ID ve mesaj gerekli</div>")

    token = _env_oku("DISCORD_BOT_TOKEN", "")
    if not token:
        return HTMLResponse(content="<div class='alert alert-error'>❌ DISCORD_BOT_TOKEN yok</div>")

    try:
        data = json.dumps({"content": metin}).encode()
        req = urllib.request.Request(
            f"https://discord.com/api/v10/channels/{kanal_id}/messages",
            data=data, method="POST",
            headers={
                "Authorization": f"Bot {token}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            resp = json.loads(r.read())
            return HTMLResponse(
                content=f"<div class='alert alert-success'>✅ Mesaj gönderildi → {kanal_id}</div>"
            )
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ Discord {e.code}: {body}</div>")
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ Hata: {e}</div>")


# ---------------------------------------------------------------------------
# API — SMS (Twilio)
# ---------------------------------------------------------------------------

from reymen.web_ui.sms import sms_gonder, bakiye_kontrol


@app.get("/api/gateway/sms")
async def api_gateway_sms():
    """SMS durumu — Twilio hesap bilgisi."""
    sid = _env_oku("TWILIO_ACCOUNT_SID", "")
    from_num = _env_oku("TWILIO_FROM_NUMBER", "")

    if not sid and not from_num:
        return HTMLResponse(
            content="<div class='alert alert-error'>❌ Twilio ayarları yok</div>"
        )

    satirlar = [
        f"<div class='flex gri' style='font-size:0.85rem'>Account SID: {'✅' if sid else '❌'}</div>",
        f"<div class='flex gri' style='font-size:0.85rem'>Gönderen No: {from_num or '❌'}</div>",
    ]

    # Bakiye kontrol (opsiyonel)
    if sid:
        try:
            bakiye = bakiye_kontrol()
            if bakiye.get("ok"):
                satirlar.append(
                    f"<div class='flex' style='margin-top:8px'>"
                    f"🟢 Hesap: <b>{bakiye.get('friendly_name', '?')}</b></div>"
                )
        except Exception:
            pass

    return HTMLResponse(content="\n".join(satirlar))


@app.post("/api/gateway/sms/gonder")
async def api_gateway_sms_gonder(request: Request):
    """SMS gönder."""
    form = await request.form()
    telefon = form.get("telefon", "").strip()
    mesaj = form.get("mesaj", "").strip()

    if not telefon or not mesaj:
        return HTMLResponse(content="<div class='alert alert-error'>❌ Telefon ve mesaj gerekli</div>")

    # Telefon numarası temizleme
    telefon = telefon.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not telefon.startswith("+"):
        telefon = "+" + telefon

    try:
        sonuc = sms_gonder(telefon, mesaj)
        if sonuc.get("ok"):
            return HTMLResponse(
                content=f"<div class='alert alert-success'>✅ SMS gönderildi → {telefon} (ID: {sonuc.get('mesaj_id', '?')[:12]}...)</div>"
            )
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ {sonuc.get('hata', '?')}</div>")
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>❌ Hata: {e}</div>")


# ---------------------------------------------------------------------------
# API — Plugin JSON
# ---------------------------------------------------------------------------


@app.get("/api/plugin/liste")
async def api_plugin_liste():
    """Plugin listesi JSON."""
    try:
        sys.path.insert(0, str(PROJE_KOK))
        from reymen.sistem.plugin_manager import PluginYoneticisi
        yonetici = PluginYoneticisi(str(PLUGIN_DIZIN))
        pluginler = yonetici.list_plugins()
        istatistik = yonetici.plugin_sayisi()
        if not pluginler:
            return HTMLResponse(content="<div class='gri'>Henüz plugin yok</div>")
        satirlar = [
            "<table><tr><th>#</th><th>Plugin</th><th>Tür</th><th>Versiyon</th><th>Durum</th><th>Araç</th><th>Açıklama</th></tr>"
        ]
        for i, p in enumerate(pluginler, 1):
            ad = p.get("name", "?")
            tur = p.get("kind", "?")
            versiyon = p.get("version", "")
            aktif = p.get("enabled", False)
            tag = "tag-yes" if aktif else "tag-no"
            durum_text = "Aktif" if aktif else "Pasif"
            arac_sayisi = p.get("tools", 0)
            aciklama = (p.get("description", "") or "")[:60]
            satirlar.append(
                f"<tr><td>{i}</td><td><b>{ad}</b></td>"
                f"<td><span class='tag tag-info'>{tur}</span></td>"
                f"<td>{versiyon}</td>"
                f"<td><span class='tag {tag}'>{durum_text}</span></td>"
                f"<td>{arac_sayisi}</td>"
                f"<td class='gri'>{aciklama}</td></tr>"
            )
        satirlar.append("</table>")
        satirlar.append(
            f"<div class='gri' style='margin-top:8px'>"
            f"Toplam: {istatistik.get('toplam', 0)} plugin, "
            f"{istatistik.get('aktif', 0)} aktif, "
            f"{istatistik.get('devre_disi', 0)} pasif"
            f"</div>"
        )
        return HTMLResponse(content="\n".join(satirlar))
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>Plugin listesi hatası: {e}</div>")


@app.get("/api/plugin/bilgi/{ad}")
async def api_plugin_bilgi(ad: str):
    """Plugin detay bilgisi."""
    try:
        sys.path.insert(0, str(PROJE_KOK))
        from reymen.sistem.plugin_manager import PluginYoneticisi
        yonetici = PluginYoneticisi(str(PLUGIN_DIZIN))
        bilgi = yonetici.plugin_info(ad)
        satirlar = [
            f"<div class='kart'><table>"
            f"<tr><td>Adı</td><td><b>{bilgi.get('adi', '?')}</b></td></tr>"
            f"<tr><td>Klasör</td><td>{bilgi.get('klasor', '?')}</td></tr>"
            f"<tr><td>Versiyon</td><td>{bilgi.get('versiyon', '-')}</td></tr>"
            f"<tr><td>Tür</td><td><span class='tag tag-info'>{bilgi.get('kind', '?')}</span></td></tr>"
            f"<tr><td>Açıklama</td><td>{bilgi.get('aciklama', '-')}</td></tr>"
            f"<tr><td>Yazar</td><td>{bilgi.get('yazar', '-')}</td></tr>"
            f"<tr><td>Durum</td><td><span class='tag {'tag-yes' if bilgi.get('aktif') else 'tag-no'}'>{'Aktif' if bilgi.get('aktif') else 'Pasif'}</span></td></tr>"
            f"<tr><td>Yüklü</td><td>{'✅' if bilgi.get('yuklu') else '❌'}</td></tr>"
            f"<tr><td>Klasör Var</td><td>{'✅' if bilgi.get('klasor_var') else '❌'}</td></tr>"
            f"<tr><td>Araç Sayısı</td><td>{len(bilgi.get('araclar', []))}</td></tr>"
            f"</table></div>"
        ]
        return HTMLResponse(content="\n".join(satirlar))
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>Plugin bilgisi alınamadı: {e}</div>")


# ---------------------------------------------------------------------------
# API — Kalite / Self-Improve
# ---------------------------------------------------------------------------


@app.get("/api/kalite")
async def api_kalite():
    """Self-improve trend raporu HTML."""
    try:
        from reymen.self_improve import report as si_report
        rapor = si_report()
        ortalama = rapor.get("ortalama_skor", 0)
        gecme = rapor.get("gecme_orani", 0)
        toplam = rapor.get("toplam_adim", 0)
        dusuk = rapor.get("dusuk_kalite", 0)
        notlar = rapor.get("not_dagilimi", {})
        haftalik = rapor.get("haftalik_ilerleme", [])
        hedefler = rapor.get("aktif_hedefler", [])
        not_str = " ".join(f"<span class='tag tag-info'>{k}: {v}</span>" for k, v in sorted(notlar.items()))
        hafta_str = ""
        for h in haftalik:
            bar = "█" * max(1, int(h["ortalama"] * 20))
            hafta_str += f"<div>{h['hafta']}: {bar} <span class='gri'>({h['ortalama']:.2f}, {h['adim']} adım)</span></div>"
        hedef_str = ""
        if hedefler:
            for h in hedefler[:5]:
                hedef_str += f"<div>🎯 {h.get('metric_name', '?')}: {h.get('current_val', 0):.1f} → {h.get('target_val', 0):.1f}</div>"
        return HTMLResponse(
            content=f"<div class='flex' style='flex-direction:column;gap:8px'>"
            f"<div><b>Ortalama Skor:</b> {ortalama:.3f}</div>"
            f"<div><b>Geçme Oranı:</b> %{gecme*100:.1f}</div>"
            f"<div><b>Toplam Adım:</b> {toplam} (<span class='tag-no'>{dusuk} düşük</span>)</div>"
            f"<div><b>Not Dağılımı:</b> {not_str}</div>"
            f"<hr><div><b>Haftalık İlerleme:</b></div>{hafta_str}"
            f"{'<hr><div><b>Aktif Hedefler:</b></div>' + hedef_str if hedef_str else ''}"
            f"</div>"
        )
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>Kalite raporu: {e}</div>")


@app.get("/api/kalite/analiz")
async def api_kalite_analiz():
    """Kod kalite analizi HTML."""
    try:
        from reymen.self_improve import kod_kalite_analizi
        sonuc = kod_kalite_analizi()
        satirlar = [
            f"<table>"
            f"<tr><td>Toplam Dosya</td><td><b>{sonuc.get('toplam_dosya', 0)}</b></td></tr>"
            f"<tr><td>Toplam Satır</td><td><b>{sonuc.get('toplam_satir', 0):,}</b></td></tr>"
            f"<tr><td>Sınıf Sayısı</td><td>{sonuc.get('sinif_sayisi', 0)}</td></tr>"
            f"<tr><td>Fonksiyon Sayısı</td><td>{sonuc.get('fonk_sayisi', 0)}</td></tr>"
            f"<tr><td>Test Dosyası</td><td>{sonuc.get('test_dosyasi', 0)}</td></tr>"
            f"<tr><td>Test Satır Oranı</td><td>%{sonuc.get('test_orani', 0)*100:.1f}</td></tr>"
            f"<tr><td>📝 TODO</td><td><span class='tag tag-info'>{sonuc.get('todo', 0)}</span></td></tr>"
            f"<tr><td>⚠️ FIXME</td><td><span class='tag tag-no'>{sonuc.get('fixme', 0)}</span></td></tr>"
            f"<tr><td>🔴 except:pass</td><td><span class='tag tag-no'>{sonuc.get('except_pass', 0)}</span></td></tr>"
            f"</table>"
        ]
        return HTMLResponse(content="\n".join(satirlar))
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>Kod kalite analizi: {e}</div>")


@app.get("/api/kalite/ozet")
async def api_kalite_ozet():
    """Kalite özet bilgisi (dashboard)."""
    try:
        from reymen.self_improve import report as si_report
        rapor = si_report()
        ortalama = rapor.get("ortalama_skor", 0)
        toplam = rapor.get("toplam_adim", 0)
        not_str = " ".join(
            f"<span class='tag tag-info'>{k}: {v}</span>"
            for k, v in sorted(rapor.get("not_dagilimi", {}).items())
        )
        return HTMLResponse(
            content=f"<div><b>{toplam}</b> adım, skor: <b>{ortalama:.3f}</b><br>{not_str}</div>"
        )
    except Exception as e:
        return HTMLResponse(content=f"<div class='gri'>Kalite: {e}</div>")


# ---------------------------------------------------------------------------
# API — Maliyet / Cost Tracker
# ---------------------------------------------------------------------------


@app.get("/api/maliyet")
async def api_maliyet():
    """Cost tracker özet HTML."""
    try:
        from reymen.cost_tracker import summary as ct_summary
        ozet = ct_summary()
        toplam_maliyet = ozet.get("total_cost_usd", 0)
        toplam_cagri = ozet.get("total_calls", 0)
        toplam_token = ozet.get("total_tokens", 0)
        by_model = ozet.get("by_model", {})
        satirlar = [
            f"<div class='flex' style='flex-direction:column;gap:6px'>"
            f"<div><b>💵 Toplam Maliyet:</b> ${toplam_maliyet:.6f}</div>"
            f"<div><b>📞 Toplam Çağrı:</b> {toplam_cagri}</div>"
            f"<div><b>🔤 Toplam Token:</b> {toplam_token:,}</div>"
            f"<hr><div><b>Modele Göre:</b></div>"
        ]
        if by_model:
            satirlar.append("<table><tr><th>Model</th><th>Çağrı</th><th>Maliyet</th></tr>")
            for model, m_data in sorted(by_model.items(), key=lambda x: x[1]["cost_usd"], reverse=True):
                satirlar.append(
                    f"<tr><td>{model}</td><td>{m_data['calls']}</td>"
                    f"<td>${m_data['cost_usd']:.6f}</td></tr>"
                )
            satirlar.append("</table>")
        satirlar.append("</div>")
        return HTMLResponse(content="\n".join(satirlar))
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>Maliyet raporu: {e}</div>")


@app.get("/api/maliyet/detay")
async def api_maliyet_detay(n: int = 20):
    """Cost tracker detay HTML."""
    try:
        from reymen.cost_tracker import dump_log
        kayitlar = dump_log(limit=n)
        if not kayitlar:
            return HTMLResponse(content="<div class='gri'>Henüz kayıt yok</div>")
        satirlar = ["<table><tr><th>#</th><th>Zaman</th><th>Model</th><th>Prompt</th><th>Completion</th><th>Maliyet</th></tr>"]
        for i, r in enumerate(kayitlar, 1):
            ts = r.get("timestamp", 0)
            from datetime import datetime as dt
            zaman = dt.fromtimestamp(ts).strftime("%d.%m %H:%M") if ts else "?"
            satirlar.append(
                f"<tr><td>{i}</td><td class='gri'>{zaman}</td>"
                f"<td>{r.get('model', '?')}</td>"
                f"<td>{r.get('prompt_tokens', 0):,}</td>"
                f"<td>{r.get('completion_tokens', 0):,}</td>"
                f"<td>${r.get('cost_usd', 0):.6f}</td></tr>"
            )
        satirlar.append("</table>")
        return HTMLResponse(content="\n".join(satirlar))
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>Maliyet detay: {e}</div>")


@app.get("/api/maliyet/ozet")
async def api_maliyet_ozet():
    """Maliyet özet (dashboard)."""
    try:
        from reymen.cost_tracker import summary as ct_summary
        ozet = ct_summary()
        toplam = ozet.get("total_cost_usd", 0)
        cagri = ozet.get("total_calls", 0)
        return HTMLResponse(
            content=f"<div><b>${toplam:.4f}</b> harcama, <b>{cagri}</b> çağrı</div>"
        )
    except Exception as e:
        return HTMLResponse(content=f"<div class='gri'>Maliyet: {e}</div>")


# ---------------------------------------------------------------------------
# API — Kanban
# ---------------------------------------------------------------------------


@app.get("/api/kanban")
async def api_kanban():
    """Kanban pano durumu HTML."""
    try:
        sys.path.insert(0, str(PROJE_KOK))
        from reymen.kanban import Board
        board = Board.load(str(PROJE_KOK / ".ReYMeN" / "board.json"))
        tum_kartlar = board.all_cards()
        toplam = len(tum_kartlar)
        done = sum(1 for c in tum_kartlar if c.status == "done")
        in_progress = sum(1 for c in tum_kartlar if c.status == "in_progress")
        blocked = sum(1 for c in tum_kartlar if c.status == "blocked")
        backlog = sum(1 for c in tum_kartlar if c.status in ("backlog", "todo", "ready"))
        geciken = len(board.overdue_cards())
        satirlar = [
            f"<div class='flex' style='flex-direction:column;gap:6px'>"
            f"<div>📊 <b>{toplam}</b> kart toplam</div>"
            f"<div class='flex'>"
            f"<span class='tag tag-yes'>✅ {done} tamam</span>"
            f"<span class='tag tag-info'>🔄 {in_progress} devam</span>"
            f"<span class='tag tag-no'>🚫 {blocked} bloke</span>"
            f"<span class='tag'>📥 {backlog} sırada</span>"
            f"</div>"
            f"<div>{'⚠️ <b>' + str(geciken) + '</b> geciken kart' if geciken else '✅ Geciken kart yok'}</div>"
            f"</div>"
        ]
        # Kolon özeti
        for col in board.columns:
            satirlar.append(
                f"<div><b>{col.name}</b>: {len(col.cards)} kart"
                f"{' (WIP: ' + str(col.wip_limit) + ')' if col.wip_limit else ''}</div>"
            )
        return HTMLResponse(content="\n".join(satirlar))
    except FileNotFoundError:
        return HTMLResponse(
            content="<div class='gri'>Kanban panosu henüz oluşturulmamış. <code>.ReYMeN/board.json</code> dosyası gerekli.</div>"
        )
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>Kanban: {e}</div>")


@app.get("/api/kanban/kartlar")
async def api_kanban_kartlar():
    """Kanban kart listesi HTML."""
    try:
        sys.path.insert(0, str(PROJE_KOK))
        from reymen.kanban import Board
        board = Board.load(str(PROJE_KOK / ".ReYMeN" / "board.json"))
        tum_kartlar = board.all_cards()
        if not tum_kartlar:
            return HTMLResponse(content="<div class='gri'>Henüz kart yok</div>")
        satirlar = [
            "<table><tr><th>Kart</th><th>Durum</th><th>Öncelik</th><th>Atanan</th><th>Teslim</th></tr>"
        ]
        for c in tum_kartlar[:50]:
            prio_map = {0: "🔴 Kritik", 1: "🟠 Yüksek", 2: "🟡 Orta", 3: "🟢 Düşük"}
            durum_map = {
                "backlog": "📥", "todo": "📋", "ready": "✅",
                "in_progress": "🔄", "blocked": "🚫", "review": "👁️", "done": "✔️"
            }
            prio = prio_map.get(c.priority, str(c.priority))
            durum_icon = durum_map.get(c.status, "❓")
            deadline = c.deadline[:10] if c.deadline else "-"
            assignee = c.assignee or "-"
            baslik = c.title[:50]
            satirlar.append(
                f"<tr><td><b>{baslik}</b></td>"
                f"<td>{durum_icon} {c.status}</td>"
                f"<td><span class='gri'>{prio}</span></td>"
                f"<td>{assignee}</td>"
                f"<td class='gri'>{deadline}</td></tr>"
            )
        satirlar.append("</table>")
        return HTMLResponse(content="\n".join(satirlar))
    except FileNotFoundError:
        return HTMLResponse(content="<div class='gri'>Board dosyası bulunamadı</div>")
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>Kanban kartları: {e}</div>")


# ---------------------------------------------------------------------------
# API — Sistem / Sağlık
# ---------------------------------------------------------------------------


@app.get("/api/sistem/saglik")
async def api_sistem_saglik():
    """Sistem sağlık kontrolü HTML."""
    try:
        import platform
        import psutil
        satirlar = [
            "<table>"
            f"<tr><td>🖥️ CPU Kullanımı</td><td><b>{psutil.cpu_percent(interval=0.1):.1f}%</b></td></tr>"
            f"<tr><td>💾 RAM Kullanımı</td><td><b>{psutil.virtual_memory().percent:.1f}%</b> "
            f"({psutil.virtual_memory().used // (1024**3)}GB / {psutil.virtual_memory().total // (1024**3)}GB)</td></tr>"
            f"<tr><td>💿 Disk Kullanımı</td><td><b>{psutil.disk_usage('/').percent:.1f}%</b></td></tr>"
        ]
        # Process durumu
        calisan = 0
        tumu = process_manager.tumu()
        for p in tumu:
            if p.get("durum") == "calisiyor":
                calisan += 1
        satirlar.append(
            f"<tr><td>⚙️ Process</td><td><b>{calisan}/{len(tumu)}</b> çalışıyor</td></tr>"
        )
        satirlar.append("</table>")
        return HTMLResponse(content="\n".join(satirlar))
    except ImportError:
        return HTMLResponse(
            content="<div class='gri'>psutil yüklü değil. <code>pip install psutil</code> ile kurabilirsiniz.</div>"
        )
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>Sistem sağlığı: {e}</div>")


@app.get("/api/sistem/saglik/ozet")
async def api_sistem_saglik_ozet():
    """Sistem sağlık özet (dashboard)."""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.05)
        ram = psutil.virtual_memory().percent
        cpu_tag = "tag-yes" if cpu < 70 else ("tag-info" if cpu < 90 else "tag-no")
        ram_tag = "tag-yes" if ram < 70 else ("tag-info" if ram < 90 else "tag-no")
        return HTMLResponse(
            content=f"<div class='flex'>"
            f"<span class='tag {cpu_tag}'>🖥️ CPU: %{cpu:.0f}</span>"
            f"<span class='tag {ram_tag}'>💾 RAM: %{ram:.0f}</span>"
            f"</div>"
        )
    except ImportError:
        return HTMLResponse(content="<div class='gri'>psutil gerekli</div>")
    except Exception as e:
        return HTMLResponse(content=f"<div class='gri'>Sistem: {e}</div>")


@app.get("/api/sistem/bilgi")
async def api_sistem_bilgi():
    """Sistem bilgisi HTML."""
    try:
        import platform
        import sys
        satirlar = [
            "<table>"
            f"<tr><td>💻 İşletim Sistemi</td><td><b>{platform.system()} {platform.release()}</b></td></tr>"
            f"<tr><td>🐍 Python</td><td><b>{sys.version.split()[0]}</b></td></tr>"
            f"<tr><td>🏠 Makine</td><td>{platform.node()}</td></tr>"
            f"<tr><td>📐 Mimarî</td><td>{platform.machine()}</td></tr>"
            f"<tr><td>📁 Proje Kökü</td><td class='gri'>{PROJE_KOK}</td></tr>"
            f"<tr><td>📦 FastAPI</td><td>{getattr(__import__('fastapi'), '__version__', '?')}</td></tr>"
            f"</table>"
        ]
        return HTMLResponse(content="\n".join(satirlar))
    except Exception as e:
        return HTMLResponse(content=f"<div class='alert alert-error'>Sistem bilgisi: {e}</div>")


# ---------------------------------------------------------------------------
# WebSocket — Canlı Log
# ---------------------------------------------------------------------------


@app.websocket("/ws/logs")
async def ws_loglar(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket log abonesi bağlandı")
    try:
        while True:
            satir = await log_kuyrugu_oku()
            try:
                await websocket.send_text(satir)
            except WebSocketDisconnect:
                break
            except Exception:
                break
    except WebSocketDisconnect:
        logger.info("WebSocket log abonesi ayrıldı")
    except Exception as e:
        logger.warning("WebSocket hatası: %s", e)

# ---------------------------------------------------------------------------
# Başlangıç
# ---------------------------------------------------------------------------


@app.on_event("startup")
async def startup():
    """Uygulama başlangıcı."""
    # Log streamer'ı başlat
    await log_streamer.basla()
    
    # Log tarama görevi
    async def log_tarama_dongusu():
        while True:
            await log_streamer.tara()
            await asyncio.sleep(1)

    asyncio.create_task(log_tarama_dongusu())
    logger.info("ReYMeN Web UI başlatıldı")


@app.get("/api/health")
async def health():
    return {"durum": "ok", "zaman": datetime.now().isoformat()}


# ── Konusma Gecmisi ────────────────────────────────────────────────────────


@app.get("/konusmalar", response_class=HTMLResponse)
async def konusmalar_sayfasi(request: Request):
    user = _require_auth(request)
    if not user:
        return RedirectResponse(url="/login")
    konusmalar = _konusma_listele()
    return templates.TemplateResponse("conversations.html", {
        "request": request, "user": user, "konusmalar": konusmalar, "tema": request.cookies.get("tema", "dark"),
    })


@app.get("/api/konusmalar")
async def api_konusmalar(request: Request):
    user = _require_auth(request)
    if not user:
        return JSONResponse({"hata": "Yetkisiz"}, status_code=401)
    konusmalar = _konusma_listele()
    if not konusmalar:
        return HTMLResponse('<div class="gri">Henüz konuşma kaydı bulunamadı.</div>')
    html = ""
    for k in konusmalar[:50]:
        html += f'''<div class="conv-item" onclick="konusmaAc('{k.get("id","")}')">
            <div class="conv-title">💬 {k.get("baslik","") or k.get("hedef","İsimsiz")}</div>
            <div class="conv-meta">{k.get("tarih","") or k.get("zaman","")} · {k.get("mesaj_sayisi",0)} mesaj</div>
        </div>'''
    return HTMLResponse(html)


@app.get("/api/konusmalar/{konusma_id}/mesajlar")
async def api_konusma_mesajlar(konusma_id: str, request: Request):
    user = _require_auth(request)
    if not user:
        return JSONResponse({"hata": "Yetkisiz"}, status_code=401)
    mesajlar = _konusma_mesajlari_getir(konusma_id)
    return {"mesajlar": mesajlar}


# ── Toast Bildirim API ──────────────────────────────────────────────────────


@app.post("/api/toast/gonder")
async def api_toast_gonder(request: Request):
    """Harici bir servisten toast bildirimi gonder. (admin yetkisi)
    
    Kullanim: curl -X POST /api/toast/gonder -H "Cookie: ..." \\
              -d "mesaj=Islem tamam&tip=success"
    """
    user = _require_auth(request)
    if not user:
        return JSONResponse({"hata": "Yetkisiz"}, status_code=401)
    data = await request.form()
    mesaj = data.get("mesaj", "")
    tip = data.get("tip", "info")
    return JSONResponse({"gonderildi": True, "mesaj": mesaj, "tip": tip})


@app.websocket("/ws/toast")
async def ws_toast(websocket: WebSocket):
    """WebSocket uzerinden anlik bildirim gonderimi.
    
    Kullanim (client): new WebSocket('ws://host:5000/ws/toast')
    Client'a gonderim: {"tip": "success", "mesaj": "Islem tamam"}
    """
    await websocket.accept()
    try:
        # Toast abonelerini izle
        _WS_TOAST_KLIENTLER.add(websocket)
        await websocket.send_json({"tip": "info", "mesaj": "Baglandi"})
        while True:
            data = await websocket.receive_text()
            # Gelen mesaji tum client'lara yayinla
            for ws in list(_WS_TOAST_KLIENTLER):
                try:
                    await ws.send_text(data)
                except Exception:
                    _WS_TOAST_KLIENTLER.discard(ws)
    except Exception:
        pass
    finally:
        _WS_TOAST_KLIENTLER.discard(websocket)


_WS_TOAST_KLIENTLER: set = set()


# ── Konusma Veri Kaynagi ───────────────────────────────────────────────────


def _konusma_listele() -> list[dict]:
    """Session DB'den son konusmalari listele."""
    import sqlite3
    # OnceHafiza / session DB
    db_yollari = [
        PROJE_KOK / ".ReYMeN" / "ogrenmeler.db",
        PROJE_KOK / "reymen" / "cereyan" / ".ReYMeN" / "session.db",
        Path.home() / ".hermes" / "state.db",
    ]
    for db_yol in db_yollari:
        if db_yol.exists():
            try:
                conn = sqlite3.connect(str(db_yol))
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                # FTS5 session tablosu
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
                if cur.fetchone():
                    cur.execute("SELECT id, title, created_at, message_count FROM sessions ORDER BY created_at DESC LIMIT 50")
                    rows = cur.fetchall()
                    conn.close()
                    if rows:
                        return [
                            {"id": r["id"], "baslik": r["title"] or "İsimsiz",
                             "tarih": str(r["created_at"])[:19] if r["created_at"] else "",
                             "mesaj_sayisi": r["message_count"] or 0}
                            for r in rows
                        ]
                # Ogrenmeler tablosu
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ogrenmeler'")
                if cur.fetchone():
                    cur.execute("SELECT hedef, cozum, kaynak, zaman FROM ogrenmeler ORDER BY zaman DESC LIMIT 50")
                    rows = cur.fetchall()
                    conn.close()
                    return [
                        {"id": r["hedef"], "baslik": r["hedef"],
                         "tarih": str(r["zaman"])[:19] if r["zaman"] else "",
                         "mesaj_sayisi": len(r["cozum"]) if r["cozum"] else 0}
                        for r in rows
                    ]
                conn.close()
            except Exception:
                pass
    # Son care: .ReYMeN/notes/ klasöründen .md dosyalari
    notes_dir = PROJE_KOK / ".ReYMeN" / "notes"
    if notes_dir.exists():
        konusmalar = []
        for f in sorted(notes_dir.glob("*.md"), reverse=True)[:50]:
            konusmalar.append({
                "id": f.stem, "baslik": f.stem.replace("-", " ").replace("_", " "),
                "tarih": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                "mesaj_sayisi": len(f.read_text().splitlines()),
            })
        return konusmalar
    return []


def _konusma_mesajlari_getir(konusma_id: str) -> list[dict]:
    """Bir konusmanin mesajlarini getir."""
    import sqlite3
    db_yollari = [
        PROJE_KOK / ".ReYMeN" / "ogrenmeler.db",
        PROJE_KOK / "reymen" / "cereyan" / ".ReYMeN" / "session.db",
    ]
    for db_yol in db_yollari:
        if db_yol.exists():
            try:
                conn = sqlite3.connect(str(db_yol))
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                # Session messages
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
                if cur.fetchone():
                    cur.execute(
                        "SELECT role, content, created_at FROM messages WHERE session_id=? ORDER BY id LIMIT 100",
                        (konusma_id,))
                    rows = cur.fetchall()
                    conn.close()
                    if rows:
                        return [
                            {"rol": r["role"], "icerik": r["content"] or "",
                             "zaman": str(r["created_at"])[:19] if r["created_at"] else ""}
                            for r in rows
                        ]
                conn.close()
            except Exception:
                pass
    # Notes fallback
    note_path = PROJE_KOK / ".ReYMeN" / "notes" / f"{konusma_id}.md"
    if note_path.exists():
        return [{"rol": "user", "icerik": note_path.read_text()[:2000], "zaman": ""}]
    return []

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def baslat(port: int = 5000, host: str = "0.0.0.0") -> None:
    """Web UI'yi başlat."""
    print(f"🌐 ReYMeN Web UI v2: http://{host}:{port}")
    print(f"   Giriş: admin / reymen (varsayılan)")
    print(f"   Canlı log: /logs")
    uvicorn.run(app, host=host, port=port, log_level="info")


def cli() -> None:
    """Komut satırından çalıştırma."""
    import argparse
    parser = argparse.ArgumentParser(description="ReYMeN Web UI v2")
    parser.add_argument("--port", type=int, default=5000, help="Port (varsayılan: 5000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host (varsayılan: 0.0.0.0)")
    args = parser.parse_args()
    baslat(args.port, args.host)


# ── Motor Entegrasyonu ──────────────────────────────────────────────────

_WEB_UI_MOTOR = None
_WEB_UI_THREAD = None


def motor_kaydet(motor) -> None:
    """Motor'a Web UI araçlarını kaydet."""
    global _WEB_UI_MOTOR
    _WEB_UI_MOTOR = motor
    motor._plugin_arac_kaydet(
        "WEB_UI_BASLAT", _web_ui_baslat,
        "Web UI'yi baslat (port 5000, FastAPI + HTMX). Parametre: port=5000 host=0.0.0.0"
    )
    motor._plugin_arac_kaydet(
        "WEB_UI_DURUM", _web_ui_durum,
        "Web UI durumunu goster: calisma, port, route sayisi"
    )
    motor._plugin_arac_kaydet(
        "WEB_UI_DURDUR", _web_ui_durdur,
        "Web UI'yi durdur."
    )
    logger.info("[WEB_UI] Motor'a 3 arac kaydedildi (BASLAT, DURUM, DURDUR)")


def _web_ui_baslat(**kw) -> str:
    """Web UI'yi ayri thread'de baslat."""
    global _WEB_UI_THREAD
    if _WEB_UI_THREAD and _WEB_UI_THREAD.is_alive():
        return "[WEB_UI] Zaten calisiyor (localhost:5000)"
    import threading
    port = int(kw.get("args", [5000])[0]) if kw.get("args") else 5000
    _WEB_UI_THREAD = threading.Thread(
        target=baslat,
        args=(port, "0.0.0.0"),
        daemon=True,
    )
    _WEB_UI_THREAD.start()
    return f"[WEB_UI] Baslatildi: http://localhost:{port}"


def _web_ui_durum(**kw) -> str:
    """Web UI durumu."""
    global _WEB_UI_THREAD
    aktif = _WEB_UI_THREAD is not None and _WEB_UI_THREAD.is_alive()
    routes = len([r for r in app.routes if hasattr(r, 'path')])
    if aktif:
        return f"  WEB_UI: AKTIF (localhost:5000)\n  Route: {routes}\n  Tool: 3"
    return "  WEB_UI: PASIF"


def _web_ui_durdur(**kw) -> str:
    """Web UI'yi durdur."""
    global _WEB_UI_THREAD
    if _WEB_UI_THREAD and _WEB_UI_THREAD.is_alive():
        import os
        os._exit(0)
        return "[WEB_UI] Durduruldu"
    return "[WEB_UI] Zaten kapali"


if __name__ == "__main__":
    cli()
