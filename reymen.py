import subprocess, os, shutil, sys, json, re
from openai import OpenAI

with open("beyin.json", encoding="utf-8") as f:
    BEYIN = json.load(f)
API_KEY = os.environ.get(BEYIN["api_key_env"])
if not API_KEY:
    print("Kurulum tamam. Baslatmak icin API anahtarini tanimla, terminali yeniden ac, 'python reymen.py' yaz.")
    sys.exit(0)
client = OpenAI(api_key=API_KEY, base_url=BEYIN["base_url"])
MODEL = BEYIN["model"]

DOSYA = "target.py"
KLASOR_GECMIS, KLASOR_FINAL = "denemeler", "aristokrat"
MAX_DENEME, TIMEOUT = 8, 30
IZINLI_PAKET = {"requests","numpy","pandas","beautifulsoup4","bs4","lxml",
                "matplotlib","openpyxl","pillow","httpx","python-dateutil","pytz","scipy"}
YASAK = ["rm ","rmdir","del ","format","mkfs",">","sudo","chmod","chown",
         "curl","wget","powershell","reg ","shutdown","mv /","dd "]

os.makedirs(KLASOR_GECMIS, exist_ok=True)
os.makedirs(KLASOR_FINAL, exist_ok=True)

def sor(p):
    r = client.chat.completions.create(model=MODEL, max_tokens=3000,
        messages=[{"role":"user","content":p}])
    return r.choices[0].message.content.strip()

def temizle(m):
    if "```" in m:
        p = m.split("```")[1]
        for d in ("python","bash","sh","json"):
            if p.startswith(d): p = p[len(d):]
        return p.strip()
    return m.strip()

def calistir(d):
    try:
        s = subprocess.run([sys.executable, d], capture_output=True, text=True, timeout=TIMEOUT)
        return s.returncode, s.stdout, s.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Zaman asimi (sonsuz dongu olabilir)."

def guvenli_paket_kur(komut):
    m = re.search(r"pip\s+install\s+([\w\-]+)", komut.lower())
    if not m: return False
    paket = m.group(1)
    if paket not in IZINLI_PAKET: return False
    s = subprocess.run([sys.executable,"-m","pip","install",paket],
                       capture_output=True, text=True)
    return s.returncode == 0

def tehlikeli_mi(komut):
    k = komut.lower()
    return any(y in k for y in YASAK)

def karar_ver(kod, hata):
    c = sor(
        "Sen ReYMeN'sin, otonom hata-cozme zekasi. Bu Python kodu hata verdi. "
        "Kok nedeni anla, TEK eylem sec, SADECE su JSON ile cevap ver:\n"
        '{"eylem":"kod"|"komut"|"dur","icerik":"...","aciklama":"kisa"}\n'
        '- "kod": sorun koddadir -> icerik=duzeltilmis tam kod.\n'
        '- "komut": kutuphane eksik -> icerik=tek "pip install X" komutu. '
        "Dosya silen/indiren/sistem degistiren komut ASLA uretme.\n"
        '- "dur": otonom cozulemez (yanlis anahtar, izin, kaynak) -> icerik bos.\n\n'
        f"KOD:\n{kod}\n\nHATA:\n{hata}")
    try:
        return json.loads(temizle(c) if "```" in c else c)
    except Exception:
        return {"eylem":"kod","icerik":temizle(c),"aciklama":""}

def dongu():
    print("ReYMeN calisiyor...\n")
    for d in range(1, MAX_DENEME+1):
        print("Cozum araniyor...")
        shutil.copy(DOSYA, f"{KLASOR_GECMIS}/v{d}.py")
        durum, cikti, hata = calistir(DOSYA)

        if durum == 0:
            d2, c2, _ = calistir(DOSYA)
            if d2 == 0 and c2 == cikti:
                print("\nCOZUM BULUNDU.\n")
                print(cikti)
                shutil.copy(DOSYA, f"{KLASOR_FINAL}/cozum.py")
                return
            hata = "Kararsiz cikti."

        karar = karar_ver(open(DOSYA, encoding="utf-8").read(), hata)
        eylem = karar.get("eylem")

        if eylem == "dur":
            print("\nBu sorun otomatik cozulemedi, manuel kontrol gerekiyor.")
            return

        if eylem == "komut":
            komut = karar.get("icerik","")
            if tehlikeli_mi(komut):
                print("Riskli islem engellendi, alternatif araniyor...")
            elif guvenli_paket_kur(komut):
                continue
        yeni = karar.get("icerik","")
        if yeni and eylem != "komut":
            with open(DOSYA,"w",encoding="utf-8") as f:
                f.write(yeni)

    print("\nCozum bulunamadi, manuel kontrol gerekiyor.")

if __name__ == "__main__":
    dongu()
