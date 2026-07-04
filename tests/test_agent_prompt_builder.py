# -*- coding: utf-8 -*-
"""
test_agent_prompt_builder.py — agent/prompt_builder.py testleri (~35 test)
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock, mock_open
from pathlib import Path
import os


# ---------------------------------------------------------------------------
# Sabitler ve yardimcilar
# ---------------------------------------------------------------------------


class TestConstants:
    def test_DEFAULT_AGENT_IDENTITY_var(self):
        from agent.prompt_builder import DEFAULT_AGENT_IDENTITY

        assert isinstance(DEFAULT_AGENT_IDENTITY, str)
        assert "Hermes Agent" in DEFAULT_AGENT_IDENTITY
        assert len(DEFAULT_AGENT_IDENTITY) > 50

    def test_MEMORY_GUIDANCE_var(self):
        from agent.prompt_builder import MEMORY_GUIDANCE

        assert isinstance(MEMORY_GUIDANCE, str)
        assert (
            "memory" in MEMORY_GUIDANCE.lower() or "hafiza" in MEMORY_GUIDANCE.lower()
        )

    def test_TOOL_USE_ENFORCEMENT_GUIDANCE_var(self):
        from agent.prompt_builder import TOOL_USE_ENFORCEMENT_GUIDANCE

        assert isinstance(TOOL_USE_ENFORCEMENT_GUIDANCE, str)
        assert "Tool-use enforcement" in TOOL_USE_ENFORCEMENT_GUIDANCE

    def test_TOOL_USE_ENFORCEMENT_MODELS(self):
        from agent.prompt_builder import TOOL_USE_ENFORCEMENT_MODELS

        assert isinstance(TOOL_USE_ENFORCEMENT_MODELS, tuple)
        assert "gpt" in TOOL_USE_ENFORCEMENT_MODELS
        assert "deepseek" in TOOL_USE_ENFORCEMENT_MODELS

    def test_DEVELOPER_ROLE_MODELS(self):
        from agent.prompt_builder import DEVELOPER_ROLE_MODELS

        assert "gpt-5" in DEVELOPER_ROLE_MODELS
        assert "codex" in DEVELOPER_ROLE_MODELS

    def test_PLATFORM_HINTS_anahtarlari(self):
        from agent.prompt_builder import PLATFORM_HINTS

        assert "whatsapp" in PLATFORM_HINTS
        assert "telegram" in PLATFORM_HINTS
        assert "discord" in PLATFORM_HINTS
        assert "cli" in PLATFORM_HINTS

    def test_SKILLS_GUIDANCE_var(self):
        from agent.prompt_builder import SKILLS_GUIDANCE

        assert isinstance(SKILLS_GUIDANCE, str)
        assert "skill" in SKILLS_GUIDANCE.lower()

    def test_TASK_COMPLETION_GUIDANCE_var(self):
        from agent.prompt_builder import TASK_COMPLETION_GUIDANCE

        assert isinstance(TASK_COMPLETION_GUIDANCE, str)
        assert "Finishing the job" in TASK_COMPLETION_GUIDANCE

    def test_OPENAI_MODEL_EXECUTION_GUIDANCE_var(self):
        from agent.prompt_builder import OPENAI_MODEL_EXECUTION_GUIDANCE

        assert isinstance(OPENAI_MODEL_EXECUTION_GUIDANCE, str)
        assert "Execution discipline" in OPENAI_MODEL_EXECUTION_GUIDANCE

    def test_GOOGLE_MODEL_OPERATIONAL_GUIDANCE_var(self):
        from agent.prompt_builder import GOOGLE_MODEL_OPERATIONAL_GUIDANCE

        assert isinstance(GOOGLE_MODEL_OPERATIONAL_GUIDANCE, str)
        assert (
            "Google model operational directives" in GOOGLE_MODEL_OPERATIONAL_GUIDANCE
        )


# ---------------------------------------------------------------------------
# _scan_context_content
# ---------------------------------------------------------------------------


class TestScanContextContent:
    def test_temiz_icerik_degismez(self):
        from agent.prompt_builder import _scan_context_content

        with patch("agent.prompt_builder._scan_for_threats", return_value=[]):
            result = _scan_context_content("temiz icerik", "test.md")
        assert result == "temiz icerik"

    def test_tehdit_bulunursa_bloklanir(self):
        from agent.prompt_builder import _scan_context_content

        with patch(
            "agent.prompt_builder._scan_for_threats", return_value=["injection"]
        ):
            result = _scan_context_content("zararli icerik", "test.md")
        assert "BLOCKED" in result
        assert "test.md" in result
        assert "injection" in result

    def test_bos_icerik(self):
        from agent.prompt_builder import _scan_context_content

        with patch("agent.prompt_builder._scan_for_threats", return_value=[]):
            result = _scan_context_content("", "empty.md")
        assert result == ""


# ---------------------------------------------------------------------------
# _find_git_root
# ---------------------------------------------------------------------------


class TestFindGitRoot:
    def test_git_root_bulunur(self, tmp_path):
        from agent.prompt_builder import _find_git_root

        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        sub_dir = tmp_path / "src" / "modul"
        sub_dir.mkdir(parents=True)
        result = _find_git_root(sub_dir)
        assert result == tmp_path

    def test_git_yoksa_none(self, tmp_path):
        from agent.prompt_builder import _find_git_root

        sub_dir = tmp_path / "src" / "modul"
        sub_dir.mkdir(parents=True)
        result = _find_git_root(sub_dir)
        assert result is None

    def test_gecerli_dizinde_git(self, tmp_path):
        from agent.prompt_builder import _find_git_root

        (tmp_path / ".git").mkdir()
        result = _find_git_root(tmp_path)
        assert result == tmp_path


# ---------------------------------------------------------------------------
# _find_ReYMeN_md
# ---------------------------------------------------------------------------


class TestFindReYMeN_md:
    def test_ReYMeN_md_bulunur(self, tmp_path):
        from agent.prompt_builder import _find_ReYMeN_md

        (tmp_path / ".git").mkdir()
        md_file = tmp_path / ".ReYMeN.md"
        md_file.write_text("test")
        result = _find_ReYMeN_md(tmp_path)
        assert result == md_file

    def test_ReYMeN_md_yoksa_none(self, tmp_path):
        from agent.prompt_builder import _find_ReYMeN_md

        (tmp_path / ".git").mkdir()
        result = _find_ReYMeN_md(tmp_path)
        assert result is None

    def test_parent_bulunur_ama_git_kokunde_durur(self, tmp_path):
        from agent.prompt_builder import _find_ReYMeN_md

        (tmp_path / ".git").mkdir()
        sub = tmp_path / "subdir"
        sub.mkdir()
        # .ReYMeN.md root'ta
        md_file = tmp_path / ".ReYMeN.md"
        md_file.write_text("test")
        result = _find_ReYMeN_md(sub)
        assert result == md_file


# ---------------------------------------------------------------------------
# _strip_yaml_frontmatter
# ---------------------------------------------------------------------------


class TestStripYamlFrontmatter:
    def test_frontmatter_yoksa_ayni(self):
        from agent.prompt_builder import _strip_yaml_frontmatter

        assert _strip_yaml_frontmatter("sadece metin") == "sadece metin"

    def test_frontmatter_varsa_strip_eder(self):
        from agent.prompt_builder import _strip_yaml_frontmatter

        content = "---\nkey: value\n---\nbody"
        assert _strip_yaml_frontmatter(content) == "body"

    def test_bos_frontmatter(self):
        from agent.prompt_builder import _strip_yaml_frontmatter

        content = "---\n---\nicerik"
        assert _strip_yaml_frontmatter(content) == "icerik"

    def test_frontmatter_sonrasi_bosluk_temizlenir(self):
        from agent.prompt_builder import _strip_yaml_frontmatter

        content = "---\nkey: val\n---\n\n\nbody"
        assert _strip_yaml_frontmatter(content) == "body"

    def test_eksik_kapanis_frontmatter(self):
        from agent.prompt_builder import _strip_yaml_frontmatter

        content = "---\nkey: val\nnormal metin"
        assert _strip_yaml_frontmatter(content) == content


# ---------------------------------------------------------------------------
# _truncate_content
# ---------------------------------------------------------------------------


class TestTruncateContent:
    def test_kisa_icerik_kesilmez(self):
        from agent.prompt_builder import _truncate_content

        assert _truncate_content("kisa", "test.md") == "kisa"

    def test_uzun_icerik_kesilir(self):
        from agent.prompt_builder import _truncate_content, CONTEXT_FILE_MAX_CHARS

        content = "x" * (CONTEXT_FILE_MAX_CHARS + 500)
        result = _truncate_content(content, "buyuk.md")
        assert len(result) < len(content)
        assert "truncated" in result

    def test_kesinti_marker_var(self):
        from agent.prompt_builder import _truncate_content, CONTEXT_FILE_MAX_CHARS

        content = "a" * (CONTEXT_FILE_MAX_CHARS + 100)
        result = _truncate_content(content, "test.md")
        assert "[...truncated test.md:" in result


# ---------------------------------------------------------------------------
# load_soul_md
# ---------------------------------------------------------------------------


class TestLoadSoulMd:
    def test_dosya_yoksa_none(self):
        from agent.prompt_builder import load_soul_md, _SKILLS_PROMPT_CACHE

        _SKILLS_PROMPT_CACHE.clear()
        with patch("agent.prompt_builder.get_reymen_home") as mock_home:
            mock_home.return_value = Path("/nonexistent")
            result = load_soul_md()
        assert result is None

    def test_dosya_var_okunur(self):
        from agent.prompt_builder import load_soul_md

        with patch("agent.prompt_builder.get_reymen_home") as mock_home:
            mock_path = MagicMock(spec=Path)
            mock_path.exists.return_value = True
            mock_path.read_text.return_value = "Benim soul md'im"
            mock_home.return_value = MagicMock()
            mock_home.return_value.__truediv__.return_value = mock_path
            with patch(
                "agent.prompt_builder._scan_context_content",
                return_value="Benim soul md'im",
            ):
                with patch(
                    "agent.prompt_builder._truncate_content",
                    return_value="Benim soul md'im",
                ):
                    result = load_soul_md()
        assert result == "Benim soul md'im"

    def test_bos_dosya_none_doner(self):
        from agent.prompt_builder import load_soul_md, _SKILLS_PROMPT_CACHE

        _SKILLS_PROMPT_CACHE.clear()
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.read_text.return_value = "   "
        with patch("agent.prompt_builder.get_reymen_home") as mock_home:
            mock_home.return_value = MagicMock()
            mock_home.return_value.__truediv__.return_value = mock_path
            result = load_soul_md()
        assert result is None


# ---------------------------------------------------------------------------
# _load_ReYMeN_md
# ---------------------------------------------------------------------------


class TestLoadReYMeN_md:
    def test_dosya_yoksa_bos(self, tmp_path):
        from agent.prompt_builder import _load_ReYMeN_md

        with patch("agent.prompt_builder._find_ReYMeN_md", return_value=None):
            result = _load_ReYMeN_md(tmp_path)
        assert result == ""

    def test_dosya_var_okunur(self, tmp_path):
        from agent.prompt_builder import _load_ReYMeN_md

        md_path = tmp_path / ".ReYMeN.md"
        md_path.write_text("## Proje bilgisi\nBu bir test projesidir.")
        with patch("agent.prompt_builder._find_ReYMeN_md", return_value=md_path):
            with patch(
                "agent.prompt_builder._strip_yaml_frontmatter", side_effect=lambda x: x
            ):
                with patch(
                    "agent.prompt_builder._scan_context_content",
                    side_effect=lambda x, y: x,
                ):
                    with patch(
                        "agent.prompt_builder._truncate_content",
                        side_effect=lambda x, y: x,
                    ):
                        result = _load_ReYMeN_md(tmp_path)
        assert "Proje bilgisi" in result
        assert ".ReYMeN.md" in result


# ---------------------------------------------------------------------------
# build_environment_hints
# ---------------------------------------------------------------------------


class TestBuildEnvironmentHints:
    def test_local_backend_host_bilgisi_verir(self):
        from agent.prompt_builder import build_environment_hints

        with patch("agent.prompt_builder.os.getenv", return_value="local"):
            with patch("agent.prompt_builder.is_wsl", return_value=False):
                with patch(
                    "agent.prompt_builder.os.path.expanduser",
                    return_value="C:\\Users\\testuser",
                ):
                    with patch(
                        "agent.prompt_builder.resolve_agent_cwd",
                        return_value="C:\\testdir",
                    ):
                        result = build_environment_hints()
        # Should contain host info (actual platform detected at runtime)
        assert "testuser" in result
        assert "testdir" in result

    def test_wsl_hint_eklenir(self):
        from agent.prompt_builder import build_environment_hints

        with patch("agent.prompt_builder.os.getenv", return_value="local"):
            with patch("agent.prompt_builder.is_wsl", return_value=True):
                with patch(
                    "agent.prompt_builder.os.path.expanduser",
                    return_value="/home/wsluser",
                ):
                    with patch(
                        "agent.prompt_builder.resolve_agent_cwd",
                        return_value="/home/wsluser/proj",
                    ):
                        result = build_environment_hints()
        assert "WSL" in result or "Windows Subsystem for Linux" in result

    def test_remote_backend_suppresses_host(self):
        from agent.prompt_builder import build_environment_hints

        with patch("agent.prompt_builder.os.getenv", return_value="docker"):
            with patch("agent.prompt_builder._probe_remote_backend", return_value=None):
                result = build_environment_hints()
        assert "Terminal backend: docker" in result
        assert "Host:" not in result

    def test_remote_backend_with_probe(self):
        from agent.prompt_builder import build_environment_hints

        with patch("agent.prompt_builder.os.getenv", return_value="docker"):
            with patch(
                "agent.prompt_builder._probe_remote_backend", return_value="OS: Linux"
            ):
                result = build_environment_hints()
        assert "Terminal backend: docker" in result
        assert "OS: Linux" in result


# ---------------------------------------------------------------------------
# _clear_backend_probe_cache
# ---------------------------------------------------------------------------


class TestClearBackendProbeCache:
    def test_cache_temizlenir(self):
        from agent.prompt_builder import (
            _clear_backend_probe_cache,
            _BACKEND_PROBE_CACHE,
        )

        _BACKEND_PROBE_CACHE[("test", "")] = "cached"
        _clear_backend_probe_cache()
        assert len(_BACKEND_PROBE_CACHE) == 0


# ---------------------------------------------------------------------------
# clear_skills_system_prompt_cache
# ---------------------------------------------------------------------------


class TestClearSkillsSystemPromptCache:
    def test_cache_temizlenir(self):
        from agent.prompt_builder import (
            clear_skills_system_prompt_cache,
            _SKILLS_PROMPT_CACHE,
        )

        _SKILLS_PROMPT_CACHE[("key",)] = "value"
        clear_skills_system_prompt_cache(clear_snapshot=False)
        assert len(_SKILLS_PROMPT_CACHE) == 0

    def test_snapshot_temizlenir(self, tmp_path):
        from agent.prompt_builder import clear_skills_system_prompt_cache

        with patch("agent.prompt_builder._skills_prompt_snapshot_path") as mock_path:
            mock_path.return_value = tmp_path / "snapshot.json"
            (tmp_path / "snapshot.json").write_text("test")
            clear_skills_system_prompt_cache(clear_snapshot=True)
        assert not (tmp_path / "snapshot.json").exists()


# ---------------------------------------------------------------------------
# build_skills_system_prompt (sinirli test — dosya sistemi gerektirir)
# ---------------------------------------------------------------------------


class TestBuildSkillsSystemPrompt:
    def test_skills_dir_yoksa_bos(self):
        from agent.prompt_builder import build_skills_system_prompt

        with patch("agent.prompt_builder.get_skills_dir") as mock_dir:
            mock_dir.return_value = MagicMock(spec=Path)
            mock_dir.return_value.exists.return_value = False
            with patch("agent.prompt_builder.get_all_skills_dirs", return_value=[]):
                result = build_skills_system_prompt()
        assert result == ""

    def test_cache_kullanilir(self, tmp_path):
        from agent.prompt_builder import build_skills_system_prompt
        from collections import OrderedDict

        resolved = str(tmp_path.resolve())
        cached_key = (
            resolved,
            (),
            (),
            (),
            "",
            (),
        )
        cache = OrderedDict()
        cache[cached_key] = "cached_value"
        with patch("agent.prompt_builder.get_skills_dir") as mock_dir:
            mock_dir.return_value = tmp_path
            with patch("agent.prompt_builder.get_all_skills_dirs", return_value=[]):
                with patch("gateway.session_context.get_session_env", return_value=""):
                    with patch("agent.prompt_builder._SKILLS_PROMPT_CACHE", cache):
                        result = build_skills_system_prompt()
        assert result == "cached_value"


# ---------------------------------------------------------------------------
# build_nous_subscription_prompt
# ---------------------------------------------------------------------------


class TestBuildNousSubscriptionPrompt:
    def test_import_hatasinda_bos(self):
        from agent.prompt_builder import build_nous_subscription_prompt

        result = build_nous_subscription_prompt()
        assert result == ""


# ---------------------------------------------------------------------------
# _parse_skill_file
# ---------------------------------------------------------------------------


class TestParseSkillFile:
    def test_basarili_parse(self, tmp_path):
        from agent.prompt_builder import _parse_skill_file

        sf = tmp_path / "SKILL.md"
        sf.write_text("---\nname: test-skill\nplatforms: []\n---\n# Test")
        with patch("agent.prompt_builder.skill_matches_platform", return_value=True):
            with patch(
                "agent.prompt_builder.extract_skill_description",
                return_value="test desc",
            ):
                ok, fm, desc = _parse_skill_file(sf)
        assert ok is True
        assert fm.get("name") == "test-skill"
        assert desc == "test desc"


# ---------------------------------------------------------------------------
# _skill_should_show
# ---------------------------------------------------------------------------


class TestSkillShouldShow:
    def test_no_filters_show(self):
        from agent.prompt_builder import _skill_should_show

        assert _skill_should_show({}, None, None) is True

    def test_fallback_for_toolsets_gizler(self):
        from agent.prompt_builder import _skill_should_show

        assert (
            _skill_should_show(
                {"fallback_for_toolsets": ["primary"]}, set(), {"primary"}
            )
            is False
        )

    def test_requires_toolsets_gosterir(self):
        from agent.prompt_builder import _skill_should_show

        assert (
            _skill_should_show({"requires_toolsets": ["required"]}, set(), {"required"})
            is True
        )

    def test_requires_toolsets_sitesi_gizler(self):
        from agent.prompt_builder import _skill_should_show

        assert (
            _skill_should_show({"requires_toolsets": ["required"]}, set(), set())
            is False
        )

    def test_fallback_for_tools_gizler(self):
        from agent.prompt_builder import _skill_should_show

        assert (
            _skill_should_show({"fallback_for_tools": ["tool_x"]}, {"tool_x"}, set())
            is False
        )
