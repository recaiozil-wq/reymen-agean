"""
tools/lsp_tool.py — ReYMeN LSP (Language Server Protocol) Entegrasyonu

Kod analizi, tamamlama, tanıma gitme, hata bildirimi ve biçimlendirme için
Language Server Protocol kullanır. pylsp (Python) ve diğer LSP sunucularını
arka planda çalıştırır.

Kullanım (ReYMeN/ReYMeN agent içinden):
    from tools.lsp_tool import LspClient
    lsp = LspClient()
    lsp.baslat("python")
    sonuc = lsp.diagnostik_al("dosya.py")
    lsp.durdur()
"""

import os
import json
import time
import logging
import subprocess
import threading
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger("reymen_lsp")

# ── LSP Sunucu Yapılandırması ──
LSP_SERVERS = {
    "python": {
        "command": [sys.executable, "-m", "pylsp"],
        "language_id": "python",
        "extensions": [".py"],
    },
    "javascript": {
        "command": ["typescript-language-server", "--stdio"],
        "language_id": "javascript",
        "extensions": [".js", ".jsx"],
    },
    "typescript": {
        "command": ["typescript-language-server", "--stdio"],
        "language_id": "typescript",
        "extensions": [".ts", ".tsx"],
    },
    "json": {
        "command": ["vscode-json-languageserver", "--stdio"],
        "language_id": "json",
        "extensions": [".json"],
    },
    # Varsayılan: Python
    "default": {
        "command": [sys.executable, "-m", "pylsp"],
        "language_id": "python",
        "extensions": [".py"],
    },
}


def _dil_bul(dosya_yolu: str) -> str:
    """Dosya uzantısından LSP dil adını bul."""
    ext = Path(dosya_yolu).suffix.lower()
    for dil, cfg in LSP_SERVERS.items():
        if ext in cfg.get("extensions", []):
            return dil
    return "python"


