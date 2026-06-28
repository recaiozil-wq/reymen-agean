# -*- coding: utf-8 -*-
"""tests/test_agent_context_references.py — Context referans testleri."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Mock agent.model_metadata BEFORE importing context_references
# because it depends on ReYMeN_constants.OPENROUTER_MODELS_URL which is missing
_model_metadata_mock = MagicMock()
_model_metadata_mock.estimate_tokens_rough.return_value = 10
sys.modules['agent.model_metadata'] = _model_metadata_mock

from agent.context_references import (
    parse_context_references,
    ContextReference,
    ContextReferenceResult,
    _strip_trailing_punctuation,
    _strip_reference_wrappers,
    _parse_file_reference_value,
    _remove_reference_tokens,
    _resolve_path,
    _code_fence_language,
)


class TestParseContextReferences:
    """parse_context_references() testleri."""

    def test_empty_message_returns_empty_list(self):
        """Bos mesaj bos liste doner."""
        assert parse_context_references("") == []

    def test_no_references_returns_empty_list(self):
        """Referans icermeyen mesaj bos liste doner."""
        assert parse_context_references("Merhaba dunya") == []

    def test_simple_diff_reference(self):
        """@diff basit referansi dogru parse edilir."""
        refs = parse_context_references("Son durum: @diff")
        assert len(refs) == 1
        assert refs[0].kind == "diff"
        assert refs[0].raw == "@diff"

    def test_simple_staged_reference(self):
        """@staged basit referansi dogru parse edilir."""
        refs = parse_context_references("Staged: @staged")
        assert len(refs) == 1
        assert refs[0].kind == "staged"

    def test_file_reference_with_backtick(self):
        """@file:`path/to/file.py` backtick ile dogru parse edilir."""
        refs = parse_context_references("Bkz: @file:`src/main.py`")
        assert len(refs) == 1
        assert refs[0].kind == "file"
        assert refs[0].target == "src/main.py"

    def test_file_reference_with_quotes(self):
        """@file:'path/to/file.py' tirnak ile dogru parse edilir."""
        refs = parse_context_references("Bkz: @file:'src/main.py'")
        assert len(refs) == 1
        assert refs[0].kind == "file"
        assert refs[0].target == "src/main.py"

    def test_file_reference_with_line_numbers(self):
        """@file:`path`:10-20 satir araligi dogru parse edilir."""
        refs = parse_context_references("Bkz: @file:`src/main.py`:10-20")
        assert len(refs) == 1
        assert refs[0].kind == "file"
        assert refs[0].target == "src/main.py"
        assert refs[0].line_start == 10
        assert refs[0].line_end == 20

    def test_file_reference_single_line(self):
        """@file:`path`:10 tek satir referansi."""
        refs = parse_context_references("Bkz: @file:`src/main.py`:10")
        assert len(refs) == 1
        assert refs[0].line_start == 10
        assert refs[0].line_end == 10

    def test_folder_reference(self):
        """@folder:`path/to/folder` dogru parse edilir."""
        refs = parse_context_references("Bkz: @folder:`src/`")
        assert len(refs) == 1
        assert refs[0].kind == "folder"
        assert refs[0].target == "src/"

    def test_git_reference(self):
        """@git:`5` referansi."""
        refs = parse_context_references("Git log: @git:`5`")
        assert len(refs) == 1
        assert refs[0].kind == "git"
        assert refs[0].target == "5"

    def test_url_reference(self):
        """@url:`https://example.com` referansi."""
        refs = parse_context_references("Bkz: @url:`https://example.com`")
        assert len(refs) == 1
        assert refs[0].kind == "url"
        assert "https://example.com" in refs[0].target

    def test_multiple_references(self):
        """Birden fazla referans dogru parse edilir."""
        refs = parse_context_references("Bkz: @file:`a.py` ve @file:`b.py`")
        assert len(refs) == 2
        assert refs[0].target == "a.py"
        assert refs[1].target == "b.py"

    def test_word_boundary_no_false_positive(self):
        """@ isareti kelime ortasinda yanlis pozitif vermez."""
        refs = parse_context_references("email@example.com adresi")
        assert len(refs) == 0

    def test_reference_with_trailing_punctuation(self):
        """@file:`path`'den sonra gelen noktalama temizlenir."""
        refs = parse_context_references("@file:`test.py`.")
        assert len(refs) == 1
        assert refs[0].target == "test.py"

    def test_reference_without_quotes(self):
        """@file:path tirnaksiz da calisir."""
        refs = parse_context_references("@file:test.py")
        assert len(refs) == 1
        assert refs[0].kind == "file"
        assert refs[0].target == "test.py"

    def test_file_reference_with_line_unquoted(self):
        """@file:path:10 satir numarasi tirnaksiz."""
        refs = parse_context_references("@file:test.py:10")
        assert len(refs) == 1
        assert refs[0].target == "test.py"
        assert refs[0].line_start == 10


