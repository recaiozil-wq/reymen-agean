---
name: ecc_windows-desktop-e2e_references_launch-via-subprocess-so-we-can-pass-env-connect-pywinauto-b
description: Launch via subprocess so we can pass env; connect pywinauto by PID
title: "Ecc Windows Desktop E2E References Launch Via Subprocess So We Can Pass Env Connect Pywinauto B"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Launch via subprocess so we can pass env; connect pywinauto by PID |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Launch via subprocess so we can pass env; connect pywinauto by PID
    proc = subprocess.Popen(
        [APP_PATH] + shlex.split(APP_ARGS),
        env=sandbox_env,
    )
    pw_app = Application(backend="uia").connect(process=proc.pid, timeout=LAUNCH_TIMEOUT)
    win    = pw_app.window(title=APP_TITLE)
    win.wait("visible", timeout=LAUNCH_TIMEOUT)
    yield win

    if getattr(getattr(request.node, "rep_call", None), "failed", False):
        os.makedirs(ARTIFACT_DIR, exist_ok=True)
        try:
            win.capture_as_image().save(
                os.path.join(ARTIFACT_DIR, f"FAIL_{request.node.name}.png")
            )
        except Exception:
            pass
    try:
        win.close()
        proc.wait(timeout=5)
    except Exception:
        proc.kill()
