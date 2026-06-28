# -*- coding: utf-8 -*-
"""
telegram_bot.py — ReYMeN Telegram Botu (standalone, no extra deps).

Komutlar:
  /start    — hosgeldin
  /help     — yardim listesi
  /run X    — X hedefini ajana gonder
  /status   — sistem durumu (LM Studio, kanban, beceriler)
  /logs     — son gateway log satirlari
  /cancel   — calisan gorevi iptal et
  /beceriler— beceri listesi

Kurulum (.env):
  TELEGRAM_BOT_TOKEN=xxxx
  TELEGRAM_CHAT_ID=12345678    (bos birakilirsa herkese acik)

Calistir:
  python telegram_bot.py
"""
import json
import os
import sys
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env", override=True)

TOKEN    = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID  = os.environ.get("TELEGRAM_CHAT_ID",  "").strip()   # "" = herkese acik
API_BASE = f"https://api.telegram.org/bot{TOKEN}"

# Aktif gorev kilidi (ayni anda 1 gorev)
_gorev_kilidi = threading.Lock()
_aktif_gorev: dict | None = None


# ── Telegram API yardimcilari ─────────────────────────────────────────────────

def _api(yontem: str, veri: dict = None, timeout: int = 30) -> dict:
    url  = f"{API_BASE}/{yontem}"
    body = json.dumps(veri or {}).encode()
    req  = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"ok": False, "error": str(e)}


def gonder(chat_id: int | str, metin: str, parse_mode: str = "") -> dict:
    """Telegram'a mesaj gonder — 4096 karakter sinirini bol."""
    sinir = 4000
    if len(metin) <= sinir:
        veri = {"chat_id": chat_id, "text": metin}
        if parse_mode:
            veri["parse_mode"] = parse_mode
        return _api("sendMessage", veri)
    # Cok uzunsa parcala
    for i in range(0, len(metin), sinir):
        parca = metin[i:i + sinir]
        veri = {"chat_id": chat_id, "text": parca}
        if parse_mode:
            veri["parse_mode"] = parse_mode
        _api("sendMessage", veri)
    return {"ok": True}


def _izin_var(chat_id: int | str) -> bool:
    """TELEGRAM_CHAT_ID tanımlanmışsa sadece o chat'e izin ver."""
    if not CHAT_ID:
        return True
    return str(chat_id) == str(CHAT_ID)


# ── Komut isleyiciler ─────────────────────────────────────────────────────────

def _cmd_start(msg: dict):
    gonder(msg["chat"]["id"],
           "ReYMeN ajan botuna hosgeldin!\n/help ile komutlari gor.")


def _cmd_help(msg: dict):
    yardim = (
        "Komutlar:\n"
        "/run <hedef>    — Ajana gorev ver\n"
        "/status         — Sistem durumu\n"
        "/logs           — Gateway logu (son 15 satir)\n"
        "/cancel         — Aktif gorevi iptal et\n"
        "/clarify <soru> — Talebi netlestir (secenekler icin | kullan)\n"
        "/exec <kod>     — Python kodu calistir\n"
        "/beceriler      — Kristallesmis beceriler\n"
        "/help           — Bu liste"
    )
    gonder(msg["chat"]["id"], yardim)


def _cmd_run(msg: dict, hedef: str):
    global _aktif_gorev
    cid = msg["chat"]["id"]

    if not hedef.strip():
        gonder(cid, "Kullanim: /run <hedef>\nOrnek: /run Python dosyasi olustur")
        return

    if not _gorev_kilidi.acquire(blocking=False):
        gonder(cid, "Simdi baska bir gorev calisiyor. /cancel ile iptal et.")
        return

    gonder(cid, f"Basladi: {hedef[:100]}")

    def _calistir():
        global _aktif_gorev
        iptal = threading.Event()
        _aktif_gorev = {"hedef": hedef, "iptal": iptal, "chat_id": cid}
        try:
            from reymen.sistem.main import AIAgentOrchestrator, CONFIG
            agent = AIAgentOrchestrator(config=CONFIG, max_tur=20, onay_iste=False)

            sonuc_listesi = [None]
            hata_listesi  = [None]

            def _run_thread():
                try:
                    sonuc_listesi[0] = agent.run_conversation(hedef)
                except Exception as e:
                    hata_listesi[0] = str(e)

            t = threading.Thread(target=_run_thread, daemon=True)
            t.start()

            # Iptal kontrolu (5 saniyede bir)
            while t.is_alive():
                if iptal.is_set():
                    gonder(cid, "Gorev iptal edildi.")
                    return
                time.sleep(5)

            if hata_listesi[0]:
                gonder(cid, f"HATA:\n{hata_listesi[0][:500]}")
            else:
                sonuc = sonuc_listesi[0] or "(tamamlandi, cikti yok)"
                gonder(cid, f"Sonuc:\n{str(sonuc)[:2000]}")

        except Exception as e:
            gonder(cid, f"Ajan baslatilamadi: {e}")
        finally:
            _aktif_gorev = None
            _gorev_kilidi.release()

    threading.Thread(target=_calistir, daemon=True).start()


