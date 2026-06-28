# -*- coding: utf-8 -*-
"""proxy/proxy_engine.py — Coklu-istek HTTP proxy motoru + SOCKS5.

ThreadingMixIn tabanli, HTTPS tunnel (CONNECT) destekli, SOCKS5 (RFC 1928)
saf Python ile (PySocks gerektirmez).
"""
from __future__ import annotations
import socket
import struct
import select
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn, TCPServer, BaseRequestHandler as _BaseRH
from typing import Optional

from .proxy_config import ProxyConfig
import logging
logger = logging.getLogger(__name__)


class ThreadingProxyServer(ThreadingMixIn, HTTPServer):
    """Thread-per-request HTTP proxy. Daemon thread'ler otomatik temizlenir."""
    daemon_threads = True
    allow_reuse_address = True

    def shutdown_request(self, request):
        try:
            request.shutdown(socket.SHUT_WR)
        except OSError:
            logger.warning("[fix_01_sessiz_except] OSError")
        super().shutdown_request(request)


class _ProxyHandler(BaseHTTPRequestHandler):
    server_version = "ReYMeN-Proxy/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass  # Sessiz; ileride logger baglanabilir

    # ── HTTPS Tunnel (CONNECT) ──────────────────────────────────────────

    def do_CONNECT(self):
        try:
            host, _, port_str = self.path.rpartition(":")
            port = int(port_str) if port_str else 443
        except (ValueError, AttributeError):
            self.send_error(400, "Bad CONNECT target")
            return
        try:
            remote = socket.create_connection((host, port), timeout=30)
        except OSError as e:
            self.send_error(502, f"Tunnel failed: {e}")
            return
        self.send_response(200, "Connection Established")
        self.end_headers()
        self._tunnel(self.connection, remote)

    def _tunnel(self, client: socket.socket, remote: socket.socket):
        """Cift yonlu daemon thread tuneli."""
        def _forward(src: socket.socket, dst: socket.socket):
            try:
                while True:
                    chunk = src.recv(65536)
                    if not chunk:
                        break
                    dst.sendall(chunk)
            except OSError:
                logger.warning("[fix_01_sessiz_except] OSError")
            finally:
                for s in (src, dst):
                    try:
                        s.close()
                    except OSError:
                        logger.warning("[fix_01_sessiz_except] OSError")
        threading.Thread(target=_forward, args=(client, remote), daemon=True).start()
        threading.Thread(target=_forward, args=(remote, client), daemon=True).start()

    # ── HTTP Forward ────────────────────────────────────────────────────

    def do_GET(self):     self._forward()
    def do_POST(self):    self._forward()
    def do_PUT(self):     self._forward()
    def do_DELETE(self):  self._forward()
    def do_HEAD(self):    self._forward()
    def do_PATCH(self):   self._forward()
    def do_OPTIONS(self): self._forward()

    def _forward(self):
        import urllib.request
        import urllib.error
        try:
            hop_by_hop = {"proxy-connection", "connection", "keep-alive",
                          "proxy-authenticate", "proxy-authorization", "te",
                          "trailers", "transfer-encoding", "upgrade"}
            headers = {k: v for k, v in self.headers.items()
                       if k.lower() not in hop_by_hop}
            body = None
            cl = self.headers.get("Content-Length")
            if cl:
                body = self.rfile.read(int(cl))
            req = urllib.request.Request(
                self.path, data=body, headers=headers, method=self.command
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in ("transfer-encoding",):
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_error(e.code, str(e.reason))
        except Exception as e:
            self.send_error(502, str(e))


# ── SOCKS5 (RFC 1928) — saf Python, PySocks gerektirmez ──────────────


class _Socks5Handler:
    """SOCKS5 protokol elcisi (RFC 1928). Her istemci baglantisi icin bir ornek."""

    def __init__(self, client: socket.socket, addr):
        self._client = client
        self._addr = addr
        self._dst: Optional[socket.socket] = None

    def handle(self):
        try:
            self._handshake()
            self._request_and_relay()
        except (OSError, struct.error, ValueError, ConnectionError) as e:
            try:
                self._send_reply(0x01, b"")
            except OSError:
                logger.warning("[fix_01_sessiz_except] OSError")
        finally:
            for s in (self._client, self._dst):
                if s:
                    try:
                        s.close()
                    except OSError:
                        logger.warning("[fix_01_sessiz_except] OSError")

    def _recv_exact(self, n: int, timeout: float = 10.0) -> bytes:
        self._client.settimeout(timeout)
        buf = b""
        while len(buf) < n:
            try:
                chunk = self._client.recv(n - len(buf))
            except OSError as e:
                raise ConnectionError(f"recv basarisiz ({n} bekleniyor, {len(buf)} alindi): {e}")
            if not chunk:
                raise ConnectionError(f"Client kapandi ({n} bekleniyor, {len(buf)} alindi)")
            buf += chunk
        return buf

    def _handshake(self):
        """Adim 1: Auth negotiation — sadece no-auth (0x00) kabul edilir."""
        ver = self._recv_exact(2)
        if ver[0] != 0x05:
            raise ValueError(f"SOCKS versiyon {ver[0]} desteklenmiyor")
        nmethods = ver[1]
        methods = self._recv_exact(nmethods)
        if 0x00 not in methods:
            # No-auth desteklenmiyor, tum methodlari reddet
            self._client.sendall(b"\x05\xff")
            raise ValueError("Istemci no-auth desteklemiyor")
        self._client.sendall(b"\x05\x00")  # No auth secildi

    def _read_addr(self, atyp: int) -> tuple:
        """Adim 2: Hedef adres ve port oku. (host, port) dondur.
        atyp _request_and_relay'den gelir (header[3]).
        """
        if atyp == 0x01:  # IPv4
            raw = self._recv_exact(4)
            host = socket.inet_ntoa(raw)
        elif atyp == 0x03:  # DOMAINNAME
            dlen = self._recv_exact(1)[0]
            host = self._recv_exact(dlen).decode("utf-8", errors="replace")
        elif atyp == 0x04:  # IPv6
            raw = self._recv_exact(16)
            host = socket.inet_ntop(socket.AF_INET6, raw)
        else:
            raise ValueError(f"Bilinmeyen adres tipi: {atyp}")
        port_raw = self._recv_exact(2)
        port = struct.unpack("!H", port_raw)[0]
        return host, port

    def _send_reply(self, rep: int, bind_addr: bytes):
        """SOCKS5 yaniti gonder: ver, rep, rsv, atyp, addr, port"""
        self._client.sendall(b"\x05" + struct.pack("!B", rep) + b"\x00" + bind_addr)

    def _request_and_relay(self):
        """Adim 2: Istek oku, hedefe baglan, relay baslat."""
        header = self._recv_exact(4)
        if header[0] != 0x05:
            raise ValueError(f"Beklenmeyen versiyon: {header[0]}")
        cmd = header[1]
        if cmd != 0x01:  # Sadece CONNECT
            self._send_reply(0x07, b"\x01\x00\x00\x00\x00\x00")
            return
        atyp = header[3]
        host, port = self._read_addr(atyp)
        try:
            self._dst = socket.create_connection((host, port), timeout=15)
        except OSError:
            self._send_reply(0x04, b"\x01\x00\x00\x00\x00\x00")
            return
        try:
            local_ip, local_port = self._dst.getsockname()[:2]
            bind_bytes = b"\x01" + socket.inet_aton(local_ip) + struct.pack("!H", local_port)
        except OSError:
            bind_bytes = b"\x01\x00\x00\x00\x00\x00\x00\x00"
        self._send_reply(0x00, bind_bytes)
        self._relay()

    def _relay(self):
        """select poll ile cift yonlu veri aktarimi."""
        sockets = {self._client, self._dst}
        self._client.setblocking(False)
        self._dst.setblocking(False)
        try:
            while True:
                r, _, _ = select.select(list(sockets), [], [], 60)
                if not r:
                    break  # timeout
                for s in r:
                    other = self._dst if s is self._client else self._client
                    try:
                        data = s.recv(65536)
                        if not data:
                            return
                        other.sendall(data)
                    except OSError:
                        return
        except (OSError, ValueError):
            logger.warning("[fix_01_sessiz_except] Exception")


class _Socks5RequestHandler(_BaseRH):
    """SOCKS5 icin bos handler — Socks5Server process_request'i override eder."""
    def handle(self):
        pass


class Socks5Server(ThreadingMixIn, TCPServer):
    """SOCKS5 proxy sunucusu. Thread-per-connection, daemon thread.
    process_request ile _Socks5Handler kullanir, _Socks5RequestHandler bos gecit.
    """
    daemon_threads = True
    allow_reuse_address = True
    timeout = 60

    def process_request(self, request, client_address):
        """Her baglantiyi SOCKS5 handler ile isle."""
        try:
            h = _Socks5Handler(request, client_address)
            h.handle()
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
        finally:
            try:
                request.close()
            except OSError:
                logger.warning("[fix_01_sessiz_except] OSError")


class ProxyEngine:
    """Proxy sunucusu. Baslat/durdur/durum sorgula."""

    def __init__(self, config: Optional[ProxyConfig] = None):
        self._config = config or ProxyConfig()
        self._server: Optional[ThreadingProxyServer] = None
        self._thread: Optional[threading.Thread] = None
        self._connections = 0
        self._lock = threading.Lock()

    @property
    def is_running(self) -> bool:
        return self._server is not None

    @property
    def connections(self) -> int:
        with self._lock:
            return self._connections

    def start(self) -> dict:
        if self.is_running:
            return {"status": "already_running", "port": self._config.port}
        self._server = ThreadingProxyServer(
            ("0.0.0.0", self._config.port), _ProxyHandler
        )
        self._thread = threading.Thread(
            target=self._server.serve_forever, daemon=True
        )
        self._thread.start()
        return {"status": "started", "port": self._config.port}

    def stop(self) -> dict:
        if not self.is_running:
            return {"status": "not_running"}
        self._server.shutdown()
        self._server.server_close()
        self._server = None
        self._thread = None
        return {"status": "stopped"}

    def status(self) -> dict:
        s5_attrs = {}
        if hasattr(self, "_socks5") and self._socks5 is not None:
            try:
                s5_addr = self._socks5.server_address
                s5_attrs = {"socks5_port": s5_addr[1] if s5_addr else None}
            except Exception:
                s5_attrs = {"socks5_port": None}
        return {
            "running": self.is_running,
            "port": self._config.port if self.is_running else None,
            "connections": self.connections,
            "config": self._config.to_dict(),
            **s5_attrs,
        }

    def start_socks5(self, port: int = 1080) -> dict:
        """SOCKS5 (RFC 1928) — saf Python, bagimsiz thread."""
        if hasattr(self, "_socks5") and self._socks5 is not None:
            return {"status": "already_running", "port": port}
        try:
            server = Socks5Server(("0.0.0.0", port), _Socks5RequestHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            self._socks5 = server
            self._socks5_thread = thread
            return {"status": "socks5_started", "port": port}
        except OSError as e:
            return {"status": "socks5_error", "reason": str(e)}
        except Exception as e:
            return {"status": "socks5_error", "reason": str(e)}

    def stop_socks5(self) -> dict:
        """SOCKS5 sunucusunu durdur."""
        if not hasattr(self, "_socks5") or self._socks5 is None:
            return {"status": "socks5_not_running"}
        try:
            self._socks5.shutdown()
            self._socks5.server_close()
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
        self._socks5 = None
        self._socks5_thread = None
        return {"status": "socks5_stopped"}
