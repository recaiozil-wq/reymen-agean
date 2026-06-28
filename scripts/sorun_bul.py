# -*- coding: utf-8 -*-
"""
sorun_bul.py — ReYMeN proje otomatik sorun tarama modülü.

6 yöntemle projeyi tarar ve ozet_rapor() ile sonucu döndürür.
Sadece .py dosyalarını tarar; skills/ klasörünü atlar.
"""
from __future__ import annotations

import ast
import importlib.util
import os
import sys
import traceback
from pathlib import Path
from typing import Any

# Proje kökü bu scriptten iki seviye yukarı
KOK = Path(__file__).resolve().parent.parent

# ReYMeN SDK klasörleri — bunları içerik olarak taramayız
ATLANACAK_KLASORLER = {
    "skills", "skills_backup", "optional-skills", "venv",
    "__pycache__", ".git", "node_modules",
    "skills_backup_20260616_153955", "skills_backup_20260616_162201",
}

# ReYMeN'e ait çekirdek dosyalar (PROJE_REHBERI.md'den)
ReYMeN_DOSYALARI = {
    "main.py", "motor.py", "beyin.py", "planlayici.py",
    "sistem_talimati.py", "prompt_assembly.py", "provider_transport.py",
    "context_manager.py", "vektorel_hafiza.py", "session_db.py",
    "bounded_memory.py", "closed_learning_loop.py",
    "araclar_ekran.py", "araclar_gelismis.py", "araclar_makro.py",
    "araclar_ses.py", "araclar_tarayici.py", "araclar_telegram.py",
    "araclar_web.py", "izole_laboratuvar.py", "terminal_backends.py",
    "insan_arayuzu.py", "security_engine.py", "sistem_sinyalleri.py",
    "setup.py", "setup_keys.py", "uygulama_hafizasi.py",
    "yetenek_fabrikasi.py", "reyment.py",
}

# ReYMeN SDK'dan kopyalandığı bilinen kök-düzey dosyalar
ReYMeN_KOPYA_IPUCLARI = {
    "agent_init.py", "agent_runtime.py", "agent_runtime_helpers.py",
    "anthropic_adapter.py", "azure_identity_adapter.py", "bedrock_adapter.py",
    "auxiliary_client.py", "background_review.py", "batch_engine.py",
    "batch_runner.py", "browser_provider.py", "browser_registry.py",
    "chat_completion_helpers.py", "context_compressor.py", "context_engine.py",
    "context_references.py", "conversation_compression.py", "conversation_loop.py",
    "copilot_acp_client.py", "credential_persistence.py", "credential_pool.py",
    "credential_sources.py", "curator.py", "curator_backup.py",
    "display.py", "error_classifier.py", "file_safety.py",
    "gemini_cloudcode_adapter.py", "gemini_native_adapter.py", "gemini_schema.py",
    "google_code_assist.py", "google_oauth.py", "i18n.py",
    "image_gen_provider.py", "image_gen_registry.py", "image_routing.py",
    "insights.py", "iteration_budget.py", "jiter_preload.py",
    "lmstudio_reasoning.py", "manual_compression_feedback.py",
    "markdown_tables.py", "memory_manager.py", "memory_provider.py",
    "message_sanitization.py", "model_metadata.py", "models_dev.py",
    "moonshot_schema.py", "nous_rate_guard.py", "onboarding.py",
    "plugin_llm.py", "portal_tags.py", "process_bootstrap.py",
    "prompt_builder.py", "prompt_caching.py", "rate_limit_tracker.py",
    "redact.py", "retry_utils.py", "shell_hooks.py", "skill_bundles.py",
    "skill_commands.py", "skill_preprocessing.py", "skill_utils.py",
    "stream_diag.py", "subdirectory_hints.py", "system_prompt.py",
    "think_scrubber.py", "title_generator.py", "tool_dispatch_helpers.py",
    "tool_executor.py", "tool_guardrails.py", "tool_result_classification.py",
    "trajectory.py", "transcription_provider.py", "transcription_registry.py",
    "tts_provider.py", "tts_registry.py", "usage_pricing.py",
    "video_gen_provider.py", "video_gen_registry.py",
    "web_search_provider.py", "web_search_registry.py",
    "account_usage.py", "rate_limiter.py",
}

bulgular: dict[str, Any] = {}


