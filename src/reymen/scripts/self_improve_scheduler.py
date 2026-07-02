# -*- coding: utf-8 -*-
"""
self_improve_scheduler.py — ReYMeN Autonomous Self-Improvement Scheduler.

Manages ALL periodic self-improvement tasks from a SINGLE point:

  1. self_improve_cron  → Every 6 hours: collect metrics, analyze, report
  2. hafiza_budama      → Every 24 hours: clean old/unused memory
  3. auto_budama        → Every 12 hours: automatic code pruning
  4. skill_iyilestirme  → Every 24 hours: skill usage analysis + improvement
  5. nudge_model        → Every 48 hours: user model summary + report
  6. konusmadan_skill   → Every 6 hours: auto-extract skills from conversations

Usage:
    python -m reymen.scripts.self_improve_scheduler --run-all   # Run all
    python -m reymen.scripts.self_improve_scheduler --status    # Show status
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent  # src/
PROJE_KOK = ROOT.parent  # proje kok
sys.path.insert(0, str(ROOT))

DURUM_DOSYASI = ROOT / ".ReYMeN" / "self_improve_scheduler.json"


class KendiniGelistirScheduler:
    """Manages all self-improvement tasks."""

    def __init__(self):
        self.sonuc: dict[str, dict] = {}

    def gorev_calistir(self, ad: str, fonk, *args, **kwargs) -> dict:
        """Run a single self-improvement task and record the result."""
        baslama = time.time()
        basarili = False
        mesaj = ""
        try:
            sonuc = fonk(*args, **kwargs)
            basarili = True
            if isinstance(sonuc, str):
                mesaj = sonuc[:200]
            elif isinstance(sonuc, dict):
                mesaj = sonuc.get("mesaj", sonuc.get("ozet", str(sonuc)[:200]))
            else:
                mesaj = str(sonuc)[:200]
        except Exception as e:
            mesaj = f"[HATA] {e}"
            log.error("[SELF_IMPROVE] %s basarisiz: %s", ad, e)

        sure = round(time.time() - baslama, 2)
        kayit = {
            "son_gorev": datetime.now(timezone.utc).isoformat(),
            "basarili": basarili,
            "sure_sn": sure,
            "mesaj": mesaj,
        }
        self.sonuc[ad] = kayit
        return kayit

    def tumunu_calistir(self) -> dict:
        """Tüm self-improvement görevlerini sırayla çalıştır."""
        log.info("[SELF_IMPROVE] === Tum gorevler baslatiliyor ===")

        # 1. Self-improve metrik toplama
        self.gorev_calistir("self_improve", self._si_cron_cagir)

        # 2. Hafıza budama (dry-run=False)
        self.gorev_calistir("hafiza_budama", self._hafiza_budama_cagir)

        # 3. Skill iyileştirme
        self.gorev_calistir("skill_iyilestirme", self._skill_iyilestir_cagir)

        # 4. Proaktif kontrol durumu
        self.gorev_calistir("proaktif_kontrol", self._proaktif_durum_cagir)

        # 5. Auto budama (kod budaması)
        self.gorev_calistir("auto_budama", self._auto_budama_cagir)

        # 5. Nudge model raporu
        self.gorev_calistir("nudge_model", self._nudge_raporu_cagir)

        # Durumu kaydet
        self._durum_kaydet()

        log.info("[SELF_IMPROVE] === Tum gorevler tamamlandi ===")
        return self.sonuc

    def _hafiza_budama_cagir(self) -> str:
        """Hafıza budamayı çalıştırır."""
        import importlib
        try:
            mod = importlib.import_module("reymen.hafiza.hafiza_budama")
            budayici = mod.HafizaBudama() if hasattr(mod, 'HafizaBudama') else None
            if budayici is None:
                # Try running directly
                import subprocess
                r = subprocess.run(
                    ["python", "-m", "reymen.hafiza.hafiza_budama"],
                    capture_output=True, text=True, timeout=60,
                    cwd=str(PROJE_KOK), env={**os.environ, "PYTHONPATH": str(ROOT)}
                )
                return r.stdout[:200] or r.stderr[:200] or "tamam"
            rapor = budayici.budama_yap(dry_run=False)
            if isinstance(rapor, dict):
                return f"Budanan: {rapor.get('budanan', 0)}"
            return f"Budama: {rapor}"
        except Exception as e:
            return f"[HATA] {e}"

    def _si_cron_cagir(self) -> str:
        """Self-improve cron metriklerini çalıştırır."""
        import subprocess
        r = subprocess.run(
            [sys.executable, "-m", "reymen.scripts.self_improve_cron"],
            capture_output=True, text=True, timeout=120,
            cwd=str(PROJE_KOK), env={**os.environ, "PYTHONPATH": str(ROOT)}
        )
        return r.stdout[:200] or r.stderr[:200] or "tamam"

    def _skill_iyilestir_cagir(self) -> str:
        """Skill iyileştirme sistemini çalıştırır."""
        from reymen.scripts.skill_iyilestirici import SkillIyilestirici
        iyilestirici = SkillIyilestirici()
        adaylar = iyilestirici.iyilestirme_adaylari_bul()
        if adaylar:
            sonuc = iyilestirici.otomatik_iyilestir()
            if isinstance(sonuc, dict):
                iyilestirilen = sonuc.get('iyilestirilen', sonuc.get('islenen', 0))
            else:
                iyilestirilen = int(sonuc) if sonuc else 0
            return f"{len(adaylar)} aday bulundu, {iyilestirilen} iyilestirildi"
        return "Iyilestirme adayi bulunamadi"

    def _auto_budama_cagir(self) -> str:
        """Kod budama sistemini çalıştırır."""
        try:
            from reymen.cereyan.auto_budama import AutoBudama
            budayici = AutoBudama()
            rapor = budayici.budama_yap()
            if isinstance(rapor, dict):
                return f"Budanan kod: {rapor.get('budanan', 0)}"
            return f"Budama sonucu: {rapor}"
        except ImportError:
            return "[ATLANDI] auto_budama modulu yok"

    def _nudge_raporu_cagir(self) -> str:
        """Nudge model raporunu oluşturur."""
        try:
            from reymen.cereyan.nudge_model import NudgeModel
            model = NudgeModel()
            rapor = model.rapor_uret()
            return rapor[:200]
        except ImportError:
            return "[ATLANDI] nudge_model modulu yok"

    def _proaktif_durum_cagir(self) -> str:
        """Proaktif kontrol durum raporunu alır."""
        try:
            from reymen.cereyan.proaktif_kontrol import proaktif_baslat
            denetci = proaktif_baslat()
            return denetci.durum_raporu()
        except ImportError:
            return "[ATLANDI] proaktif_kontrol modulu yok"

    def _durum_kaydet(self):
        """Son durumu JSON'a kaydet."""
        DURUM_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f:
            json.dump({
                "son_guncelleme": datetime.now(timezone.utc).isoformat(),
                "gorevler": self.sonuc,
            }, f, indent=2, ensure_ascii=False)

    def durum_goster(self) -> str:
        """Kayıtlı durumu göster."""
        if not DURUM_DOSYASI.exists():
            return "Henüz çalıştırılmamış."
        with open(DURUM_DOSYASI, "r", encoding="utf-8") as f:
            data = json.load(f)
        lines = [f"Son güncelleme: {data.get('son_guncelleme', '?')}"]
        for ad, kayit in data.get("gorevler", {}).items():
            durum = "✅" if kayit.get("basarili") else "❌"
            lines.append(f"  {durum} {ad}: {kayit.get('mesaj', '')} ({kayit.get('sure_sn', '?')}s)")
        return "\n".join(lines)


def main():
    """Komut satırı giriş noktası."""
    logging.basicConfig(level=logging.INFO, format="[SI] %(message)s")

    if "--run-all" in sys.argv:
        scheduler = KendiniGelistirScheduler()
        scheduler.tumunu_calistir()
        print(scheduler.durum_goster())
    elif "--status" in sys.argv:
        scheduler = KendiniGelistirScheduler()
        print(scheduler.durum_goster())
    else:
        print("Kullanım:")
        print("  python -m reymen.scripts.self_improve_scheduler --run-all")
        print("  python -m reymen.scripts.self_improve_scheduler --status")


if __name__ == "__main__":
    main()
