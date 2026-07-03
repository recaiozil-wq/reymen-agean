import subprocess, os, sys, time

profile = sys.argv[1] if len(sys.argv) > 1 else "kiral38"
hermes = r"C:\Users\marko\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe"

# Eski state'i temizle
state_path = os.path.expanduser(f"~/AppData/Local/hermes/profiles/{profile}/gateway_state.json")
if os.path.exists(state_path):
    os.remove(state_path)

# Log
log_dir = os.path.expanduser(f"~/AppData/Local/hermes/profiles/{profile}/logs")
os.makedirs(log_dir, exist_ok=True)
logfile = os.path.join(log_dir, f"gw_{profile}.log")

with open(logfile, "w") as f:
    f.write(f"{time.ctime()} START {profile}\n")
    f.flush()
    proc = subprocess.Popen(
        [hermes, "-p", profile, "gateway", "start"],
        stdout=f, stderr=subprocess.STDOUT,
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
        close_fds=True
    )
    f.write(f"PID: {proc.pid}\n")

time.sleep(5)

# Log son 10 satir 
with open(logfile) as f:
    lines = f.readlines()
print(f"{profile}: PID started, log lines={len(lines)}")
for l in lines[-10:]:
    print(f"  {l.strip()[:120]}")
