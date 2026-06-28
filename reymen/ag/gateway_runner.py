# -*- coding: utf-8 -*-
"""
gateway_runner.py — Gelişmiş Çoklu Kanal Gateway Runner
ReYMeN için Terminal, Telegram, WebSocket kanal yönetimi.

Özellikler:
- Terminal kanalı (doğrudan kullanıcı girdisi)
- Telegram kanalı (telegram_bot/bot.py'yi başlatır)
- WebSocket kanalı (web_ui.py için)
- Thread-safe mesaj kuyruğu (queue.Queue)
- Kanal durumu takibi (aktif/pasif/bağlantı hatası)
- Mesaj yönlendirme (kanaldan kanala)
- JSON log (logs/gateway.jsonl)
"""

import json
import logging
import os
import queue
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

# gateway/platforms entegrasyonu
try:
    from gateway.platforms import platform_listele, platform_baslat, mesaj_gonder as platform_mesaj
    _PLATFORMLAR_AKTIF = True
except ImportError:
    _PLATFORMLAR_AKTIF = False

try:
    from gateway.session import yonetici as session_yonetici
    _SESSION_AKTIF = True
except ImportError:
    _SESSION_AKTIF = False

try:
    from gateway.mirror import aynalayici
    _MIRROR_AKTIF = True
except ImportError:
    _MIRROR_AKTIF = False

# ── Logging ──────────────────────────────────────────────────────────
logger = logging.getLogger("gateway_runner")

# ── Sabitler ─────────────────────────────────────────────────────────
PROJE_KOK = Path(__file__).parent.resolve()
LOGS_DIR = PROJE_KOK / "logs"
GATEWAY_LOG = LOGS_DIR / "gateway.jsonl"
TELEGRAM_BOT_PATH = PROJE_KOK / "telegram_bot" / "bot.py"
GATEWAY_PID_DOSYASI = PROJE_KOK / ".ReYMeN" / "gateway.pid"


# ── PID Yönetimi ─────────────────────────────────────────────────────

def _pid_kaydet():
    """Mevcut PID'i dosyaya yaz."""
    GATEWAY_PID_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
    GATEWAY_PID_DOSYASI.write_text(str(os.getpid()))


def _pid_sil():
    """PID dosyasini sil."""
    try:
        GATEWAY_PID_DOSYASI.unlink(missing_ok=True)
    except Exception as _gateway__e70:
        print(f"[UYARI] gateway_runner.py:71 - {_gateway__e70}")


def _eski_pid_oldur():
    """
    Onceki gateway hala calisiyorsa oldur.
    PID 25648 gibi stale process'leri temizler.
    """
    if not GATEWAY_PID_DOSYASI.exists():
        return
    try:
        eski_pid = int(GATEWAY_PID_DOSYASI.read_text().strip())
        if eski_pid == os.getpid():
            return  # Kendimiz
        logger.warning(f"[gateway] Eski PID bulundu: {eski_pid} — sonlandiriliyor")
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/PID", str(eski_pid)],
                capture_output=True, timeout=5,
            )
        else:
            os.kill(eski_pid, signal.SIGTERM)
            time.sleep(1)
            try:
                os.kill(eski_pid, signal.SIGKILL)
            except ProcessLookupError as _gateway__e96:
                print(f"[UYARI] gateway_runner.py:97 - {_gateway__e96}")
        _pid_sil()
        logger.info(f"[gateway] Eski PID {eski_pid} sonlandirildi.")
    except Exception as e:
        logger.debug(f"[gateway] Eski PID temizleme: {e}")
        _pid_sil()


