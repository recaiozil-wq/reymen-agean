---
skill_id: 2b91e26a1308
usage_count: 1
last_used: 2026-06-16
---
# Bilinen Hatalar ve Cozumleri (ReYMeN Projesi)

## `AttributeError: 'AIAgentOrchestrator' object has no attribute 'learning'`
**Sebep**: `__init__`'te self.learning = ClosedLearningLoop() satiri,
PromptAssemblyEngine icinde kullanildiktan SONRA tanimlanmis.
**Cozum**: Attribute tanimini kullanimdan onceye al.

```python
# YANLIS:
self.prompt_engine = PromptAssemblyEngine(learning_loop=self.learning)  # self.learning henuz yok!
self.learning = ClosedLearningLoop()

# DOGRU:
self.learning = ClosedLearningLoop()                                     # once tanimla
self.prompt_engine = PromptAssemblyEngine(learning_loop=self.learning)  # sonra kullan
```

## `LM Studio 400 Bad Request: "Only user and assistant roles are supported"`
**Sebep**: LM Studio, llava modelinde system rolunu kabul etmez.
**Cozum**: system mesajini user mesajina cevir:
```python
cevrilmis_mesajlar = []
if sistem_prompt:
    cevrilmis_mesajlar.append({"role": "user", "content": "[SISTEM]: " + sistem_prompt})
for m in mesajlar:
    if m["role"] == "system":
        cevrilmis_mesajlar.append({"role": "user", "content": "[SISTEM]: " + m["content"]})
    else:
        cevrilmis_mesajlar.append(m)
```

## `.env'de DEE...n gibi bozuk satirlar`
**Sebep**: write_file veya pipe ile .env yazarken tirnak/karakter kaybi.
**Cozum**: .env dosyasi Python ile yazilmali:
```python
# Dogru: Python ile yaz
with open('.env', 'w', encoding='utf-8') as f:
    f.write('DEEPSEEK_API_KEY=...\n')

# Yanlis: pipe veya write_file ile
cat > .env << 'EOF'   # pipeline sorunlu
```

## `== "***"` ile env kontrolu yanlis negatif verir
**Sebep**: LMSTUDIO_API_KEY=*** DeepSeek... gibi degerlerde `==` eslesmez.
**Cozum**: `startswith("***")` kullan:
```python
# Dogru
if not deger or deger.startswith("***"):
    return varsayilan
```
