import subprocess, sys, os, time

profile = sys.argv[1] if len(sys.argv) > 1 else "kiral38"
hermes = r"C:\Users\marko\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe"
log_dir = os.path.expanduser(f"~/AppData/Local/hermes/profiles/{profile}/logs")
os.makedirs(log_dir, exist_ok=True)

log = os.path.join(log_dir, f"gateway_launch_{profile}.log")

with open(log, "w") as f:
    f.write(f"{time.ctime()} Baslatiliyor: {profile}\n")
    f.write(f"hermes: {hermes}\n")
    f.flush()
    
    proc = subprocess.Popen(
        [hermes, "-p", profile, "gateway", "start"],
        stdout=f,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
        close_fds=True
    )
    f.write(f"PID: {proc.pid}\n")

print(f"{profile} gateway PID: {proc.pid}")
