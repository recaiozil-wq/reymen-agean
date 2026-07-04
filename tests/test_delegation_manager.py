# -*- coding: utf-8 -*-
"""test_delegation_manager.py — Delegasyon birim testleri (yüzeyel geçiş)."""

import pytest

from src.core.delegation_manager import (
    DelegationManager,
    GorevAyrıştırıcı,
    SubAgent,
    SubAgentCalistirici,
)


# ── Happy Path ──────────────────────────────────────────────────────────


class TestGorevBol:
    """gorev_bol (GorevAyrıştırıcı.ayir) işlemleri."""

    def test_ayir_birden_fazla_alt_gorev(self):
        """Karmasik hedef → en az 2 alt-göreve ayrilir (heuristic)."""
        alt_gorevler = GorevAyrıştırıcı.ayir(
            "Veritabanini analiz et, rapor olustur ve sonuclari kaydet"
        )
        assert isinstance(alt_gorevler, list)
        assert len(alt_gorevler) >= 1, "En az 1 alt-görev olmali"
        for g in alt_gorevler:
            assert isinstance(g, SubAgent)
            assert g.goal

    def test_ayir_numarali_liste(self):
        """Numarali liste → heuristic ayristirma calisir."""
        alt_gorevler = GorevAyrıştırıcı.ayir(
            "1. Kullanici girdisini al\n2. Isle\n3. Sonucu dondur"
        )
        assert len(alt_gorevler) >= 2

    def test_ayir_madde_isareti(self):
        """Madde isaretli liste → heuristic ayristirma."""
        alt_gorevler = GorevAyrıştırıcı.ayir(
            "- Loglari temizle\n- DB yedekle\n- Servisi yeniden baslat"
        )
        assert len(alt_gorevler) >= 2


class TestSubAgentCalistir:
    """SubAgent calistirma islemleri."""

    def test_delege_et_basarili(self):
        """TEK mod subagent calistirma → status success olur."""
        manager = DelegationManager()
        agent = manager.delege_et("Test gorev: dosya tara")
        assert (
            agent.status == "success"
        ), f"Basit simulasyon success olmali: {agent.status}"
        assert agent.result, "Sonuc bos olmamali"

    def test_gorev_bol_ve_calistir(self):
        """Alt-görevlere ayir + hepsini calistir."""
        manager = DelegationManager()
        agentler = manager.gorev_bol_ve_calistir("Sistem analizi yap ve rapor olustur")
        assert isinstance(agentler, list)
        assert len(agentler) >= 1
        for a in agentler:
            assert a.status in ("success", "error")


# ── Error Cases ─────────────────────────────────────────────────────────


class TestGorevBolHata:
    """gorev_bol hata durumlari."""

    def test_ayir_bos_hedef(self):
        """Bos hedef → bos liste."""
        alt_gorevler = GorevAyrıştırıcı.ayir("")
        assert alt_gorevler == []

    def test_ayir_gecersiz_hedef(self):
        """Gecersiz (bosluk) hedef → bos liste."""
        alt_gorevler = GorevAyrıştırıcı.ayir("   ")
        assert alt_gorevler == []

    def test_delege_et_kisa_goal_calisir(self):
        """Kisa ama gecerli goal ile delege_et basarili olur."""
        manager = DelegationManager()
        agent = manager.delege_et("test")
        assert agent.status == "success"
