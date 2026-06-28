---
skill_id: 4047b7a01b51
usage_count: 1
last_used: 2026-06-16
---
# greet("Alice") returns ["Hello, Alice!", "Hello, Alice!", "Hello, Alice!"]
```

### Class-Based Decorators

```python
class CountCalls:
    """Decorator that counts how many times a function is called."""
    def __init__(self, func: Callable):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"{self.func.__name__} has been called {self.count} times")
        return self.func(*args, **kwargs)

@CountCalls
def process():
    pass