def _py_dosyalari_bul(sadece_kok: bool = False) -> list[Path]:
    """Kökü tarar, atlanacak klasörleri ve skills/ yi geçer."""
    sonuc = []
    if sadece_kok:
        for f in KOK.iterdir():
            if f.suffix == ".py" and f.is_file():
                sonuc.append(f)
    else:
        for f in KOK.rglob("*.py"):
            # Atlanacak klasör içindeyse geç
            parcalar = set(f.relative_to(KOK).parts)
            if parcalar & ATLANACAK_KLASORLER:
                continue
            sonuc.append(f)
    return sorted(sonuc)


def dosya_tara() -> dict[str, Any]:
    """
    Kök dizini tara: ReYMeN/ReYMeN ayrımı, boyut ve anomali raporu.
    """
    kok_dosyalar = list(KOK.glob("*.py"))
    ReYMeN_bulunan = []
    ReYMeN_kopyalar = []
    bilinmeyen = []
    cok_buyuk = []   # >200 KB

    for d in kok_dosyalar:
        ad = d.name
        boyut_kb = d.stat().st_size / 1024
        if boyut_kb > 200:
            cok_buyuk.append((ad, f"{boyut_kb:.1f} KB"))
        if ad in ReYMeN_DOSYALARI:
            ReYMeN_bulunan.append(ad)
        elif ad in ReYMeN_KOPYA_IPUCLARI:
            ReYMeN_kopyalar.append(ad)
        else:
            bilinmeyen.append(ad)

    # Alt klasörlerdeki .py sayısı (skills hariç)
    alt_dosyalar = _py_dosyalari_bul(sadece_kok=False)
    kok_sayisi = len(kok_dosyalar)
    toplam_sayisi = len(alt_dosyalar)

    sonuc = {
        "kok_py_sayisi": kok_sayisi,
        "toplam_py_sayisi": toplam_sayisi,
        "ReYMeN_dosyalari": ReYMeN_bulunan,
        "ReYMeN_kopyalar_kok": ReYMeN_kopyalar,
        "bilinmeyen_kok": bilinmeyen,
        "cok_buyuk_dosyalar": cok_buyuk,
        "eksik_ReYMeN": sorted(ReYMeN_DOSYALARI - {d.name for d in kok_dosyalar}),
    }
    bulgular["dosya_tara"] = sonuc
    return sonuc


def import_test() -> dict[str, list[str]]:
    """
    ReYMeN çekirdek dosyalarını import etmeyi dene, nerede kırıldığını raporla.
    """
    hatalar = []
    basarili = []

    hedefler = [KOK / ad for ad in ReYMeN_DOSYALARI if (KOK / ad).exists()]

    # Kök dizini sys.path'e ekle
    if str(KOK) not in sys.path:
        sys.path.insert(0, str(KOK))

    for dosya in sorted(hedefler):
        modul_adi = dosya.stem
        try:
            spec = importlib.util.spec_from_file_location(modul_adi, dosya)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            basarili.append(dosya.name)
        except Exception:
            tb = traceback.format_exc(limit=3)
            # Son satırı al (asıl hata)
            ozet = tb.strip().splitlines()[-1]
            hatalar.append(f"{dosya.name}: {ozet}")

    sonuc = {"basarili": basarili, "hatali": hatalar}
    bulgular["import_test"] = sonuc
    return sonuc


def derleme_kontrol() -> dict[str, list[str]]:
    """
    ast.parse ile tüm taranabilir .py dosyalarını derle, syntax hatası varsa bul.
    """
    syntax_hatalar = []
    temiz = []

    for dosya in _py_dosyalari_bul():
        try:
            kaynak = dosya.read_text(encoding="utf-8", errors="replace")
            ast.parse(kaynak, filename=str(dosya))
            temiz.append(str(dosya.relative_to(KOK)))
        except SyntaxError as e:
            gorecel = str(dosya.relative_to(KOK))
            syntax_hatalar.append(f"{gorecel} satir {e.lineno}: {e.msg}")
        except Exception as e:
            gorecel = str(dosya.relative_to(KOK))
            syntax_hatalar.append(f"{gorecel}: {e}")

    sonuc = {
        "temiz_dosya_sayisi": len(temiz),
        "syntax_hata_sayisi": len(syntax_hatalar),
        "syntax_hatalar": syntax_hatalar,
    }
    bulgular["derleme_kontrol"] = sonuc
    return sonuc