class LspClient:
    """JSON-RPC üzerinden LSP sunucusu ile iletişim.

    Kullanım:
        lsp = LspClient()
        if lsp.baslat("python"):
            # Diagnostics
            hatalar = lsp.diagnostik_al("script.py", "print('merhaba')\\n")
            for h in hatalar:
                print(f"{h['sevviye']}: {h['mesaj']} (satir {h['satir']})")

            # Completion
            oneriler = lsp.tamamlama_al("script.py", "import os\\nos.", 2, 4)
            for o in oneriler[:5]:
                print(f"  {o['label']} ({o['tip']})")

            # Hover
            hover = lsp.hover_al("script.py", "import os\\nprint(os.getcwd())", 2, 6)
            if hover:
                print(hover)

            # Format
            formatli = lsp.formatla("script.py", "x=1\\ny=2\\n")
            if formatli:
                print(formatli)

            # Definition
            defs = lsp.tanima_git("script.py", "import os\\nprint(os.getcwd())", 2, 9)
            for d in defs:
                print(f"{d['uri']}:{d['satir']}:{d['sutun']}")
        lsp.durdur()
    """

    def __init__(self, root_uri: str = ""):
        self._proc: Optional[subprocess.Popen] = None
        self._reader: Optional[threading.Thread] = None
        self._buffer: list[dict] = []
        self._lock = threading.Lock()
        self._request_id = 0
        self._ready = False
        self._root_uri = root_uri or str(Path.cwd().as_uri())
        self._server_caps = {}
        self._read_buf = b""

    # ── Yaşam Döngüsü ──

    def baslat(self, dil: str = "python", root_uri: str = "") -> bool:
        """LSP sunucusunu başlat.

        Args:
            dil: "python", "javascript", "typescript", "json"
            root_uri: Proje kök URI'si (opsiyonel)

        Returns:
            Başarılı mı
        """
        self.durdur()

        cfg = LSP_SERVERS.get(dil) or LSP_SERVERS["default"]
        cmd = cfg["command"]
        self._dil = dil
        self._language_id = cfg["language_id"]
        if root_uri:
            self._root_uri = root_uri

        try:
            self._proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,  # Binary mode — LSP Content-Length header ile çalışır
            )

            # Okuyucu thread
            self._buffer = []
            self._read_buf = b""
            self._reader = threading.Thread(target=self._oku, daemon=True)
            self._reader.start()

            # Initialize
            init_result = self._istek("initialize", {
                "processId": os.getpid(),
                "rootUri": self._root_uri,
                "capabilities": {
                    "textDocument": {
                        "completion": {"completionItem": {"snippetSupport": True}},
                        "hover": {"contentFormat": ["markdown", "plaintext"]},
                        "definition": {},
                        "formatting": {},
                        "diagnostics": {},
                    }
                },
            })
            if init_result:
                self._server_caps = init_result.get("capabilities", {})
                self._bildirim("initialized", {})  # notification
                self._ready = True
                logger.info(f"LSP baslatildi: {dil} (PID: {self._proc.pid})")
                return True

            logger.error("LSP initialize basarisiz")
            self.durdur()
            return False

        except FileNotFoundError:
            logger.warning(f"LSP sunucusu bulunamadi: {cmd[0]}")
            return False
        except Exception as e:
            logger.error(f"LSP baslatma hatasi: {e}")
            self.durdur()
            return False

    def durdur(self):
        """LSP sunucusunu durdur."""
        if self._proc:
            try:
                self._bildirim("shutdown", {})
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")
            try:
                self._proc.terminate()
                self._proc.wait(timeout=3)
            except Exception:
                try:
                    self._proc.kill()
                    self._proc.wait(timeout=2)
                except Exception:
                    logger.warning("[fix_01_sessiz_except] Exception")
            self._proc = None
        self._ready = False

    @property
    def hazir(self) -> bool:
        return self._ready

    # ── LSP İstekleri ──

    def diagnostik_al(self, dosya_yolu: str, icerik: str) -> list[dict]:
        """Kod hatalarını/uyarılarını al."""
        if not self._ready:
            return [{"sevviye": "HATA", "mesaj": "LSP sunucusu hazir degil", "satir": 0}]

        uri = Path(dosya_yolu).absolute().as_uri()
        self._bildirim("textDocument/didOpen", {
            "textDocument": {
                "uri": uri,
                "languageId": self._language_id,
                "version": 1,
                "text": icerik,
            }
        })

        # Diagnostics pub/sub üzerinden gelir — kısa bekle
        time.sleep(0.5)
        sonuclar = []
        for msg in self._buffer[:]:
            if msg.get("method") == "textDocument/publishDiagnostics":
                for d in msg.get("params", {}).get("diagnostics", []):
                    sonuclar.append({
                        "mesaj": d.get("message", ""),
                        "sevviye": d.get("severity", 1),
                        "satir": d.get("range", {}).get("start", {}).get("line", 0) + 1,
                        "sutun": d.get("range", {}).get("start", {}).get("character", 0) + 1,
                        "kod": d.get("code", ""),
                        "kaynak": d.get("source", ""),
                    })

        with self._lock:
            self._buffer[:] = [m for m in self._buffer if m.get("method") != "textDocument/publishDiagnostics"]

        return sonuclar

    def tamamlama_al(self, dosya_yolu: str, icerik: str, satir: int, sutun: int) -> list[dict]:
        """Kod tamamlama önerileri al."""
        if not self._ready:
            return []

        uri = Path(dosya_yolu).absolute().as_uri()
        self._bildirim("textDocument/didOpen", {
            "textDocument": {"uri": uri, "languageId": self._language_id, "version": 1, "text": icerik},
        })

        sonuc = self._istek("textDocument/completion", {
            "textDocument": {"uri": uri},
            "position": {"line": satir - 1, "character": sutun - 1},
            "context": {"triggerKind": 1},
        })

        if not sonuc:
            return []

        items = sonuc.get("items", [])
        return [
            {
                "label": i.get("label", ""),
                "tip": i.get("detail", i.get("kind", 0)),
                "dokumantasyon": i.get("documentation", {}).get("value", "") if isinstance(i.get("documentation"), dict) else str(i.get("documentation", "")),
            }
            for i in (items if isinstance(items, list) else items.get("items", items))
        ][:10]

    def hover_al(self, dosya_yolu: str, icerik: str, satir: int, sutun: int) -> str:
        """İmleç üzerindeki sembolün dokümantasyonunu al."""
        if not self._ready:
            return ""

        uri = Path(dosya_yolu).absolute().as_uri()
        self._bildirim("textDocument/didOpen", {
            "textDocument": {"uri": uri, "languageId": self._language_id, "version": 1, "text": icerik},
        })

        sonuc = self._istek("textDocument/hover", {
            "textDocument": {"uri": uri},
            "position": {"line": satir - 1, "character": sutun - 1},
        })

        if not sonuc:
            return ""

        contents = sonuc.get("contents", {})
        if isinstance(contents, str):
            return contents
        if isinstance(contents, dict):
            return contents.get("value", "")
        if isinstance(contents, list):
            return "\n".join(
                c.get("value", str(c)) if isinstance(c, dict) else str(c)
                for c in contents
            )
        return ""

    def tanima_git(self, dosya_yolu: str, icerik: str, satir: int, sutun: int) -> list[dict]:
        """Sembolün tanımlandığı yere git."""
        if not self._ready:
            return []

        uri = Path(dosya_yolu).absolute().as_uri()
        self._bildirim("textDocument/didOpen", {
            "textDocument": {"uri": uri, "languageId": self._language_id, "version": 1, "text": icerik},
        })

        sonuc = self._istek("textDocument/definition", {
            "textDocument": {"uri": uri},
            "position": {"line": satir - 1, "character": sutun - 1},
        })

        if not sonuc:
            return []

        # Tek veya dizi olabilir
        locations = sonuc if isinstance(sonuc, list) else [sonuc]
        return [
            {
                "uri": loc.get("uri", ""),
                "satir": loc.get("range", {}).get("start", {}).get("line", 0) + 1,
                "sutun": loc.get("range", {}).get("start", {}).get("character", 0) + 1,
            }
            for loc in locations
        ]

    def formatla(self, dosya_yolu: str, icerik: str) -> str:
        """Kodu LSP sunucusu ile biçimlendir."""
        if not self._ready:
            return icerik

        uri = Path(dosya_yolu).absolute().as_uri()
        self._bildirim("textDocument/didOpen", {
            "textDocument": {"uri": uri, "languageId": self._language_id, "version": 1, "text": icerik},
        })

        edits = self._istek("textDocument/formatting", {
            "textDocument": {"uri": uri},
            "options": {"tabSize": 4, "insertSpaces": True},
        })

        if not edits:
            return icerik

        # Edits'i uygula (sondan başa)
        satirlar = icerik.split("\n")
        for edit in sorted(edits, key=lambda e: e["range"]["start"]["line"], reverse=True):
            r = edit["range"]
            bas_satir = r["start"]["line"]
            bas_sutun = r["start"]["character"]
            bit_satir = r["end"]["line"]
            bit_sutun = r["end"]["character"]

            if bas_satir == bit_satir:
                # Tek satır
                satir = satirlar[bas_satir]
                satirlar[bas_satir] = satir[:bas_sutun] + edit["newText"].rstrip("\n") + satir[bit_sutun:]
            else:
                # Çok satır
                satirlar[bas_satir] = satirlar[bas_satir][:bas_sutun] + edit["newText"].rstrip("\n")
                sil_satir = bit_satir - bas_satir
                for _ in range(sil_satir):
                    if bas_satir + 1 < len(satirlar):
                        satirlar.pop(bas_satir + 1)

        return "\n".join(satirlar)

    def referanslari_bul(self, dosya_yolu: str, icerik: str, satir: int, sutun: int) -> list[dict]:
        """Sembolün tüm referanslarını bul."""
        if not self._ready:
            return []

        uri = Path(dosya_yolu).absolute().as_uri()
        self._bildirim("textDocument/didOpen", {
            "textDocument": {"uri": uri, "languageId": self._language_id, "version": 1, "text": icerik},
        })

        sonuc = self._istek("textDocument/references", {
            "textDocument": {"uri": uri},
            "position": {"line": satir - 1, "character": sutun - 1},
            "context": {"includeDeclaration": True},
        })

        if not sonuc:
            return []

        return [
            {
                "uri": ref.get("uri", ""),
                "satir": ref.get("range", {}).get("start", {}).get("line", 0) + 1,
            }
            for ref in sonuc
        ]

    # ── İç Metodlar ──

    def _istek(self, method: str, params: dict) -> Optional[dict]:
        """JSON-RPC isteği gönder ve yanıt bekle (Content-Length header ile)."""
        if not self._proc or not self._proc.stdin:
            return None

        with self._lock:
            self._request_id += 1
            req_id = self._request_id

        payload = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params,
        }

        try:
            veri = json.dumps(payload).encode("utf-8")
            header = f"Content-Length: {len(veri)}\r\n\r\n".encode("ascii")
            self._proc.stdin.write(header + veri)
            self._proc.stdin.flush()

            # Yanıt bekle (max 10sn)
            bas = time.time()
            while time.time() - bas < 10:
                with self._lock:
                    for i, msg in enumerate(self._buffer):
                        if msg.get("id") == req_id:
                            self._buffer.pop(i)
                            if "error" in msg:
                                logger.warning(f"LSP hatasi [{method}]: {msg['error']}")
                                return None
                            return msg.get("result")
                time.sleep(0.02)

            logger.warning(f"LSP istek zamani asti: {method} (ID={req_id})")
            return None

        except Exception as e:
            logger.error(f"LSP iletisim hatasi [{method}]: {e}")
            return None

    def _bildirim(self, method: str, params: dict):
        """JSON-RPC bildirim gönder (Content-Length header ile, yanıt beklenmez)."""
        if not self._proc or not self._proc.stdin:
            return

        payload = {"jsonrpc": "2.0", "method": method, "params": params}
        try:
            veri = json.dumps(payload).encode("utf-8")
            header = f"Content-Length: {len(veri)}\r\n\r\n".encode("ascii")
            self._proc.stdin.write(header + veri)
            self._proc.stdin.flush()
        except Exception as e:
            logger.error(f"LSP bildirim hatasi [{method}]: {e}")

    def _oku(self):
        """LSP stdout'undan Content-Length header + JSON mesajlarını oku (thread)."""
        if not self._proc or not self._proc.stdout:
            return

        while self._proc and self._proc.poll() is None:
            try:
                # Header oku: "Content-Length: N\r\n\r\n"
                ch = self._proc.stdout.read(1)
                if not ch:
                    break
                self._read_buf += ch

                if self._read_buf.endswith(b"\r\n\r\n"):
                    # Parse Content-Length
                    header_text = self._read_buf.decode("ascii", errors="ignore")
                    length = 0
                    for line in header_text.split("\r\n"):
                        if line.lower().startswith("content-length:"):
                            try:
                                length = int(line.split(":")[1].strip())
                            except ValueError:
                                logger.warning("[fix_01_sessiz_except] ValueError")

                    self._read_buf = b""

                    if length > 0:
                        # İçeriği oku
                        content = self._proc.stdout.read(length)
                        if content:
                            try:
                                msg = json.loads(content.decode("utf-8"))
                                with self._lock:
                                    self._buffer.append(msg)
                            except json.JSONDecodeError:
                                logger.warning("[fix_01_sessiz_except] JSONDecodeError")
            except Exception:
                break

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.durdur()


