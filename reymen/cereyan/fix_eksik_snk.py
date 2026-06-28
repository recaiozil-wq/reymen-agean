#!/usr/bin/env python3
"""Kategorisiz kalan dosyalara 5N1K tablo ekle + frontmatter testi"""
import os, glob, re

skills_dir = r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi\reymen\cereyan\skills"

# Klasor -> 5N1K haritasi
KLASOR_SNK = {
    'ai-ml/ecc':      {'kim':'AI kalite muhendisi','ne':'Edge Case Classification, hata tespiti, sinir durumlari','nerede':'ai-ml/ecc/','nezaman':'AI model testi gerektiginde','neden':'Kenar durumlari yakalamak icin','nasil':'Test senaryolarini uygulayarak'},
    'ai-ml/prompt':   {'kim':'Prompt muhendisi','ne':'Prompt tasarimi, structured output, function calling','nerede':'ai-ml/prompt/','nezaman':'LLM promptu yazarken','neden':'Dogru cikti almak icin','nasil':'Prompt patternlerini kullanarak'},
    'ai-ml/nlp':      {'kim':'NLP muhendisi','ne':'Dogal dil isleme, tokenizasyon, metin analizi','nerede':'ai-ml/nlp/','nezaman':'Metin isleme gerektiginde','neden':'Metin tabanli AI gorevleri icin','nasil':'NLP adimlarini takip ederek'},
    'ai-ml/architecture': {'kim':'AI mimari muhendisi','ne':'Transformer, MoE, attention mekanizmasi','nerede':'ai-ml/architecture/','nezaman':'Model mimarisi secimi gerektiginde','neden':'Dogru mimariyi secmek icin','nasil':'Mimari dokumanlarini inceleyerek'},
    'windows/automation': {'kim':'Windows ajani','ne':'Windows otomasyon, klavye/fare, pencere yonetimi, ADB','nerede':'windows/automation/','nezaman':'Windows sistem yonetimi gerektiginde','neden':'Windows islemlerini otomatize etmek icin','nasil':'Otomasyon adimlarini takip ederek'},
    'productivity':   {'kim':'Tum kullanicilar','ne':'Verimlilik araclari, workflow, not alma, PDF isleme','nerede':'productivity/','nezaman':'Gunluk is akisini iyilestirirken','neden':'Daha verimli calismak icin','nasil':'Skill adimlarini uygulayarak'},
    'devops':         {'kim':'DevOps muhendisi','ne':'CI/CD, deployment, backup, Docker, Kubernetes','nerede':'devops/','nezaman':'Sistem yonetimi veya deploy gerektiginde','neden':'Sistemleri otomatize etmek icin','nasil':'DevOps adimlarini takip ederek'},
    'mlops':          {'kim':'ML/Veri bilimci','ne':'ML pipeline, model deploy, veri yonetimi, inference','nerede':'mlops/','nezaman':'ML modeli yonetimi gerektiginde','neden':'ML surecini standartlastirmak icin','nasil':'MLOps adimlarini takip ederek'},
    'mlops/skills':   {'kim':'ML/Veri bilimci','ne':'ML skillleri, model training, feature engineering','nerede':'mlops/skills/','nezaman':'ML modeli egitiminde','neden':'Model kalitesini artirmak icin','nasil':'ML skill adimlarini uygulayarak'},
    'creative':       {'kim':'Icerik ureticisi','ne':'Yaratici icerik, ASCII sanat, video, muzik, tasarim','nerede':'creative/','nezaman':'Gorsel icerik uretimi gerektiginde','neden':'Yaratici isleri standartlastirmak icin','nasil':'Yaratici skill adimlarini takip ederek'},
    'user/preferences':{'kim':'Kullanici','ne':'Kullanici tercihleri, kisilestirme, profil ayarlari','nerede':'user/preferences/','nezaman':'Kullanici ayarlari duzenlenirken','neden':'Kullanici deneyimini iyilestirmek icin','nasil':'Tercih adimlarini takip ederek'},
    'security':       {'kim':'Guvenlik arastirmacisi','ne':'Guvenlik denetimi, audit, zafiyet taramasi','nerede':'security/','nezaman':'Guvenlik testi gerektiginde','neden':'Sistem guvenligini saglamak icin','nasil':'Guvenlik adimlarini uygulayarak'},
    'research':       {'kim':'Arastirmaci','ne':'Arastirma, literatur taramasi, arxiv, paper inceleme','nerede':'research/','nezaman':'Arastirma gerektiginde','neden':'Bilgiye ulasmak icin','nasil':'Arastirma adimlarini takip ederek'},
    'media':          {'kim':'Medya uzmani','ne':'Medya isleme, GIF, muzik, YouTube icerik','nerede':'media/','nezaman':'Medya dosyasi isleme gerektiginde','neden':'Medya icerigini yonetmek icin','nasil':'Medya adimlarini takip ederek'},
    'github':         {'kim':'Gelistirici','ne':'GitHub yonetimi, PR, issue, repo yonetimi','nerede':'github/','nezaman':'GitHub islemleri gerektiginde','neden':'GitHub verimli kullanmak icin','nasil':'GitHub adimlarini takip ederek'},
    'apple':          {'kim':'Apple kullanicisi','ne':'Apple ekosistemi, macOS, iOS yonetimi','nerede':'apple/','nezaman':'Apple cihaz yonetimi gerektiginde','neden':'Apple cihazlarini yonetmek icin','nasil':'Apple adimlarini takip ederek'},
    'gaming':         {'kim':'Oyun gelistirici','ne':'Oyun gelistirme, oyun testi','nerede':'gaming/','nezaman':'Oyun gelistirme gerektiginde','neden':'Oyun projesini yonetmek icin','nasil':'Gaming adimlarini takip ederek'},
    'kali':           {'kim':'Kali ajani','ne':'Pentest adimlari, nmap, metasploit, zafiyet analizi','nerede':'kali/','nezaman':'Guvenlik testi gerektiginde','neden':'Sistem aciklarini tespit etmek icin','nasil':'Kali adimlarini takip ederek'},
    'voice':          {'kim':'Ses/video muhendisi','ne':'Ses isleme, TTS, STT, VAD, Whisper','nerede':'voice/','nezaman':'Ses isleme gerektiginde','neden':'Ses tabanli isleri yapmak icin','nasil':'Voice adimlarini takip ederek'},
    'data-science':   {'kim':'Veri bilimci','ne':'Veri analizi, Jupyter, huggingface, veri gorsellestirme','nerede':'data-science/','nezaman':'Veri analizi gerektiginde','neden':'Veriden anlam cikarmak icin','nasil':'Veri bilimi adimlarini takip ederek'},
    'android':        {'kim':'Android gelistiricisi','ne':'Android gelistirme, APK, SDK','nerede':'android/','nezaman':'Android uygulamasi gelistirirken','neden':'Android projesini yonetmek icin','nasil':'Android adimlarini takip ederek'},
    'tor':            {'kim':'Guvenlik arastirmacisi','ne':'Tor browser, anonim web erisimi','nerede':'tor/','nezaman':'Anonim erisim gerektiginde','neden':'Guvenli ve anonim gezinmek icin','nasil':'Tor adimlarini takip ederek'},
    'smart-home':     {'kim':'Akilli ev kullanicisi','ne':'Akilli ev cihazlari, OpenHue, ev otomasyonu','nerede':'smart-home/','nezaman':'Akilli ev yonetimi gerektiginde','neden':'Ev cihazlarini yonetmek icin','nasil':'Smart home adimlarini takip ederek'},
    'social-media':   {'kim':'Sosyal medya yoneticisi','ne':'Sosyal medya yonetimi, icerik paylasimi','nerede':'social-media/','nezaman':'Sosyal medya yonetimi gerektiginde','neden':'Sosyal medyayi yonetmek icin','nasil':'Sosyal medya adimlarini takip ederek'},
    'egitim':         {'kim':'Egitmen','ne':'Egitim icerikleri, ders notlari, ogrenme materyalleri','nerede':'egitim/','nezaman':'Egitim icerigi hazirlarken','neden':'Egitim materyallerini duzenlemek icin','nasil':'Egitim adimlarini takip ederek'},
    'test/dil-test':  {'kim':'Test muhendisi','ne':'Dil testi, benchmark, metrik olcumu','nerede':'test/dil-test/','nezaman':'Dil modeli testi gerektiginde','neden':'Model performansini olcmek icin','nasil':'Test senaryolarini uygulayarak'},
    'test/benchmark': {'kim':'Test muhendisi','ne':'Benchmark, karsilastirma, basari olcumu','nerede':'test/benchmark/','nezaman':'Model karsilastirmasi gerektiginde','neden':'Modelleri objektif karsilastirmak icin','nasil':'Benchmark adimlarini takip ederek'},
}