def bagimlilik_zinciri() -> dict[str, Any]:
    """
    ReYMeN dosyalarının import zincirini takip et.
    Eksik modül / fonksiyon varsa tespit et.
    """
    eksik_moduller: list[str] = []
    mevcut_moduller: list[str] = []
    import_haritasi: dict[str, list[str]] = {}

    hedefler = [KOK / ad for ad in ReYMeN_DOSYALARI if (KOK / ad).exists()]

    for dosya in sorted(hedefler):
        try:
            kaynak = dosya.read_text(encoding="utf-8", errors="replace")
            agac = ast.parse(kaynak)
        except Exception:
            continue

        dosya_importlari: list[str] = []
        for dugum in ast.walk(agac):
            if isinstance(dugum, ast.Import):
                for alias in dugum.names:
                    dosya_importlari.append(alias.name.split(".")[0])
            elif isinstance(dugum, ast.ImportFrom):
                if dugum.module:
                    dosya_importlari.append(dugum.module.split(".")[0])

        import_haritasi[dosya.name] = dosya_importlari

        # Her import'u kontrol et
        for modul in dosya_importlari:
            if modul in ("__future__", "typing", "pathlib", "os", "sys",
                         "re", "json", "time", "datetime", "threading",
                         "subprocess", "traceback", "ast", "importlib",
                         "collections", "functools", "itertools", "io",
                         "hashlib", "base64", "copy", "math", "random",
                         "string", "struct", "socket", "logging", "warnings",
                         "contextlib", "dataclasses", "enum", "abc"):
                continue  # stdlib
            spec = importlib.util.find_spec(modul)
            if spec is None:
                # Proje dosyası mı?
                proje_dosyasi = KOK / f"{modul}.py"
                if not proje_dosyasi.exists():
                    kayit = f"{dosya.name} → '{modul}' bulunamadi"
                    if kayit not in eksik_moduller:
                        eksik_moduller.append(kayit)
            else:
                if modul not in mevcut_moduller:
                    mevcut_moduller.append(modul)

    sonuc = {
        "eksik_moduller": eksik_moduller,
        "mevcut_dis_moduller": sorted(set(mevcut_moduller)),
        "import_haritasi": import_haritasi,
    }
    bulgular["bagimlilik_zinciri"] = sonuc
    return sonuc


def karsilastir() -> dict[str, Any]:
    """
    ReYMeN SDK agent/ dizini vs ReYMeN kök dosyaları farkını çıkar.
    Aynı ada sahip ama farklı içerikli dosyaları tespit et.
    """
    agent_klasoru = KOK / "agent"
    eslesme_farklar: list[str] = []
    sadece_ReYMeN: list[str] = []
    sadece_ReYMeN: list[str] = []
    ayni_icerik: list[str] = []

    if not agent_klasoru.exists():
        sonuc = {"durum": "agent/ klasoru bulunamadi"}
        bulgular["karsilastir"] = sonuc
        return sonuc

    agent_dosyalari = {f.name for f in agent_klasoru.glob("*.py")}
    kok_dosyalari = {f.name for f in KOK.glob("*.py")}

    ortak = agent_dosyalari & kok_dosyalari
    for ad in sorted(ortak):
        if ad == "__init__.py":
            continue
        kok_icerik = (KOK / ad).read_bytes()
        agent_icerik = (agent_klasoru / ad).read_bytes()
        if kok_icerik == agent_icerik:
            ayni_icerik.append(ad)
        else:
            # Boyut farkı
            fark_byte = len(kok_icerik) - len(agent_icerik)
            eslesme_farklar.append(
                f"{ad}: kok={len(kok_icerik)}B agent={len(agent_icerik)}B fark={fark_byte:+d}B"
            )

    for ad in sorted(kok_dosyalari - agent_dosyalari):
        if ad in ReYMeN_DOSYALARI:
            sadece_ReYMeN.append(ad)

    for ad in sorted(agent_dosyalari - kok_dosyalari):
        sadece_ReYMeN.append(ad)

    sonuc = {
        "ortak_farkli": eslesme_farklar,
        "ortak_ayni_icerik": ayni_icerik,
        "sadece_ReYMeN_koku": sadece_ReYMeN,
        "sadece_ReYMeN_agent": sadece_ReYMeN[:20],  # ilk 20
    }
    bulgular["karsilastir"] = sonuc
    return sonuc


