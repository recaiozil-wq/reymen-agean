---
title: Zamanlanmış Görev
description: Windows Task Scheduler veya Python ile görev zamanlama
tags: [cron, zamanlama, scheduler, windows]
---

## Windows Task Scheduler ile (PowerShell)
KOMUT_CALISTIR "powershell -Command \"schtasks /create /tn 'ReymenGorev' /tr 'python C:\proje\script.py' /sc daily /st 09:00\""

## Python schedule ile (kurulu ise)
PYTHON_CALISTIR "
import schedule, time
def gorev():
    print('Görev çalıştı')
schedule.every(10).minutes.do(gorev)
# schedule.every().hour.do(gorev)
# schedule.every().day.at('09:00').do(gorev)
print('Scheduler hazır')
"

## Basit gecikme ile çalıştır
PYTHON_CALISTIR "
import time, threading
def gecikme_ile_calistir(fn, saniye):
    def _():
        time.sleep(saniye)
        fn()
    threading.Thread(target=_, daemon=True).start()
gecikme_ile_calistir(lambda: print('Çalıştı!'), 30)
print('30 saniye sonra çalışacak')
"