def test_frontmatter(icerik):
    """Frontmatter gecerlilik testi"""
    m = re.match(r'^---\s*\n.*?\n---', icerik, re.DOTALL)
    if not m:
        return False, "frontmatter yok"
    fm = m.group(0)
    # name alani var mi?
    if 'name:' not in fm:
        return False, "name alani yok"
    return True, "ok"

def snk_ekle(dosya, bilgi):
    with open(dosya, 'r', encoding='utf-8', errors='ignore') as f:
        icerik = f.read()
    
    m = re.match(r'^(---\s*\n.*?\n---)', icerik, re.DOTALL)
    if not m:
        return False, "frontmatter yok"
    
    fm_block = m.group(1)
    govde = icerik[len(fm_block):]
    
    if '| 5N1K ' in govde[:500]:
        return False, "zaten var"
    
    # Eski 5N1K alanlarini temizle
    snk_keys = ('kim:', 'ne:', 'nerede:', 'ne_zaman:', 'neden:', 'nasil:')
    yeni_fm = []
    for line in fm_block.split('\n'):
        if any(line.strip().lower().startswith(k) for k in snk_keys):
            continue
        yeni_fm.append(line)
    yeni_fm_str = '\n'.join(yeni_fm)
    
    tablo = f'''\
| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | {bilgi["kim"]} |
| **Ne** | {bilgi["ne"]} |
| **Nerede** | {bilgi["nerede"]} |
| **Ne Zaman** | {bilgi["nezaman"]} |
| **Neden** | {bilgi["neden"]} |
| **Nasıl** | {bilgi["nasil"]} |'''
    
    yeni_icerik = yeni_fm_str + '\n\n' + tablo + '\n\n' + icerik[len(fm_block):].lstrip()
    
    # Test
    ok, msg = test_frontmatter(yeni_icerik)
    if not ok:
        return False, f"test basarisiz: {msg}"
    
    with open(dosya, 'w', encoding='utf-8') as f:
        f.write(yeni_icerik)
    return True, "ok"

