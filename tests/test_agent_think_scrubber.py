# -*- coding: utf-8 -*-
"""tests/test_agent_think_scrubber.py — Think scrubber testleri."""

from agent.think_scrubber import StreamingThinkScrubber


class TestStreamingThinkScrubberBasics:
    """Temel <think> blok temizleme testleri."""

    def test_simple_think_block_removed(self):
        """<think>...</think> blogu tamamen temizlenir."""
        scrubber = StreamingThinkScrubber()
        text = "<think>Let me think about this carefully</think>"
        result = scrubber.feed(text)
        assert result == ""

    def test_text_around_think_block(self):
        """<think> blogu etrafindaki metin korunur."""
        scrubber = StreamingThinkScrubber()
        text = "Diger bilgiler <think>biraz dusunelim</think> devam ediyor."
        result = scrubber.feed(text)
        assert "Diger bilgiler" in result
        assert "devam ediyor" in result
        assert "dusunelim" not in result

    def test_thinking_tag_removed(self):
        """<thinking>...</thinking> blogu temizlenir."""
        scrubber = StreamingThinkScrubber()
        text = "<thinking>Derin dusunce</thinking>"
        result = scrubber.feed(text)
        assert result == ""

    def test_reasoning_tag_removed(self):
        """<reasoning>...</reasoning> blogu temizlenir."""
        scrubber = StreamingThinkScrubber()
        text = "<reasoning>Akıl yurutme</reasoning>"
        result = scrubber.feed(text)
        assert result == ""

    def test_normal_text_unchanged(self):
        """<think> etiketi icermeyen metin degismez."""
        scrubber = StreamingThinkScrubber()
        text = "Bu normal bir metin. Herhangi bir dusunce blogu yok."
        result = scrubber.feed(text)
        assert result == text

    def test_empty_feed_returns_empty(self):
        """Bos feed() cagrisi bos string doner."""
        scrubber = StreamingThinkScrubber()
        assert scrubber.feed("") == ""


class TestStreamingThinkScrubberStream:
    """Stream (delta) bazinda testler."""

    def test_split_delta_full_block(self):
        """<think> ve </think> ayri deltalarda gelse de blok temizlenir."""
        scrubber = StreamingThinkScrubber()
        # delta1: <think> baslangici
        r1 = scrubber.feed("<think>")
        assert r1 == ""  # hold-back veya block icinde
        # delta2: icerik
        r2 = scrubber.feed("Bu kisim dusunce")
        assert r2 == ""
        # delta3: kapanis
        r3 = scrubber.feed("</think>")
        assert r3 == ""

    def test_split_delta_with_tail_text(self):
        """Kapanis etiketinden sonra metin gelirse o metin gorunur."""
        scrubber = StreamingThinkScrubber()
        scrubber.feed("<think>")
        scrubber.feed("dusunce")
        result = scrubber.feed("</think>Devam metni")
        assert result == "Devam metni"

    def test_partial_open_tag_at_boundary(self):
        """Yarim <th etiketi bir sonraki delta'da tamamlanir."""
        scrubber = StreamingThinkScrubber()
        r1 = scrubber.feed("<th")
        # <th tam bir tag degil, hold-back edilir
        assert r1 == ""  # veya "<th" hold-back
        r2 = scrubber.feed("ink>")
        # Simdi <think> olarak algilanmali
        assert r2 == ""  # ya da blok acildiysa bos

    def test_flush_after_unterminated_block(self):
        """Bitmemis blok varsa flush() bos doner."""
        scrubber = StreamingThinkScrubber()
        scrubber.feed("<think>")
        scrubber.feed("hala dusunuyor")
        result = scrubber.flush()
        assert result == ""

    def test_flush_normal_text(self):
        """Blok yoksa flush() tutulan metni dondurur."""
        scrubber = StreamingThinkScrubber()
        r = scrubber.feed("merhaba")
        assert r == "merhaba"
        result = scrubber.flush()
        assert result == ""


