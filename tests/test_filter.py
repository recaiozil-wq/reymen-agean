import pytest
from processors.filter import (
    quality_filter,
    filter_batch,
    _domain_name,
    _check_url,
    _check_length,
    _check_word_count,
    _check_sentence_count,
    _check_spam_ratio,
    _check_encoding,
    _check_duplicate_ratio,
)

# ── Sabitler ────────────────────────────────────────────────────────
GOOD_CONTENT = (
    "Artificial intelligence is transforming industries worldwide. "
    "Researchers at leading universities have published groundbreaking findings. "
    "The implications for healthcare, finance, and education are profound. "
    "Companies are investing billions to stay ahead of the curve. "
    "Experts warn that regulation must keep pace with innovation. "
    "Machine learning algorithms now diagnose diseases with remarkable accuracy. "
    "Natural language processing has revolutionized human-computer interaction. "
    "Autonomous vehicles are actively being tested around the globe. "
    "Quantum computing promises to solve problems beyond classical reach. "
    "The ethics of artificial intelligence spark heated debates everywhere. "
    "Deep learning models require vast amounts of training data. "
    "Reinforcement learning achieves superhuman performance in complex games. "
    "Computer vision systems identify objects with near-human precision. "
    "General artificial intelligence remains a distant but compelling goal. "
    "Neural networks were inspired by the structure of the human brain. "
    "Transfer learning lets models apply knowledge across different domains. "
    "Edge computing brings AI capabilities directly to mobile devices. "
    "Robotics has benefited enormously from recent AI advancements. "
    "Data privacy concerns lead to stricter global regulations. "
    "Cloud-based AI services democratize access to advanced analytics. "
)


# ══════════════════════════════════════════════════════════════════
# _domain_name
# ══════════════════════════════════════════════════════════════════

class TestDomainName:
    def test_plain(self):
        assert _domain_name("https://example.com/page") == "example"

    def test_www_stripped(self):
        assert _domain_name("https://www.example.com") == "example"

    def test_www2_stripped(self):
        result = _domain_name("https://www2.example.com")
        assert "www2" not in result

    def test_country_tld(self):
        result = _domain_name("https://www.google.com.tr/search")
        assert result == "google"

    def test_subdomain_ignored(self):
        result = _domain_name("https://news.ycombinator.com/item?id=1")
        assert result == "ycombinator"

    def test_invalid_url(self):
        assert _domain_name("not-a-url") == ""


# ══════════════════════════════════════════════════════════════════
# _check_url
# ══════════════════════════════════════════════════════════════════

class TestCheckUrl:
    def test_valid_url(self):
        ok, _ = _check_url("https://techcrunch.com/article")
        assert ok is True

    def test_blocked_google(self):
        ok, reason = _check_url("https://www.google.com/search?q=test")
        assert ok is False
        assert "google" in reason

    def test_blocked_google_country(self):
        ok, _ = _check_url("https://www.google.com.tr/search")
        assert ok is False

    def test_blocked_youtube(self):
        ok, _ = _check_url("https://youtube.com/watch?v=abc")
        assert ok is False

    def test_no_scheme(self):
        ok, _ = _check_url("example.com/page")
        assert ok is False

    def test_empty(self):
        ok, _ = _check_url("")
        assert ok is False


# ══════════════════════════════════════════════════════════════════
# _check_length
# ══════════════════════════════════════════════════════════════════

class TestCheckLength:
    def test_empty(self):
        ok, _ = _check_length("")
        assert ok is False

    def test_too_short(self):
        ok, _ = _check_length("x" * 500)
        assert ok is False

    def test_exact_min(self):
        ok, _ = _check_length("x" * 1200)
        assert ok is True

    def test_too_long(self):
        ok, _ = _check_length("x" * 100_001)
        assert ok is False

    def test_good_length(self):
        ok, _ = _check_length("x" * 5000)
        assert ok is True


# ══════════════════════════════════════════════════════════════════
# _check_word_count
# ══════════════════════════════════════════════════════════════════

class TestCheckWordCount:
    def test_too_few(self):
        ok, _ = _check_word_count("hello world " * 20)
        assert ok is False

    def test_enough(self):
        ok, _ = _check_word_count("word " * 200)
        assert ok is True


# ══════════════════════════════════════════════════════════════════
# _check_sentence_count
# ══════════════════════════════════════════════════════════════════

class TestCheckSentenceCount:
    def test_too_few_sentences(self):
        content = "One sentence only. Another one."
        ok, _ = _check_sentence_count(content)
        assert ok is False

    def test_enough_sentences(self):
        content = ". ".join(["This is a sentence with enough words"] * 8) + "."
        ok, _ = _check_sentence_count(content)
        assert ok is True


