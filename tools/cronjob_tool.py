#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cronjob_tool.py — ReYMeN cron job yönetimi API tool'u.

Hermes cronjob() API'si ile uyumlu. Mevcut cron/jobs.py altyapısını kullanır.

Kullanım:
    cronjob(action="create", schedule="every 30m", prompt="...")
    cronjob(action="list")
    cronjob(action="update", job_id="abc", updates={"name": "yeni isim"})
    cronjob(action="pause", job_id="abc")
    cronjob(action="resume", job_id="abc")
    cronjob(action="remove", job_id="abc")
    cronjob(action="run", job_id="abc")

Schedule formatları:
    - "30m"         → 30 dk sonra bir kere
    - "every 30m"   → her 30 dk
    - "every 2h"    → her 2 saat
    - "0 9 * * *"   → cron expression
    - "2026-07-01T14:00" → belirli zamanda
"""

import json
import logging
import os
import sys
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Proje kökünü path'e ekle ─────────────────────────────────────────────
_PROJE_KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJE_KOK not in sys.path:
    sys.path.insert(0, _PROJE_KOK)


def _iceri_aktar():
    """cron/jobs.py modülünü içeri aktar (lazy)."""
    try:
        from cron import jobs as cron_jobs
        return cron_jobs
    except ImportError:
        try:
            # Direkt import dene (Python 3.4+)
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "cron_jobs",
                os.path.join(_PROJE_KOK, "cron", "jobs.py")
            )
            cron_jobs = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cron_jobs)
            return cron_jobs
        except Exception as e:
            raise ImportError(f"cron/jobs.py yüklenemedi: {e}")


def _json_cevap(ok: bool, **kwargs) -> str:
    """Standart JSON cevap formatı."""
    cevap = {"ok": ok, **kwargs}
    return json.dumps(cevap, ensure_ascii=False, default=str, indent=2)


# ── Ana API ───────────────────────────────────────────────────────────────

def cronjob(
    action: str = "list",
    schedule: str = "",
    prompt: str = "",
    name: str = "",
    job_id: str = "",
    skills: list = None,
    script: str = "",
    model: str = "",
    provider: str = "",
    deliver: str = "",
    repeat: int = 0,
    no_agent: bool = False,
    workdir: str = "",
    updates: dict = None,
    enabled_toolsets: list = None,
    context_from: list = None,
):
    """
    ReYMeN cron job yönetimi — Hermes cronjob() API'si ile uyumlu.

    Args:
        action: create / list / update / pause / resume / remove / run
        schedule: Zamanlama (örn. "every 30m", "0 9 * * *")
        prompt: Job prompt'u (create'de zorunlu, no_agent=False ise)
        name: Job adı
        job_id: Job ID (update/pause/resume/remove/run için)
        skills: Skill listesi
        script: Script yolu (no_agent=True ile kullanılır)
        model: Model override
        provider: Provider override
        deliver: Teslim yeri ("origin", "local")
        repeat: Tekrar sayısı (0=sonsuz)
        no_agent: True = script direkt çalışır, LLM yok
        workdir: Çalışma dizini
        updates: update action'ı için güncelleme sözlüğü
        enabled_toolsets: Kısıtlı toolset listesi
        context_from: Zincirleme job ID'leri

    Returns:
        str: JSON formatında sonuç
    """
    try:
        cron_jobs = _iceri_aktar()
    except ImportError as e:
        return _json_cevap(False, error=f"Cron altyapısı yüklenemedi: {e}")

    try:
        if action == "create":
            return _create(cron_jobs, schedule, prompt, name, skills,
                           script, model, provider, deliver, repeat,
                           no_agent, workdir, enabled_toolsets, context_from)
        elif action == "list":
            return _list(cron_jobs)
        elif action == "update":
            return _update(cron_jobs, job_id, updates)
        elif action == "pause":
            return _pause(cron_jobs, job_id)
        elif action == "resume":
            return _resume(cron_jobs, job_id)
        elif action == "remove":
            return _remove(cron_jobs, job_id)
        elif action == "run":
            return _run(cron_jobs, job_id)
        else:
            return _json_cevap(False, error=f"Bilinmeyen action: {action}. "
                               "Geçerli: create/list/update/pause/resume/remove/run")
    except Exception as e:
        logger.exception("cronjob hatası")
        return _json_cevap(False, error=str(e))


def _create(cron_jobs, schedule, prompt, name, skills, script,
            model, provider, deliver, repeat, no_agent, workdir,
            enabled_toolsets, context_from):
    """Yeni cron job oluştur."""
    if not schedule:
        return _json_cevap(False, error="schedule zorunlu")

    if no_agent:
        if not script:
            return _json_cevap(False, error="no_agent=True iken script zorunlu")
    elif not prompt and not skills:
        return _json_cevap(False, error="prompt veya skills zorunlu (no_agent=False)")

    kwargs = {
        "prompt": prompt or None,
        "schedule": schedule,
        "name": name or None,
        "skills": skills or None,
        "script": script or None,
        "model": model or None,
        "provider": provider or None,
        "deliver": deliver or None,
        "repeat": repeat if repeat > 0 else None,
        "no_agent": no_agent,
        "workdir": workdir or None,
        "enabled_toolsets": enabled_toolsets or None,
        "context_from": context_from or None,
    }
    # prompt her zaman gitsin (positional arg), diğer None'ları temizle
    prompt_val = kwargs.pop("prompt")
    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    job = cron_jobs.create_job(prompt_val, **kwargs)
    return _json_cevap(True, islem="create", job=_normalize_job(job))


def _list(cron_jobs):
    """Tüm cron job'larını listele."""
    jobs = cron_jobs.list_jobs(include_disabled=True)
    return _json_cevap(True, islem="list", jobs=[_normalize_job(j) for j in jobs], toplam=len(jobs))


