#!/usr/bin/env python3
# DeepSeek Ajan v1.0 - Minimal CLI Agent for DeepSeek-v4-flash
# Tek dosya, sifir bagimlilik. pip install openai python-dotenv

import json, os, sys, time, readline
from datetime import datetime
from pathlib import Path

DEFAULT_MODEL = "deepseek-chat"
API_BASE = "https://api.deepseek.com/v1"
MAX_HISTORY = 50
SESSIONS_DIR = Path.home() / ".deepseek_ajan" / "sessions"


class R:
    R = chr(27) + "[0m"
    B = chr(27) + "[1m"
    D = chr(27) + "[2m"
    G = chr(27) + "[92m"
    C = chr(27) + "[96m"
    Y = chr(27) + "[93m"
    R2 = chr(27) + "[91m"


def banner():
    print(f"{R.B}{R.C}D E E P S E E K   A J A N   v1.0{R.R}")
    print(f"{R.D}  Model: deepseek-chat | /help ile komutlar{R.R}")
    print()


def load_env():
    p = Path(".env")
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())
    return os.environ.get("DEEPSEEK_API_KEY", "")


def sp(name):
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    return SESSIONS_DIR / f"{name}.jsonl"


def list_sessions():
    ss = sorted(SESSIONS_DIR.glob("*.jsonl"), key=os.path.getmtime, reverse=True)
    if not ss:
        print(f"  {R.D}Hic session yok.{R.R}")
        return []
    for i, s in enumerate(ss, 1):
        n = s.stem
        sz = sum(1 for _ in open(s))
        mt = datetime.fromtimestamp(os.path.getmtime(s)).strftime("%d/%m %H:%M")
        print(f"  {R.C}{i}.{R.R} {n} ({sz} mesaj, {mt})")
    return ss


def api_istek(msgs, api_key, model=None, temp=0.7):
    try:
        from openai import OpenAI
    except ImportError:
        print("openai kutuphanesi gerekli: pip install openai python-dotenv")
        sys.exit(1)
    client = OpenAI(api_key=api_key, base_url=API_BASE)
    model = model or DEFAULT_MODEL
    try:
        r = client.chat.completions.create(
            model=model, messages=msgs, max_tokens=4096, temperature=temp
        )
        return r.choices[0].message.content.strip() or ""
    except Exception as e:
        return f"[API Hatasi] {e}"


def cmd_py(code):
    try:
        import io
        from contextlib import redirect_stdout, redirect_stderr

        fo, fe = io.StringIO(), io.StringIO()
        with redirect_stdout(fo), redirect_stderr(fe):
            exec(code)
        if fo.getvalue():
            print("  " + R.G + fo.getvalue().strip() + R.R)
        if fe.getvalue():
            print("  " + R.R2 + fe.getvalue().strip() + R.R)
        if not fo.getvalue() and not fe.getvalue():
            print("  " + R.D + "OK (cikti yok)" + R.R)
    except Exception as e:
        print("  " + R.R2 + "Hata: " + str(e) + R.R)


def cmd_sys(cmd):
    try:
        import subprocess

        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if r.stdout:
            print("  " + r.stdout.strip())
        if r.stderr:
            print("  " + R.R2 + r.stderr.strip() + R.R)
        if r.returncode != 0:
            print("  " + R.R2 + "Exit: " + str(r.returncode) + R.R)
    except subprocess.TimeoutExpired:
        print("  " + R.R2 + "Zaman asimi (30sn)" + R.R)
    except Exception as e:
        print("  " + R.R2 + "Hata: " + str(e) + R.R)


def kaydet(ad, msgs):
    if not ad:
        ad = "sohbet_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    p = sp(ad)
    with open(p, "w", encoding="utf-8") as f:
        for m in msgs[-MAX_HISTORY:]:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    return p


