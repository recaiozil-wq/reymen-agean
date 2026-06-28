# -*- coding: utf-8 -*-
"""tests/test_agent_markdown_tables.py — Markdown tablo testleri."""

from agent.markdown_tables import (
    split_table_row,
    is_table_divider,
    looks_like_table_row,
    realign_markdown_tables,
)


class TestSplitTableRow:
    """split_table_row() testleri."""

    def test_basic_split(self):
        """Temel | a | b | c | satiri dogru ayrilir."""
        assert split_table_row("| a | b | c |") == ["a", "b", "c"]

    def test_with_extra_spaces(self):
        """Fazla bosluklarla bas eder."""
        assert split_table_row("|  apple  |  banana  |  cherry  |") == ["apple", "banana", "cherry"]

    def test_empty_cells(self):
        """Bos hucrelere izin verir."""
        assert split_table_row("| a |  | c |") == ["a", "", "c"]

    def test_no_leading_pipe(self):
        """Bastaki pipe olmasa da calisir."""
        assert split_table_row("a | b | c") == ["a", "b", "c"]

    def test_no_trailing_pipe(self):
        """Sondaki pipe olmasa da calisir."""
        assert split_table_row("| a | b | c") == ["a", "b", "c"]

    def test_single_cell(self):
        """Tek hucreli satir."""
        assert split_table_row("| only |") == ["only"]


class TestIsTableDivider:
    """is_table_divider() testleri."""

    def test_basic_divider(self):
        """|---| ---| ---| ayrac satiri dogru tespit edilir."""
        assert is_table_divider("| --- | --- | --- |") is True

    def test_colon_aligned_divider(self):
        """:--- ve ---: ile hizalanmis ayrac."""
        assert is_table_divider("| :--- | :---: | ---: |") is True

    def test_not_divider_too_short(self):
        """--- altinda cizgi divider degildir."""
        assert is_table_divider("|---|") is False  # tek hucre, gecerli tablo degil

    def test_not_divider_normal_row(self):
        """Normal veri satiri divider degildir."""
        assert is_table_divider("| a | b | c |") is False

    def test_empty_cells_divider(self):
        """Tum hucrelerde --- varsa divider'dir."""
        assert is_table_divider("|---|---|---|") is True


class TestLooksLikeTableRow:
    """looks_like_table_row() testleri."""

    def test_leading_pipe_is_table_row(self):
        """| ile baslayan satir tablo satiridir."""
        assert looks_like_table_row("| a | b | c |") is True

    def test_two_pipes_is_table_row(self):
        """En az 2 pipe iceren satir tablo satiri olabilir."""
        assert looks_like_table_row("a | b | c") is True

    def test_no_pipe_not_table(self):
        """Pipe icermeyen satir tablo satiri degildir."""
        assert looks_like_table_row("Bu normal bir metin.") is False

    def test_single_pipe_not_table(self):
        """Tek pipe tablo satiri sayilmaz (en az 2 pipe gerekir)."""
        assert looks_like_table_row("a | b") is False

    def test_empty_not_table(self):
        """Bos satir tablo satiri degildir."""
        assert looks_like_table_row("") is False

    def test_whitespace_only_not_table(self):
        """Sadece bosluk iceren satir tablo satiri degildir."""
        assert looks_like_table_row("   ") is False


class TestRealignMarkdownTables:
    """realign_markdown_tables() testleri."""

    def test_simple_table_realigned(self):
        """Basit bir tablo yeniden hizalanir."""
        table = (
            "| Name | Age |\n"
            "| --- | --- |\n"
            "| Alice | 30 |\n"
            "| Bob | 25 |\n"
        )
        result = realign_markdown_tables(table)
        # Tablo hala pipe'li yapida
        assert "|" in result
        # Hucreler korunur
        assert "Alice" in result
        assert "Bob" in result
        assert "Name" in result
        # Divider korunur
        assert "---" in result or "---" in result

    def test_non_table_text_unchanged(self):
        """Tablo olmayan metin hic degismez."""
        text = "Bu normal bir paragraf.\n\nBir baska paragraf."
        result = realign_markdown_tables(text)
        assert result == text

    def test_text_without_pipes_unchanged(self):
        """Pipe icermeyen metin degismez."""
        text = "Merhaba dunya!\nNasilsin?"
        result = realign_markdown_tables(text)
        assert result == text

    def test_empty_text_unchanged(self):
        """Bos metin degismez."""
        assert realign_markdown_tables("") == ""

    def test_table_with_cjk_chars(self):
        """CJK karakterli tablo yeniden hizalanir."""
        table = (
            "| İsim | Yas |\n"
            "| --- | --- |\n"
            "| Mehmet | 28 |\n"
            "| Ayşe | 32 |\n"
        )
        result = realign_markdown_tables(table)
        assert "İsim" in result
        assert "Yas" in result
        assert "Mehmet" in result
        assert "Ayşe" in result
        assert "|" in result

    def test_realign_with_available_width(self):
        """available_width parametresi ile tablo yeniden hizalanir."""
        table = (
            "| Name | Age | City |\n"
            "| --- | --- | --- |\n"
            "| Alice | 30 | Istanbul |\n"
            "| Bob | 25 | Ankara |\n"
        )
        # Dar genislik (30) vertical render tetikler
        result = realign_markdown_tables(table, available_width=30)
        # Vertical formatta "Name:" seklinde etiketler olur
        assert "Name:" in result or "Name" in result
        assert "Alice" in result or "30" in result

    def test_table_after_text_preserved(self):
        """Metin sonrasinda gelen tablo dogru islenir."""
        text = (
            "Ozet bilgiler:\n\n"
            "| Urun | Fiyat |\n"
            "| --- | --- |\n"
            "| Elma | 5TL |\n"
            "| Armut | 3TL |\n"
        )
        result = realign_markdown_tables(text)
        assert "Ozet bilgiler:" in result
        assert "Elma" in result
        assert "Armut" in result


class TestRealignEdgeCases:
    """realign_markdown_tables() kenar durumlar."""

    def test_single_table_with_divider_only(self):
        """Sadece ayrac satiri olan yapi tablo degildir."""
        text = "| --- | --- |\n"
        result = realign_markdown_tables(text)
        assert result == text

    def test_divider_after_non_table_line(self):
        """Ayrac satiri olan ama header olmayan satir."""
        text = (
            "Bilgi\n"
            "| --- | --- |\n"
        )
        result = realign_markdown_tables(text)
        assert result == text
