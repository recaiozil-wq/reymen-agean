# -*- coding: utf-8 -*-
"""
dashboard/app.py — ReYMeN Web Dashboard (FastAPI + HTMX).

Ozellikler:
- Canli ReAct adim gecmisi (SSE ile otomatik guncelleme)
- Ajan durumu: bos / calisiyor / tamamlandi / hata
- Oturum gecmisi (SQLite'ten)
- Hafiza / beceri karti goruntuleme
- Hizli hedef gonderme (web'den ajan baslatma)
- Islem gunlugu canli akisi
"""

import json
import os
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from filelock import FileLock
import logging
logger = logging.getLogger(__name__)

# Proje kokune eris
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

app = FastAPI(title="ReYMeN Dashboard")

# --- Veri yollari ---
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
JOBS_FILE = DATA_DIR / "jobs.json"
LOCK_FILE = DATA_DIR / "jobs.json.lock"
LOGS_DIR = DATA_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Canli log tampon (son 200 satir, thread-safe)
_log_tampon: list[str] = []
_log_kilit = threading.Lock()
MAX_LOG = 200

# Ajan durumu
_ajan_durumu = {"durum": "bos", "hedef": "", "tur": 0, "max_tur": 0, "son_eylem": ""}
_ajan_kilit = threading.Lock()


# ── Yardimcilar ─────────────────────────────────────────────────────

def log_ekle(mesaj: str):
    zaman = datetime.now().strftime("%H:%M:%S")
    satir = f"[{zaman}] {mesaj}"
    with _log_kilit:
        _log_tampon.append(satir)
        if len(_log_tampon) > MAX_LOG:
            _log_tampon.pop(0)


def durum_guncelle(**kwargs):
    with _ajan_kilit:
        _ajan_durumu.update(kwargs)


def load_jobs() -> dict:
    lock = FileLock(str(LOCK_FILE), timeout=5)
    with lock:
        if JOBS_FILE.exists():
            return json.loads(JOBS_FILE.read_text(encoding="utf-8"))
        return {}


def save_jobs(jobs: dict):
    lock = FileLock(str(LOCK_FILE), timeout=5)
    with lock:
        JOBS_FILE.write_text(json.dumps(jobs, indent=2, default=str), encoding="utf-8")


def oturum_gecmisi_yukle(limit=20) -> list[dict]:
    """SQLite oturum gunlugunden son N kaydi oku."""
    try:
        db_yolu = ROOT / ".ReYMeN" / "session.db"
        if not db_yolu.exists():
            return []
        import sqlite3
        con = sqlite3.connect(str(db_yolu), check_same_thread=False)
        try:
            rows = con.execute(
                "SELECT hedef, eylem, gozlem, zaman FROM oturumlar "
                "ORDER BY rowid DESC LIMIT ?", (limit,)
            ).fetchall()
        except Exception:
            rows = []
        finally:
            con.close()
        return [
            {"hedef": r[0], "eylem": r[1], "gozlem": r[2][:120], "zaman": r[3]}
            for r in rows
        ]
    except Exception:
        return []


def beceri_listesi_yukle() -> list[str]:
    """skills/ ve .ReYMeN/skills/ klasorlerindeki .md dosyalarini listele."""
    beceriler = []
    for klasor in [ROOT / "skills", ROOT / ".ReYMeN" / "skills"]:
        if klasor.exists():
            for f in sorted(klasor.glob("*.md")):
                beceriler.append(f.stem)
    return beceriler


def ajan_calistir_arka_plan(hedef: str):
    """Ajani ayri thread'de calistir; log ve durumu guncelle."""
    try:
        durum_guncelle(durum="calisiyor", hedef=hedef, tur=0)
        log_ekle(f"Hedef alindi: {hedef}")

        from main import AIAgentOrchestrator, CONFIG, _env_anahtar
        mod = CONFIG.get("backend_mode", "local")
        max_tur = int(_env_anahtar("ReYMeN_MAX_TURNS", "15"))

        # Log baslama
        import io
        from contextlib import redirect_stdout

        class LogYakalayici(io.StringIO):
            def write(self, s):
                if s.strip():
                    log_ekle(s.rstrip())
                return super().write(s)

        agent = AIAgentOrchestrator(
            config=CONFIG, backend_mode=mod, max_tur=max_tur, onay_iste=False
        )

        # Tur sayacini takip et
        orijinal_run = agent.run_conversation.__func__

        with redirect_stdout(LogYakalayici()):
            ozet = agent.run_conversation(hedef)

        durum_guncelle(
            durum="tamamlandi" if ozet else "hata",
            son_eylem=ozet or "Tamamlanamadi",
        )
        log_ekle(f"Sonuc: {ozet or 'Tamamlanamadi'}")

    except Exception as e:
        durum_guncelle(durum="hata", son_eylem=str(e))
        log_ekle(f"[HATA] {e}")