# ── Tek Seferlik Kullanım (Agent Tool) ──

def _lsp_kontrol_et(dil: str = "python") -> tuple[bool, str]:
    """LSP sunucusunun kurulu olup olmadığını kontrol et."""
    cfg = LSP_SERVERS.get(dil) or LSP_SERVERS["default"]
    cmd = cfg["command"]
    if len(cmd) > 1 and cmd[0] == sys.executable:
        # python -m pylsp: modül kontrolü
        try:
            import importlib
            importlib.import_module(cmd[2])
            return True, f"{cmd[2]} hazir ({sys.executable})"
        except ImportError:
            return False, f"{cmd[2]} bulunamadi"
    return False, "bilinmeyen LSP konfigurasyonu"


def kod_analiz_et(dosya_yolu: str, icerik: str = "") -> dict:
    """Bir Python dosyasını LSP ile analiz et.

    Args:
        dosya_yolu: Analiz edilecek dosya yolu
        icerik: Dosya içeriği (boşsa dosyadan okur)

    Returns:
        {"hazir": bool, "hatalar": [...], "dil": str}
    """
    if not icerik:
        try:
            icerik = Path(dosya_yolu).read_text(encoding="utf-8")
        except Exception as e:
            return {"hazir": False, "hata": str(e), "hatalar": []}

    dil = _dil_bul(dosya_yolu)
    lsp = LspClient()
    if not lsp.baslat(dil):
        # Fallback: Jedi ile basit analiz
        return _jedi_fallback_analiz(icerik, dosya_yolu)

    try:
        hatalar = lsp.diagnostik_al(dosya_yolu, icerik)
        return {
            "hazir": True,
            "hatalar": hatalar,
            "dil": dil,
            "hata_sayisi": len([h for h in hatalar if h["sevviye"] <= 2]),
            "uyari_sayisi": len([h for h in hatalar if h["sevviye"] > 2]),
        }
    finally:
        lsp.durdur()


