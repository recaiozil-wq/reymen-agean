---
skill_id: 4b39af26867f
usage_count: 1
last_used: 2026-06-16
---
# .env Yonetimi

## Temel Kurallar
1. `.env` dosyasi Python ile yazilir (PowerShell heredoc tirnak sorunu yapar)
2. Her degisken ayri satirda, yorum ayri satirda olmali
3. `***` maskeli degerler `startswith("***")` ile kontrol edilir
4. `.env.example` asla guncel kalmaz — dogrudan `.env` kullan

## Cift Yonlu Senkronizasyon
Iki sistem ortak `.env` kullaniyorsa:
1. Once kendi .env'ni oku
2. `***` olan degerleri digerinin .env'sinden doldur
3. Kendi .env'nde olup digerinde olmayan degerleri karsiya yaz

```python
def _env_anahtar(anahtar, varsayilan=""):
    deger = os.environ.get(anahtar, "").strip()
    if not deger or deger.startswith("***") or deger == "...":
        hermes_env = Path(r"C:\Users\marko\AppData\Local\hermes\.env")
        if hermes_env.exists():
            with open(hermes_env, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{anahtar}="):
                        val = line.split("=", 1)[1].strip()
                        if val and not val.startswith("***"):
                            os.environ[anahtar] = val
                            return val
        return varsayilan
    return deger
```

## Provider Fallback Env
Provider zinciri sirasi: LM Studio (yerel, anahtarsiz) → DeepSeek → OpenAI → Anthropic → Groq
Her provider icin ayri env degiskeni:
- `DEEPSEEK_API_KEY`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GROQ_API_KEY`
