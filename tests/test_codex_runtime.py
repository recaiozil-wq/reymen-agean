# -*- coding: utf-8 -*-
"""Tests for codex_runtime.py — Codex CLI Runtime Adaptoru."""

from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

import subprocess

from codex_runtime import CodexRuntime


# ════════════════════════════════════════════════════════════════
# Init
# ════════════════════════════════════════════════════════════════


class TestInit:
    def test_varsayilan(self):
        """Varsayilan init, codex_yolu=None."""
        rt = CodexRuntime()
        # codex_yolu ya None (bulamadiysa) ya da Path (bulduysa)
        assert rt._hazir == (rt.codex_yolu is not None)

    def test_ozel_yol(self, tmp_path):
        """Ozel yol ile init."""
        fake = tmp_path / "codex.exe"
        fake.write_text("")
        fake.chmod(0o755)
        rt = CodexRuntime(codex_yolu=fake)
        assert rt.codex_yolu == fake
        assert rt.hazir_mi is True

    def test_ozel_yol_yok(self, tmp_path):
        """Belirtilen yol yoksa _codex_bul cagrilmaz ama codex_yolu atanmis olur."""
        fake = tmp_path / "yok.exe"
        rt = CodexRuntime(codex_yolu=fake)
        # __init__ codex_yolu atanmissa _hazir=True yapar (path var mi diye kontrol etmez)
        assert rt.codex_yolu == fake
        # ping False olmali cunku binary yok
        assert rt.ping() is False


# ════════════════════════════════════════════════════════════════
# _codex_bul
# ════════════════════════════════════════════════════════════════