def kod_tamamla(dosya_yolu: str, icerik: str, satir: int, sutun: int) -> list[dict]:
    """Kod tamamlama önerileri al."""
    dil = _dil_bul(dosya_yolu)
    lsp = LspClient()
    if not lsp.baslat(dil):
        return _jedi_fallback_tamamlama(icerik, satir, sutun)
    try:
        return lsp.tamamlama_al(dosya_yolu, icerik, satir, sutun)
    finally:
        lsp.durdur()


def kod_hover(dosya_yolu: str, icerik: str, satir: int, sutun: int) -> str:
    """Sembol dokümantasyonunu al."""
    dil = _dil_bul(dosya_yolu)
    lsp = LspClient()
    if not lsp.baslat(dil):
        return _jedi_fallback_hover(icerik, satir, sutun)
    try:
        return lsp.hover_al(dosya_yolu, icerik, satir, sutun)
    finally:
        lsp.durdur()


def kod_formatla(dosya_yolu: str, icerik: str = "") -> str:
    """Kodu otomatik biçimlendir."""
    if not icerik:
        try:
            icerik = Path(dosya_yolu).read_text(encoding="utf-8")
        except Exception:
            return ""

    dil = _dil_bul(dosya_yolu)
    lsp = LspClient()
    if not lsp.baslat(dil):
        return _black_fallback(icerik)
    try:
        return lsp.formatla(dosya_yolu, icerik)
    finally:
        lsp.durdur()


