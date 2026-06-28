---
name: software-development_skill-creation-standards_references_sifir-siskinlik
description: Sıfır Şişkinlik Politikası
title: "Software Development Skill Creation Standards References Sifir Siskinlik"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Sıfır Şişkinlik Politikası |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Sıfır Şişkinlik Politikası

## Temel Kural

Bir SKILL.md dosyasına **devasa kod blokları, log çıktıları, ham metinler veya uzun listelemeler** doğrudan gömülmez.

## Ne Kadar "Çok Fazla"?

| Öğe | Limit | Aşılırsa |
|-----|-------|----------|
| Kod bloğu | ≤ 20 satır | references/ altına taşı |
| Komut listesi | ≤ 10 komut | references/ altına taşı |
| Tablo | ≤ 10 satır | references/ altına taşı |
| Log çıktısı | 0 satır | Asla SKILL.md'ye koyma |
| Ham metin / dump | 0 satır | Asla SKILL.md'ye koyma |
| JSON/YAML örneği | ≤ 30 satır | references/ altına taşı |

## Doğru Kullanım

### Yanlış (şişkin)
```markdown
## Kurulum

sudo apt update
sudo apt install -y python3 python3-pip git
git clone https://github.com/example/repo.git
cd repo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 setup.py install
# ... 40 satır daha ...
```

### Doğru (Router)
```markdown
## Kurulum

Kurulum adımları → [references/kurulum.md](references/kurulum.md)
```

## Kod Blokları İçin Kural

> **Teknik olarak gerekli** küçük kod parçaları (5-10 satır) SKILL.md'de kalabilir.
> **Uzun örnekler, tüm API parametreleri, kompleks script'ler** references/ altına taşınmalıdır.

**SKILL.md'de kalabilir:**
```python
# Kısa, açıklayıcı kod parçası
result = some_function(param1, param2)
print(f"Sonuç: {result}")
```

**references/ altına gitmeli:**
```python
# Uzun, kompleks işlem. örn: tüm API sarmalayıcı
class ComplexAPI:
    def __init__(self):
        ...
    # 100+ satır implementasyon
```

## Reference Dosyasından Kod Çağırma

Router dosyası, reference içindeki kodun sadece ne yaptığını açıklar:

```markdown
Kurulum script'i → [scripts/install.sh](scripts/install.sh)
API wrapper → [references/api-wrapper.md](references/api-wrapper.md)
```

## skill-shrink ile Otomatik Kontrol

Skill oluşturulduktan sonra `skill-shrink` şunları kontrol eder:

1. **Dosya boyutu > 10 KB** → uyarı
2. **Satır sayısı > 300** → uyarı
3. **Ham log/metin içeriği** → tespit
4. **Frontmatter kontrolü** → eksik alanlar

Uyarı durumunda skill otomatik olarak references/ altına bölünür.

## Log Çıktıları

Loglar ASLA SKILL.md'ye yazılmaz. Bunun yerine:

```markdown
Çıktı örneği → [references/ornek-cikti.log](references/ornek-cikti.log)
```

Veya doğrudan terminal'de gösterilir (kullanıcı çalıştırdığında görecek).