def _cmd_cancel(msg: dict):
    cid = msg["chat"]["id"]
    global _aktif_gorev
    if _aktif_gorev:
        _aktif_gorev["iptal"].set()
        gonder(cid, f"Iptal istegi gonderildi: {_aktif_gorev['hedef'][:80]}")
    else:
        gonder(cid, "Aktif gorev yok.")


def _cmd_status(msg: dict):
    cid = msg["chat"]["id"]
    satirlar = ["ReYMeN DURUM\n"]

    # LM Studio
    import urllib.error
    try:
        urllib.request.urlopen("http://localhost:1234/v1/models", timeout=2)
        satirlar.append("LM Studio: AKTIF")
    except Exception:
        satirlar.append("LM Studio: KAPALI")

    # Aktif gorev
    if _aktif_gorev:
        satirlar.append(f"Aktif gorev: {_aktif_gorev['hedef'][:60]}")
    else:
        satirlar.append("Aktif gorev: yok")

    # Beceriler
    try:
        from reymen.cereyan.closed_learning_loop import ClosedLearningLoop
        n = ClosedLearningLoop().toplam_beceri_sayisi()
        satirlar.append(f"Beceriler: {n}")
    except Exception:
        satirlar.append("Beceriler: ?")

    # Kanban
    try:
        from reymen.arac.kanban_orchestrator import AdvancedKanbanOrchestrator
        ozet = AdvancedKanbanOrchestrator().ozet()
        toplam = ozet.get("toplam", 0)
        satirlar.append(f"Kanban: {toplam} gorev")
    except Exception as _telegram_e205:
        print(f"[UYARI] telegram_bot.py:206 - {_telegram_e205}")

    # Gateway PID
    pid_dosyasi = ROOT / ".ReYMeN" / "gateway.pid"
    if pid_dosyasi.exists():
        satirlar.append(f"Gateway PID: {pid_dosyasi.read_text().strip()}")
    else:
        satirlar.append("Gateway: kapali")

    gonder(cid, "\n".join(satirlar))


def _cmd_logs(msg: dict):
    cid = msg["chat"]["id"]
    log_dosyasi = ROOT / "logs" / "gateway.jsonl"
    if not log_dosyasi.exists():
        gonder(cid, "Log dosyasi henuz olusturulmamis.")
        return
    with open(log_dosyasi, encoding="utf-8") as f:
        satirlar = f.readlines()
    son = satirlar[-15:]
    cikti_satirlari = []
    for s in son:
        try:
            e = json.loads(s)
            ts  = e.get("timestamp", "")[:16]
            tip = e.get("type", "")
            msg_ = e.get("message", "")[:80]
            cikti_satirlari.append(f"[{ts}] {tip}: {msg_}")
        except Exception:
            cikti_satirlari.append(s.strip()[:100])
    gonder(cid, "GATEWAY LOG (son 15):\n" + "\n".join(cikti_satirlari))


def _cmd_clarify(msg: dict, hedef: str):
    """Telegram'da /clarify komutu - net olmayan talebi netleştir."""
    cid = msg["chat"]["id"]
    if not hedef.strip():
        gonder(cid,
               "Kullanım: /clarify <soru> | <secenek1,secenek2> | <varsayılan>\n"
               "Örnek: /clarify Hangi ortam? | local,docker | local\n"
               "Sadece soru: /clarify Bu işlemi onaylıyor musun?")
        return
    try:
        from tools.clarify_tool import run as clarify_run
        parcalar = hedef.split("|")
        soru = parcalar[0].strip()
        secenekler = [s.strip() for s in parcalar[1].split(",")] if len(parcalar) > 1 and parcalar[1].strip() else None
        varsayilan = parcalar[2].strip() if len(parcalar) > 2 and parcalar[2].strip() else ""
        sonuc = clarify_run(soru=soru, secenekler=secenekler, varsayilan=varsayilan)
        gonder(cid, sonuc)
    except Exception as e:
        gonder(cid, f"[CLARIFY HATASI] {e}")


def _cmd_exec(msg: dict, kod: str):
    """Telegram'da /exec komutu - Python kodunu çalıştır."""
    cid = msg["chat"]["id"]
    if not kod.strip():
        gonder(cid,
               "Kullanım: /exec <python_kodu>\n"
               "Örnek: /exec print(sum(range(100)))\n"
               "Çok satırlı: gönderirken alt satıra geçmeden tek satırda yazın, noktalı virgül ile ayırın.")
        return
    try:
        from tools.execute_code_tool import run as exec_run
        sonuc = exec_run(kod=kod)
        cikti = sonuc[:3000]  # Telegram limiti
        gonder(cid, cikti)
    except Exception as e:
        gonder(cid, f"[EXEC HATASI] {e}")


