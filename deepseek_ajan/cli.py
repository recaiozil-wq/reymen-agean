"""Ana REPL arayuzu."""

import os, sys, time, json
from datetime import datetime
from pathlib import Path

from deepseek_ajan.api import api_istek
from deepseek_ajan.guvenlik import yetki_kontrol, onay_gerekli, durum as guvenlik_durum
from deepseek_ajan.hafiza import (
    hafizada_ara,
    kaydet as h_kaydet,
    basari_kaydet,
    hata_kaydet,
    istatistik,
    temizle,
)
from deepseek_ajan.session import (
    listele as s_listele,
    kaydet as s_kaydet,
    yukle as s_yukle,
)
from deepseek_ajan.tools import cmd_py, cmd_sys, cmd_read, cmd_write, cmd_ls


class R:
    R = chr(27) + "[0m"
    B = chr(27) + "[1m"
    D = chr(27) + "[2m"
    G = chr(27) + "[92m"
    C = chr(27) + "[96m"
    Y = chr(27) + "[93m"
    R2 = chr(27) + "[91m"


def banner():
    print(f"{R.B}{R.C}")
    print("  DeepSeek Ajan v1.0")
    print(f"  Guvenli, full yetkili, ogrenen AI agent{R.R}")
    print(f"  {R.D}Model: deepseek-v4-flash | /help ile komutlar{R.R}")
    print(f"  {R.D}{guvenlik_durum()}{R.R}")
    print()


def help():
    print()
    print(f"{R.B}{R.C}Komutlar:{R.R}")
    for k, v in [
        ("/help", "Bu mesaj"),
        ("/exit", "Cikis"),
        ("/new", "Yeni session"),
        ("/save <ad>", "Session kaydet"),
        ("/load <ad>", "Session yukle"),
        ("/list", "Session listele"),
        ("/model <ad>", "Model degistir"),
        ("/guvenlik", "Guvenlik durumu"),
        ("/allow", "allow_all_users=true (DIKKAT)"),
        ("/strict", "approvals strict mode"),
        ("/approve-off", "Onaylari kapat (DIKKAT)"),
        ("/hafiza", "Hafiza istatistik"),
        ("/py <kod>", "Python calistir"),
        ("/sys <komut>", "Shell calistir"),
        ("/read <yol>", "Dosya oku"),
        ("/write <yol> <ic>", "Dosya yaz"),
        ("/ls <yol>", "Klasor listele"),
        ("/clear", "Ekran temizle"),
    ]:
        print(f"  {R.G}{k}{R.R}  {v}")
    print()


