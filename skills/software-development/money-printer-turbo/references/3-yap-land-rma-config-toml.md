---
skill_id: 41a4e1442ab5
usage_count: 1
last_used: 2026-06-16
---
## 3. Yapılandırma (config.toml)

`config.toml` mevcut değilse `config.example.toml`'dan otomatik kopyalanır.

### LLM Sağlayıcıları

| Provider | Anahtarlar |
|----------|-----------|
| deepseek | `llm_provider=deepseek`, `deepseek_api_key`, `deepseek_base_url=https://api.deepseek.com`, `deepseek_model_name=deepseek-chat` |
| openai | `openai_api_key`, `openai_model_name=gpt-4o-mini` |
| aihubmix | `aihubmix_api_key`, `aihubmix_model_name` |
| ollama | `ollama_base_url`, `ollama_model_name` |

```toml
[app]
llm_provider = "deepseek"
deepseek_api_key = "sk-..."
deepseek_base_url = "https://api.deepseek.com"
deepseek_model_name = "deepseek-chat"
```

### Video Kaynağı

```toml
pexels_api_keys = ["your-pexels-key"]   # pexels.com/api — ücretsiz
pixabay_api_keys = []                    # pixabay.com/api
video_source = "pexels"                  # pexels/pixabay/coverr/local
```

### Arkaplan Müziği

```toml
bgm_type = "random"    # random/local
bgm_file = ""          # local için dosya yolu
bgm_volume = 0.2
```