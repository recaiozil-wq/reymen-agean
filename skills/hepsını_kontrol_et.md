---
name: hepsını kontrol et
description: Tamamlanamadi: tur asimi
created: 2026-06-21
usage_count: 1
last_used: 2026-06-21
---

# hepsını kontrol et

Tamamlanamadi: tur asimi

## Adimlar

PYTHON_CALISTIR: "import os; skills_dir = 'skills'; items = [d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))]; print(f'Toplam skill sayisi: {len(items)}')"
PYTHON_CALISTIR: """
import os

skills_dir = 'skills'
items = sorted([d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))])

# İlk 50 skill'in SKILL.md içeriğini kontrol et
for i, skill in enumerate(items[:50]):
    skill_path = os.path.join(skills_dir, skill)
    md_file = os.path.join(skill_path, 'SKILL.md')
    if os.path.exists(md_file):
        with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        print(f'[{i+1}/50] {skill}: {len(content)} karakter')
    else:
        print(f'[{i+1}/50] {skill}: SKILL.md YOK')

print('---')
print(f'Toplam: {len(items)} skill')
print(f'SKILL.md olanlar kontrol ediliyor...')
"""
KOMUT_CALISTIR: "dir skills /b"
PYTHON_CALISTIR: "import os; print('Merhaba')"
PYTHON_CALISTIR: "import os; items = [d for d in os.listdir('skills') if os.path.isdir(os.path.join('skills', d))]; print(f'{len(items)} skill bulundu'); print(items[:5])"
PYTHON_CALISTIR: """
import os

skills_dir = 'skills'
items = sorted([d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))])

sonuclar = []
for i, skill in enumerate(items[:100]):
    md_file = os.path.join(skills_dir, skill, 'SKILL.md')
    if os.path.exists(md_file):
        with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        sonuclar.append(f'[{i+1}] {skill}: OK ({len(content)} karakter)')
    else:
        sonuclar.append(f'[{i+1}] {skill}: SKILL.md YOK')

print('\\n'.join(sonuclar[:20]))
print(f'...\\nToplam {len(sonuclar)} skill kontrol edildi')
print(f'SKILL.md olan: {sum(1 for s in sonuclar if "OK" in s)}')
print(f'SKILL.md olmayan: {sum(1 for s in sonuclar if "YOK" in s)}')
"""
PYTHON_CALISTIR: "import os; d='skills'; items=[x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x))]; print(f'Sayı: {len(items)}'); print(f'İlk: {items[0] if items else \"yok\"}')"
PYTHON_CALISTIR: "import os; d='skills'; items=[x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x))]; print('Sayi:', len(items)); print('Ilk:', items[0] if items else 'yok')"
PYTHON_CALISTIR: "import os; d='skills'; items=sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x))]); sonuc=[]; ok=0; yok=0; dos=0; for i,s in enumerate(items[:50]): p=os.path.join(d,s,'SKILL.md'); dos+=1; ok+=1 if os.path.exists(p) else 0; yok+=0 if os.path.exists(p) else 1; sonuc.append(f'{i+1}. {s}: {"VAR" if os.path.exists(p) else "YOK"}'); print('Ilk 50 skill kontrolu:'); print('\\n'.join(sonuc)); print(f'\\nVAR: {ok}, YOK: {yok}')"
PYTHON_CALISTIR: "import os; d='skills'; items=os.listdir(d); print('Toplam:', len(items))"
PYTHON_CALISTIR: "import os; p='skills/3d-pipeline/SKILL.md'; print(os.path.exists(p))"
PYTHON_CALISTIR: "with open('skills/3d-pipeline/SKILL.md','r',encoding='utf-8') as f: print(f.read()[:200])"
PYTHON_CALISTIR: """
import os
d='skills'
items=sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x))])
var=0
yok=0
for s in items:
    if os.path.exists(os.path.join(d,s,'SKILL.md')):
        var+=1
    else:
        yok+=1
print('Toplam skill:', len(items))
print('SKILL.md VAR:', var)
print('SKILL.md YOK:', yok)
"""
PYTHON_CALISTIR: "import os; d='skills'; items=[x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x))]; var=sum(1 for s in items if os.path.exists(os.path.join(d,s,'SKILL.md'))); print('Toplam:', len(items), 'VAR:', var, 'YOK:', len(items)-var)"
PYTHON_CALISTIR: "import os; d='skills'; items=sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x)) and os.path.exists(os.path.join(d,x,'SKILL.md'))]); print('Ilk 10 skill:'); [print(f'{i+1}. {s}') for i,s in enumerate(items[:10])]"
PYTHON_CALISTIR: "with open('skills/3d-pipeline/SKILL.md','r',encoding='utf-8') as f: print(f.read())"
PYTHON_CALISTIR: "import os; d='skills'; items=sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x)) and not os.path.exists(os.path.join(d,x,'SKILL.md'))]); print('SKILL.md OLMAYANLAR ('+str(len(items))+')'); [print(x) for x in items]"
PYTHON_CALISTIR: "import os; d='skills'; items=sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x)) and os.path.exists(os.path.join(d,x,'SKILL.md'))]); [print(f'--- {items[i]} ---') or print(open(os.path.join(d,items[i],'SKILL.md'),'r',encoding='utf-8').read()[:150]) for i in range(30)]"
PYTHON_CALISTIR: "import os; d='skills'; items=sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x)) and os.path.exists(os.path.join(d,x,'SKILL.md'))]); [print(f'--- {items[i]} ---') or print(open(os.path.join(d,items[i],'SKILL.md'),'r',encoding='utf-8').read()[:150]) for i in range(30,60)]"
PYTHON_CALISTIR: "import os; d='skills'; items=sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x)) and os.path.exists(os.path.join(d,x,'SKILL.md'))]); [print(f'--- {items[i]} ---') or print(open(os.path.join(d,items[i],'SKILL.md'),'r',encoding='utf-8').read()[:150]) for i in range(60,90)]"
PYTHON_CALISTIR: "import os; d='skills'; items=sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x)) and os.path.exists(os.path.join(d,x,'SKILL.md'))]); [print(f'--- {items[i]} ---') or print(open(os.path.join(d,items[i],'SKILL.md'),'r',encoding='utf-8').read()[:150]) for i in range(90,120)]"
PYTHON_CALISTIR: "import os; d='skills'; items=sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x)) and os.path.exists(os.path.join(d,x,'SKILL.md'))]); [print(f'--- {items[i]} ---') or print(open(os.path.join(d,items[i],'SKILL.md'),'r',encoding='utf-8').read()[:150]) for i in range(120,150)]"
PYTHON_CALISTIR: "import os; d='skills'; items=sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x)) and os.path.exists(os.path.join(d,x,'SKILL.md'))]); [print(f'--- {items[i]} ---') or print(open(os.path.join(d,items[i],'SKILL.md'),'r',encoding='utf-8').read()[:150]) for i in range(150,180)]"
PYTHON_CALISTIR: "import os; d='skills'; items=sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x)) and os.path.exists(os.path.join(d,x,'SKILL.md'))]); [print(f'--- {items[i]} ---') or print(open(os.path.join(d,items[i],'SKILL.md'),'r',encoding='utf-8').read()[:150]) for i in range(180,210)]"
PYTHON_CALISTIR: "import os; d='skills'; items=sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x)) and os.path.exists(os.path.join(d,x,'SKILL.md'))]); [print(f'--- {items[i]} ---') or print(open(os.path.join(d,items[i],'SKILL.md'),'r',encoding='utf-8').read()[:150]) for i in range(210,240)]"
PYTHON_CALISTIR: "import os; d='skills'; items=sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x)) and os.path.exists(os.path.join(d,x,'SKILL.md'))]); [print(f'--- {items[i]} ---') or print(open(os.path.join(d,items[i],'SKILL.md'),'r',encoding='utf-8').read()[:150]) for i in range(240,270)]"
PYTHON_CALISTIR: "import os; d='skills'; items=sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x)) and os.path.exists(os.path.join(d,x,'SKILL.md'))]); [print(f'--- {items[i]} ---') or print(open(os.path.join(d,items[i],'SKILL.md'),'r',encoding='utf-8').read()[:150]) for i in range(270,300)]"
PYTHON_CALISTIR: "import os; d='skills'; items=sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x)) and os.path.exists(os.path.join(d,x,'SKILL.md'))]); [print(f'--- {items[i]} ---') or print(open(os.path.join(d,items[i],'SKILL.md'),'r',encoding='utf-8').read()[:150]) for i in range(300,330)]"
PYTHON_CALISTIR: "import os; d='skills'; items=sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x)) and os.path.exists(os.path.join(d,x,'SKILL.md'))]); [print(f'--- {items[i]} ---') or print(open(os.path.join(d,items[i],'SKILL.md'),'r',encoding='utf-8').read()[:150]) for i in range(330,360)]"