def ozet_rapor() -> str:
    """
    Tüm bulguları tek bir metin haline getirir (Claude Code'a göndermek için).
    Henüz çalıştırılmamış yöntemleri otomatik çalıştırır.
    """
    if "dosya_tara" not in bulgular:
        dosya_tara()
    if "import_test" not in bulgular:
        import_test()
    if "derleme_kontrol" not in bulgular:
        derleme_kontrol()
    if "bagimlilik_zinciri" not in bulgular:
        bagimlilik_zinciri()
    if "karsilastir" not in bulgular:
        karsilastir()

    satirlar: list[str] = [
        "=" * 60,
        "ReYMeN OTOMATİK SORUN TARAMA RAPORU",
        f"Proje koku: {KOK}",
        "=" * 60,
    ]

    # --- 1. Dosya tarama ---
    dt = bulgular["dosya_tara"]
    satirlar += [
        "",
        "## 1. DOSYA TARAMA",
        f"  Kok .py dosyasi: {dt['kok_py_sayisi']}",
        f"  Toplam .py (skills hariç): {dt['toplam_py_sayisi']}",
        f"  ReYMeN cekirdek dosyalari: {len(dt['ReYMeN_dosyalari'])} adet",
    ]
    if dt["eksik_ReYMeN"]:
        satirlar.append(f"  !! EKSİK ReYMeN DOSYALARI: {dt['eksik_ReYMeN']}")
    if dt["cok_buyuk_dosyalar"]:
        satirlar.append("  Cok buyuk dosyalar (>200 KB):")
        for ad, boyut in dt["cok_buyuk_dosyalar"]:
            satirlar.append(f"    - {ad}: {boyut}")
    if dt["bilinmeyen_kok"]:
        satirlar.append(f"  Siniflandirilmamis kok dosyalari: {dt['bilinmeyen_kok']}")

    # --- 2. Import testi ---
    it = bulgular["import_test"]
    satirlar += [
        "",
        "## 2. IMPORT TESTİ",
        f"  Basarili: {len(it['basarili'])} dosya",
        f"  Hatali:   {len(it['hatali'])} dosya",
    ]
    if it["hatali"]:
        satirlar.append("  Import hatalari:")
        for h in it["hatali"]:
            satirlar.append(f"    !! {h}")

    # --- 3. Derleme kontrolü ---
    dk = bulgular["derleme_kontrol"]
    satirlar += [
        "",
        "## 3. DERLEME KONTROLÜ (AST)",
        f"  Temiz: {dk['temiz_dosya_sayisi']} dosya",
        f"  Syntax hatasi: {dk['syntax_hata_sayisi']} dosya",
    ]
    if dk["syntax_hatalar"]:
        satirlar.append("  Syntax hatalari:")
        for h in dk["syntax_hatalar"]:
            satirlar.append(f"    !! {h}")

    # --- 4. Bağımlılık zinciri ---
    bz = bulgular["bagimlilik_zinciri"]
    satirlar += [
        "",
        "## 4. BAĞIMLILIK ZİNCİRİ",
        f"  Eksik modul sayisi: {len(bz['eksik_moduller'])}",
    ]
    if bz["eksik_moduller"]:
        satirlar.append("  Eksik moduller:")
        for e in bz["eksik_moduller"][:20]:
            satirlar.append(f"    ?? {e}")

    # --- 5. Karşılaştırma ---
    ks = bulgular["karsilastir"]
    satirlar += ["", "## 5. ReYMeN vs ReYMeN KARŞILAŞTIRMA"]
    if "durum" in ks:
        satirlar.append(f"  {ks['durum']}")
    else:
        satirlar += [
            f"  Ayni ada sahip, farkli icerik: {len(ks['ortak_farkli'])} dosya",
            f"  Ayni ada sahip, ayni icerik (kopyalar): {len(ks['ortak_ayni_icerik'])} dosya",
            f"  Sadece ReYMeN kokunde: {len(ks['sadece_ReYMeN_koku'])} dosya",
        ]
        if ks["ortak_farkli"]:
            satirlar.append("  Farkli icerikli dosyalar:")
            for f in ks["ortak_farkli"][:10]:
                satirlar.append(f"    ~ {f}")
        if ks["ortak_ayni_icerik"]:
            satirlar.append(f"  Birebir kopyalar: {ks['ortak_ayni_icerik'][:5]} ...")

    satirlar += ["", "=" * 60, "TARAMA TAMAMLANDI", "=" * 60]
    return "\n".join(satirlar)


if __name__ == "__main__":
    print("ReYMeN sorun taramasi basliyor...\n")
    rapor = ozet_rapor()
    print(rapor)

    # Raporu dosyaya da kaydet
    cikti = KOK / "output" / "sorun_raporu.txt"
    cikti.parent.mkdir(exist_ok=True)
    cikti.write_text(rapor, encoding="utf-8")
    print(f"\nRapor kaydedildi: {cikti}")
