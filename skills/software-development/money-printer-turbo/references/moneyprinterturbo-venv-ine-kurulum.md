---
skill_id: 735ec85de6a2
usage_count: 1
last_used: 2026-06-16
---
# MoneyPrinterTurbo venv'ine kurulum
cd /c/Users/marko/hermes-ai
C:/Users/marko/hermes-ai/venv/Scripts/python.exe -m pip install manim
```

Test:
```python
from manim import *

class TestScene(Scene):
    def construct(self):
        circle = Circle()
        circle.set_fill(BLUE, opacity=0.5)
        self.play(Create(circle))
        self.wait(1)
```

Render:
```bash
python -m manim test_scene.py TestScene -ql  # düşük kalite
python -m manim test_scene.py TestScene -qh  # yüksek kalite
```

### API Key'leri .env'ye Kaydetme Pattern'i

```bash