# ── Fallback: Jedi (LSP olmadan) ──

def _jedi_fallback_analiz(icerik: str, dosya_yolu: str = "") -> dict:
    """Jedi ile basit kod analizi."""
    try:
        import jedi
        import ast

        hatalar = []

        # 1. Syntax kontrolü
        try:
            ast.parse(icerik)
        except SyntaxError as e:
            hatalar.append({
                "mesaj": f"Syntax hatasi: {e.msg}",
                "sevviye": 1,
                "satir": e.lineno or 0,
                "sutun": e.offset or 0,
                "kod": "syntax",
            })

        # 2. Jedi ile undefined name kontrolü
        try:
            script = jedi.Script(code=icerik, path=dosya_yolu or "temp.py")
            for name in script.get_names(all_scopes=True):
                if name.type == "statement" and not name.full_name:
                    refs = script.get_references(name.line, name.column)
                    using = [r for r in refs if not r.is_definition()]
                    if len(using) > len([r for r in refs if r.is_definition()]):
                        pass  # Sadece tanım kontrolü
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")

        return {
            "hazir": True,
            "hatalar": hatalar,
            "dil": "python",
            "hata_sayisi": len([h for h in hatalar if h["sevviye"] <= 2]),
            "uyari_sayisi": 0,
            "kaynak": "jedi-fallback",
        }
    except ImportError:
        return {"hazir": False, "hata": "Jedi veya ast kurulu degil", "hatalar": [], "hata_sayisi": 0, "uyari_sayisi": 0, "dil": "python"}


