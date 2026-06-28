---
skill_id: 676e61a31f15
usage_count: 1
last_used: 2026-06-16
---
# Qt 5.x: "Qt5QWindowIcon"  |  Qt 6.x: "Qt6QWindowIcon" — verify with Accessibility Insights
    popup = Desktop(backend="uia").window(class_name_re="Qt[56]QWindowIcon")
    popup.wait("visible", timeout=5)
    popup.child_window(title=item_text).click_input()
```

**QMessageBox / QDialog** — also separate top-level windows:

```python
dlg = page.wait_window("Confirm")          # wait for dialog title
dlg.child_window(title="OK").click_input() # click button inside it
```

**QTableWidget / QTableView** — row/cell access:

```python
table = page.by_id("tblUsers").wrapper_object()
cell  = table.cell(row=0, column=1)
print(cell.window_text())
```

**Self-drawn controls** (`paintEvent`-only, `QGraphicsView`, `QOpenGLWidget`) — UIA cannot see their internals. Use the Fallback section below.