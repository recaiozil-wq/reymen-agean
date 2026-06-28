import os
import httpx
from typing import Protocol

class ModelAdapter(Protocol):
    def complete(self, prompt: str) -> str: ...

class OllamaAdapter:
    def __init__(self, model: str = "llama3"):
        self.url = "http://localhost:11434/api/generate"
        self.model = model
    def complete(self, prompt: str) -> str:
        resp = httpx.post(self.url, json={"model": self.model, "prompt": prompt, "stream": False}, timeout=120)
        return resp.json()["response"]

class OpenAICompatAdapter:
    """LM Studio / GLM / DeepSeek / OpenAI — aynı endpoint"""
    def __init__(self, base_url: str, model: str, api_key: str = "none"):
        self.url = f"{base_url.rstrip('/')}/v1/chat/completions"
        self.model = model
        self.headers = {"Authorization": f"Bearer {api_key}"}
    def complete(self, prompt: str) -> str:
        resp = httpx.post(self.url, headers=self.headers, json={
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }, timeout=120)
        return resp.json()["choices"][0]["message"]["content"]

class AnthropicAdapter:
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        self.model = model
        self.headers = {
            "x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    def complete(self, prompt: str) -> str:
        resp = httpx.post("https://api.anthropic.com/v1/messages",
            headers=self.headers, json={
                "model": self.model, "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}]
            }, timeout=120)
        return resp.json()["content"][0]["text"]

def get_active_adapter() -> ModelAdapter:
    spec = os.environ.get("REYMEN_MODEL", "auto")
    if spec == "auto":
        return _auto_detect()
    provider, *rest = spec.split(":")
    model = rest[0] if rest else None
    match provider:
        case "ollama":    return OllamaAdapter(model or "llama3")
        case "lmstudio":  return OpenAICompatAdapter("http://localhost:1234", model or "local")
        case "openai":    return OpenAICompatAdapter("https://api.openai.com/v1", model or "gpt-4o", os.environ.get("OPENAI_API_KEY",""))
        case "deepseek":  return OpenAICompatAdapter("https://api.deepseek.com", model or "deepseek-chat", os.environ.get("DEEPSEEK_API_KEY",""))
        case "anthropic": return AnthropicAdapter(model or "claude-3-5-sonnet-20241022")
        case "glm":       return OpenAICompatAdapter("http://localhost:8000", model or "glm-4")
        case _: raise ValueError(f"Bilinmeyen provider: {provider}")

def _auto_detect() -> ModelAdapter:
    candidates = [
        ("Ollama",    lambda: OllamaAdapter()),
        ("LM Studio", lambda: OpenAICompatAdapter("http://localhost:1234", "local")),
        ("GLM local", lambda: OpenAICompatAdapter("http://localhost:8000", "glm-4")),
    ]
    for name, factory in candidates:
        try:
            a = factory()
            a.complete("ping")
            print(f"[ADAPTER] ✅ {name} aktif")
            return a
        except Exception:
            continue
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("[ADAPTER] ✅ Anthropic (cloud)")
        return AnthropicAdapter()
    if os.environ.get("DEEPSEEK_API_KEY"):
        print("[ADAPTER] ✅ DeepSeek (cloud)")
        return OpenAICompatAdapter("https://api.deepseek.com", "deepseek-chat", os.environ["DEEPSEEK_API_KEY"])
    raise RuntimeError("Hiçbir model bulunamadı. REYMEN_MODEL env var set et.")
