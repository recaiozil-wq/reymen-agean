"""
ReYMeN Service Orchestrator — start.py

Usage:
    python start.py                    # All services
    python start.py --dashboard-only   # Web UI only
    python start.py --agent-only       # Gateway only

Architecture:
    WebUI (subprocess, port 8080)
    TelegramBot (subprocess, token from .env)
    Gateway (thread, multi-channel)

Graceful shutdown on Ctrl+C: terminate → wait(5) → kill
"""

import os, sys, time, signal, subprocess, threading, socket, json
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).parent

class Servis:
    """Base service manager: process/thread lifecycle."""
    def __init__(self, ad, env=None):
        self.ad = ad
        self.env = env or os.environ.copy()
        self.process = None
        self.thread = None
        self.durum = "durdu"  # durdu / basliyor / calisiyor / hata

    def baslat(self):
        raise NotImplementedError

    def durdur(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.durum = "durdu"

    def saglik_kontrol(self):
        if self.process and self.process.poll() is not None:
            self.durum = "hata"
            return False
        return self.durum == "calisiyor"
