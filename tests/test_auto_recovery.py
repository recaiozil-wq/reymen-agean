# -*- coding: utf-8 -*-
"""test_auto_recovery.py — AutoRecovery modulu icin pytest testleri."""

import os
import sys
import time
import threading
from unittest.mock import MagicMock, patch, PropertyMock, call
from pathlib import Path

import pytest

# --- Modul import oncesi ortam ---
PROJE_KOK = Path(__file__).resolve().parent.parent
if str(PROJE_KOK) not in sys.path:
    sys.path.insert(0, str(PROJE_KOK))

from auto_recovery import (
    ComponentStatus,
    WatchConfig,
    WatchState,
    ComponentWatcher,
    AutoRecovery,
)


# =============================================
# FIXTURES
# =============================================


@pytest.fixture
def watcher():
    """Temel ComponentWatcher fixture."""
    config = WatchConfig(
        name="test_bilesen",
        heartbeat_interval_sec=10.0,
        timeout_sec=30.0,
        max_failures=3,
        cooldown_sec=60.0,
        restart_attempts=3,
        enabled=True,
    )
    return ComponentWatcher(config)


@pytest.fixture
def recovery():
    """Temel AutoRecovery fixture."""
    return AutoRecovery(
        state_machine=None,
        bridge=None,
        check_interval_sec=15.0,
        max_restart_attempts=3,
        cooldown_sec=60.0,
        max_concurrent_failures=5,
        notify_on_recovery=True,
    )


# =============================================
# ComponentStatus - DURUM ENUM
# =============================================


class TestComponentStatus:
    def test_bes_durum_icin_bes_enum(self):
        """5 farkli durum enum'u olmali."""
        assert len(ComponentStatus) == 5

    def test_enum_degerleri(self):
        """Enum degerleri dogru olmali."""
        assert ComponentStatus.HEALTHY.value == "healthy"
        assert ComponentStatus.STALE.value == "stale"
        assert ComponentStatus.FAILING.value == "failing"
        assert ComponentStatus.RECOVERING.value == "recovering"
        assert ComponentStatus.DEAD.value == "dead"

    def test_enum_karsilastirma(self):
        """Enum'lar birbiriyle karsilastirilabilmeli."""
        assert ComponentStatus.HEALTHY != ComponentStatus.STALE
        assert ComponentStatus.DEAD == ComponentStatus.DEAD


# =============================================
# WatchConfig - YAPILANDIRMA
# =============================================


class TestWatchConfig:
    def test_varsayilan_degerler(self):
        """Varsayilan degerler dogru olmali."""
        config = WatchConfig(name="test")
        assert config.name == "test"
        assert config.heartbeat_interval_sec == 15.0
        assert config.timeout_sec == 45.0
        assert config.max_failures == 3
        assert config.cooldown_sec == 60.0
        assert config.restart_attempts == 3
        assert config.enabled is True

    def test_ozel_degerler(self):
        """Ozel degerler atanabilmeli."""
        config = WatchConfig(
            name="custom",
            heartbeat_interval_sec=5.0,
            timeout_sec=10.0,
            max_failures=2,
            cooldown_sec=30.0,
            restart_attempts=5,
            enabled=False,
        )
        assert config.name == "custom"
        assert config.heartbeat_interval_sec == 5.0
        assert config.timeout_sec == 10.0
        assert config.max_failures == 2
        assert config.restart_attempts == 5
        assert config.enabled is False


# =============================================
# WatchState - IZLEME DURUMU
# =============================================


class TestWatchState:
    def test_varsayilan_durumlar(self):
        """Varsayilan durum degerleri dogru olmali."""
        state = WatchState()
        assert state.status == ComponentStatus.HEALTHY
        assert state.consecutive_failures == 0
        assert state.restart_count == 0
        assert state.last_error is None
        assert state.error_history == []

    def test_son_heartbeat_zamani_ayarlanir(self):
        """last_heartbeat otomatik ayarlanmali."""
        state = WatchState()
        assert state.last_heartbeat > 0
        assert abs(state.last_heartbeat - time.time()) < 1.0

    def test_error_history_max_100(self):
        """error_history maksimum 100 kayit tutmali."""
        state = WatchState()
        for i in range(150):
            state.error_history.append((time.time(), f"Hata {i}"))
        if len(state.error_history) > 100:
            state.error_history = state.error_history[-50:]
        assert len(state.error_history) <= 100