# ── HTML Sablon ──────────────────────────────────────────────────────

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', system-ui, sans-serif;
       background: #0d1117; color: #c9d1d9; min-height: 100vh; }
.nav { background: #161b22; border-bottom: 1px solid #30363d;
       padding: 0.75rem 2rem; display: flex; align-items: center; gap: 1.5rem; }
.nav-brand { font-size: 1.1rem; font-weight: 700; color: #58a6ff; letter-spacing: 1px; }
.nav a { color: #8b949e; text-decoration: none; font-size: 0.85rem; }
.nav a:hover { color: #c9d1d9; }
.container { max-width: 1300px; margin: 0 auto; padding: 1.5rem 2rem; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }
.card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 1.25rem; }
.card-title { font-size: 0.8rem; font-weight: 600; color: #8b949e;
              text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.75rem; }
h1 { font-size: 1.5rem; color: #e6edf3; margin-bottom: 1.25rem; }
.badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px;
         font-size: 0.72rem; font-weight: 600; }
.badge-bos      { background: #21262d; color: #8b949e; }
.badge-calisiyor { background: #1f3a5c; color: #58a6ff; animation: pulse 1.5s infinite; }
.badge-tamamlandi { background: #1a3d2b; color: #3fb950; }
.badge-hata     { background: #3d1a1a; color: #f85149; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.6} }
.durum-kart { display: flex; align-items: center; gap: 1rem; }
.durum-ikon { font-size: 2rem; }
.durum-bilgi .hedef-metin { font-size: 0.9rem; color: #e6edf3; margin-top: 0.25rem; }
input[type="text"] { width: 100%; padding: 0.6rem 0.8rem; border-radius: 6px;
                     border: 1px solid #30363d; background: #0d1117; color: #c9d1d9;
                     font-size: 0.9rem; }
input[type="text"]:focus { outline: none; border-color: #58a6ff; }
.btn { padding: 0.55rem 1.2rem; border-radius: 6px; border: none; cursor: pointer;
       font-size: 0.85rem; font-weight: 600; }
.btn-primary { background: #238636; color: white; }
.btn-primary:hover { background: #2ea043; }
.btn-sm { padding: 0.3rem 0.8rem; font-size: 0.75rem; }
.btn-danger { background: #b91c1c; color: white; }
.log-kutu { background: #0d1117; border: 1px solid #21262d; border-radius: 6px;
            padding: 0.75rem 1rem; font-family: 'Cascadia Code','Courier New',monospace;
            font-size: 0.78rem; height: 280px; overflow-y: auto;
            white-space: pre-wrap; color: #79c0ff; line-height: 1.5; }
.adim-satiri { padding: 0.4rem 0; border-bottom: 1px solid #21262d;
               font-size: 0.82rem; display: flex; gap: 0.5rem; }
.adim-zaman { color: #6e7681; min-width: 70px; }
.adim-eylem { color: #d2a8ff; font-weight: 600; min-width: 120px; }
.adim-hedef { color: #79c0ff; }
.beceri-chip { display: inline-block; background: #21262d; border: 1px solid #30363d;
               border-radius: 4px; padding: 0.25rem 0.6rem; margin: 0.2rem;
               font-size: 0.75rem; color: #8b949e; }
.form-row { display: flex; gap: 0.75rem; margin-top: 0.75rem; }
.stat { text-align: center; }
.stat-sayi { font-size: 1.6rem; font-weight: 700; color: #58a6ff; }
.stat-etiket { font-size: 0.72rem; color: #8b949e; margin-top: 0.2rem; }
"""

def _escape(s: str) -> str:
    return (str(s)
            .replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _render_durum():
    with _ajan_kilit:
        d = dict(_ajan_durumu)
    ikon = {"bos": "💤", "calisiyor": "⚙️", "tamamlandi": "✅", "hata": "❌"}.get(d["durum"], "❓")
    hedef_k = _escape(d["hedef"][:80]) if d["hedef"] else "<i>Hedef bekleniyor...</i>"
    return f"""
    <div id="durum-panel" hx-get="/api/durum" hx-trigger="every 2s" hx-swap="outerHTML">
      <div class="durum-kart">
        <div class="durum-ikon">{ikon}</div>
        <div class="durum-bilgi">
          <span class="badge badge-{d['durum']}">{d['durum'].upper()}</span>
          <div class="hedef-metin">{hedef_k}</div>
        </div>
      </div>
    </div>"""


def _render_gecmis(rows):
    if not rows:
        return '<div style="color:#6e7681;font-size:0.82rem;">Henuz kayit yok.</div>'
    satirlar = ""
    for r in rows:
        eylem = _escape(r.get("eylem", "")[:30])
        hedef = _escape(r.get("hedef", "")[:50])
        zaman = _escape(r.get("zaman", "")[:16])
        satirlar += f"""<div class="adim-satiri">
          <span class="adim-zaman">{zaman}</span>
          <span class="adim-eylem">{eylem}</span>
          <span class="adim-hedef">{hedef}</span>
        </div>"""
    return satirlar


def _render_istatistik():
    rows = oturum_gecmisi_yukle(limit=500)
    toplam = len(rows)
    beceriler = len(beceri_listesi_yukle())
    tamamlanan = sum(1 for r in rows if "GOREV_BITTI" in r.get("eylem", ""))
    return f"""
    <div class="grid-3">
      <div class="card stat"><div class="stat-sayi">{toplam}</div>
        <div class="stat-etiket">Toplam Adim</div></div>
      <div class="card stat"><div class="stat-sayi">{tamamlanan}</div>
        <div class="stat-etiket">Tamamlanan Gorev</div></div>
      <div class="card stat"><div class="stat-sayi">{beceriler}</div>
        <div class="stat-etiket">Kristal Beceri</div></div>
    </div>"""


SAYFA = """<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>ReYMeN Dashboard</title>
  <script src="https://unpkg.com/htmx.org@1.9.10"></script>
  <style>{css}</style>
</head>
<body>
  <nav class="nav">
    <span class="nav-brand">ReYMeN</span>
    <a href="/">Panel</a>
    <a href="/gecmis">Gecmis</a>
    <a href="/beceriler">Beceriler</a>
  </nav>
  <div class="container">
    <h1>Ajan Kontrol Paneli</h1>

    <!-- Istatistik -->
    <div id="istatistik" hx-get="/api/istatistik" hx-trigger="every 10s" hx-swap="innerHTML">
      {istatistik}
    </div>

    <div style="margin-top:1.5rem;" class="grid">

      <!-- Sol: Durum + Hedef Gonder -->
      <div>
        <div class="card" style="margin-bottom:1rem;">
          <div class="card-title">Ajan Durumu</div>
          {durum}
        </div>

        <div class="card">
          <div class="card-title">Yeni Hedef Gonder</div>
          <form hx-post="/api/calistir" hx-target="#log-kutusu" hx-swap="innerHTML"
                hx-indicator="#spinner">
            <input type="text" name="hedef"
                   placeholder="Hedefini buraya yaz ve Enter'a bas..."
                   autocomplete="off" required>
            <div class="form-row">
              <button type="submit" class="btn btn-primary">Calistir</button>
              <span id="spinner" class="htmx-indicator" style="color:#58a6ff;font-size:0.8rem;">
                Ajan baslatiliyor...
              </span>
            </div>
          </form>
        </div>
      </div>

      <!-- Sag: Canli Log -->
      <div class="card">
        <div class="card-title" style="display:flex;justify-content:space-between;">
          <span>Canli Log</span>
          <button class="btn btn-sm btn-danger"
                  hx-post="/api/log/temizle" hx-target="#log-kutusu" hx-swap="innerHTML">
            Temizle
          </button>
        </div>
        <div id="log-kutusu"
             hx-get="/api/log" hx-trigger="every 2s" hx-swap="innerHTML">
          {log}
        </div>
      </div>

    </div>

    <!-- Son Adimlar -->
    <div class="card" style="margin-top:1.5rem;">
      <div class="card-title">Son ReAct Adimlari
        <span style="float:right;cursor:pointer;" title="Yenile"
              hx-get="/api/gecmis" hx-target="#gecmis-icerik" hx-swap="innerHTML">↻</span>
      </div>
      <div id="gecmis-icerik" hx-get="/api/gecmis" hx-trigger="every 5s" hx-swap="innerHTML">
        {gecmis}
      </div>
    </div>

  </div>
</body>
</html>"""


# ── Rotalar ─────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    return SAYFA.format(
        css=CSS,
        istatistik=_render_istatistik(),
        durum=_render_durum(),
        log=_render_log(),
        gecmis=_render_gecmis(oturum_gecmisi_yukle(10)),
    )


@app.get("/api/durum", response_class=HTMLResponse)
async def api_durum():
    return _render_durum()


@app.get("/api/log", response_class=HTMLResponse)
async def api_log():
    return _render_log()


@app.post("/api/log/temizle", response_class=HTMLResponse)
async def api_log_temizle():
    with _log_kilit:
        _log_tampon.clear()
    return '<div style="color:#6e7681;font-size:0.8rem;">Log temizlendi.</div>'


@app.get("/api/gecmis", response_class=HTMLResponse)
async def api_gecmis():
    return _render_gecmis(oturum_gecmisi_yukle(10))


@app.get("/api/istatistik", response_class=HTMLResponse)
async def api_istatistik():
    return _render_istatistik()


@app.post("/api/calistir", response_class=HTMLResponse)
async def api_calistir(hedef: str = Form(...)):
    with _ajan_kilit:
        if _ajan_durumu["durum"] == "calisiyor":
            return '<div style="color:#f85149;">Ajan zaten calisiyor. Bitirmesini bekle.</div>'
    t = threading.Thread(target=ajan_calistir_arka_plan, args=(hedef,), daemon=True)
    t.start()
    log_ekle(f"Dashboard'dan hedef gonderildi: {hedef[:60]}")
    return '<div style="color:#3fb950;">Ajan baslatildi. Log panelini izle.</div>'


@app.get("/gecmis", response_class=HTMLResponse)
async def gecmis_sayfasi():
    rows = oturum_gecmisi_yukle(50)
    satirlar = _render_gecmis(rows)
    return f"""<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8">
    <title>ReYMeN - Gecmis</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <style>{CSS}</style></head><body>
    <nav class="nav"><span class="nav-brand">ReYMeN</span>
      <a href="/">Panel</a><a href="/gecmis">Gecmis</a><a href="/beceriler">Beceriler</a>
    </nav>
    <div class="container">
      <h1>ReAct Adim Gecmisi (son 50)</h1>
      <div class="card">{satirlar}</div>
    </div></body></html>"""


@app.get("/beceriler", response_class=HTMLResponse)
async def beceriler_sayfasi():
    beceriler = beceri_listesi_yukle()
    chipler = "".join(f'<span class="beceri-chip">{_escape(b)}</span>' for b in beceriler)
    if not chipler:
        chipler = '<div style="color:#6e7681;">Henuz kristalize beceri yok.</div>'
    return f"""<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8">
    <title>ReYMeN - Beceriler</title>
    <style>{CSS}</style></head><body>
    <nav class="nav"><span class="nav-brand">ReYMeN</span>
      <a href="/">Panel</a><a href="/gecmis">Gecmis</a><a href="/beceriler">Beceriler</a>
      <a href="/ogrenme">Ogrenme</a><a href="/arama">Arama</a>
    </nav>
    <div class="container">
      <h1>Kristal Beceriler ({len(beceriler)})</h1>
      <div class="card">{chipler}</div>
    </div></body></html>"""


@app.get("/ogrenme", response_class=HTMLResponse)
async def ogrenme_sayfasi():
    """Öğrenme döngüsü istatistikleri sayfası."""
    try:
        from reymen.core.ogrenme import istatistik as ogrenme_ist, ttl_temizle, eski_basarisizlari_temizle
        eski_basarisizlari_temizle()
        stats = ogrenme_ist()
    except Exception as e:
        stats = {"toplam": 0, "basarili": 0, "basarisiz": 0, "hata": str(e)}

    try:
        from reymen.core.session_search import session_istatistik
        sess_stats = session_istatistik()
    except Exception as e:
        sess_stats = {"hata": str(e)}

    return f"""<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8">
    <title>ReYMeN - Ogrenme</title>
    <style>{CSS}</style></head><body>
    <nav class="nav"><span class="nav-brand">ReYMeN</span>
      <a href="/">Panel</a><a href="/gecmis">Gecmis</a><a href="/beceriler">Beceriler</a>
      <a href="/ogrenme">Ogrenme</a><a href="/arama">Arama</a>
    </nav>
    <div class="container">
      <h1>Ogrenme Dongusu Istatistikleri</h1>
      <div class="grid-3">
        <div class="card stat"><div class="stat-sayi">{stats.get('toplam', 0)}</div>
          <div class="stat-etiket">Toplam Cozum</div></div>
        <div class="card stat"><div class="stat-sayi" style="color:#3fb950;">{stats.get('basarili', 0)}</div>
          <div class="stat-etiket">Basarili</div></div>
        <div class="card stat"><div class="stat-sayi" style="color:#f85149;">{stats.get('basarisiz', 0)}</div>
          <div class="stat-etiket">Basarisiz</div></div>
      </div>
      <div class="card" style="margin-top:1.5rem;">
        <div class="card-title">Session Veritabani</div>
        <div style="font-size:0.85rem;color:#8b949e;">
          <p>Session sayisi: <b style="color:#58a6ff;">{sess_stats.get('session_sayisi', 0)}</b></p>
          <p>Mesaj sayisi: <b style="color:#58a6ff;">{sess_stats.get('mesaj_sayisi', 0)}</b></p>
          <p>Tool cagri sayisi: <b style="color:#58a6ff;">{sess_stats.get('tool_cagri_sayisi', 0)}</b></p>
          <p>FTS5 aktif: <b style="color:{"#3fb950" if sess_stats.get('fts5_aktif') else "#f85149"};">{"Evet" if sess_stats.get('fts5_aktif') else "Hayir"}</b></p>
        </div>
      </div>
    </div></body></html>"""


@app.get("/arama", response_class=HTMLResponse)
async def arama_sayfasi(request: Request):
    """Session arama sayfası."""
    q = request.query_params.get("q", "")
    sonuclar_html = ""
    if q:
        try:
            from reymen.core.session_search import session_ara
            sonuclar = session_ara(q, limit=20)
            if sonuclar:
                for s in sonuclar:
                    icerik = _escape(s.get("icerik", "")[:200])
                    sid = _escape(s.get("session_id", "")[:12])
                    rol = _escape(s.get("rol", ""))
                    skor = s.get("skor", 0)
                    sonuclar_html += f"""<div class="adim-satiri">
                      <span class="adim-zaman">[{sid}]</span>
                      <span class="adim-eylem">{rol}</span>
                      <span class="adim-hedef">{icerik}... <small style="color:#6e7681;">skor:{skor}</small></span>
                    </div>"""
            else:
                sonuclar_html = '<div style="color:#6e7681;">Sonuc bulunamadi.</div>'
        except Exception as e:
            sonuclar_html = f'<div style="color:#f85149;">Arama hatasi: {_escape(str(e))}</div>'

    return f"""<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8">
    <title>ReYMeN - Arama</title>
    <style>{CSS}</style></head><body>
    <nav class="nav"><span class="nav-brand">ReYMeN</span>
      <a href="/">Panel</a><a href="/gecmis">Gecmis</a><a href="/beceriler">Beceriler</a>
      <a href="/ogrenme">Ogrenme</a><a href="/arama">Arama</a>
    </nav>
    <div class="container">
      <h1>Session Arama (FTS5)</h1>
      <div class="card">
        <form method="get" action="/arama">
          <input type="text" name="q" value="{_escape(q)}"
                 placeholder="Arama sorgusu..." autocomplete="off">
          <div class="form-row">
            <button type="submit" class="btn btn-primary">Ara</button>
          </div>
        </form>
      </div>
      <div class="card" style="margin-top:1rem;">
        <div class="card-title">Sonuclar</div>
        {sonuclar_html if sonuclar_html else '<div style="color:#6e7681;">Arama yapmak icin yukariya yaz.</div>'}
      </div>
    </div></body></html>"""


def _render_log():
    with _log_kilit:
        satirlar = list(_log_tampon[-50:])
    if not satirlar:
        return '<div style="color:#6e7681;font-size:0.8rem;">Log bos.</div>'
    icerik = "\n".join(_escape(s) for s in reversed(satirlar))
    return f'<div class="log-kutu">{icerik}</div>'


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=False)