def _onayla(komut_tipi, detay=""):
    if not onay_gerekli(komut_tipi):
        return True
    print(f"  {R.Y}[ONAY] {komut_tipi}{R.R}")
    if detay:
        print(f"  {R.D}{detay}{R.R}")
    print(f"  {R.Y}Devam? (E/h):{R.R} ", end="")
    try:
        c = input().strip().lower()
        return c in ("", "e", "evet", "y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


def repl():
    if not os.environ.get("DEEPSEEK_API_KEY"):
        from deepseek_ajan.api import _dotenv_key

        _dotenv_key()
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("HATA: DEEPSEEK_API_KEY bulunamadi.")
        print("  .env dosyasina ekle")
        sys.exit(1)

    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
    messages = [
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

        # --- Komutlar ---
        if ui.startswith("/"):
            parts = ui[1:].split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd == "exit":
                print(f"{R.Y}Gorusuruz!{R.R}")
                break
            elif cmd == "help":
                help()
            elif cmd == "new":
                messages = messages[:1]
                print(f"  {R.G}Yeni session.{R.R}")
            elif cmd == "save":
                p = s_kaydet(arg, messages)
                print(f"  {R.G}Kaydedildi: {p}{R.R}")
            elif cmd == "load":
                msgs = s_yukle(arg)
                if msgs:
                    messages = msgs
                else:
                    print(f"  {R.R2}Session bulunamadi.{R.R}")
            elif cmd == "list":
                for s in s_listele():
                    print(
                        f"  {R.C}{s['id']}.{R.R} {s['name']} ({s['mesaj']} mesaj, {s['tarih']})"
                    )
            elif cmd == "model":
                if arg:
                    model = arg
                    print(f"  {R.G}Model: {model}{R.R}")
                else:
                    print(f"  Model: {R.C}{model}{R.R}")
            elif cmd == "guvenlik":
                print(f"  {guvenlik_durum()}")
            elif cmd == "allow":
                from deepseek_ajan.guvenlik import set_key

                set_key("allow_all_users", True)
                print(f"  {R.R2}allow_all_users=True - HERKES erisebilir!{R.R}")
            elif cmd == "strict":
                from deepseek_ajan.guvenlik import set_key

                set_key("approvals_mode", "strict")
                print(f"  {R.G}approvals_mode=strict{R.R}")
            elif cmd == "approve-off":
                from deepseek_ajan.guvenlik import set_key

                set_key("approvals_mode", "off")
                print(f"  {R.R2}Onaylar KAPALI - tum komutlar direkt calisir!{R.R}")
            elif cmd == "hafiza":
                s = istatistik()
                print(
                    f"  Kayit: {s['kayit']}, Basari: {s['basari']}, Hata: {s['hata']}"
                )
            elif cmd == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                banner()
            elif cmd == "py":
                if arg:
                    if _onayla("py", arg[:80]):
                        r = cmd_py(arg)
                        if r.output:
                            print(f"  {R.G}{r.output}{R.R}")
                        if r.error:
                            print(f"  {R.R2}{r.error}{R.R}")
                else:
                    print(f"  {R.Y}Kullanim: /py <kod>{R.R}")
            elif cmd == "sys":
                if arg:
                    if _onayla("sys", arg[:80]):
                        r = cmd_sys(arg)
                        if r.output:
                            print(f"  {r.output}")
                        if r.error:
                            print(f"  {R.R2}{r.error}{R.R}")
                else:
                    print(f"  {R.Y}Kullanim: /sys <komut>{R.R}")
            elif cmd == "read":
                if arg:
                    if _onayla("read", arg):
                        r = cmd_read(arg)
                        if r.output:
                            print(f"  {r.output}")
                        if r.error:
                            print(f"  {R.R2}{r.error}{R.R}")
                else:
                    print(f"  {R.Y}Kullanim: /read <yol>{R.R}")
            elif cmd == "write":
                parts2 = arg.split(maxsplit=1)
                if len(parts2) == 2:
                    if _onayla("write", parts2[0]):
                        r = cmd_write(parts2[0], parts2[1])
                        print(f"  {r.output or r.error}")
                else:
                    print(f"  {R.Y}Kullanim: /write <yol> <icerik>{R.R}")
            elif cmd == "ls":
                if _onayla("ls", arg or "."):
                    r = cmd_ls(arg or ".")
                    if r.output:
                        print(f"  {r.output}")
                    if r.error:
                        print(f"  {R.R2}{r.error}{R.R}")
            else:
                print(f"  {R.R2}Bilinmeyen: /{cmd}{R.R} (/help)")
            continue

        # --- API Cagrisi ---
        if _onayla("soru", ui[:80]):
            messages.append({"role": "user", "content": ui})

            # Once hafizada ara
            hafiza_sonuc = hafizada_ara(ui)
            if hafiza_sonuc and hafiza_sonuc[0]["guven"] > 0.8:
                cevap = hafiza_sonuc[0]["cozum"]
                print(f"  {R.D}(hafizada bulundu){R.R}")
            else:
                print(f"  {R.D}DeepSeek dusunuyor...{R.R}", end="\r")
                t0 = time.time()
                cevap = api_istek(messages, model=model)
                elapsed = time.time() - t0
                print(f"  {' '*30}", end="\r")
                print(f"  {R.D}{chr(9203)} {elapsed:.1f}s{R.R}")

            if cevap:
                print(f"\n{R.B}{R.C}DeepSeek:{R.R}")
                print(f"  {cevap.replace(chr(10), chr(10)+'  ')}")
                messages.append({"role": "assistant", "content": cevap})
            else:
                print(f"  {R.R2}Bos yanit.{R.R}")

            if len(messages) % 5 == 0:
                s_kaydet("otomatik", messages)


def main():
    try:
        repl()
    except KeyboardInterrupt:
        print(f"\n{R.Y}Gorusuruz!{R.R}")


if __name__ == "__main__":
    main()
