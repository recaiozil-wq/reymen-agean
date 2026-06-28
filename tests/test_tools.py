# -*- coding: utf-8 -*-
"""tests/test_tools.py — pytest ile tüm tool'ları test et."""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))


# ── MEMORY ───────────────────────────────────────────
class TestMemoryTool:
    def test_yaz_ve_oku(self, tmp_path, monkeypatch):
        import memory_tool
        monkeypatch.setattr(memory_tool, "_ReYMeN_DIR", tmp_path)
        assert "kaydedildi" in memory_tool.run("yaz", "TEST.md", "merhaba")
        assert memory_tool.run("oku", "TEST.md") == "merhaba"

    def test_olmayan_dosya(self, tmp_path, monkeypatch):
        import memory_tool
        monkeypatch.setattr(memory_tool, "_ReYMeN_DIR", tmp_path)
        assert memory_tool.run("oku", "YOK.md") == "[Yok]"

    def test_bos_icerik(self, tmp_path, monkeypatch):
        import memory_tool
        monkeypatch.setattr(memory_tool, "_ReYMeN_DIR", tmp_path)
        sonuc = memory_tool.run("yaz", "X.md", "")
        assert "[Hata]" in sonuc

    def test_gecersiz_eylem(self):
        import memory_tool
        assert "[Hata]" in memory_tool.run("sil")


# ── SKILL ────────────────────────────────────────────
class TestSkillTool:
    def test_bos_klasor(self, tmp_path, monkeypatch):
        import skill_tool
        monkeypatch.setattr(skill_tool, "SKILLS_DIR", tmp_path)
        assert "[Bilgi]" in skill_tool.run("liste")

    def test_skill_listele(self, tmp_path, monkeypatch):
        import skill_tool
        monkeypatch.setattr(skill_tool, "SKILLS_DIR", tmp_path)
        (tmp_path / "ornek.md").write_text("# Test")
        sonuc = skill_tool.run("liste")
        assert "ornek.md" in sonuc

    def test_skill_goruntule(self, tmp_path, monkeypatch):
        import skill_tool
        monkeypatch.setattr(skill_tool, "SKILLS_DIR", tmp_path)
        (tmp_path / "xyz.md").write_text("içerik", encoding="utf-8")
        assert skill_tool.run("goruntule", "xyz") == "içerik"

    def test_olmayan_skill(self, tmp_path, monkeypatch):
        import skill_tool
        monkeypatch.setattr(skill_tool, "SKILLS_DIR", tmp_path)
        assert "[Hata]" in skill_tool.run("goruntule", "yok_skill")


# ── WEB SEARCH ───────────────────────────────────────
class TestWebSearchTool:
    def test_bos_sorgu(self):
        import web_search_tool
        assert "[Hata]" in web_search_tool.run("")

    def test_gecersiz_kaynak(self):
        import web_search_tool
        assert "[Hata]" in web_search_tool.run("test", kaynak="bing")

    def test_ddg_network(self, monkeypatch):
        """Network mock — gerçek istek atma."""
        import web_search_tool
        import json

        sahte_veri = json.dumps({
            "AbstractText": "Test özeti",
            "AbstractURL":  "https://ornek.com",
            "RelatedTopics": [],
        }).encode("utf-8")

        class SahteCevap:
            def read(self): return sahte_veri
            def __enter__(self): return self
            def __exit__(self, *_): pass

        monkeypatch.setattr(
            "urllib.request.urlopen",
            lambda *a, **kw: SahteCevap()
        )
        sonuc = web_search_tool.run("python")
        assert "Test özeti" in sonuc


# ── EXECUTE CODE ─────────────────────────────────────
class TestExecuteCodeTool:
    def test_bos_kod(self):
        import execute_code_tool
        assert "[Hata]" in execute_code_tool.run("")

    def test_gecersiz_zaman_asimi(self):
        import execute_code_tool
        # String limit → varsayılan kullanılmalı, patlamalı
        sonuc = execute_code_tool.run("print(1)", zaman_asimi="abc")
        # Hata değil, varsayılanla devam etmeli
        assert "[Hata]" not in sonuc or "kurulu" in sonuc.lower()


# ── DELEGATE TASK ────────────────────────────────────
class TestDelegateTaskTool:
    def test_bos_gorev(self):
        import delegate_task_tool
        assert "[Hata]" in delegate_task_tool.run("")

    def test_main_py_yok(self, monkeypatch):
        import delegate_task_tool
        from pathlib import Path
        monkeypatch.setattr(delegate_task_tool, "_MAIN_PY", Path("/yok/main.py"))
        assert "[Hata]" in delegate_task_tool.run("bir görev")