def yukle(ad):
    p = sp(ad)
    if not p.exists():
        ss = sorted(SESSIONS_DIR.glob("*.jsonl"), key=os.path.getmtime, reverse=True)
        try:
            idx = int(ad) - 1
            if 0 <= idx < len(ss):
                p = ss[idx]
        except ValueError:
            pass
    if not p.exists():
        print("  " + R.R2 + "Session bulunamadi: " + ad + R.R)
        return []
    msgs = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                msgs.append(json.loads(line))
    print("  " + R.G + "Yuklendi: " + p.name + " (" + str(len(msgs)) + " mesaj)" + R.R)
    return msgs


def help():
    print()
    print(R.B + R.C + "Komutlar:" + R.R)
    for k, v in [
        ("/help", "Bu mesaj"),
        ("/exit", "Cikis (Ctrl+C)"),
        ("/new", "Yeni session"),
        ("/save <ad>", "Session kaydet"),
        ("/load <ad>", "Session yukle"),
        ("/list", "Session listele"),
        ("/model <ad>", "Model degistir"),
        ("/clear", "Ekran temizle"),
        ("/py <kod>", "Python calistir"),
        ("/sys <komut>", "Shell calistir"),
    ]:
        print(f"  {R.G}{k}{R.R}  {v}")
    print()


def repl():
    api_key = load_env()
    if not api_key:
        print("HATA: DEEPSEEK_API_KEY bulunamadi.")
        print("  .env'ye ekle: DEEPSEEK_API_KEY=***")
        print("  Veya: $env:DEEPSEEK_API_KEY=*** (PowerShell)")
        sys.exit(1)

    model = os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL)
    msgs = [
        {
            "role": "system",
            "content": "Sen yardimsever bir AI asistanisin. Turkce cevap ver.",
        }
    ]

    banner()
    help()

    while True:
        try:
            ui = input(f"\n{R.B}{R.G}>>{R.R} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{R.Y}Gorusuruz!{R.R}")
            break

        if not ui:
            continue

        if ui.startswith("/"):
            parts = ui[1:].split(maxsplit=1)
            cmd, arg = parts[0].lower(), (parts[1] if len(parts) > 1 else "")

            if cmd == "exit":
                print(f"{R.Y}Gorusuruz!{R.R}")
                break
            elif cmd == "help":
                help()
            elif cmd == "new":
                msgs = msgs[:1]
                print("  " + R.G + "Yeni session." + R.R)
            elif cmd == "save":
                print("  " + R.G + "Kaydedildi: " + str(kaydet(arg, msgs)) + R.R)
            elif cmd == "load":
                loaded = yukle(arg)
                if loaded:
                    msgs = loaded
            elif cmd == "list":
                list_sessions()
            elif cmd == "model":
                if arg:
                    model = arg
                    print("  " + R.G + "Model: " + model + R.R)
                else:
                    print("  Model: " + R.C + model + R.R)
            elif cmd == "clear":
                os.system("cls" if os.name == "nt" else "clear")
            elif cmd == "py":
                if arg:
                    cmd_py(arg)
                else:
                    print("  " + R.Y + "Kullanim: /py <kod>" + R.R)
            elif cmd == "sys":
                if arg:
                    cmd_sys(arg)
                else:
                    print("  " + R.Y + "Kullanim: /sys <komut>" + R.R)
            else:
                print("  " + R.R2 + "Bilinmeyen: /" + cmd + R.R + " (/help)")
            continue

        msgs.append({"role": "user", "content": ui})
        print("  " + R.D + "DeepSeek dusunuyor..." + R.R, end="\r")
        t0 = time.time()

        response = api_istek(msgs, api_key, model=model)
        elapsed = time.time() - t0

        print("  " + " " * 30, end="\r")
        print("  " + R.D + chr(9203) + " " + f"{elapsed:.1f}s" + R.R)

        if response:
            print(f"\n{R.B}{R.C}DeepSeek:{R.R}")
            print("  " + response.replace("\n", "\n  "))
            msgs.append({"role": "assistant", "content": response})
        else:
            print("  " + R.R2 + "Bos yanit." + R.R)

        if len(msgs) % 5 == 0:
            kaydet("otomatik", msgs)


def main():
    try:
        repl()
    except KeyboardInterrupt:
        print(f"\n{R.Y}Gorusuruz!{R.R}")


if __name__ == "__main__":
    main()
