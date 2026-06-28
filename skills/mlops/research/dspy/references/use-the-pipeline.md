---
skill_id: 895998341567
usage_count: 1
last_used: 2026-06-16
---
# Use the pipeline
qa_system = MultiHopQA()
result = qa_system(question="Who wrote the book that inspired the movie Blade Runner?")
```

#### RAG System with Optimization

```python
import dspy
from dspy.retrieve.chromadb_rm import ChromadbRM