# ── Channel Handler Prototypes ──────────────────────────────────────
class ChannelHandler:
    """Kanal işleyici temel sınıfı. Her kanal bunu extend eder."""

    def __init__(self, name: str):
        self.name = name
        self._running = False
        self._status = "stopped"  # stopped | running | error
        self._error: Optional[str] = None

    @property
    def running(self) -> bool:
        return self._running

    @property
    def status(self) -> str:
        return self._status

    @property
    def error(self) -> Optional[str]:
        return self._error

    def start(self) -> None:
        """Kanala özel başlatma. Alt sınıflar override eder."""
        self._running = True
        self._status = "running"
        self._error = None

    def stop(self) -> None:
        """Kanala özel durdurma. Alt sınıflar override eder."""
        self._running = False
        self._status = "stopped"
        self._error = None

    def send(self, message: str) -> None:
        """Kanala mesaj gönder. Alt sınıflar override eder."""
        raise NotImplementedError(
            f"Kanal '{self.name}' send() metodunu override etmeli"
        )

    def info(self) -> dict:
        """Kanal durum bilgisini döndür."""
        return {
            "name": self.name,
            "running": self._running,
            "status": self._status,
            "error": self._error,
        }


class TerminalChannel(ChannelHandler):
    """Terminal kanalı — doğrudan stdin'den okur, stdout'a yazar."""

    def __init__(self):
        super().__init__("terminal")
        self._input_buffer: queue.Queue = queue.Queue()
        self._reader_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        super().start()
        self._reader_thread = threading.Thread(
            target=self._stdin_reader, daemon=True, name="terminal-reader"
        )
        self._reader_thread.start()
        logger.info("[terminal] Kanal başlatıldı (stdin okuyucu)")

    def stop(self) -> None:
        super().stop()
        logger.info("[terminal] Kanal durduruldu")

    def send(self, message: str) -> None:
        """Terminal kanalına mesaj bas (stdout)."""
        if not self._running:
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\r\033[2K\033[33m[Gateway {timestamp}]\033[0m {message}")

    def _stdin_reader(self) -> None:
        """Arka plan thread'inde stdin'i oku, input_buffer'a koy."""
        try:
            while self._running:
                try:
                    line = sys.stdin.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    line = line.strip()
                    if line:
                        self._input_buffer.put(line)
                except (EOFError, OSError):
                    time.sleep(0.5)
        except Exception as e:
            logger.error(f"[terminal] stdin okuyucu hatası: {e}")
            self._status = "error"
            self._error = str(e)

    def get_input(self, timeout: float = 0.1) -> Optional[str]:
        """Kuyruktan bir girdi oku (non-blocking)."""
        try:
            return self._input_buffer.get(timeout=timeout)
        except queue.Empty:
            return None


class TelegramChannel(ChannelHandler):
    """Telegram kanalı — telegram_bot/bot.py'yi alt süreç olarak başlatır."""

    def __init__(self):
        super().__init__("telegram")
        self._process: Optional[subprocess.Popen] = None
        self._monitor_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Telegram bot'u subprocess olarak başlat."""
        if not TELEGRAM_BOT_PATH.exists():
            self._status = "error"
            self._error = f"Telegram bot bulunamadı: {TELEGRAM_BOT_PATH}"
            logger.error(f"[telegram] {self._error}")
            return

        token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        if not token or token.startswith("***"):
            # .env'den dene
            env_path = PROJE_KOK / ".env"
            if env_path.exists():
                from dotenv import load_dotenv
                load_dotenv(env_path)
                token = os.getenv("TELEGRAM_BOT_TOKEN", "")

        if not token:
            self._status = "error"
            self._error = "TELEGRAM_BOT_TOKEN bulunamadı"
            logger.error(f"[telegram] {self._error}")
            return

        try:
            self._process = subprocess.Popen(
                [sys.executable, str(TELEGRAM_BOT_PATH)],
                cwd=str(PROJE_KOK),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, "TELEGRAM_BOT_TOKEN": token},
            )
            super().start()
            self._monitor_thread = threading.Thread(
                target=self._monitor_process,
                daemon=True,
                name="telegram-monitor",
            )
            self._monitor_thread.start()
            logger.info("[telegram] Bot süreci başlatıldı (PID: %d)", self._process.pid)
        except Exception as e:
            self._status = "error"
            self._error = str(e)
            logger.error(f"[telegram] Başlatma hatası: {e}")

    def stop(self) -> None:
        """Telegram bot sürecini durdur."""
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait(timeout=2)
            logger.info("[telegram] Bot süreci sonlandırıldı")
        super().stop()

    def send(self, message: str) -> None:
        """Telegram kanalına mesaj gönderme (şimdilik log'a yaz)."""
        if not self._running:
            return
        # Telegram bot'una mesaj göndermek için python-telegram-bot API'si kullanılabilir
        # Şimdilik log ile yetiniyoruz, bot.py kendi mesajlarını yönetir
        logger.info(f"[telegram] Gönderilecek mesaj (bot.py yönetir): {message[:60]}...")

    def _monitor_process(self) -> None:
        """Bot sürecini izle, çökerse durumu güncelle."""
        try:
            stdout, stderr = self._process.communicate()
            if self._running:
                logger.warning(
                    "[telegram] Bot süreci beklenmedik şekilde sonlandı.\n"
                    f"  stdout: {stdout[-200:] if stdout else ''}\n"
                    f"  stderr: {stderr[-200:] if stderr else ''}"
                )
                self._status = "error"
                self._error = f"Process exited: {stderr[-200:] if stderr else 'unknown'}"
        except Exception as e:
            logger.error(f"[telegram] Monitör hatası: {e}")


class DashboardChannel(ChannelHandler):
    """Dashboard log tamponuna mesaj iten kanal.

    dashboard/app.py'deki log_ekle() fonksiyonunu cagirarak
    canli log panelini besler. dashboard import edilemezse sessizce atlar.
    """

    def __init__(self):
        super().__init__("dashboard")
        self._log_fn = None

    def start(self) -> None:
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "dashboard_app",
                Path(__file__).parent / "dashboard" / "app.py",
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self._log_fn = mod.log_ekle
            super().start()
            logger.info("[dashboard] Kanal baslati ldi (log tamponu aktif)")
        except Exception as e:
            self._status = "error"
            self._error = str(e)
            logger.warning(f"[dashboard] Kanal baslatılamadi (dashboard calismiyor): {e}")

    def send(self, message: str) -> None:
        if not self._running or not self._log_fn:
            return
        try:
            self._log_fn(f"[Gateway] {message}")
        except Exception as _gateway__e331:
            print(f"[UYARI] gateway_runner.py:332 - {_gateway__e331}")


class WebSocketChannel(ChannelHandler):
    """WebSocket kanalı — web_ui.py için FastAPI WebSocket endpoint'ine bağlanır."""

    def __init__(self):
        super().__init__("websocket")
        self._clients: list = []
        self._lock = threading.Lock()
        self._ws_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """WebSocket sunucusunu başlat (web_ui.py zaten çalışıyorken)."""
        super().start()
        self._ws_thread = threading.Thread(
            target=self._websocket_poller, daemon=True, name="ws-poller"
        )
        self._ws_thread.start()
        logger.info("[websocket] Kanal başlatıldı")

    def stop(self) -> None:
        super().stop()
        logger.info("[websocket] Kanal durduruldu")

    def send(self, message: str) -> None:
        """Bağlı tüm WebSocket istemcilerine mesaj gönder."""
        if not self._running:
            return
        with self._lock:
            for client in list(self._clients):
                try:
                    # WebSocket client'ına mesaj gönderme
                    # (web_ui.py içindeki global ws_clients listesine ekleme)
                    logger.debug(f"[websocket] İstemciye mesaj: {message[:40]}...")
                except Exception as e:
                    logger.error(f"[websocket] İstemci gönderme hatası: {e}")
                    self._clients.remove(client)

    def register_client(self, client: Any) -> None:
        """Yeni bir WebSocket istemcisi kaydet."""
        with self._lock:
            self._clients.append(client)
            logger.debug(f"[websocket] İstemci eklendi (toplam: {len(self._clients)})")

    def unregister_client(self, client: Any) -> None:
        """WebSocket istemcisini kaldır."""
        with self._lock:
            if client in self._clients:
                self._clients.remove(client)
                logger.debug(f"[websocket] İstemci çıkarıldı (toplam: {len(self._clients)})")

    @property
    def client_count(self) -> int:
        with self._lock:
            return len(self._clients)

    def _websocket_poller(self) -> None:
        """WebSocket bağlantılarını yokla (arka plan)."""
        while self._running:
            time.sleep(5)


# ── GatewayRunner ────────────────────────────────────────────────────


class GatewayRunner:
    """
    Çoklu kanal iletişim merkezi.

    Kullanım:
        gr = GatewayRunner()
        gr.register_channel("terminal", TerminalChannel())
        gr.register_channel("telegram", TelegramChannel())
        gr.start()

        # Tüm kanallara mesaj gönder
        gr.broadcast("Sistem başlatıldı.")

        # Belirli kanala mesaj gönder
        gr.send("Sadece terminale", channel="terminal")

        # Durum sorgula
        print(gr.status())
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._channels: dict[str, ChannelHandler] = {}
        self._message_queue: queue.Queue = queue.Queue()
        self._running = False
        self._main_thread: Optional[threading.Thread] = None
        self._queue_processor: Optional[threading.Thread] = None

        # logs/ klasörünü oluştur
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Kanal Yönetimi ──────────────────────────────────────────────

    def register_channel(self, name: str, handler: ChannelHandler) -> None:
        """
        Yeni bir kanal kaydet.

        Args:
            name: Kanal adı (ör: "terminal", "telegram", "websocket")
            handler: ChannelHandler alt sınıfı örneği
        """
        with self._lock:
            if name in self._channels:
                logger.warning(f"[gateway] '{name}' kanalı zaten kayıtlı, değiştiriliyor")
            self._channels[name] = handler
            logger.info(f"[gateway] Kanal kaydedildi: '{name}' ({handler.__class__.__name__})")

    def unregister_channel(self, name: str) -> Optional[ChannelHandler]:
        """Bir kanalı kaldır ve durdur."""
        with self._lock:
            handler = self._channels.pop(name, None)
        if handler:
            handler.stop()
            logger.info(f"[gateway] Kanal kaldırıldı: '{name}'")
        return handler

    def get_channel(self, name: str) -> Optional[ChannelHandler]:
        """İsme göre kanal handler'ını döndür."""
        with self._lock:
            return self._channels.get(name)

    # ── Yaşam Döngüsü ───────────────────────────────────────────────

    def start(self) -> None:
        """Tüm kayıtlı kanalları başlat ve mesaj kuyruğunu işlemeye başla."""
        with self._lock:
            if self._running:
                logger.warning("[gateway] Zaten çalışıyor")
                return
            self._running = True

        # Eski gateway prosesini temizle, PID kaydet
        _eski_pid_oldur()
        _pid_kaydet()

        # Cikista PID sil
        import atexit
        atexit.register(_pid_sil)

        # SIGTERM/SIGINT yakalayici
        def _sinyal_isle(sig, frame):
            logger.info(f"[gateway] Sinyal alindi ({sig}) — duruluyor")
            _pid_sil()
            self.stop()
            sys.exit(0)
        try:
            signal.signal(signal.SIGTERM, _sinyal_isle)
            signal.signal(signal.SIGINT, _sinyal_isle)
        except Exception as _gateway__e486:
            print(f"[UYARI] gateway_runner.py:487 - {_gateway__e486}")

        # Tüm kanalları başlat
        with self._lock:
            channel_list = list(self._channels.items())
        for name, handler in channel_list:
            try:
                handler.start()
                self._log_entry("system", f"Kanal başlatıldı: {name}")
            except Exception as e:
                logger.error(f"[gateway] '{name}' kanalı başlatılamadı: {e}")
                handler._status = "error"
                handler._error = str(e)

        # Kuyruk işleyici thread'ini başlat
        self._queue_processor = threading.Thread(
            target=self._process_message_queue,
            daemon=True,
            name="queue-processor",
        )
        self._queue_processor.start()

        # Watchdog: thread sagligini izle, cokunce yeniden basla
        self._watchdog_thread = threading.Thread(
            target=self._watchdog, daemon=True, name="gateway-watchdog"
        )
        self._watchdog_thread.start()

        # Cron zamanlayici thread'i
        self._cron_thread = threading.Thread(
            target=self._cron_tick_loop, daemon=True, name="cron-scheduler"
        )
        self._cron_thread.start()

        # Opsiyonel MCP sunucu (ReYMeN_MCP_SERVE=true ise)
        if os.environ.get("ReYMeN_MCP_SERVE", "").lower() == "true":
            _mcp_path = PROJE_KOK / "mcp_serve.py"
            if _mcp_path.exists():
                try:
                    self._mcp_proc = subprocess.Popen(
                        [sys.executable, str(_mcp_path)],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    logger.info(f"[gateway] MCP sunucu başlatıldı (pid={self._mcp_proc.pid})")
                    self._log_entry("system", f"mcp_serve pid={self._mcp_proc.pid}")
                except Exception as e:
                    logger.warning(f"[gateway] MCP sunucu başlatılamadı: {e}")

        logger.info(
            f"[gateway] GatewayRunner başlatıldı — "
            f"{len(channel_list)} kanal aktif"
        )
        self._log_entry("system", "GatewayRunner başlatıldı")

    def stop(self) -> None:
        """Tüm kanalları durdur ve kuyruk işlemeyi sonlandır."""
        with self._lock:
            self._running = False
        _pid_sil()

        # Tüm kanalları durdur
        with self._lock:
            channel_list = list(self._channels.items())
        for name, handler in channel_list:
            try:
                handler.stop()
                self._log_entry("system", f"Kanal durduruldu: {name}")
            except Exception as e:
                logger.error(f"[gateway] '{name}' kanalı durdurulamadı: {e}")

        # Kuyruk işleyicinin bitmesini bekle
        if self._queue_processor and self._queue_processor.is_alive():
            self._queue_processor.join(timeout=3)

        logger.info("[gateway] GatewayRunner durduruldu")
        self._log_entry("system", "GatewayRunner durduruldu")

    # ── Mesaj Gönderme ──────────────────────────────────────────────

    def send(self, message: str, channel: Optional[str] = None) -> None:
        """
        Belirtilen kanala veya tüm kanallara mesaj gönder.

        Args:
            message: Gönderilecek mesaj
            channel: Kanal adı (None = tüm kanallar)
        """
        entry = {
            "type": "outgoing",
            "message": message,
            "target": channel or "all",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._log_entry_raw(entry)

        with self._lock:
            if channel:
                handler = self._channels.get(channel)
                if handler and handler.running:
                    try:
                        handler.send(message)
                    except Exception as e:
                        logger.error(f"[gateway] '{channel}' gönderme hatası: {e}")
                else:
                    logger.warning(f"[gateway] '{channel}' kanalı çalışmıyor veya bulunamadı")
            else:
                for cname, handler in self._channels.items():
                    if handler.running:
                        try:
                            handler.send(message)
                        except Exception as e:
                            logger.error(f"[gateway] '{cname}' gönderme hatası: {e}")

    def broadcast(self, message: str) -> None:
        """Tüm kanallara mesaj gönder (send ile aynı, channel=None)."""
        self.send(message, channel=None)

    def enqueue_message(self, message: str, source: str = "external") -> None:
        """
        Mesajı işlenmek üzere kuyruğa ekle.

        Args:
            message: Mesaj içeriği
            source: Mesaj kaynağı (örn: "terminal", "telegram", "websocket")
        """
        entry = {
            "type": "incoming",
            "message": message,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._message_queue.put(entry)
        self._log_entry_raw(entry)
        logger.debug(f"[gateway] Kuyruğa eklendi ({source}): {message[:40]}...")

    # ── Kuyruk İşleme ───────────────────────────────────────────────

    def _process_message_queue(self) -> None:
        """Kuyruktaki mesajları sürekli işleyen arka plan thread'i."""
        while self._running:
            try:
                entry = self._message_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            try:
                self._handle_message(entry)
            except Exception as e:
                logger.error(f"[gateway] Mesaj işleme hatası: {e}")

            self._message_queue.task_done()

    def _cron_tick_loop(self) -> None:
        """Her 60 saniyede CronSchedulerCore.execute_tick_cycle() çalıştır."""
        try:
            from reymen.sistem.cron_scheduler import CronScheduler
            cron = CronScheduler()
        except ImportError:
            return
        try:
            import psutil as _psutil
        except ImportError:
            _psutil = None
        while self._running:
            time.sleep(60)
            if not self._running:
                break
            # Kaynak izleme
            if _psutil:
                try:
                    cpu = _psutil.cpu_percent(interval=0.1)
                    ram = _psutil.virtual_memory().percent
                    if cpu > 85 or ram > 90:
                        logger.warning(f"[kaynak] Yüksek kullanım — CPU:{cpu:.1f}% RAM:{ram:.1f}%")
                        self._log_entry("system", f"yüksek kaynak: cpu={cpu:.1f} ram={ram:.1f}")
                except Exception as _gateway__e663:
                    print(f"[UYARI] gateway_runner.py:664 - {_gateway__e663}")
            try:
                n = cron.execute_tick_cycle()
                if n > 0:
                    logger.info(f"[cron] {n} iş çalıştırıldı")
                    self._log_entry("cron", f"{n} cron isi calistirildi")
            except Exception as e:
                logger.warning(f"[cron] Tick hatası: {e}")

    def _watchdog(self) -> None:
        """Kuyruk isleyici thread cokerse yeniden baslatir."""
        while self._running:
            time.sleep(10)
            if not self._running:
                break
            if self._queue_processor and not self._queue_processor.is_alive():
                logger.warning("[gateway] Watchdog: kuyruk isleyici oldu, yeniden baslatiliyor")
                self._queue_processor = threading.Thread(
                    target=self._process_message_queue,
                    daemon=True,
                    name="queue-processor",
                )
                self._queue_processor.start()
                self._log_entry("system", "Watchdog: kuyruk isleyici yeniden baslatildi")

    def _handle_message(self, entry: dict) -> None:
        """Kuyruktan gelen bir mesajı işle (tüm kanallara yönlendir)."""
        message = entry.get("message", "")
        source = entry.get("source", "unknown")

        # Kaynak kanal hariç tüm kanallara yönlendir
        with self._lock:
            for cname, handler in self._channels.items():
                if cname != source and handler.running:
                    try:
                        handler.send(f"[{source} → {cname}] {message}")
                    except Exception as e:
                        logger.error(f"[gateway] Yönlendirme hatası {source}→{cname}: {e}")

    # ── Durum Sorgulama ─────────────────────────────────────────────

    def status(self) -> dict:
        """Tüm kanalların durumunu döndür."""
        with self._lock:
            channels = {
                name: handler.info() for name, handler in self._channels.items()
            }
        return {
            "running": self._running,
            "queue_size": self._message_queue.qsize(),
            "channels": channels,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def status_text(self) -> str:
        """İnsan tarafından okunabilir durum metni."""
        s = self.status()
        lines = ["📡 GatewayRunner Durumu", f"   Çalışıyor: {'✅' if s['running'] else '❌'}"]
        lines.append(f"   Kuyruk: {s['queue_size']} mesaj")
        lines.append("")
        for cname, info in s["channels"].items():
            status_icon = {
                "running": "🟢",
                "stopped": "⚫",
                "error": "🔴",
            }.get(info["status"], "⚪")
            lines.append(f"   {status_icon} {cname}: {info['status']}")
            if info.get("error"):
                lines.append(f"      └ Hata: {info['error']}")
        return "\n".join(lines)

    # ── JSON Log ─────────────────────────────────────────────────────

    def _log_entry(self, event_type: str, message: str) -> None:
        """Sistemsel bir olayı JSON log'a yaz."""
        self._log_entry_raw({
            "type": event_type,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def _log_entry_raw(self, entry: dict) -> None:
        """Ham bir entry'yi JSON log dosyasına ekle."""
        try:
            with open(GATEWAY_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"[gateway] Log yazma hatası: {e}")

    def get_logs(self, limit: int = 50) -> list[dict]:
        """JSON log'dan son N kaydı oku."""
        if not GATEWAY_LOG.exists():
            return []
        try:
            with open(GATEWAY_LOG, "r", encoding="utf-8") as f:
                lines = f.readlines()
            entries = []
            for line in lines[-limit:]:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            return entries
        except Exception as e:
            logger.error(f"[gateway] Log okuma hatası: {e}")
            return []

    # ── Yönetici Metodları ───────────────────────────────────────────

    def wait_for_input(self, timeout: float = 0.1) -> Optional[str]:
        """Terminal kanalından girdi bekle (non-blocking)."""
        terminal = self.get_channel("terminal")
        if isinstance(terminal, TerminalChannel):
            return terminal.get_input(timeout=timeout)
        return None


# ── Varsayılan Kanal Kurulumu ────────────────────────────────────────


def create_default_gateway() -> GatewayRunner:
    """
    Varsayılan kanallarla (terminal, telegram, websocket)
    hazır bir GatewayRunner oluştur.
    """
    gr = GatewayRunner()
    gr.register_channel("terminal", TerminalChannel())
    gr.register_channel("telegram", TelegramChannel())
    gr.register_channel("websocket", WebSocketChannel())
    gr.register_channel("dashboard", DashboardChannel())
    return gr


# ── CLI Entry Point ──────────────────────────────────────────────────


def interactive_mode(gr: GatewayRunner) -> None:
    """
    Etkileşimli terminal modu.
    Kullanıcı girdilerini alır, kuyruğa ekler, gateway durumunu gösterir.
    """
    print("\n" + "=" * 56)
    print("  ReYMeN Gateway Runner — Etkileşimli Mod")
    print("  Komutlar: /status, /channels, /logs, /broadcast <msg>")
    print("            /send <kanal> <msg>, /stop, /help")
    print("=" * 56 + "\n")

    try:
        while gr._running:
            line = gr.wait_for_input(timeout=0.5)
            if line is None:
                continue

            if line.startswith("/"):
                parts = line.split(maxsplit=2)
                cmd = parts[0].lower() if parts else ""

                if cmd == "/status":
                    print("\n" + gr.status_text() + "\n")

                elif cmd == "/channels":
                    print("\n📋 Kayıtlı Kanallar:")
                    for cname, handler in gr._channels.items():
                        h = handler.info()
                        print(f"   • {cname}: {h['status']} ({type(handler).__name__})")
                    print()

                elif cmd == "/logs":
                    limit = int(parts[1]) if len(parts) > 1 else 10
                    logs = gr.get_logs(limit=limit)
                    print(f"\n📜 Son {len(logs)} log kaydı:")
                    for log_entry in logs:
                        ts = log_entry.get("timestamp", "?")[:19]
                        msg = log_entry.get("message", "")[:60]
                        typ = log_entry.get("type", "?")
                        print(f"   [{ts}] {typ}: {msg}")
                    print()

                elif cmd == "/broadcast" and len(parts) > 1:
                    msg = parts[1]
                    print(f"📢 Tüm kanallara gönderiliyor: {msg}")
                    gr.broadcast(msg)

                elif cmd == "/send" and len(parts) > 2:
                    target = parts[1]
                    msg = parts[2]
                    print(f"📤 '{target}' kanalına gönderiliyor: {msg}")
                    gr.send(msg, channel=target)

                elif cmd == "/stop":
                    print("🛑 Durduruluyor...")
                    gr.stop()
                    break

                elif cmd == "/help" or cmd == "/?":
                    print("""
  Mevcut Komutlar:
    /status              — Kanal durumlarını göster
    /channels            — Kayıtlı kanalları listele
    /logs [N]            — Son N log kaydını göster (varsayılan: 10)
    /broadcast <msg>     — Tüm kanallara mesaj gönder
    /send <kanal> <msg>  — Belirtilen kanala mesaj gönder
    /stop                — Gateway'i durdur
    /help                — Bu yardım mesajını göster

  Normal yazılan her şey mesaj kuyruğuna eklenir.
""")

            else:
                # Normal mesaj — kuyruğa ekle
                gr.enqueue_message(line, source="terminal")

    except KeyboardInterrupt:
        print("\n\n⚠️  Kesme sinyali alındı, durduruluyor...")
        gr.stop()


def main():
    """Ana giriş noktası — gateway'i başlat ve etkileşimli moda geç."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    print("""
    ╔══════════════════════════════════════════╗
    ║     ReYMeN Gateway Runner  v2.0         ║
    ║     Çoklu Kanal İletişim Merkezi          ║
    ╚══════════════════════════════════════════╝
    """)

    gr = create_default_gateway()
    gr.start()

    try:
        interactive_mode(gr)
    except KeyboardInterrupt:
        print("\n🛑 Kapatılıyor...")
        gr.stop()

    print("✅ Gateway durduruldu. Hoşça kal!")


if __name__ == "__main__":
    main()
