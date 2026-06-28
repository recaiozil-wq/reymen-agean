# -*- coding: utf-8 -*-
"""tests/test_skills.py — Skill modulu testleri."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSkillUtils:
    def test_skill_sayisi(self):
        from skill_utils import skill_sayisi
        assert skill_sayisi() >= 10

    def test_kategoriler(self):
        from skill_utils import kategorileri_listele
        katlar = kategorileri_listele()
        assert len(katlar) >= 3

    def test_skill_ara(self):
        from skill_utils import skill_ara
        sonuc = skill_ara("test")
        assert isinstance(sonuc, list)

    def test_skill_bul(self):
        from skill_utils import skill_bul
        from skill_commands import listele
        liste = listele()
        assert len(liste) > 50


class TestSkillCommands:
    def test_istatistik(self):
        from skill_commands import istatistik
        ist = istatistik()
        assert "SKILL.md" in ist


class TestSkillBundles:
    def test_paket_listele(self):
        from skill_bundles import paket_listele
        sonuc = paket_listele()
        assert isinstance(sonuc, str)


class TestSkillsHub:
    def test_hub_listele(self):
        from skills_hub import hub_listele
        sonuc = hub_listele()
        assert "ReYMeN" in sonuc.lower() or "Hub" in sonuc