# En buyuk 3 klasoru isle (ai-ml/ecc, ai-ml/prompt, windows/automation)
HEDEF = ['ai-ml/ecc', 'ai-ml/prompt', 'windows/automation']

toplam_guncel = 0
toplam_atla = 0
toplam_hata = 0

for hedef in HEDEF:
    kat_yol = os.path.join(skills_dir, hedef.replace('/', os.sep))
    if not os.path.isdir(kat_yol):
        print(f'[YOK] {hedef}')
        continue
    
    bilgi = KLASOR_SNK.get(hedef)
    if not bilgi:
        print(f'[SNK YOK] {hedef}')
        continue
    
    dosyalar = sorted(glob.glob(os.path.join(kat_yol, '*.md')))
    kat_guncel = 0
    kat_atla = 0
    kat_hata = 0
    
    for dosya in dosyalar:
        ad = os.path.basename(dosya)
        if ad in ('SKILL.md','DESCRIPTION.md','SKILL_INDEX.md'):
            continue
        ok, msg = snk_ekle(dosya, bilgi)
        if ok:
            kat_guncel += 1
        elif 'zaten' in msg:
            kat_atla += 1
        else:
            kat_hata += 1
            print(f'  [HATA] {hedef}/{ad}: {msg}')
    
    print(f'[{hedef}] {kat_guncel} eklendi, {kat_atla} vardi, {kat_hata} hata')
    toplam_guncel += kat_guncel
    toplam_atla += kat_atla
    toplam_hata += kat_hata

print(f'\n=== RAPOR (3 klasor) ===')
print(f'Eklenen: {toplam_guncel}')
print(f'Atlanan: {toplam_atla}')
print(f'Hata:    {toplam_hata}')
