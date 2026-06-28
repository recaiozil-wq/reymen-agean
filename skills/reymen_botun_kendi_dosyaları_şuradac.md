---
name: ReYMeN bot'un kendi dosyaları şurada:

C
description: Tamamlanamadi: tur asimi
created: 2026-06-18
usage_count: 1
last_used: 2026-06-18
---

# ReYMeN bot'un kendi dosyaları şurada:

C

Tamamlanamadi: tur asimi

## Adimlar

KOMUT_CALISTIR: "dir /s /b \"C:\\Users\\marko\\OneDrive\\Desktop\\Reymen Proje\\hermes_projesi\""
KOMUT_CALISTIR: "powershell -Command \"Get-ChildItem -Path 'C:\\Users\\marko\\OneDrive\\Desktop\\Reymen Proje\\hermes_projesi' -Recurse | Select-Object FullName, Length, Extension | Format-Table -AutoSize\""
KOMUT_CALISTIR: "powershell -Command \"Get-ChildItem -Path 'C:\\Users\\marko\\OneDrive\\Desktop\\Reymen Proje\\hermes_projesi' -Recurse | Select-Object FullName, Length, Extension | Format-Table -AutoSize | Out-String -Width 4096\""
KOMUT_CALISTIR: "powershell -Command \"Get-ChildItem -Path 'C:\\Users\\marko\\OneDrive\\Desktop\\Reymen Proje\\hermes_projesi' -Recurse | Select-Object FullName, Length, Extension | Format-Table -AutoSize | Out-String -Width 4096 | Out-File -FilePath 'C:\\Users\\marko\\OneDrive\\Desktop\\Reymen Proje\\hermes_projesi\\_analiz_temp.txt' -Encoding UTF8\""
