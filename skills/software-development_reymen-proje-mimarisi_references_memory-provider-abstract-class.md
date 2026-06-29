---
name: software-development_reymen-proje-mimarisi_references_memory-provider-abstract-class
description: MemoryProvider Pattern (Plugin-Based Memory Backend)
title: "Software Development Reymen Proje Mimarisi References Memory Provider Abstract Class"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | MemoryProvider Pattern (Plugin-Based Memory Backend) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# MemoryProvider Pattern (Plugin-Based Memory Backend)

## Hermes Agent MemoryProvider

```python
from abc import ABC, abstractmethod
from typing import Optional, Any

class MemoryProvider(ABC):
    """Base class for all memory providers.
    Override these to create a custom memory backend.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider adi (ornek: 'json', 'sqlite', 'chroma')."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider can activate. NO network calls."""
        ...

    @abstractmethod
    def initialize(self, session_id: str, **kwargs) -> None:
        """Called once at agent startup.
        kwargs always includes:
          hermes_home (str): Active HERMES_HOME path.
        """
        ...

    @abstractmethod
    def save(self, collection: str, document: dict, **kwargs) -> str:
        """Bir dokumani kaydet. Return: dokuman ID."""
        ...

    @abstractmethod
    def search(self, collection: str, query: str, limit: int = 5) -> list[dict]:
        """Anlamsal arama yap."""
        ...

    @abstractmethod
    def get(self, collection: str, doc_id: str) -> Optional[dict]:
        """ID ile dokuman getir."""
        ...

    @abstractmethod
    def delete(self, collection: str, doc_id: str) -> bool:
        ...

    @abstractmethod
    def list_collections(self) -> list[str]:
        ...

    @abstractmethod
    def clear(self, collection: str) -> bool:
        ...

    @abstractmethod
    def stats(self) -> dict:
        """Provider istatistikleri (kayit sayisi, boyut, vs)."""
        ...
```

## Provider Registry (Plugin Kayit)

```python
class MemoryProviderRegistry:
    _providers: dict[str, type[MemoryProvider]] = {}

    @classmethod
    def register(cls, provider_class: type[MemoryProvider]):
        cls._providers[provider_class().name] = provider_class

    @classmethod
    def get(cls, name: str) -> Optional[type[MemoryProvider]]:
        return cls._providers.get(name)

    @classmethod
    def list_available(cls) -> list[str]:
        """Sadece is_available=True olanlari listele."""
        available = []
        for name, cls_ in cls._providers.items():
            try:
                if cls_().is_available():
                    available.append(name)
            except Exception:
                continue
        return available
```

## Decorator ile Kayit

```python
@MemoryProviderRegistry.register
class JsonBackend(MemoryProvider):
    @property
    def name(self) -> str:
        return "json"

    def is_available(self) -> bool:
        return True

    def initialize(self, session_id: str, **kwargs) -> None:
        self._dosya_yolu = kwargs.get("hermes_home", ".") / "memory.json"
        ...
```

## Kullanim

```python
# Varsayilan (JSON):
memory = JsonBackend(dosya_yolu=".ReYMeN/memory.json")
memory.initialize(session_id="abc123")
memory.save("notlar", {"baslik": "test", "icerik": "deneme"})

# Registry ile secim:
provider_cls = MemoryProviderRegistry.get("sqlite")
memory = provider_cls(db_yolu=".ReYMeN/memory.db")
memory.initialize(session_id="abc123")

# Tum available provider'lari listele:
MemoryProviderRegistry.list_available()
# -> ["json", "sqlite"]
```

## ReYMeN'deki Mevcut Durum

- `memory_provider.py` (369 satir) — JsonBackend + SqliteBackend
- Ortak interface yok, plugin sistemi yok
- `vektorel_hafiza.py` — chroma ayri yerde

Yapilmasi gereken:
- MemoryProvider abstract base class ekle
- JsonBackend ve SqliteBackend'i bu interface'e uyarla
- MemoryProviderRegistry ekle (decorator tabanli)
- ChromaBackend ekle (opsiyonel, graceful degrade)

Detayli task: `MEMORY_PROVIDER_TASK.md`
