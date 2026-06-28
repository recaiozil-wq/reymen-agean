; ============================================================================
; windows-shortcuts.ahk — ReYMeN Agent Windows Otomasyon Kısayolları
; ============================================================================
; Tüm özel script'ler Ctrl+Alt+<Harf> ile tetiklenir.
; AutoHotkey v2 ile çalışır.
;
#NoTrayIcon
#Persistent

; ------------- MOUSE/KLAVYE OTOMASYONU -------------
!^m::{
    Run("python C:\Users\marko\hermesmouse.py")
}

; ------------- GÖRSEL ONAYLAMA -------------
!^o::{
    Run('python C:\Users\marko\AppData\Local\hermes\scripts\approve_popup.py')
}

; ------------- EKRAN VİZYON ANALİZ -------------
!^v::{
    Run('powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\marko\AppData\Local\hermes\scripts\capture_screen_temp.ps1"')
}

; ------------- KALI LİNUX VM -------------
!^k::{
    Run('ssh kali@192.168.56.103')
}

; ------------- KALI HELP EXPLORER -------------
!^h::{
    Run('ssh kali@192.168.56.103 "apropos . | head -50"')
}

; ------------- KALI USB WIFI -------------
!^w::{
    Run('VBoxManage controlvm "Kali" keyboardputstring "sudo iwlist wlan0 scan\n"')
}

; ------------- VM WEB TERMINAL -------------
!^t::{
    Run('python C:\Users\marko\AppData\Local\hermes\scripts\vm_web_terminal.py')
}

; ------------- OLLAMA -------------
!^q::{
    Run('python C:\Users\marko\AppData\Local\hermes\scripts\ollama_start.py')
}

; ------------- VSCODE AGENT KONTROL -------------
!^a::{
    Run('code')
}

; ------------- TOR BROWSER -------------
!^b::{
    Run('"C:\Users\marko\OneDrive\Desktop\Tor Browser\Browser\firefox.exe"')
}

; ------------- PYTHON CLI INSTALLER -------------
!^i::{
    Run('python -c "import sys; print('\''CLI kurulum script'\''ni calistir'\'')"')
    MsgBox("CLI kurulum script'ini calistir")
}

; ------------- HAFIZA TEMİZLİĞİ -------------
!^r::{
    Run('python -c "import os, glob; [os.remove(f) for f in glob.glob('\''C:\\\\Users\\\\marko\\\\AppData\\\\Local\\\\hermes\\\\state.db'\'')]"')
}

; ------------- ENV KAYIT KURALLARI -------------
!^n::{
    Run('notepad "C:\Users\marko\AppData\Local\hermes\.env"')
}

; ------------- SKILL + OBSIDIAN ÖN KONTROL -------------
!^s::{
    Run('python C:\Users\marko\AppData\Local\hermes\hooks\sync_skills_to_obsidian.py')
}

; ============================================================================
; KISA NOTLAR:
; ! = Alt, ^ = Ctrl, + = Shift, # = Win
; !^m = Ctrl+Alt+M
; Kendi ihtiyacına göre harfleri değiştirebilirsin.
; ============================================================================