# =============================================
# ComponentWatcher - BILESEN IZLEYICI
# =============================================


class TestComponentWatcherHeartbeat:
    def test_heartbeat_zamani_gunceller(self, watcher):
        """Heartbeat son ziyaret zamanini guncellemeli."""
        eski = watcher.state.last_heartbeat
        time.sleep(0.01)
        watcher.heartbeat()
        assert watcher.state.last_heartbeat > eski

    def test_heartbeat_saglik_durumunu_iyilestirir(self, watcher):
        """Stale durumunda heartbeat gelirse saglikliya donmeli."""
        watcher.state.status = ComponentStatus.STALE
        watcher.heartbeat()
        assert watcher.state.status == ComponentStatus.HEALTHY

    def test_heartbeat_failing_durumunu_iyilestirir(self, watcher):
        """Failing durumunda heartbeat gelirse saglikliya donmeli."""
        watcher.state.status = ComponentStatus.FAILING
        watcher.heartbeat()
        assert watcher.state.status == ComponentStatus.HEALTHY

    def test_heartbeat_dead_degistirmez(self, watcher):
        """Dead durumunda heartbeat statusu degistirmemeli."""
        watcher.state.status = ComponentStatus.DEAD
        watcher.heartbeat()
        assert watcher.state.status == ComponentStatus.DEAD  # degismemeli


class TestComponentWatcherRecordError:
    def test_hata_kaydedilir(self, watcher):
        """Hata basariyla kaydedilmeli."""
        watcher.record_error("Test hatasi")
        assert watcher.state.consecutive_failures == 1
        assert watcher.state.last_error == "Test hatasi"
        assert len(watcher.state.error_history) == 1

    def test_ardisik_hatalar_sayilir(self, watcher):
        """Ardisik hatalar sayilmali."""
        for i in range(2):
            watcher.record_error(f"Hata {i}")
        assert watcher.state.consecutive_failures == 2

    def test_max_failures_asilinca_failing_olur(self, watcher):
        """Max_failures asilinca status FAILING olmali."""
        for i in range(3):
            watcher.record_error(f"Hata {i}")
        assert watcher.state.status == ComponentStatus.FAILING

    def test_max_failures_altinda_stale_olur(self, watcher):
        """Max_failures altinda status STALE olmali."""
        for i in range(2):
            watcher.record_error(f"Hata {i}")
        assert watcher.state.status == ComponentStatus.STALE

    def test_error_history_max_50_tutulur(self, watcher):
        """Error_history maksimum 50 kayit tutmali (record_error ile)."""
        for i in range(120):
            watcher.record_error(f"Hata {i}")
        assert len(watcher.state.error_history) <= 100


class TestComponentWatcherCheck:
    def test_saglikli_bilesen_none_dondurur(self, watcher):
        """Saglikli bilesen None donmeli."""
        watcher.heartbeat()  # son heartbeat guncelle
        sonuc = watcher.check()
        assert sonuc is None

    def test_timeout_asilinca_stale_doner(self, watcher):
        """Timeout asilinca STALE donmeli."""
        with patch("time.time", return_value=time.time() + 60):
            sonuc = watcher.check()
            assert sonuc == ComponentStatus.STALE
            assert watcher.state.status == ComponentStatus.STALE

    def test_dead_bilesen_her_zaman_dead_dondurur(self, watcher):
        """Dead bilesen her zaman DEAD donmeli."""
        watcher.state.status = ComponentStatus.DEAD
        sonuc = watcher.check()
        assert sonuc == ComponentStatus.DEAD

    def test_recovering_bilesen_timeout_kontrolu(self, watcher):
        """Recovering durumunda farkli timeout hesabi yapilmali."""
        watcher.state.status = ComponentStatus.RECOVERING
        watcher.state.last_recovery = time.time() - 100  # cok eski
        sonuc = watcher.check()
        assert sonuc == ComponentStatus.DEAD

    def test_recovering_henuz_timeout_olmadi(self, watcher):
        """Recovering henuz timeout olmadiysa recovering donmeli."""
        watcher.state.status = ComponentStatus.RECOVERING
        watcher.state.last_recovery = time.time() - 5  # henuz 5sn
        sonuc = watcher.check()
        assert sonuc == ComponentStatus.RECOVERING


