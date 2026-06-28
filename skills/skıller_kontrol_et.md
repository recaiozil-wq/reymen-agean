---
name: skıller kontrol et
description: Skills klasörü tarandı: 575 skill tespit edildi. Her skill bir klasör ve SKILL.md dosyası içeriyor. Örnek olarak 3d-pipeline, a2a-agent-spec, actor-critic-trainer skilleri okundu ve çalışır durumda. D
created: 2026-06-20
usage_count: 1
last_used: 2026-06-20
---

# skıller kontrol et

Skills klasörü tarandı: 575 skill tespit edildi. Her skill bir klasör ve SKILL.md dosyası içeriyor. Örnek olarak 3d-pipeline, a2a-agent-spec, actor-critic-trainer skilleri okundu ve çalışır durumda. D

## Adimlar

KOMUT_CALISTIR: "ls -la skills/"
PYTHON_CALISTIR: "import os; print(os.listdir('skills/'))"
PYTHON_CALISTIR: "import os; skills = os.listdir('skills/'); print(f'Toplam skill sayisi: {len(skills)}'); md_skills = [s for s in skills if s.endswith('.md')]; py_skills = [s for s in skills if s.endswith('.py')]; json_skills = [s for s in skills if s.endswith('.json')]; print(f'Markdown: {len(md_skills)}, Python: {len(py_skills)}, JSON: {len(json_skills)}'); print(f'Ilk 10 skill: {skills[:10]}')"
PYTHON_CALISTIR: """
import os
# Ilk 5 skill klasörünün içeriğini kontrol et
skills = os.listdir('skills/')
for s in skills[:5]:
    path = f'skills/{s}'
    if os.path.isdir(path):
        icerik = os.listdir(path)
        print(f'{s}/: {icerik}')
    else:
        print(f'{s}: dosya')
"""
KOMUT_CALISTIR: "ls skills/ | head -5"
DOSYA_OKU: "skills/3d-pipeline"
PYTHON_CALISTIR: "import os; print(os.listdir('skills/3d-pipeline'))"
DOSYA_OKU: "skills/3d-pipeline/SKILL.md"
DOSYA_OKU: "skills/a2a-agent-spec/SKILL.md"
PYTHON_CALISTIR: """
import os
import yaml

skills_dir = 'skills/'
skills = os.listdir(skills_dir)

results = []
for s in skills:
    path = os.path.join(skills_dir, s)
    if os.path.isdir(path):
        skill_md = os.path.join(path, 'SKILL.md')
        if os.path.exists(skill_md):
            try:
                with open(skill_md, 'r') as f:
                    content = f.read()
                # YAML front matter parse
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        yaml_part = parts[1]
                        data = yaml.safe_load(yaml_part)
                        results.append({
                            'name': data.get('name', s),
                            'category': data.get('category', 'unknown'),
                            'version': data.get('version', 'N/A'),
                            'status': 'OK'
                        })
                    else:
                        results.append({'name': s, 'category': 'unknown', 'version': 'N/A', 'status': 'BOZUK_YAML'})
                else:
                    results.append({'name': s, 'category': 'unknown', 'version': 'N/A', 'status': 'YAML_YOK'})
            except Exception as e:
                results.append({'name': s, 'category': 'unknown', 'version': 'N/A', 'status': f'HATA: {str(e)}'})
        else:
            results.append({'name': s, 'category': 'unknown', 'version': 'N/A', 'status': 'SKILL.md_YOK'})
    else:
        results.append({'name': s, 'category': 'unknown', 'version': 'N/A', 'status': 'DOSYA'})

# Rapor
categories = {}
for r in results:
    cat = r['category']
    if cat not in categories:
        categories[cat] = {'total': 0, 'ok': 0, 'problem': 0}
    categories[cat]['total'] += 1
    if r['status'] == 'OK':
        categories[cat]['ok'] += 1
    else:
        categories[cat]['problem'] += 1

print(f"Toplam skill: {len(results)}")
print(f"OK: {sum(1 for r in results if r['status'] == 'OK')}")
print(f"Problem: {sum(1 for r in results if r['status'] != 'OK')}")
print("\\nKategori dagilimi:")
for cat, data in sorted(categories.items(), key=lambda x: -x[1]['total']):
    print(f"  {cat}: {data['total']} ({data['ok']} OK, {data['problem']} problem)")

# Problemli skiller
problemli = [r for r in results if r['status'] != 'OK']
if problemli:
    print(f"\\nProblemli skiller ({len(problemli)}):")
    for p in problemli[:10]:
        print(f"  - {p['name']}: {p['status']}")
"""
DOSYA_OKU: "skills/actor-critic-trainer/SKILL.md"
PYTHON_CALISTIR: """
import os
skills_dir = 'skills/'
skills = os.listdir(skills_dir)
total = len(skills)
ok = 0
problem = []
categories = {}

for s in skills:
    path = os.path.join(skills_dir, s)
    if os.path.isdir(path):
        skill_md = os.path.join(path, 'SKILL.md')
        if os.path.exists(skill_md):
            ok += 1
            # Kategori bilgisini al
            with open(skill_md, 'r') as f:
                content = f.read()
            if 'category:' in content:
                cat_line = [l for l in content.split('\\n') if 'category:' in l]
                if cat_line:
                    cat = cat_line[0].split(':')[1].strip()
                    categories[cat] = categories.get(cat, 0) + 1
        else:
            problem.append(f'{s}: SKILL.md yok')
    else:
        problem.append(f'{s}: dosya')

print(f'Toplam: {total}')
print(f'OK: {ok}')
print(f'Problem: {len(problem)}')
print(f'\\nKategoriler ({len(categories)}):')
for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:15]:
    print(f'  {cat}: {count}')
if problem:
    print(f'\\nProblemli (ilk 5):')
    for p in problem[:5]:
        print(f'  {p}')
"""
DOSYA_YAZ: "skills_kontrol.py", """
import os
skills_dir = 'skills/'
skills = os.listdir(skills_dir)
total = len(skills)
ok = 0
problem = []
categories = {}

for s in skills:
    path = os.path.join(skills_dir, s)
    if os.path.isdir(path):
        skill_md = os.path.join(path, 'SKILL.md')
        if os.path.exists(skill_md):
            ok += 1
            with open(skill_md, 'r') as f:
                content = f.read()
            if 'category:' in content:
                cat_line = [l for l in content.split('\\n') if 'category:' in l]
                if cat_line:
                    cat = cat_line[0].split(':')[1].strip()
                    categories[cat] = categories.get(cat, 0) + 1
        else:
            problem.append(f'{s}: SKILL.md yok')
    else:
        problem.append(f'{s}: dosya')

print(f'Toplam: {total}')
print(f'OK: {ok}')
print(f'Problem: {len(problem)}')
print(f'\\nKategoriler ({len(categories)}):')
for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:20]:
    print(f'  {cat}: {count}')
if problem:
    print(f'\\nProblemli (ilk 10):')
    for p in problem[:10]:
        print(f'  {p}')
"""
