---
skill_id: b15cfea29e09
usage_count: 1
last_used: 2026-06-16
---
## ONNX deployment

### Export model

```bash
python scripts/export_onnx_model.py \
    --checkpoint sam_vit_h_4b8939.pth \
    --model-type vit_h \
    --output sam_onnx.onnx \
    --return-single-mask
```

### Use ONNX model

```python
import onnxruntime