class TestStreamingThinkScrubberBoundary:
    """Block boundary kurallari testleri."""

    def test_inline_think_mention_preserved(self):
        """<think> metin icinde gecerse (block boundary'de degilse) korunur."""
        scrubber = StreamingThinkScrubber()
        # "kullan <think> etiketini" - boundary'de olmadigi icin korunmali
        text = 'Lutfen <think> etiketini kullanin'
        result = scrubber.feed(text)
        # NOT: bu inline mention block-boundary kuralina tabi.
        # Eger onceki emisyon yeni satirla bitmediyse ve ayni satirda
        # whitespace'ten baska sey varsa boundary degildir.
        # Ancak bu metin stream'in basi (boundary=True) oldugu icin
        # <think> acilis olarak algilanabilir. Testin stream ortasinda
        # olmasini simule edelim.
        scrubber2 = StreamingThinkScrubber()
        scrubber2._last_emitted_ended_newline = False
        result2 = scrubber2.feed('Lutfen <think> etiketini kullanin')
        # _last_emitted_ended_newline=False ve oncesinde newline yok,
        # boundary degil, bu yuzden korunur.
        assert '<think>' in result2

    def test_newline_before_think_is_boundary(self):
        """Yeni satirdan sonra gelen <think> boundary'dir ve blok acar."""
        scrubber = StreamingThinkScrubber()
        result = scrubber.feed("Onceki satir\n<think>gizli")
        assert "Onceki satir\n" in result  # \n oncesi gecer
        # <think> sonrasi blok icine girer
        r2 = scrubber.feed("icerik")
        assert r2 == ""
        r3 = scrubber.feed("</think>")
        assert r3 == ""


class TestStreamingThinkScrubberOrphanTags:
    """Yetim kapanis etiketleri testleri."""

    def test_orphan_close_tag_removed(self):
        """Acik <think> olmadan gelen </think> temizlenir."""
        scrubber = StreamingThinkScrubber()
        text = "Birkac sey </think> devam"
        result = scrubber.feed(text)
        assert "Birkac sey" in result
        assert "devam" in result
        assert "</think>" not in result


class TestStreamingThinkScrubberReset:
    """reset() metodu testleri."""

    def test_reset_clears_state(self):
        """reset() tum state'i sifirlar."""
        scrubber = StreamingThinkScrubber()
        scrubber.feed("<think>")
        scrubber.feed("icerik")
        scrubber.reset()
        assert scrubber._in_block is False
        assert scrubber._buf == ""
        assert scrubber._last_emitted_ended_newline is True

    def test_reset_allows_new_block(self):
        """Reset sonrasi yeni blok dogru calisir."""
        scrubber = StreamingThinkScrubber()
        scrubber.feed("<think>icerik</think>")
        scrubber.reset()
        result = scrubber.feed("<think>yeni blok</think>")
        assert result == ""


class TestStreamingThinkScrubberMultipleVariants:
    """Birden fazla tag varyanti ile test."""

    def test_thought_tag(self):
        """<thought>...</thought> blogu temizlenir."""
        scrubber = StreamingThinkScrubber()
        result = scrubber.feed("<thought>anlik fikir</thought>")
        assert result == ""

    def test_reasoning_scratchpad_tag(self):
        """<REASONING_SCRATCHPAD>...</REASONING_SCRATCHPAD> blogu temizlenir."""
        scrubber = StreamingThinkScrubber()
        result = scrubber.feed("<REASONING_SCRATCHPAD>cok fazla dusunce</REASONING_SCRATCHPAD>")
        assert result == ""


class TestStreamingThinkScrubberEdgeCases:
    """Kenar durum testleri."""

    def test_multiple_blocks_in_one_feed(self):
        """Tek feed'de birden fazla blok olabilir."""
        scrubber = StreamingThinkScrubber()
        text = "bas <think>bir</think> orta <think>iki</think> son"
        result = scrubber.feed(text)
        assert result == "bas  orta  son"
        assert "bir" not in result
        assert "iki" not in result

    def test_think_at_stream_start_is_boundary(self):
        """Stream basinda <think> boundary'dir ve blok acar."""
        scrubber = StreamingThinkScrubber()
        result = scrubber.feed("<think>")
        assert result == ""
        scrubber.feed("dusunce")
        result2 = scrubber.feed("</think>")
        assert result2 == ""

    def test_only_whitespace_before_think_on_new_line(self):
        """Yeni satirda whitespace + <think> boundary'dir."""
        scrubber = StreamingThinkScrubber()
        result = scrubber.feed("  \n  <think>gizli</think>")
        # \n oncesi "  " emmit edilir, <think> blok acar
        assert "  \n  " in result
        # <think>gizli</think> blok olarak temizlenir
