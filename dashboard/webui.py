# -*- coding: utf-8 -*-
"""
dashboard/webui.py — ReYMeN Gelişmiş Web UI (FastAPI + HTMX).

Hermes Web UI seviyesinde arayüz:
- Ana sayfa: sistem durumu, son aktivite
- Görevler: çalışan/bitmiş görev listesi
- Loglar: run_log.jsonl + fail_log.jsonl görüntüleme
- Öğrenme: hafızadaki çözüm sayısı, TTL durumu
- Session search: geçmiş arama (FTS5)

API Endpoint'leri:
- GET  /api/durum       — sistem durumu
- GET  /api/istatistik  — öğrenme istatistikleri
- GET  /api/loglar      — son loglar
- POST /api/session-ara — session search
- POST /api/gorev-baslat — görev başlat

Koyu tema, mobil uyumlu, canlı güncelleme (polling).

Kullanım:
    python -m dashboard.webui
    # veya
    uvicorn dashboard.webui:app --host 0.0.0.0 --port 8080
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import logging

logger = logging.getLogger(__name__)

# Proje kökü
ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT))

app = FastAPI(
    title="ReYMeN Web UI",
    description="Gelişmiş dashboard — görev takibi, loglar, öğrenme, arama",
    version="2.0.0",
)

# ── Veri Yolları ─────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR = ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

RUN_LOG = LOGS_DIR / "run_log.jsonl"
FAIL_LOG = LOGS_DIR / "fail_log.jsonl"
ACIL_FIX_LOG = LOGS_DIR / "acil_fix_log.jsonl"

# Canlı log tamponu (thread-safe)
_log_tampon: deque = deque(maxlen=300)
_log_kilit = threading.Lock()

# Ajan durumu
_ajan_durumu: Dict[str, Any] = {
    "durum": "bos",
    "hedef": "",
    "tur": 0,
    "max_tur": 0,
    "son_eylem": "",
    "baslangiç": None,
}
_ajan_kilit = threading.Lock()

# Görev listesi (bellek içi)
_gorevler: List[Dict[str, Any]] = []
_gorev_kilit = threading.Lock()


# ── Yardımcılar ──────────────────────────────────────────────────────

def log_ekle(mesaj: str, seviye: str = "INFO"):
    """Canlı log tamponuna satır ekle."""
    zaman = datetime.now().strftime("%H:%M:%S")
    satir = f"[{zaman}] [{seviye}] {mesaj}"
    with _log_kilit:
        _log_tampon.append(satir)


def durum_guncelle(**kwargs):
    with _ajan_kilit:
        _ajan_durumu.update(kwargs)


def gorev_ekle(hedef: str) -> str:
    """Yeni görev ekle, ID döndür."""
    gorev_id = f" gorev_{int(time.time())}"
    with _gorev_kilit:
        _gorevler.append({
            "id": gorev_id,
            "hedef": hedef,
            "durum": "bekliyor",
            "baslangiç": datetime.now().isoformat(),
            "bitis": None,
            "sonuc": None,
        })
    return gorev_id


def gorev_guncelle(gorev_id: str, **kwargs):
    with _gorev_kilit:
        for g in _gorevler:
            if g["id"] == gorev_id:
                g.update(kwargs)
                break


def jsonl_oku(dosya: Path, limit: int = 50) -> List[Dict]:
    """JSONL dosyasını oku, son N satır."""
    if not dosya.exists():
        return []
    sonuclar = []
    try:
        with open(dosya, "r", encoding="utf-8") as f:
            satirlar = f.readlines()
        for satir in reversed(satirlar[-limit:]):
            try:
                sonuclar.append(json.loads(satir.strip()))
            except json.JSONDecodeError:
                continue
    except Exception as e:
        logger.warning("Log okuma hatası %s: %s", dosya, e)
    return sonuclar


def _escape(s: str) -> str:
    """HTML escape."""
    import html
    return html.escape(str(s))


# ── CSS (Koyu Tema) ──────────────────────────────────────────────────

CSS = """
:root {
  --bg: #0d1117;
  --bg-card: #161b22;
  --bg-hover: #1c2128;
  --border: #30363d;
  --text: #c9d1d9;
  --text-muted: #8b949e;
  --text-dim: #6e7681;
  --blue: #58a6ff;
  --green: #3fb950;
  --red: #f85149;
  --yellow: #d29922;
  --purple: #d2a8ff;
  --orange: #db6d28;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Segoe UI', -apple-system, system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  line-height: 1.5;
}
/* Nav */
.nav {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
  position: sticky;
  top: 0;
  z-index: 100;
}
.nav-brand {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--blue);
  letter-spacing: 1px;
}
.nav a {
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.85rem;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  transition: all 0.15s;
}
.nav a:hover { color: var(--text); background: var(--bg-hover); }
.nav a.active { color: var(--blue); background: rgba(88,166,255,0.1); }
/* Layout */
.container { max-width: 1400px; margin: 0 auto; padding: 1.5rem; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
@media (max-width: 768px) {
  .grid, .grid-3, .grid-4 { grid-template-columns: 1fr; }
  .nav { padding: 0.5rem 1rem; gap: 0.5rem; }
  .container { padding: 1rem; }
}
/* Card */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}
.card-title {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
/* Typography */
h1 { font-size: 1.5rem; color: #e6edf3; margin-bottom: 1.25rem; }
h2 { font-size: 1.15rem; color: #e6edf3; margin-bottom: 0.75rem; }
/* Badge */
.badge {
  display: inline-block;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
}
.badge-bos { background: #21262d; color: var(--text-muted); }
.badge-calisiyor { background: rgba(88,166,255,0.15); color: var(--blue); animation: pulse 1.5s infinite; }
.badge-tamamlandi { background: rgba(63,185,80,0.15); color: var(--green); }
.badge-hata { background: rgba(248,81,73,0.15); color: var(--red); }
.badge-bekliyor { background: rgba(210,153,34,0.15); color: var(--yellow); }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
/* Stats */
.stat { text-align: center; }
.stat-sayi { font-size: 1.8rem; font-weight: 700; }
.stat-etiket { font-size: 0.72rem; color: var(--text-muted); margin-top: 0.2rem; }
/* Form */
input[type="text"], input[type="search"], textarea, select {
  width: 100%;
  padding: 0.6rem 0.8rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  font-size: 0.9rem;
  font-family: inherit;
}
input:focus, textarea:focus, select:focus {
  outline: none;
  border-color: var(--blue);
  box-shadow: 0 0 0 3px rgba(88,166,255,0.1);
}
textarea { resize: vertical; min-height: 80px; }
/* Button */
.btn {
  padding: 0.55rem 1.2rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  background: var(--bg-card);
  color: var(--text);
  transition: all 0.15s;
}
.btn:hover { background: var(--bg-hover); }
.btn-primary { background: #238636; border-color: #238636; color: white; }
.btn-primary:hover { background: #2ea043; }
.btn-danger { background: #b91c1c; border-color: #b91c1c; color: white; }
.btn-sm { padding: 0.3rem 0.8rem; font-size: 0.75rem; }
.form-row { display: flex; gap: 0.75rem; margin-top: 0.75rem; flex-wrap: wrap; }
/* Log */
.log-kutu {
  background: #010409;
  border: 1px solid #21262d;
  border-radius: 6px;
  padding: 0.75rem 1rem;
  font-family: 'Cascadia Code', 'Fira Code', 'Courier New', monospace;
  font-size: 0.78rem;
  height: 350px;
  overflow-y: auto;
  white-space: pre-wrap;
  color: #79c0ff;
  line-height: 1.6;
}
/* Table */
table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
th { text-align: left; padding: 0.5rem; color: var(--text-muted); border-bottom: 1px solid var(--border); font-weight: 600; }
td { padding: 0.5rem; border-bottom: 1px solid #21262d; }
tr:hover { background: var(--bg-hover); }
/* Adim satiri */
.adim-satiri {
  padding: 0.5rem 0;
  border-bottom: 1px solid #21262d;
  font-size: 0.82rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.adim-zaman { color: var(--text-dim); min-width: 70px; }
.adim-eylem { color: var(--purple); font-weight: 600; min-width: 100px; }
.adim-hedef { color: var(--blue); flex: 1; }
.adim-sonuc { color: var(--green); }
.adim-hata { color: var(--red); }
/* Beceri chip */
.beceri-chip {
  display: inline-block;
  background: #21262d;
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 0.25rem 0.7rem;
  margin: 0.2rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}
/* Spinner */
.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid var(--border);
  border-top-color: var(--blue);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #484f58; }
/* HTMX indicator */
.htmx-indicator { display: none; }
.htmx-request .htmx-indicator { display: inline; }
.htmx-request.htmx-indicator { display: inline; }
"""


# ── HTML Şablonları ──────────────────────────────────────────────────

def _nav_html(aktif: str = "") -> str:
    """Navigasyon çubuğu HTML."""
    sayfalar = [
        ("/", "Ana Sayfa", "anasayfa"),
        ("/gorevler", "Görevler", "gorevler"),
        ("/loglar", "Loglar", "loglar"),
        ("/ogrenme", "Öğrenme", "ogrenme"),
        ("/arama", "Arama", "arama"),
        ("/beceriler", "Beceriler", "beceriler"),
    ]
    linkler = ""
    for url, etiket, key in sayfalar:
        cls = ' class="active"' if key == aktif else ""
        linkler += f'<a href="{url}"{cls}>{etiket}</a>'
    return f'<nav class="nav"><span class="nav-brand">⚡ ReYMeN</span>{linkler}</nav>'


def _sayfa_kabugu(baslik: str, aktif: str, icerik: str) -> str:
    """Tam HTML sayfa kabuğu."""
    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ReYMeN — {baslik}</title>
  <script src="https://unpkg.com/htmx.org@1.9.10"></script>
  <style>{CSS}</style>
</head>
<body>
  {_nav_html(aktif)}
  <div class="container">
    {icerik}
  </div>
</body>
</html>"""


# ── Sayfa Render Fonksiyonları ───────────────────────────────────────

def _render_durum_kart() -> str:
    """Ajan durum kartı."""
    with _ajan_kilit:
        d = dict(_ajan_durumu)
    ikonlar = {"bos": "💤", "calisiyor": "⚙️", "tamamlandi": "✅", "hata": "❌"}
    ikon = ikonlar.get(d["durum"], "❓")
    hedef = _escape(d["hedef"][:80]) if d["hedef"] else "<i>Hedef bekleniyor...</i>"
    return f"""
    <div id="durum-panel" hx-get="/api/durum" hx-trigger="every 3s" hx-swap="outerHTML">
      <div style="display:flex;align-items:center;gap:1rem;">
        <span style="font-size:2rem;">{ikon}</span>
        <div>
          <span class="badge badge-{d['durum']}">{d['durum'].upper()}</span>
          <div style="margin-top:0.3rem;font-size:0.9rem;">{hedef}</div>
        </div>
      </div>
    </div>"""


def _render_log_kutusu() -> str:
    """Canlı log kutusu."""
    with _log_kilit:
        satirlar = list(_log_tampon)[-80:]
    if not satirlar:
        return '<div id="log-kutusu" class="log-kutu" hx-get="/api/loglar" hx-trigger="every 3s" hx-swap="innerHTML"><span style="color:var(--text-dim);">Log boş.</span></div>'
    icerik = "\n".join(_escape(s) for s in reversed(satirlar))
    return f'<div id="log-kutusu" class="log-kutu" hx-get="/api/loglar" hx-trigger="every 3s" hx-swap="innerHTML">{icerik}</div>'


def _render_istatistik_kartlari() -> str:
    """İstatistik kartları."""
    # Öğrenme istatistikleri
    try:
        from reymen.core.ogrenme import istatistik as ogrenme_ist
        o_stats = ogrenme_ist()
    except Exception:
        o_stats = {"toplam": 0, "basarili": 0, "basarisiz": 0}

    # Session istatistikleri
    try:
        from reymen.core.session_search import session_istatistik
        s_stats = session_istatistik()
    except Exception:
        s_stats = {"session_sayisi": 0, "mesaj_sayisi": 0}

    # Görev sayısı
    with _gorev_kilit:
        toplam_gorev = len(_gorevler)
        calisan_gorev = sum(1 for g in _gorevler if g["durum"] == "calisiyor")

    return f"""
    <div class="grid-4" id="istatistik-kartlari" hx-get="/api/istatistik" hx-trigger="every 10s" hx-swap="outerHTML">
      <div class="card stat">
        <div class="stat-sayi" style="color:var(--blue);">{toplam_gorev}</div>
        <div class="stat-etiket">Toplam Görev</div>
      </div>
      <div class="card stat">
        <div class="stat-sayi" style="color:var(--green);">{o_stats.get('basarili', 0)}</div>
        <div class="stat-etiket">Başarılı Çözüm</div>
      </div>
      <div class="card stat">
        <div class="stat-sayi" style="color:var(--purple);">{s_stats.get('session_sayisi', 0)}</div>
        <div class="stat-etiket">Session</div>
      </div>
      <div class="card stat">
        <div class="stat-sayi" style="color:var(--orange);">{s_stats.get('mesaj_sayisi', 0)}</div>
        <div class="stat-etiket">Mesaj</div>
      </div>
    </div>"""


def _render_son_gorevler(limit: int = 5) -> str:
    """Son görevler listesi."""
    with _gorev_kilit:
        gorevler = list(_gorevler)[-limit:]

    if not gorevler:
        return '<div style="color:var(--text-dim);font-size:0.85rem;">Henüz görev yok.</div>'

    satirlar = ""
    for g in reversed(gorevler):
        hedef = _escape(g["hedef"][:60])
        durum = g["durum"]
        baslangic = g.get("baslangiç", "")[:16]
        satirlar += f"""<div class="adim-satiri">
          <span class="adim-zaman">{baslangic}</span>
          <span class="badge badge-{durum}">{durum}</span>
          <span class="adim-hedef">{hedef}</span>
        </div>"""
    return satirlar


def _render_log_tablosu(loglar: List[Dict], baslik: str) -> str:
    """Log tablosu render."""
    if not loglar:
        return f'<div style="color:var(--text-dim);">{baslik} bulunamadı.</div>'

    satirlar = ""
    for log in loglar:
        ts = _escape(str(log.get("ts", ""))[:19])
        step = _escape(str(log.get("step", "")))
        attempt = log.get("attempt", "")
        ok = log.get("ok", False)
        tail = _escape(str(log.get("tail", ""))[:150])
        durum_cls = "adim-sonuc" if ok else "adim-hata"
        durum_ikon = "✅" if ok else "❌"
        satirlar += f"""<div class="adim-satiri">
          <span class="adim-zaman">{ts}</span>
          <span class="adim-eylem">{step}</span>
          <span>{durum_ikon} deneme {attempt}</span>
          <span class="{durum_cls}">{tail}</span>
        </div>"""
    return satirlar


# ── Sayfa Rotaları ───────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def ana_sayfa():
    """Ana sayfa: sistem durumu, son aktivite."""
    icerik = f"""
    <h1>⚡ ReYMeN Kontrol Paneli</h1>

    <!-- İstatistik Kartları -->
    {_render_istatistik_kartlari()}

    <div class="grid" style="margin-top:1.5rem;">
      <!-- Sol: Durum + Hedef -->
      <div>
        <div class="card">
          <div class="card-title">Ajan Durumu</div>
          {_render_durum_kart()}
        </div>

        <div class="card">
          <div class="card-title">Yeni Görev Başlat</div>
          <form hx-post="/api/gorev-baslat" hx-target="#gorev-sonuc" hx-swap="innerHTML"
                hx-indicator="#gorev-spinner">
            <input type="text" name="hedef"
                   placeholder="Görev hedefini yazın..."
                   autocomplete="off" required>
            <div class="form-row">
              <button type="submit" class="btn btn-primary">▶ Başlat</button>
              <span id="gorev-spinner" class="htmx-indicator">
                <span class="spinner"></span> Başlatılıyor...
              </span>
            </div>
          </form>
          <div id="gorev-sonuc" style="margin-top:0.5rem;"></div>
        </div>
      </div>

      <!-- Sağ: Canlı Log -->
      <div class="card">
        <div class="card-title">
          <span>📡 Canlı Log</span>
          <button class="btn btn-sm btn-danger"
                  hx-post="/api/log-temizle" hx-target="#log-kutusu" hx-swap="innerHTML">
            🗑 Temizle
          </button>
        </div>
        {_render_log_kutusu()}
      </div>
    </div>

    <!-- Son Görevler -->
    <div class="card" style="margin-top:1.5rem;">
      <div class="card-title">
        <span>📋 Son Görevler</span>
        <a href="/gorevler" style="font-size:0.78rem;color:var(--blue);text-decoration:none;">Tümü →</a>
      </div>
      <div id="son-gorevler" hx-get="/api/son-gorevler" hx-trigger="every 5s" hx-swap="innerHTML">
        {_render_son_gorevler()}
      </div>
    </div>
    """
    return _sayfa_kabugu("Ana Sayfa", "anasayfa", icerik)


@app.get("/gorevler", response_class=HTMLResponse)
async def gorevler_sayfasi():
    """Görevler sayfası: çalışan/bitmiş görev listesi."""
    with _gorev_kilit:
        gorevler = list(_gorevler)

    tablo = ""
    if not gorevler:
        tablo = '<div style="color:var(--text-dim);padding:1rem;">Henüz görev yok.</div>'
    else:
        tablo = '<table><thead><tr><th>ID</th><th>Hedef</th><th>Durum</th><th>Başlangıç</th><th>Bitiş</th><th>Sonuç</th></tr></thead><tbody>'
        for g in reversed(gorevler):
            gid = _escape(g["id"][:12])
            hedef = _escape(g["hedef"][:50])
            durum = f'<span class="badge badge-{g["durum"]}">{g["durum"]}</span>'
            baslangic = _escape(str(g.get("baslangiç", ""))[:19])
            bitis = _escape(str(g.get("bitis", ""))[:19]) if g.get("bitis") else "—"
            sonuc = _escape(str(g.get("sonuc", ""))[:60]) if g.get("sonuc") else "—"
            tablo += f"<tr><td>{gid}</td><td>{hedef}</td><td>{durum}</td><td>{baslangic}</td><td>{bitis}</td><td>{sonuc}</td></tr>"
        tablo += "</tbody></table>"

    icerik = f"""
    <h1>📋 Görevler</h1>
    <div class="card">
      <div class="card-title">Görev Listesi ({len(gorevler)})</div>
      <div hx-get="/api/gorevler" hx-trigger="every 5s" hx-swap="innerHTML">
        {tablo}
      </div>
    </div>
    """
    return _sayfa_kabugu("Görevler", "gorevler", icerik)


@app.get("/loglar", response_class=HTMLResponse)
async def loglar_sayfasi():
    """Loglar sayfası: run_log.jsonl + fail_log.jsonl görüntüleme."""
    run_logs = jsonl_oku(RUN_LOG, 30)
    fail_logs = jsonl_oku(FAIL_LOG, 30)
    acil_logs = jsonl_oku(ACIL_FIX_LOG, 20)

    icerik = f"""
    <h1>📜 Loglar</h1>

    <div class="grid">
      <div class="card">
        <div class="card-title">
          <span>✅ Run Log ({len(run_logs)})</span>
          <a href="/api/loglar?tip=run&format=raw" style="font-size:0.75rem;color:var(--blue);">Ham →</a>
        </div>
        <div hx-get="/api/loglar?tip=run" hx-trigger="every 10s" hx-swap="innerHTML">
          {_render_log_tablosu(run_logs, "Run log")}
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span>❌ Fail Log ({len(fail_logs)})</span>
          <a href="/api/loglar?tip=fail&format=raw" style="font-size:0.75rem;color:var(--red);">Ham →</a>
        </div>
        <div hx-get="/api/loglar?tip=fail" hx-trigger="every 10s" hx-swap="innerHTML">
          {_render_log_tablosu(fail_logs, "Fail log")}
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">🔧 Acil Fix Log ({len(acil_logs)})</div>
      <div hx-get="/api/loglar?tip=acil" hx-trigger="every 10s" hx-swap="innerHTML">
        {_render_log_tablosu(acil_logs, "Acil fix log")}
      </div>
    </div>
    """
    return _sayfa_kabugu("Loglar", "loglar", icerik)


@app.get("/ogrenme", response_class=HTMLResponse)
async def ogrenme_sayfasi():
    """Öğrenme sayfası: hafızadaki çözüm sayısı, TTL durumu."""
    try:
        from reymen.core.ogrenme import istatistik, ttl_temizle, eski_basarisizlari_temizle, TTL_GUN, TTL_MUAF_BASARI
        eski_basarisizlari_temizle()
        silinen = ttl_temizle()
        stats = istatistik()
    except Exception as e:
        stats = {"toplam": 0, "basarili": 0, "basarisiz": 0, "hata": str(e)}
        silinen = 0
        TTL_GUN = 30
        TTL_MUAF_BASARI = 3

    try:
        from reymen.core.session_search import session_istatistik
        sess_stats = session_istatistik()
    except Exception as e:
        sess_stats = {"hata": str(e)}

    basari_orani = (stats.get("basarili", 0) / stats.get("toplam", 1) * 100) if stats.get("toplam", 0) > 0 else 0

    icerik = f"""
    <h1>🧠 Öğrenme Döngüsü</h1>

    <div class="grid-3">
      <div class="card stat">
        <div class="stat-sayi" style="color:var(--blue);">{stats.get('toplam', 0)}</div>
        <div class="stat-etiket">Toplam Çözüm</div>
      </div>
      <div class="card stat">
        <div class="stat-sayi" style="color:var(--green);">{stats.get('basarili', 0)}</div>
        <div class="stat-etiket">Başarılı</div>
      </div>
      <div class="card stat">
        <div class="stat-sayi" style="color:var(--red);">{stats.get('basarisiz', 0)}</div>
        <div class="stat-etiket">Başarısız</div>
      </div>
    </div>

    <div class="card" style="margin-top:1.5rem;">
      <div class="card-title">📊 Detaylar</div>
      <table>
        <tr><td>Başarı Oranı</td><td><b style="color:var(--green);">%{basari_orani:.1f}</b></td></tr>
        <tr><td>TTL Süresi</td><td><b>{TTL_GUN} gün</b></td></tr>
        <tr><td>TTL Muafiyet (başarı sayısı)</td><td><b>{TTL_MUAF_BASARI}</b></td></tr>
        <tr><td>Son Temizlikte Silinen</td><td><b style="color:var(--orange);">{silinen}</b></td></tr>
      </table>
    </div>

    <div class="card">
      <div class="card-title">💾 Session Veritabanı</div>
      <table>
        <tr><td>Session Sayısı</td><td><b style="color:var(--blue);">{sess_stats.get('session_sayisi', 0)}</b></td></tr>
        <tr><td>Mesaj Sayısı</td><td><b style="color:var(--blue);">{sess_stats.get('mesaj_sayisi', 0)}</b></td></tr>
        <tr><td>Tool Çağrı Sayısı</td><td><b style="color:var(--blue);">{sess_stats.get('tool_cagri_sayisi', 0)}</b></td></tr>
        <tr><td>FTS5 Aktif</td><td><b style="color:{"var(--green)" if sess_stats.get("fts5_aktif") else "var(--red)"};">{"Evet" if sess_stats.get("fts5_aktif") else "Hayır"}</b></td></tr>
      </table>
    </div>
    """
    return _sayfa_kabugu("Öğrenme", "ogrenme", icerik)


@app.get("/arama", response_class=HTMLResponse)
async def arama_sayfasi(request: Request):
    """Session search sayfası."""
    q = request.query_params.get("q", "")
    limit = int(request.query_params.get("limit", "20"))
    sonuclar_html = ""

    if q:
        try:
            from reymen.core.session_search import session_ara
            sonuclar = session_ara(q, limit=limit)
            if sonuclar:
                for s in sonuclar:
                    sid = _escape(s.get("session_id", "")[:12])
                    rol = _escape(s.get("rol", ""))
                    icerik_kisa = _escape(s.get("icerik", "")[:200])
                    skor = s.get("skor", 0)
                    rol_renk = "var(--purple)" if rol == "assistant" else "var(--blue)"
                    sonuclar_html += f"""<div class="adim-satiri">
                      <span class="adim-zaman">[{sid}]</span>
                      <span class="adim-eylem" style="color:{rol_renk};">{rol}</span>
                      <span class="adim-hedef">{icerik_kisa}...</span>
                      <span style="color:var(--text-dim);font-size:0.75rem;">skor:{skor}</span>
                    </div>"""
            else:
                sonuclar_html = '<div style="color:var(--text-dim);padding:1rem;">Sonuç bulunamadı.</div>'
        except Exception as e:
            sonuclar_html = f'<div style="color:var(--red);padding:1rem;">Arama hatası: {_escape(str(e))}</div>'

    icerik = f"""
    <h1>🔍 Session Arama (FTS5)</h1>

    <div class="card">
      <div class="card-title">Arama Yap</div>
      <form method="get" action="/arama">
        <input type="search" name="q" value="{_escape(q)}"
               placeholder="Arama sorgusu... (örn: 'hata düzeltme')"
               autocomplete="off" autofocus>
        <div class="form-row">
          <label style="font-size:0.82rem;color:var(--text-muted);">Limit:</label>
          <select name="limit" style="width:auto;">
            <option value="10" {"selected" if limit == 10 else ""}>10</option>
            <option value="20" {"selected" if limit == 20 else ""}>20</option>
            <option value="50" {"selected" if limit == 50 else ""}>50</option>
          </select>
          <button type="submit" class="btn btn-primary">🔍 Ara</button>
        </div>
      </form>
    </div>

    <div class="card">
      <div class="card-title">Sonuçlar {"(" + str(len(sonuclar)) + ")" if q else ""}</div>
      {sonuclar_html if sonuclar_html else '<div style="color:var(--text-dim);padding:1rem;">Arama yapmak için yukarıya yazın.</div>'}
    </div>
    """
    return _sayfa_kabugu("Arama", "arama", icerik)


@app.get("/beceriler", response_class=HTMLResponse)
async def beceriler_sayfasi():
    """Beceriler sayfası."""
    beceriler = []
    for klasor in [ROOT / "skills", ROOT / ".ReYMeN" / "skills"]:
        if klasor.exists():
            for f in sorted(klasor.glob("*.md")):
                beceriler.append(f.stem)

    chipler = "".join(f'<span class="beceri-chip">{_escape(b)}</span>' for b in beceriler)
    if not chipler:
        chipler = '<div style="color:var(--text-dim);">Henüz kristalize beceri yok.</div>'

    icerik = f"""
    <h1>💎 Kristal Beceriler ({len(beceriler)})</h1>
    <div class="card">{chipler}</div>
    """
    return _sayfa_kabugu("Beceriler", "beceriler", icerik)


# ── API Endpoint'leri ────────────────────────────────────────────────

@app.get("/api/durum", response_class=HTMLResponse)
async def api_durum():
    """Sistem durumu (HTMX partial)."""
    return _render_durum_kart()


@app.get("/api/istatistik", response_class=HTMLResponse)
async def api_istatistik():
    """Öğrenme istatistikleri (HTMX partial)."""
    return _render_istatistik_kartlari()


@app.get("/api/loglar", response_class=HTMLResponse)
async def api_loglar(tip: str = "canli", format: str = ""):
    """Son loglar (HTMX partial veya raw JSON)."""
    if format == "raw":
        if tip == "run":
            dosya = RUN_LOG
        elif tip == "fail":
            dosya = FAIL_LOG
        elif tip == "acil":
            dosya = ACIL_FIX_LOG
        else:
            dosya = RUN_LOG
        if not dosya.exists():
            return JSONResponse({"hata": "Log dosyası yok"}, status_code=404)
        return JSONResponse(jsonl_oku(dosya, 100))

    if tip == "run":
        return _render_log_tablosu(jsonl_oku(RUN_LOG, 30), "Run log")
    elif tip == "fail":
        return _render_log_tablosu(jsonl_oku(FAIL_LOG, 30), "Fail log")
    elif tip == "acil":
        return _render_log_tablosu(jsonl_oku(ACIL_FIX_LOG, 20), "Acil fix log")
    else:
        # Canlı log
        with _log_kilit:
            satirlar = list(_log_tampon)[-80:]
        if not satirlar:
            return '<span style="color:var(--text-dim);">Log boş.</span>'
        return "\n".join(_escape(s) for s in reversed(satirlar))


@app.post("/api/session-ara", response_class=HTMLResponse)
async def api_session_ara(request: Request):
    """Session search (POST)."""
    body = await request.json()
    sorgu = body.get("sorgu", "")
    limit = body.get("limit", 20)

    try:
        from reymen.core.session_search import session_ara
        sonuclar = session_ara(sorgu, limit=limit)
        return JSONResponse({"sonuclar": sonuclar, "sayi": len(sonuclar)})
    except Exception as e:
        return JSONResponse({"hata": str(e)}, status_code=500)


@app.post("/api/gorev-baslat", response_class=HTMLResponse)
async def api_gorev_baslat(hedef: str = Form(...)):
    """Görev başlat."""
    with _ajan_kilit:
        if _ajan_durumu["durum"] == "calisiyor":
            return '<div style="color:var(--red);">⚠ Ajan zaten çalışıyor. Bitirmesini bekleyin.</div>'

    gorev_id = gorev_ekle(hedef)
    log_ekle(f"Görev başlatıldı: {hedef[:60]}", "INFO")

    # Arka plan thread
    def _arka_plan():
        try:
            durum_guncelle(durum="calisiyor", hedef=hedef, baslangiç=datetime.now().isoformat())
            gorev_guncelle(gorev_id, durum="calisiyor")

            # Ajanı çalıştır (varsa)
            try:
                from main import AIAgentOrchestrator, CONFIG
                mod = CONFIG.get("backend_mode", "local")
                agent = AIAgentOrchestrator(config=CONFIG, backend_mode=mod, max_tur=15, onay_iste=False)
                ozet = agent.run_conversation(hedef)
                sonuc = ozet or "Tamamlandı"
            except ImportError:
                sonuc = "Ajan modülü bulunamadı (main.py)"
                log_ekle(sonuc, "WARN")
            except Exception as e:
                sonuc = f"Hata: {e}"
                log_ekle(f"Görev hatası: {e}", "ERROR")

            durum_guncelle(durum="tamamlandi", son_eylem=sonuc)
            gorev_guncelle(gorev_id, durum="tamamlandi", bitis=datetime.now().isoformat(), sonuc=sonuc)
            log_ekle(f"Görev tamamlandı: {sonuc[:60]}", "INFO")

        except Exception as e:
            durum_guncelle(durum="hata", son_eylem=str(e))
            gorev_guncelle(gorev_id, durum="hata", bitis=datetime.now().isoformat(), sonuc=str(e))
            log_ekle(f"Görev hatası: {e}", "ERROR")

    t = threading.Thread(target=_arka_plan, daemon=True)
    t.start()

    return f'<div style="color:var(--green);">✅ Görev başlatıldı: <b>{_escape(hedef[:50])}</b></div>'


@app.get("/api/son-gorevler", response_class=HTMLResponse)
async def api_son_gorevler():
    """Son görevler (HTMX partial)."""
    return _render_son_gorevler(5)


@app.get("/api/gorevler", response_class=HTMLResponse)
async def api_gorevler():
    """Tüm görevler tablosu (HTMX partial)."""
    with _gorev_kilit:
        gorevler = list(_gorevler)

    if not gorevler:
        return '<div style="color:var(--text-dim);padding:1rem;">Henüz görev yok.</div>'

    tablo = '<table><thead><tr><th>ID</th><th>Hedef</th><th>Durum</th><th>Başlangıç</th><th>Bitiş</th></tr></thead><tbody>'
    for g in reversed(gorevler):
        gid = _escape(g["id"][:12])
        hedef = _escape(g["hedef"][:50])
        durum = f'<span class="badge badge-{g["durum"]}">{g["durum"]}</span>'
        baslangic = _escape(str(g.get("baslangiç", ""))[:19])
        bitis = _escape(str(g.get("bitis", ""))[:19]) if g.get("bitis") else "—"
        tablo += f"<tr><td>{gid}</td><td>{hedef}</td><td>{durum}</td><td>{baslangic}</td><td>{bitis}</td></tr>"
    tablo += "</tbody></table>"
    return tablo


@app.post("/api/log-temizle", response_class=HTMLResponse)
async def api_log_temizle():
    """Canlı log tamponunu temizle."""
    with _log_kilit:
        _log_tampon.clear()
    return '<span style="color:var(--text-dim);">Log temizlendi.</span>'


@app.get("/api/saglik")
async def api_saglik():
    """Health check."""
    return {"status": "ok", "version": "2.0.0", "uptime": time.time()}


# ── Ana Giriş ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    log_ekle("ReYMeN Web UI başlatıldı", "INFO")
    uvicorn.run("dashboard.webui:app", host="0.0.0.0", port=8080, reload=False)