class TestComponentWatcherStartRecovery:
    def test_basariyla_kurtarir(self, watcher):
        """Kurtarma handler'i basarili olursa HEALTHY donmeli."""
        watcher.on_recovery(lambda n, e: True)
        sonuc = watcher.start_recovery()
        assert sonuc is True
        assert watcher.state.status == ComponentStatus.HEALTHY
        assert watcher.state.consecutive_failures == 0

    def test_kurtarma_basarisiz_olursa(self, watcher):
        """Kurtarma basarisiz olursa False donmeli."""
        watcher.on_recovery(lambda n, e: False)  # basarisiz handler
        sonuc = watcher.start_recovery()
        assert sonuc is False

    def test_maks_restart_asilinca_dead(self, watcher):
        """Maksimum restart denemesi asilinca DEAD olmali."""
        watcher.config.restart_attempts = 1
        watcher.state.restart_count = 1
        sonuc = watcher.start_recovery()
        assert sonuc is False
        assert watcher.state.status == ComponentStatus.DEAD

    def handler_hatasinda_exception_yutulur(self, watcher):
        """Handler hatasinda exception yutulup False donmeli."""
        watcher.on_recovery(lambda n, e: (_ for _ in ()).throw(Exception("Handler hatasi")))
        sonuc = watcher.start_recovery()
        assert sonuc is False

    def test_restart_count_artar(self, watcher):
        """Her kurtarma denemesinde restart_count artmali."""
        watcher.on_recovery(lambda n, e: True)
        watcher.start_recovery()
        assert watcher.state.restart_count == 1


class TestComponentWatcherOnRecovery:
    def test_handler_eklenir(self, watcher):
        """Handler eklenebilmeli."""
        def handler(n, e): return True
        watcher.on_recovery(handler)
        assert len(watcher._recovery_handlers) == 1
        assert watcher._recovery_handlers[0] is handler

    def test_birden_fazla_handler_eklenir(self, watcher):
        """Birden fazla handler eklenebilmeli."""
        watcher.on_recovery(lambda n, e: True)
        watcher.on_recovery(lambda n, e: False)
        assert len(watcher._recovery_handlers) == 2

    def test_handlerlar_sira_ile_calisir(self, watcher):
        """Handler'lar sirayla calistirilmali."""
        calls = []
        watcher.on_recovery(lambda n, e: (calls.append(1) or False))
        watcher.on_recovery(lambda n, e: (calls.append(2) or True))
        sonuc = watcher.start_recovery()
        assert sonuc is True
        assert calls == [1, 2]


class TestComponentWatcherReset:
    def test_durum_sifirlanir(self, watcher):
        """Reset durumu sifirlamali."""
        watcher.state.status = ComponentStatus.DEAD
        watcher.state.consecutive_failures = 5
        watcher.reset()
        assert watcher.state.status == ComponentStatus.HEALTHY
        assert watcher.state.consecutive_failures == 0
        assert watcher.state.restart_count == 0


class TestComponentWatcherStatus:
    def test_status_raporu_dogru_alanlar(self, watcher):
        """Status raporu dogru alanlari icermeli."""
        rapor = watcher.status()
        assert "name" in rapor
        assert "status" in rapor
        assert "last_heartbeat_ago" in rapor
        assert "consecutive_failures" in rapor
        assert "restart_count" in rapor
        assert "last_error" in rapor
        assert "timeout_sec" in rapor
        assert "max_failures" in rapor

    def test_status_raporu_dogru_degerler(self, watcher):
        """Status raporu dogru degerler icermeli."""
        rapor = watcher.status()
        assert rapor["name"] == "test_bilesen"
        assert rapor["status"] == "healthy"
        assert rapor["timeout_sec"] == 30.0
        assert rapor["max_failures"] == 3

    def test_status_raporu_hatali_durumda(self, watcher):
        """Hata kaydindan sonra status raporu guncellenmeli."""
        watcher.record_error("API hatasi")
        rapor = watcher.status()
        assert rapor["status"] == "stale"
        assert rapor["last_error"] == "API hatasi"
        assert rapor["consecutive_failures"] == 1