def _cmd_beceriler(msg: dict):
    cid = msg["chat"]["id"]
    try:
        from reymen.cereyan.closed_learning_loop import ClosedLearningLoop
        beceriler = ClosedLearningLoop().tum_beceriler()
        if not beceriler:
            gonder(cid, "Hic beceri yok.")
            return
        satirlar = [f"Beceriler ({len(beceriler)}):"]
        for b in beceriler[:20]:
            satirlar.append(f"  {b['ad']}: {b['aciklama'][:60]}")
        if len(beceriler) > 20:
            satirlar.append(f"  ... ve {len(beceriler)-20} tane daha")
        gonder(cid, "\n".join(satirlar))
    except Exception as e:
        gonder(cid, f"Beceri hatasi: {e}")


# ── Mesaj yonlendirici ─────────────────────────────────────────────────────────

def _isle(msg: dict):
    """Gelen mesaji komutlara yonlendir."""
    cid = msg.get("chat", {}).get("id")
    if not cid:
        return
    if not _izin_var(cid):
        gonder(cid, "Bu bota erisim izniniz yok.")
        return

    metin = (msg.get("text") or "").strip()
    if not metin:
        return

    if metin.startswith("/start"):
        _cmd_start(msg)
    elif metin.startswith("/help"):
        _cmd_help(msg)
    elif metin.startswith("/run"):
        hedef = metin[4:].strip()
        _cmd_run(msg, hedef)
    elif metin.startswith("/cancel"):
        _cmd_cancel(msg)
    elif metin.startswith("/status"):
        _cmd_status(msg)
    elif metin.startswith("/logs"):
        _cmd_logs(msg)
    elif metin.startswith("/clarify"):
        hedef = metin[8:].strip()
        _cmd_clarify(msg, hedef)
    elif metin.startswith("/exec"):
        hedef = metin[5:].strip()
        _cmd_exec(msg, hedef)
    elif metin.startswith("/beceriler"):
        _cmd_beceriler(msg)
    else:
        # Normal mesaj = /run olarak isle
        _cmd_run(msg, metin)


# ── Polling dongusu ───────────────────────────────────────────────────────────

def polling():
    """Uzun polling ile Telegram'dan mesaj al."""
    if not TOKEN or TOKEN.startswith("***"):
        print("[TelegramBot] TELEGRAM_BOT_TOKEN ayarli degil — cikiliyor.")
        return

    print(f"[TelegramBot] Basliyor... (chat_id filtresi: {CHAT_ID or 'yok'})")
    offset = 0

    # Bildirim gonder
    if CHAT_ID:
        gonder(CHAT_ID, "ReYMeN botu aktif. /help yazin.")

    while True:
        try:
            sonuc = _api("getUpdates", {"offset": offset, "timeout": 30}, timeout=40)
            if not sonuc.get("ok"):
                time.sleep(5)
                continue

            for upd in sonuc.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message") or upd.get("edited_message")
                if msg:
                    threading.Thread(target=_isle, args=(msg,), daemon=True).start()

        except KeyboardInterrupt:
            print("\n[TelegramBot] Durduruldu.")
            break
        except Exception as e:
            print(f"[TelegramBot] Polling hatasi: {e}")
            time.sleep(5)


# ── Motor entegrasyon fonksiyonu ──────────────────────────────────────────────

def motor_bildirim_gonder(mesaj: str) -> str:
    """motor.py'den dogrudan Telegram bildirimi gonder."""
    if not TOKEN or not CHAT_ID:
        return "[Telegram] Token/chat_id ayarli degil."
    sonuc = gonder(CHAT_ID, mesaj)
    return "[Telegram] Gonderildi." if sonuc.get("ok") else f"[Telegram] Hata: {sonuc}"


def telegram_araclari_kaydet(motor) -> None:
    """Motor'a TELEGRAM_GONDER aracini ekle."""
    import re as _re
    try:
        from plugins.kanban import _plugin_arac_kaydet
    except ImportError:
        return

    def _telegram_gonder(ham: str) -> str:
        params = _re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        mesaj = params[0] if params else ham.strip('"')
        return motor_bildirim_gonder(mesaj)

    _plugin_arac_kaydet(motor, "TELEGRAM_GONDER", _telegram_gonder)
    print("[TelegramBot] TELEGRAM_GONDER araci kayit edildi.")


def motor_kaydet(motor):
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return
    motor._plugin_arac_kaydet(
        "TELEGRAM_BOT_GONDER",
        lambda metin="", chat_id="": motor_bildirim_gonder(metin) if not chat_id
        else (gonder(chat_id, metin).get("ok") and "[Telegram] Gonderildi." or "[Telegram] Hata."),
        "Telegram bot ile mesaj gonder (metin, chat_id: opsiyonel — bos=env'den)",
    )


if __name__ == "__main__":
    polling()
