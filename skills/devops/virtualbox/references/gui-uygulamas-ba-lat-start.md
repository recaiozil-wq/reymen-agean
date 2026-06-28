---
skill_id: ebfce08bb25b
usage_count: 1
last_used: 2026-06-16
---
# GUI uygulaması başlat (start)
subprocess.run([
    vbox, "guestcontrol", vm, "start",
    "--exe", "/usr/bin/qterminal",
    "--username", user, "--password", pwd
], env=env)