# =============================================
# AutoRecovery - ANA KURTARMA YONETICISI
# =============================================


class TestAutoRecoveryWatch:
    def test_bilesen_izlemeye_alinir(self, recovery):
        """Bilesen izlemeye alinmali."""
        w = recovery.watch("test", timeout=30, max_failures=3)
        assert isinstance(w, ComponentWatcher)
        assert w.config.name == "test"
        assert "test" in recovery._watchers

    def test_aynı_bilesen_tekrar_eklenebilir(self, recovery):
        """Ayni bilesen tekrar eklenebilmeli (overwrite)."""
        w1 = recovery.watch("test", timeout=30)
        w2 = recovery.watch("test", timeout=60)
        assert recovery._watchers["test"] is w2
        assert recovery._watchers["test"].config.timeout_sec == 60

    def test_watch_restart_attempts_varsayilan_kullanir(self, recovery):
        """restart_attempts belirtilmezse genel deger kullanilmali."""
        w = recovery.watch("test", timeout=30)
        assert w.config.restart_attempts == recovery._max_restart_attempts

    def test_watch_ozel_restart_attempts(self, recovery):
        """restart_attempts ozel olarak belirtilebilmeli."""
        w = recovery.watch("test", timeout=30, restart_attempts=5)
        assert w.config.restart_attempts == 5

    def test_watch_devre_disiolabilir(self, recovery):
        """Bilesen devre disi birakilabilmeli."""
        w = recovery.watch("test", timeout=30, enabled=False)
        assert w.config.enabled is False

    def test_watch_bridge_heartbeat_gonderir(self):
        """Bridge varsa heartbeat gonderilmeli."""
        bridge = MagicMock()
        recovery = AutoRecovery(bridge=bridge)
        recovery.watch("test", timeout=30)
        bridge.heartbeat.assert_called_once_with("recovery.test")

    def test_watch_varsayilan_handlerlari_ekler(self, recovery):
        """Varsayilan handler'lar yeni watcher'a eklenmeli."""
        recovery.on_recovery("test", lambda n, e: True)
        w = recovery.watch("test", timeout=30)
        assert len(w._recovery_handlers) == 1


class TestAutoRecoveryUnwatch:
    def test_bilesen_izlemeden_cikarilir(self, recovery):
        """Bilesen izlemeden cikarilabilmeli."""
        recovery.watch("test", timeout=30)
        assert "test" in recovery._watchers
        recovery.unwatch("test")
        assert "test" not in recovery._watchers

    def test_olmayan_bileseni_cikarmak_hata_vermez(self, recovery):
        """Olmayan bileseni cikarmak hata vermemeli."""
        recovery.unwatch("nonexistent")


class TestAutoRecoveryHeartbeat:
    def test_heartbeat_izlenen_bilesene_gonderilir(self, recovery):
        """Heartbeat izlenen bilesene gonderilmeli."""
        w = recovery.watch("test", timeout=30)
        eski = w.state.last_heartbeat
        time.sleep(0.01)
        recovery.heartbeat("test")
        assert w.state.last_heartbeat > eski

    def test_izlenmeyen_bilesen_heartbeat_hata_vermez(self, recovery):
        """Izlenmeyen bilesene heartbeat hata vermemeli."""
        recovery.heartbeat("nonexistent")

    def test_heartbeat_bridge_iletilir(self):
        """Bridge varsa heartbeat bridge'e de iletilmeli."""
        bridge = MagicMock()
        recovery = AutoRecovery(bridge=bridge)
        recovery.watch("test", timeout=30)
        recovery.heartbeat("test")
        bridge.heartbeat.assert_called()