def _update(cron_jobs, job_id, updates):
    """Job güncelle."""
    if not job_id:
        return _json_cevap(False, error="job_id zorunlu")
    if not updates:
        return _json_cevap(False, error="updates sözlüğü zorunlu")

    # job_id name de olabilir — resolve et
    job = cron_jobs.resolve_job_ref(job_id)
    if not job:
        return _json_cevap(False, error=f"Job bulunamadı: {job_id}")

    result = cron_jobs.update_job(job["id"], updates)
    if result:
        return _json_cevap(True, islem="update", job=_normalize_job(result))
    return _json_cevap(False, error="Job güncellenemedi")


def _pause(cron_jobs, job_id):
    """Job'u duraklat."""
    if not job_id:
        return _json_cevap(False, error="job_id zorunlu")

    result = cron_jobs.pause_job(job_id)
    if result:
        return _json_cevap(True, islem="pause", job=_normalize_job(result))
    return _json_cevap(False, error=f"Job bulunamadı: {job_id}")


def _resume(cron_jobs, job_id):
    """Duraklatılmış job'ı devam ettir."""
    if not job_id:
        return _json_cevap(False, error="job_id zorunlu")

    result = cron_jobs.resume_job(job_id)
    if result:
        return _json_cevap(True, islem="resume", job=_normalize_job(result))
    return _json_cevap(False, error=f"Job bulunamadı: {job_id}")


def _remove(cron_jobs, job_id):
    """Job'u sil."""
    if not job_id:
        return _json_cevap(False, error="job_id zorunlu")

    result = cron_jobs.remove_job(job_id)
    if result:
        return _json_cevap(True, islem="remove", job_id=job_id)
    return _json_cevap(False, error=f"Job bulunamadı: {job_id}")


def _run(cron_jobs, job_id):
    """Job'u hemen çalıştır (bir sonraki tick'te)."""
    if not job_id:
        return _json_cevap(False, error="job_id zorunlu")

    result = cron_jobs.trigger_job(job_id)
    if result:
        return _json_cevap(True, islem="run", mesaj=f"'{job_id}' bir sonraki tick'te çalışacak",
                           job=_normalize_job(result))
    return _json_cevap(False, error=f"Job bulunamadı: {job_id}")


def _normalize_job(job: dict) -> dict:
    """Job dict'ini temiz formatla — sadece kullanıcıya gösterilecek alanlar."""
    if not job:
        return {}
    return {
        "id": job.get("id", ""),
        "name": job.get("name", ""),
        "schedule": job.get("schedule_display", ""),
        "state": job.get("state", "?"),
        "enabled": job.get("enabled", True),
        "next_run": job.get("next_run_at", ""),
        "last_run": job.get("last_run_at", ""),
        "last_status": job.get("last_status", ""),
        "repeat": job.get("repeat", {}),
        "skills": job.get("skills", []),
        "script": job.get("script", ""),
        "no_agent": job.get("no_agent", False),
        "model": job.get("model", ""),
        "provider": job.get("provider", ""),
        "prompt": (job.get("prompt") or "")[:120] if job.get("prompt") else "",
        "workdir": job.get("workdir", ""),
        "created_at": job.get("created_at", ""),
    }


# ── ReYMeN tool standardı ─────────────────────────────────────────────────

def run(**kwargs) -> str:
    """
    ReYMeN tool standardı — cronjob() wrapper'ı.

    Kullanım:
        run(action="list")
        run(action="create", schedule="every 30m", prompt="Merhaba")
        run(action="remove", job_id="abc123")
    """
    return cronjob(**kwargs)


def motor_kaydet(motor) -> None:
    """Motor'a CRON_JOB aracını kaydet."""
    motor._plugin_arac_kaydet(
        "CRON_JOB",
        run,
        (
            "Cron job yönetimi — CRON_JOB(action, schedule, prompt, job_id, ...)\n"
            "Actions: create/list/update/pause/resume/remove/run\n"
            "Schedule: 'every 30m', '0 9 * * *', '2026-07-01T14:00'\n"
            "Örnek: CRON_JOB(action='create', schedule='every 1h', prompt='Saatlik rapor')"
        ),
    )


if __name__ == "__main__":
    # Test
    print(cronjob(action="list"))