class TestStripTrailingPunctuation:
    """_strip_trailing_punctuation() testleri."""

    def test_trailing_comma_removed(self):
        """Sondaki virgul temizlenir."""
        assert _strip_trailing_punctuation("test.py,") == "test.py"

    def test_trailing_period_removed(self):
        """Sondaki nokta temizlenir."""
        assert _strip_trailing_punctuation("test.py.") == "test.py"

    def test_no_trailing_punctuation_unchanged(self):
        """Noktalama yoksa degisiklik olmaz."""
        assert _strip_trailing_punctuation("test.py") == "test.py"

    def test_trailing_period_after_bracket_removed(self):
        """Nokta + parantez kombinasyonu temizlenir."""
        assert _strip_trailing_punctuation("test.py).") == "test.py"

    def text_trailing_exclamation_removed(self):
        """Sondaki unlem temizlenir."""
        assert _strip_trailing_punctuation("test.py!") == "test.py"


class TestStripReferenceWrappers:
    """_strip_reference_wrappers() testleri."""

    def test_backtick_wrapper_removed(self):
        """Backtick wrapper temizlenir."""
        assert _strip_reference_wrappers("`test.py`") == "test.py"

    def test_double_quote_removed(self):
        """Cift tirnak wrapper temizlenir."""
        assert _strip_reference_wrappers('"test.py"') == "test.py"

    def test_single_quote_removed(self):
        """Tek tirnak wrapper temizlenir."""
        assert _strip_reference_wrappers("'test.py'") == "test.py"

    def test_no_wrapper_unchanged(self):
        """Wrapper yoksa degisiklik olmaz."""
        assert _strip_reference_wrappers("test.py") == "test.py"

    def test_single_char_not_stripped(self):
        """Tek karakterli wrapper degildir."""
        assert _strip_reference_wrappers("a") == "a"


class TestParseFileReferenceValue:
    """_parse_file_reference_value() testleri."""

    def test_quoted_path(self):
        """Tirnakli yol dogru parse edilir."""
        path, start, end = _parse_file_reference_value("`src/main.py`")
        assert path == "src/main.py"
        assert start is None
        assert end is None

    def test_quoted_path_with_range(self):
        """Tirnakli yol + satir araligi."""
        path, start, end = _parse_file_reference_value("`src/main.py`:10-20")
        assert path == "src/main.py"
        assert start == 10
        assert end == 20

    def test_quoted_path_single_line(self):
        """Tirnakli yol + tek satir."""
        path, start, end = _parse_file_reference_value("`src/main.py`:10")
        assert path == "src/main.py"
        assert start == 10
        assert end == 10

    def test_unquoted_path(self):
        """Tirnaksiz yol."""
        path, start, end = _parse_file_reference_value("src/main.py")
        assert path == "src/main.py"
        assert start is None
        assert end is None

    def test_unquoted_path_with_range(self):
        """Tirnaksiz yol + satir araligi."""
        path, start, end = _parse_file_reference_value("src/main.py:10-20")
        assert path == "src/main.py"
        assert start == 10
        assert end == 20