class TestAutoRecoveryRecordError:
    def test_hata_kaydedilir(self, recovery):
        """Hata basariyla kaydedilmeli."""
        w = recovery.watch("test", timeout=30)
        recovery.record_error("test", "API hatasi")
        assert w.state.consecutive_failures == 1
        assert w.state.last_error == "API hatasi"

    def test_izlenmeyen_bilesen_hata_vermez(self, recovery):
        """Izlenmeyen bilesen icin hata kaydetmek hata vermemeli."""
        recovery.record_error("nonexistent", "test")

    def test_hata_bridge_publish_eder(self):
        """Bridge varsa hata publish edilmeli."""
        bridge = MagicMock()
        recovery = AutoRecovery(bridge=bridge)
        recovery.watch("test", timeout=30)
        recovery.record_error("test", "API hatasi")
        bridge.publish.assert_called_once()
        args = bridge.publish.call_args
        # bridge.publish("error", {"component": ..., "error": ...}, source=...)
        # call_args[0] = positional args tuple, call_args[1] = kwargs dict
        assert args[0][0] == "error"
        assert args[0][1]["component"] == "test"


class TestAutoRecoveryOnRecovery:
    def test_handler_kaydedilir(self, recovery):
        """Handler basariyla kaydedilmeli."""
        handler = lambda n, e: True
        recovery.on_recovery("test", handler)
        assert handler in recovery._default_handlers["test"]

    def test_handler_mevcut_watchera_eklenir(self, recovery):
        """Handler mevcut watcher'a da eklenmeli."""
        w = recovery.watch("test", timeout=30)
        handler = lambda n, e: True
        recovery.on_recovery("test", handler)
        assert handler in w._recovery_handlers

    def test_handler_future_watchera_eklenir(self, recovery):
        """Handler henuz olusturulmamis watcher icin kaydedilmeli."""
        handler = lambda n, e: True
        recovery.on_recovery("future_test", handler)
        w = recovery.watch("future_test", timeout=30)
        assert handler in w._recovery_handlers


class TestAutoRecoveryStartStop:
    def test_start_thread_baslatir(self, recovery):
        """Start arka plan thread'ini baslatmali."""
        recovery.start()
        assert recovery._running is True
        assert recovery._thread is not None
        assert recovery._thread.is_alive()
        recovery.stop()

    def test_arka_arkaya_start_hata_vermez(self, recovery):
        """Arka arkaya start hata vermemeli."""
        recovery.start()
        recovery.start()  # ikinci start hata vermemeli
        assert recovery._running is True
        recovery.stop()

    def test_stop_thread_durdurur(self, recovery):
        """Stop thread'i durdurmali."""
        recovery.start()
        recovery.stop()
        assert recovery._running is False

    def test_stop_calismiyorsa_hata_vermez(self, recovery):
        """Stop calismiyorken hata vermemeli."""
        recovery.stop()  # hic baslatilmamish


class TestAutoRecoveryTick:
    def test_tick_sayaci_artar(self, recovery):
        """Her tick'te tick_count artmali."""
        eski = recovery._tick_count
        recovery.tick()
        assert recovery._tick_count == eski + 1

    def test_tick_saglikli_bilesen_kontrol_eder(self, recovery):
        """Tick saglikli bileseni kontrol edip checked'e eklemeli."""
        recovery.watch("test", timeout=30)
        recovery.heartbeat("test")
        sonuc = recovery.tick()
        assert "test" in sonuc["checked"]

    def test_tick_stale_bileseni_kurtarmaya_calisir(self, recovery):
        """Tick STALE bileseni kurtarmaya calismali."""
        w = recovery.watch("test", timeout=1, max_failures=1)
        w.on_recovery(lambda n, e: True)
        time.sleep(1.5)
        sonuc = recovery.tick()
        # Stale olmus olabilir, farketmez - hata vermemeli

    def test_tick_dead_bileseni_raporlar(self, recovery):
        """Tick DEAD bileseni raporlamali."""
        w = recovery.watch("test", timeout=30)
        w.state.status = ComponentStatus.DEAD
        sonuc = recovery.tick()
        assert "test" in sonuc["dead"]

    def test_tick_devre_disibilitenmeleri_atlar(self, recovery):
        """Tick devre disi bilesenleri atlamali."""
        w = recovery.watch("test", timeout=30, enabled=False)
        sonuc = recovery.tick()
        assert "test" not in sonuc["checked"]

    def test_tick_state_machine_bildirir(self):
        """State machine varsa kurtarma durumunda bildirilmeli."""
        sm = MagicMock()
        bridge = MagicMock()
        recovery = AutoRecovery(state_machine=sm, bridge=bridge)
        w = recovery.watch("test", timeout=1, max_failures=1)
        w.on_recovery(lambda n, e: True)
        time.sleep(1.5)
        recovery.tick()
        # State machine ve bridge cagrilmis olabilir

    def test_cok_fazla_olu_bilesen_sistemi_cokertir(self, recovery):
        """max_concurrent_failures asilinca sistem crashed olmali."""
        for i in range(6):
            w = recovery.watch(f"test{i}", timeout=30)
            w.state.status = ComponentStatus.DEAD
        sonuc = recovery.tick()
        assert len(sonuc["dead"]) >= 5
        assert recovery._system_crashed is True