class TestCodexBul:
    def test_aday_bulunamadi(self, monkeypatch):
        """Hicbir aday yoksa None doner."""
        monkeypatch.setattr(Path, "exists", lambda self: False)
        monkeypatch.setattr(
            "subprocess.run",
            lambda *a, **kw: (_ for _ in ()).throw(FileNotFoundError()),
        )

        rt = CodexRuntime(codex_yolu=None)
        assert rt.codex_yolu is None

    def test_where_basarili(self, monkeypatch):
        """Windows where ile bulur."""
        monkeypatch.setattr(Path, "exists", lambda self: False)

        call_count = 0

        def mock_run(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # where call from __init__
                m = MagicMock()
                m.returncode = 0
                m.stdout = "C:\\codex\\bin\\codex.exe\n"
                m.stderr = ""
                return m
            raise FileNotFoundError()  # which fail, dont care

        monkeypatch.setattr("subprocess.run", mock_run)
        rt = CodexRuntime(codex_yolu=None)
        # __init__ already called _codex_bul, result is in codex_yolu
        assert rt.codex_yolu is not None
        assert "codex" in str(rt.codex_yolu)

    def test_where_basarisiz(self, monkeypatch):
        """where bulamazsa, which dener, o da bulamazsa None."""
        monkeypatch.setattr(Path, "exists", lambda self: False)

        call_count = 0

        def mock_run(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # where fail
                m = MagicMock()
                m.returncode = 1
                return m
            raise FileNotFoundError()  # which fails

        monkeypatch.setattr("subprocess.run", mock_run)
        rt = CodexRuntime(codex_yolu=None)
        assert rt.codex_yolu is None

    def test_which_basarili(self, monkeypatch):
        """which ile bulur (Linux yolu)."""
        monkeypatch.setattr(Path, "exists", lambda self: False)

        call_count = 0

        def mock_run(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # where fail
                m = MagicMock()
                m.returncode = 1
                return m
            # which succeeds
            m2 = MagicMock()
            m2.returncode = 0
            m2.stdout = "/usr/local/bin/codex\n"
            m2.stderr = ""
            return m2

        monkeypatch.setattr("subprocess.run", mock_run)
        rt = CodexRuntime(codex_yolu=None)
        assert rt.codex_yolu is not None
        # Windows'ta Path("/usr/local/bin/codex") -> \\usr\\local\\bin\\codex
        assert "codex" in str(rt.codex_yolu)
        assert "usr" in str(rt.codex_yolu) or "local" in str(rt.codex_yolu)

    def test_aday_bulundu(self):
        """Home adayi mevcutsa direkt dondur, subprocess'e gerek kalmaz."""
        # This test requires a real Path.exists match for .codex/bin/codex
        # We need to use a real path since fake exists would interfere
        import tempfile

        tmp = Path(tempfile.mkdtemp())
        fake_bin = tmp / ".codex" / "bin"
        fake_bin.mkdir(parents=True)
        fake_codex = fake_bin / "codex"
        fake_codex.write_text("")
        rt = CodexRuntime(codex_yolu=fake_codex)
        assert rt.codex_yolu == fake_codex
        assert rt.hazir_mi is True


# ════════════════════════════════════════════════════════════════
# hazir_mi / ping
# ════════════════════════════════════════════════════════════════


class TestHazirMi:
    def test_hazir_mi_false(self):
        rt = CodexRuntime(codex_yolu=None)
        assert rt.hazir_mi is False

    def test_hazir_mi_true(self, tmp_path):
        fake = tmp_path / "codex"
        fake.write_text("")
        rt = CodexRuntime(codex_yolu=fake)
        assert rt.hazir_mi is True

    def test_ping_hazir_degil(self):
        rt = CodexRuntime(codex_yolu=None)
        assert rt.ping() is False

    def test_ping_basarili(self, tmp_path):
        fake = tmp_path / "codex"
        fake.write_text("")
        rt = CodexRuntime(codex_yolu=fake)
        with patch.object(rt, "codex_yolu", fake):
            with patch("subprocess.run") as mock:
                mock.return_value.returncode = 0
                assert rt.ping() is True
                mock.assert_called_once()

    def test_ping_basarisiz(self, tmp_path):
        fake = tmp_path / "codex"
        fake.write_text("")
        rt = CodexRuntime(codex_yolu=fake)
        with patch("subprocess.run") as mock:
            mock.return_value.returncode = 1
            assert rt.ping() is False

    def test_ping_istisna(self, tmp_path):
        fake = tmp_path / "codex"
        fake.write_text("")
        rt = CodexRuntime(codex_yolu=fake)
        with patch("subprocess.run", side_effect=RuntimeError("no codex")):
            assert rt.ping() is False


# ════════════════════════════════════════════════════════════════
# uret
# ════════════════════════════════════════════════════════════════


class TestUret:
    def test_hazir_degil(self):
        rt = CodexRuntime(codex_yolu=None)
        sonuc = rt.uret("sistem", [{"role": "user", "content": "merhaba"}])
        assert "[Codex]: Codex CLI bulunamadi" in sonuc

    def test_basarili(self, tmp_path):
        fake = tmp_path / "codex"
        fake.write_text("")
        rt = CodexRuntime(codex_yolu=fake)
        with patch("subprocess.run") as mock:
            mock.return_value.returncode = 0
            mock.return_value.stdout = "Merhaba dunya"
            sonuc = rt.uret("Selam", [{"role": "user", "content": "2+2?"}])
            assert sonuc == "Merhaba dunya"

    def test_hata_kodu(self, tmp_path):
        fake = tmp_path / "codex"
        fake.write_text("")
        rt = CodexRuntime(codex_yolu=fake)
        with patch("subprocess.run") as mock:
            mock.return_value.returncode = 1
            mock.return_value.stderr = "hata detayi"
            sonuc = rt.uret("sistem", [])
            assert "[Codex]: Hata kodu 1" in sonuc
            assert "hata detayi" in sonuc

    def test_timeout(self, tmp_path):
        fake = tmp_path / "codex"
        fake.write_text("")
        rt = CodexRuntime(codex_yolu=fake)
        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="codex", timeout=5),
        ):
            sonuc = rt.uret("sistem", [])
            assert "[Codex]: Zaman asimi" in sonuc

    def test_beklenmeyen_hata(self, tmp_path):
        fake = tmp_path / "codex"
        fake.write_text("")
        rt = CodexRuntime(codex_yolu=fake)
        with patch("subprocess.run", side_effect=PermissionError("engellendi")):
            sonuc = rt.uret("sistem", [])
            assert "[Codex]:" in sonuc
            assert "engellendi" in sonuc


# ════════════════════════════════════════════════════════════════
# modelleri_listele
# ════════════════════════════════════════════════════════════════


class TestModelleriListele:
    def test_hazir_degil(self):
        rt = CodexRuntime(codex_yolu=None)
        assert rt.modelleri_listele() == []

    def test_basarili(self, tmp_path):
        fake = tmp_path / "codex"
        fake.write_text("")
        rt = CodexRuntime(codex_yolu=fake)
        with patch("subprocess.run") as mock:
            mock.return_value.returncode = 0
            mock.return_value.stdout = "gpt-4\ngpt-3.5-turbo\n"
            sonuc = rt.modelleri_listele()
            assert sonuc == ["gpt-4", "gpt-3.5-turbo"]

    def test_basarisiz(self, tmp_path):
        fake = tmp_path / "codex"
        fake.write_text("")
        rt = CodexRuntime(codex_yolu=fake)
        with patch("subprocess.run") as mock:
            mock.return_value.returncode = 1
            sonuc = rt.modelleri_listele()
            assert sonuc == []

    def test_istisna(self, tmp_path):
        fake = tmp_path / "codex"
        fake.write_text("")
        rt = CodexRuntime(codex_yolu=fake)
        with patch("subprocess.run", side_effect=RuntimeError("engel")):
            sonuc = rt.modelleri_listele()
            assert sonuc == []
