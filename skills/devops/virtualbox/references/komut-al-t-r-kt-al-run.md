---
skill_id: e7d4a23ced69
usage_count: 1
last_used: 2026-06-16
---
# Komut çalıştır + çıktı al (run)
r = subprocess.run([
    vbox, "guestcontrol", vm, "run",
    "--exe", "/usr/bin/ls",
    "--username", user, "--password", pwd,
    "--wait-stdout", "--", "-la", "/usr/bin/",
], env=env, capture_output=True, text=True)
print(r.stdout)
```