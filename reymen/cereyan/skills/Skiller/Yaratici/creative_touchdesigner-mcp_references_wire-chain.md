
> **Kategori:** Yaratici

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Creative_Touchdesigner Mcp_References_Wire Chain |
| **Nerede?** | Yaratici/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Wire chain
for i in range(len(nodes)-1):
    op(nodes[i]).outputConnectors[0].connect(op(nodes[i+1]).inputConnectors[0])
result = {'created': nodes}
```

### Step 2: Set Parameters

Prefer the native tool (validates params, won't crash):

```
td_set_operator_pars(path="/project1/bg", parameters={"roughness": 0.6, "monochrome": true})
```

For expressions or modes, use `td_execute_python`:

```python
op('/project1/time_driver').par.colorr.expr = "absTime.seconds % 1000.0"
```

### Step 3: Wire

Use `td_execute_python` — no native wire tool exists:

```python
op('/project1/bg').outputConnectors[0].connect(op('/project1/fx').inputConnectors[0])
```

### Step 4: Verify

```
td_get_errors(path="/project1", recursive=true)
td_get_perf()
td_get_operator_info(path="/project1/out", detail="full")
```

### Step 5: Display / Capture

```
td_get_screenshot(path="/project1/out")
```

Or open a window via script:

```python
win = op('/project1').create(windowCOMP, 'display')
win.par.winop = op('/project1/out').path
win.par.winw = 1280; win.par.winh = 720
win.par.winopen.pulse()
```