def _jedi_fallback_tamamlama(icerik: str, satir: int, sutun: int) -> list[dict]:
    """Jedi ile tamamlama fallback."""
    try:
        import jedi
        script = jedi.Script(code=icerik)
        completions = script.complete(satir, sutun)
        return [
            {"label": c.name, "tip": c.type, "dokumantasyon": c.docstring()[:200]}
            for c in completions[:10]
        ]
    except Exception:
        return []


def _jedi_fallback_hover(icerik: str, satir: int, sutun: int) -> str:
    """Jedi ile hover fallback."""
    try:
        import jedi
        script = jedi.Script(code=icerik)
        definitions = script.infer(satir, sutun)
        if definitions:
            d = definitions[0]
            doc = d.docstring()
            tip = d.type
            if doc:
                return f"**{d.name}** ({tip})\n\n{doc[:500]}"
            return f"**{d.name}** ({tip})"
        return ""
    except Exception:
        return ""


def _black_fallback(icerik: str) -> str:
    """Black ile biçimlendirme fallback."""
    try:
        import black
        mode = black.Mode()
        return black.format_str(icerik, mode=mode)
    except Exception:
        try:
            import autopep8
            return autopep8.fix_code(icerik)
        except Exception:
            return icerik


# ── Motor Kaydı ──
def motor_kaydet(motor: object):
    """Motor.py entegrasyonu: araçları kaydet."""
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return
    motor._plugin_arac_kaydet(
        "LSP_KOD_ANALIZ_ET", kod_analiz_et,
        "Bir Python dosyasını LSP ile analiz eder, hata/uyarıları döndürür",
    )
    motor._plugin_arac_kaydet(
        "LSP_KOD_TAMAMLA", kod_tamamla,
        "İmleç konumunda kod tamamlama önerileri alır",
    )
    motor._plugin_arac_kaydet(
        "LSP_KOD_HOVER", kod_hover,
        "İmleç üzerindeki sembolün dokümantasyonunu alır",
    )
    motor._plugin_arac_kaydet(
        "LSP_KOD_FORMATLA", kod_formatla,
        "Python kodunu otomatik biçimlendirir (pylsp/Black)",
    )


# ── Doğrudan Kullanım ──
if __name__ == "__main__":
    import sys
    test_kod = """
import os
import sys

def merhaba():
    x = 10
    print(x)
    return x

merhaba()
"""

    print("=== LSP Test ===")
    hazir, msg = _lsp_kontrol_et("python")
    print(f"LSP Kontrol: {hazir} ({msg})")

    if hazir:
        lsp = LspClient()
        if lsp.baslat("python"):
            print("\n=== Diagnostics ===")
            hatalar = lsp.diagnostik_al("test.py", test_kod)
            for h in hatalar:
                print(f"  [{h['sevviye']}] Satir {h['satir']}: {h['mesaj']}")

            print("\n=== Completion (imleç 4. satir, 9. sutun) ===")
            oneriler = lsp.tamamlama_al("test.py", test_kod, 4, 9)
            for o in oneriler[:5]:
                print(f"  {o['label']}")

            lsp.durdur()
        else:
            print("LSP baslatilamadi, Jedi fallback...")
            sonuc = _jedi_fallback_analiz(test_kod, "test.py")
            print(f"  Hata sayisi: {sonuc.get('hata_sayisi', '?')}")
    else:
        print("pylsp PATH'te bulunamadi — Jedi fallback...")
        sonuc = _jedi_fallback_analiz(test_kod, "test.py")
        print(f"  Hazir: {sonuc.get('hazir')}, Hata sayisi: {sonuc.get('hata_sayisi', '?')}")
