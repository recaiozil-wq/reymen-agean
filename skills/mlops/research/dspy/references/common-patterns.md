---
skill_id: 9e4948680437
usage_count: 1
last_used: 2026-06-16
---
## Common Patterns

### Pattern 1: Structured Output

```python
from pydantic import BaseModel, Field

class PersonInfo(BaseModel):
    name: str = Field(description="Full name")
    age: int = Field(description="Age in years")
    occupation: str = Field(description="Current job")

class ExtractPerson(dspy.Signature):
    """Extract person information from text."""
    text = dspy.InputField()
    person: PersonInfo = dspy.OutputField()

extractor = dspy.TypedPredictor(ExtractPerson)
result = extractor(text="John Doe is a 35-year-old software engineer.")
print(result.person.name)  # "John Doe"
print(result.person.age)   # 35
```

### Pattern 2: Assertion-Driven Optimization

```python
import dspy
from dspy.primitives.assertions import assert_transform_module, backtrack_handler

class MathQA(dspy.Module):
    def __init__(self):
        super().__init__()
        self.solve = dspy.ChainOfThought("problem -> solution: float")

    def forward(self, problem):
        solution = self.solve(problem=problem).solution