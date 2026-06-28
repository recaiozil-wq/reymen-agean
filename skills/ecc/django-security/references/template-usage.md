---
skill_id: 8cd149a0a32f
usage_count: 1
last_used: 2026-06-16
---
# Template usage
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>