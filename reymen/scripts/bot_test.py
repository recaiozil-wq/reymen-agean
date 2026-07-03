import os, http.client, json, time, sys

def read_token_hex(profile):
    env_path = os.path.expanduser(f"~/.hermes/profiles/{profile}/.env")
    with open(env_path, 'rb') as f:
        raw = f.read()
    lines = raw.split(b'\n')
    target = b'TELEGRAM_BOT_TOKEN='
    for line in lines:
        if target in line:
            eq_pos = line.find(b'=')
            token_bytes = line[eq_pos+1:].strip()
            return token_bytes.decode('utf-8', errors='replace')
    return None

test_type = sys.argv[1] if len(sys.argv) > 1 else "all"

def test_bot(name, profile):
    token = read_token_hex(profile)
    if not token:
        print(f"[{name}] Token bulunamadi")
        return None
    
    # getMe
    conn = http.client.HTTPSConnection("api.telegram.org", timeout=10)
    conn.request("GET", f"/bot{token}/getMe")
    data = json.loads(conn.getresponse().read().decode())
    conn.close()
    
    if data.get("ok"):
        bot = data["result"]
        print(f"[{name}] @{bot['username']} — CANLI (id={bot['id']})")
        return token
    else:
        print(f"[{name}] ❌ {data.get('description','?')}")
        return None

def send_and_check(profile, chat_id, question, wait=12):
    token = read_token_hex(profile)
    
    # Soruyu gonder
    payload = json.dumps({"chat_id": chat_id, "text": question})
    conn = http.client.HTTPSConnection("api.telegram.org", timeout=10)
    conn.request("POST", f"/bot{token}/sendMessage", body=payload, headers={"Content-Type": "application/json"})
    r = json.loads(conn.getresponse().read().decode())
    conn.close()
    print(f"  Soru gonderildi: {'OK' if r.get('ok') else 'HATA'}")
    
    # Bekle
    print(f"  {wait}s bekleniyor...")
    time.sleep(wait)
    
    # Cevabi oku
    conn = http.client.HTTPSConnection("api.telegram.org", timeout=10)
    conn.request("GET", f"/bot{token}/getUpdates?limit=10")
    data = json.loads(conn.getresponse().read().decode())
    conn.close()
    
    bot_msgs = []
    last_user_msg_id = None
    if data.get("ok") and data.get("result"):
        for u in data["result"]:
            msg = u.get("message", {})
            if msg.get("from", {}).get("is_bot"):
                bot_msgs.append(msg)
            else:
                last_user_msg_id = msg.get("message_id")
    
    # Sadece son sorudan sonraki bot cevaplarini goster
    if last_user_msg_id:
        recent = [m for m in bot_msgs if m.get("reply_to",{}).get("message_id") == last_user_msg_id or m.get("message_id",0) > last_user_msg_id]
        if recent:
            for m in recent:
                print(f"  🤖 CEVAP: {m['text'][:400]}")
            return recent[-1]['text']
        else:
            print(f"  ❌ BOT CEVAP VERMEDI (son soru icin)")
            return None
    else:
        print(f"  ❌ Kullanici mesaji bulunamadi")
        return None

# Test all bots
print("="*50)
print("BOT TEST - getMe")
print("="*50)

for name, prof in [("Pasa_38","default"), ("ReYMeNbot","reymen"), ("Kiral38","kiral38")]:
    test_bot(name, prof)

print("\n" + "="*50)
print("KIRAL38 - CEVAP TESTI")
print("="*50)

k_token = test_bot("Kiral38", "kiral38")
if k_token:
    # Chat_id al
    conn = http.client.HTTPSConnection("api.telegram.org", timeout=10)
    conn.request("GET", f"/bot{k_token}/getUpdates?limit=1")
    data = json.loads(conn.getresponse().read().decode())
    conn.close()
    
    if data.get("ok") and data.get("result"):
        chat_id = data["result"][-1]["message"]["chat"]["id"]
        print(f"Chat ID: {chat_id}")
        
        # 1. test: "sen kimsin"
        cevap1 = send_and_check("kiral38", chat_id, "sen kimsin hangi kurallarla calisiyorsun", 12)
        
        if cevap1:
            print("\n--- ANALIZ ---")
            # SOUL.md mi yoksa default mu?
            has_reymen = "ReYMeN" in cevap1
            has_hermes = "Hermes" in cevap1 or "Nous Research" in cevap1
            has_cave = "Cave" in cevap1
            has_emoji_tablo = "✅" in cevap1 or "|" in cevap1
            
            print(f"  ReYMeN referansi: {'EVET' if has_reymen else 'HAYIR'}")
            print(f"  Hermes referansi: {'EVET' if has_hermes else 'HAYIR'}")
            print(f"  Cave Modu: {'EVET' if has_cave else 'HAYIR'}")
            print(f"  Emoji+Tablo: {'EVET' if has_emoji_tablo else 'HAYIR'}")
        else:
            print("\nKiral38 gateway calismiyor. Alternatif test yapilamadi.")
