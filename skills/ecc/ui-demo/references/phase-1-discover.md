---
skill_id: 86f0718b299b
usage_count: 1
last_used: 2026-06-16
---
## Phase 1: Discover

Before writing any script, explore the target pages to understand what is actually there.

### Why

You cannot script what you have not seen. Fields may be `<input>` not `<textarea>`, dropdowns may be custom components not `<select>`, and comment boxes may support `@mentions` or `#tags`. Assumptions break recordings silently.

### How

Navigate to each page in the flow and dump its interactive elements:

```javascript
// Run this for each page in the flow BEFORE writing the demo script
const fields = await page.evaluate(() => {
  const els = [];
  document.querySelectorAll('input, select, textarea, button, [contenteditable]').forEach(el => {
    if (el.offsetParent !== null) {
      els.push({
        tag: el.tagName,
        type: el.type || '',
        name: el.name || '',
        placeholder: el.placeholder || '',
        text: el.textContent?.trim().substring(0, 40) || '',
        contentEditable: el.contentEditable === 'true',
        role: el.getAttribute('role') || '',
      });
    }
  });
  return els;
});
console.log(JSON.stringify(fields, null, 2));
```

### What to look for

- **Form fields**: Are they `<select>`, `<input>`, custom dropdowns, or comboboxes?
- **Select options**: Dump option values AND text. Placeholders often have `value="0"` or `value=""` which looks non-empty. Use `Array.from(el.options).map(o => ({ value: o.value, text: o.text }))`. Skip options where text includes "Select" or value is `"0"`.
- **Rich text**: Does the comment box support `@mentions`, `#tags`, markdown, or emoji? Check placeholder text.
- **Required fields**: Which fields block form submission? Check `required`, `*` in labels, and try submitting empty to see validation errors.
- **Dynamic content**: Do fields appear after other fields are filled?
- **Button labels**: Exact text such as `"Submit"`, `"Submit Request"`, or `"Send"`.
- **Table column headers**: For table-driven modals, map each `input[type="number"]` to its column header instead of assuming all numeric inputs mean the same thing.

### Output

A field map for each page, used to write correct selectors in the script. Example:

```text
/purchase-requests/new:
  - Budget Code: <select> (first select on page, 4 options)
  - Desired Delivery: <input type="date">
  - Context: <textarea> (not input)
  - BOM table: inline-editable cells with span.cursor-pointer -> input pattern
  - Submit: <button> text="Submit"

/purchase-requests/N (detail):
  - Comment: <input placeholder="Type a message..."> supports @user and #PR tags
  - Send: <button> text="Send" (disabled until input has content)
```

---