# ══════════════════════════════════════════════════════════════════
# _check_spam_ratio
# ══════════════════════════════════════════════════════════════════

class TestCheckSpamRatio:
    def test_clean_content(self):
        ok, _ = _check_spam_ratio(GOOD_CONTENT)
        assert ok is True

    def test_high_spam(self):
        spam = ("click here buy now limited offer subscribe to unlock " * 10
                + "normal word " * 5)
        ok, _ = _check_spam_ratio(spam)
        assert ok is False

    def test_single_spam_in_long_content(self):
        content = GOOD_CONTENT + " click here"
        ok, _ = _check_spam_ratio(content)
        assert ok is True


# ══════════════════════════════════════════════════════════════════
# _check_encoding
# ══════════════════════════════════════════════════════════════════

class TestCheckEncoding:
    def test_clean_text(self):
        ok, _ = _check_encoding(GOOD_CONTENT)
        assert ok is True

    def test_emoji_not_flagged(self):
        content = GOOD_CONTENT + " 😀🚀🎉"
        ok, _ = _check_encoding(content)
        assert ok is True

    def test_cjk_not_flagged(self):
        content = GOOD_CONTENT + " 中文日本語"
        ok, _ = _check_encoding(content)
        assert ok is True

    def test_private_use_area_flagged(self):
        weird = GOOD_CONTENT + "\uFFF0" * 500
        ok, _ = _check_encoding(weird)
        assert ok is False

    def test_control_chars_flagged(self):
        content = GOOD_CONTENT + "\x01" * 500
        ok, _ = _check_encoding(content)
        assert ok is False

    def test_newline_tab_allowed(self):
        content = GOOD_CONTENT.replace(". ", ".\n\t")
        ok, _ = _check_encoding(content)
        assert ok is True


# ══════════════════════════════════════════════════════════════════
# _check_duplicate_ratio
# ══════════════════════════════════════════════════════════════════

class TestCheckDuplicateRatio:
    def test_unique_content(self):
        ok, _ = _check_duplicate_ratio(GOOD_CONTENT)
        assert ok is True

    def test_high_duplicate(self):
        repeated = "This exact sentence keeps appearing again and again. " * 30
        ok, _ = _check_duplicate_ratio(repeated)
        assert ok is False

    def test_empty_content(self):
        ok, _ = _check_duplicate_ratio("")
        assert ok is True


# ══════════════════════════════════════════════════════════════════
# quality_filter — entegrasyon
# ══════════════════════════════════════════════════════════════════

class TestQualityFilter:
    def _good_item(self, **overrides):
        base = {
            "url": "https://techcrunch.com/article/ai-news",
            "content": GOOD_CONTENT,
            "method": "curl",
            "length": len(GOOD_CONTENT),
        }
        base.update(overrides)
        return base

    def test_good_item_passes(self):
        assert quality_filter(self._good_item()) is True

    def test_none_fails(self):
        assert quality_filter(None) is False

    def test_empty_dict_fails(self):
        assert quality_filter({}) is False

    def test_blocked_url_fails(self):
        item = self._good_item(url="https://www.google.com/search")
        assert quality_filter(item) is False

    def test_short_content_fails(self):
        item = self._good_item(content="Too short.")
        assert quality_filter(item) is False

    def test_missing_content_key_fails(self):
        item = {"url": "https://techcrunch.com/article"}
        assert quality_filter(item) is False


# ══════════════════════════════════════════════════════════════════
# filter_batch — FIX #9 hata koruması
# ══════════════════════════════════════════════════════════════════

class TestFilterBatch:
    def test_empty_list(self):
        assert filter_batch([]) == []

    def test_all_pass(self):
        items = [
            {"url": "https://techcrunch.com/a", "content": GOOD_CONTENT},
            {"url": "https://wired.com/b", "content": GOOD_CONTENT},
        ]
        result = filter_batch(items)
        assert len(result) == 2

    def test_mixed_pass_fail(self):
        items = [
            {"url": "https://techcrunch.com/a", "content": GOOD_CONTENT},
            {"url": "https://google.com/bad", "content": GOOD_CONTENT},
        ]
        result = filter_batch(items)
        assert len(result) == 1

    def test_broken_item_skipped(self):
        items = [
            None,
            "not a dict",
            42,
            {"url": "https://techcrunch.com/a", "content": GOOD_CONTENT},
        ]
        result = filter_batch(items)
        assert len(result) == 1

    def test_none_in_list(self):
        items = [None, None, None]
        result = filter_batch(items)
        assert result == []