class TestRemoveReferenceTokens:
    """_remove_reference_tokens() testleri."""

    def test_remove_single_reference(self):
        """Tek referans metinden cikarilir."""
        refs = [
            ContextReference(raw="@file:`test.py`", kind="file", target="test.py", start=5, end=20),
        ]
        result = _remove_reference_tokens("Bkz: @file:`test.py`", refs)
        assert result == "Bkz:"


class TestResolvePath:
    """_resolve_path() testleri."""

    def test_absolute_path_resolved(self, tmp_path):
        """Mutlak yol dogru cozulur."""
        from pathlib import Path
        target = str(tmp_path / "test.txt")
        result = _resolve_path(Path.cwd(), target, allowed_root=tmp_path)
        assert result == Path(target).resolve()

    def test_relative_path_resolved(self, tmp_path):
        """Goreceli yol cwd'e gore cozulur."""
        (tmp_path / "test.txt").touch()
        result = _resolve_path(tmp_path, "test.txt", allowed_root=tmp_path)
        assert result == (tmp_path / "test.txt").resolve()

    def test_path_outside_allowed_root_raises(self, tmp_path):
        """Allowed root disindaki yol hata firlatir."""
        import pytest
        outside = tmp_path.parent / "outside.txt"
        with pytest.raises(ValueError, match="outside the allowed workspace"):
            _resolve_path(tmp_path, str(outside), allowed_root=tmp_path)


class TestCodeFenceLanguage:
    """_code_fence_language() testleri."""

    def test_python_file(self):
        """.py dosyasi icin 'python' doner."""
        assert _code_fence_language(Path("test.py")) == "python"

    def test_javascript_file(self):
        """.js dosyasi icin 'javascript' doner."""
        assert _code_fence_language(Path("test.js")) == "javascript"

    def test_markdown_file(self):
        """.md dosyasi icin 'markdown' doner."""
        assert _code_fence_language(Path("test.md")) == "markdown"

    def test_json_file(self):
        """.json dosyasi icin 'json' doner."""
        assert _code_fence_language(Path("test.json")) == "json"

    def test_unknown_extension(self):
        """Bilinmeyen uzanti icin '' doner."""
        assert _code_fence_language(Path("test.xyz")) == ""


class TestContextReferenceDataclass:
    """ContextReference veri sinifi testleri."""

    def test_create_reference(self):
        """ContextReference olusturma ve alanlar."""
        ref = ContextReference(
            raw="@file:`test.py`",
            kind="file",
            target="test.py",
            start=0,
            end=17,
            line_start=1,
            line_end=10,
        )
        assert ref.raw == "@file:`test.py`"
        assert ref.kind == "file"
        assert ref.target == "test.py"
        assert ref.start == 0
        assert ref.end == 17
        assert ref.line_start == 1
        assert ref.line_end == 10

    def test_default_line_none(self):
        """line_start ve line_end varsayilan None."""
        ref = ContextReference(raw="@diff", kind="diff", target="", start=0, end=5)
        assert ref.line_start is None
        assert ref.line_end is None

    def test_dataclass_frozen(self):
        """ContextReference frozen=True ile sabitlenmis."""
        import pytest
        ref = ContextReference(raw="@diff", kind="diff", target="", start=0, end=5)
        with pytest.raises(Exception):
            ref.kind = "file"


class TestContextReferenceResult:
    """ContextReferenceResult veri sinifi testleri."""

    def test_create_result(self):
        """ContextReferenceResult olusturma."""
        result = ContextReferenceResult(
            message="test mesaji",
            original_message="test mesaji",
            references=[],
        )
        assert result.message == "test mesaji"
        assert result.expanded is False
        assert result.blocked is False
        assert result.injected_tokens == 0
