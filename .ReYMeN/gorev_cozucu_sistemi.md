# ReYMeN Otonom Görev Çözücü Sistemi

## ADIMLAR
ADIM_1 | reymen/scripts/step_01_pyproject.py
ADIM_2 | reymen/scripts/step_02_shell_true.py
ADIM_3 | reymen/scripts/step_03_except_pass.py
ADIM_4 | reymen/scripts/step_04_init_all.py
ADIM_5 | reymen/scripts/step_05_cicd.py
ADIM_6 | reymen/scripts/step_06_cron_topla.py

## NE
ReYMeN projesinde otonom çalışan bir görev çözücü motor kur.
Sistem herhangi bir görevi alır, Python kod çalıştırarak çözer,
hata alırsa kendi kendine düzeltir.

## NASIL ÇALIŞACAK
1. Görev dosyasından ADIMLARI oku
2. Her adımda Python script çalıştır
3. Hata varsa LLM'e sor, düzeltilmiş kod al, fix/ klasörüne kaydet
4. Tekrar dene (max 3)
5. Başarılıysa sonraki adım
6. Tüm adımlar bitince rapor ver

## KULLANILACAK ARAÇLAR
- model_adapter.py → get_active_adapter() ile model seç
- orchestrator.py → solve_step() ile adım çöz
- motor.py → gorev_coz() ile başlat
