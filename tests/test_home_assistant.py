#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_home_assistant.py — HAClient testleri."""

import sys
sys.path.insert(0, ".")

from agent.home_assistant import HAClient, ha_client


class TestHAInit:
    def test_init_bos(self):
        ha = HAClient({})
        assert ha._hazir is False
        assert ha.ping() is True

    def test_init_ozel(self):
        ha = HAClient({"homeassistant": {
            "base_url": "http://192.168.1.100:8123",
            "access_token": "test_token",
        }})
        assert ha._hazir is True

    def test_singleton(self):
        ha1 = ha_client({"homeassistant": {}})
        ha2 = ha_client()
        assert ha1 is ha2


class TestHAIslem:
    def test_servis_hazir_degil(self):
        ha = HAClient({})
        r = ha.servis_cagir("light", "turn_on", "light.oturma")
        assert "yapilandirilmamis" in r

    def test_entity_durum_hazir_degil(self):
        ha = HAClient({})
        r = ha.entity_durum("sensor.sicaklik")
        assert "yapilandirilmamis" in r

    def test_entity_listele(self):
        ha = HAClient({"homeassistant": {"base_url": "x", "access_token": "y"}})
        r = ha.entity_listele("light")
        assert "[HA]" in r


class TestHAKomut:
    def test_komut_bos(self):
        ha = HAClient({})
        r = ha.komut_islem("")
        assert "Home Assistant" in r

    def test_komut_servis(self):
        ha = HAClient({})
        r = ha.komut_islem("servis light.turn_on light.oturma")
        assert "[HA]" in r

    def test_komut_durum(self):
        ha = HAClient({})
        r = ha.komut_islem("durum sensor.sicaklik")
        assert "[HA]" in r

    def test_komut_list(self):
        ha = HAClient({})
        r = ha.komut_islem("list light")
        assert "[HA]" in r

    def test_komut_bilinmeyen(self):
        ha = HAClient({})
        r = ha.komut_islem("olmayan")
        assert "Bilinmeyen" in r