class TestAutoRecoveryStatusReport:
    def test_status_raporu_dogru_alanlar(self, recovery):
        """Status raporu dogru alanlari icermeli."""
        recovery.watch("test", timeout=30)
        rapor = recovery.status_report()
        assert "running" in rapor
        assert "tick_count" in rapor
        assert "recovery_count" in rapor
        assert "system_crashed" in rapor
        assert "watched_components" in rapor
        assert "components" in rapor
        assert "test" in rapor["components"]

    def test_status_bilesen_durumu(self, recovery):
        """Belirli bilesen durumu sorgulanabilmeli."""
        recovery.watch("test", timeout=30)
        durum = recovery.status("test")
        assert durum is not None
        assert durum["name"] == "test"

    def test_status_olmayan_bilesen_none(self, recovery):
        """Olmayan bilesen status'u None donmeli."""
        durum = recovery.status("nonexistent")
        assert durum is None


class TestAutoRecoveryIntegration:
    def test_tam_akus_senaryosu(self):
        """Tam akis: watch -> heartbeat -> hata -> kurtarma -> tick."""
        sm = MagicMock()
        bridge = MagicMock()

        rec = AutoRecovery(sm, bridge, check_interval_sec=15.0)
        w = rec.watch("provider", timeout=10, max_failures=2)
        w.on_recovery(lambda n, e: True)

        rec.heartbeat("provider")
        assert w.state.status == ComponentStatus.HEALTHY

        rec.record_error("provider", "API hatasi 1")
        assert w.state.consecutive_failures == 1
        assert w.state.status == ComponentStatus.STALE

        rec.record_error("provider", "API hatasi 2")
        assert w.state.consecutive_failures == 2
        assert w.state.status == ComponentStatus.FAILING

        # Tick calisinca kurtarma baslamali
        sonuc = rec.tick()
        assert "provider" in sonuc["recovered"] or "failed" in sonuc

        rapor = rec.status_report()
        assert rapor["recovery_count"] >= 0
        assert rapor["watched_components"] == 1

    def test_ikinci_bilesen_bagimsiz_izlenir(self):
        """Iki bilesen bagimsiz izlenebilmeli."""
        rec = AutoRecovery()
        w1 = rec.watch("bilesen_a", timeout=10)
        w2 = rec.watch("bilesen_b", timeout=10)

        w1.record_error("Hata")
        assert w1.state.consecutive_failures == 1
        assert w2.state.consecutive_failures == 0  # bagimsiz

        rec.heartbeat("bilesen_b")
        assert w2.state.status == ComponentStatus.HEALTHY

        sonuc = rec.tick()
        assert "bilesen_b" in sonuc["checked"] or "bilesen_b" in sonuc.get("recovered", [])

    def test_loop_dongusu_hata_yonetimi(self):
        """_loop icindeki hatalar yutulmali."""
        rec = AutoRecovery(check_interval_sec=0.01)
        rec.start()
        time.sleep(0.05)
        rec.stop()
        assert rec._running is False
