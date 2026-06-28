---
skill_id: 82d37502987f
usage_count: 1
last_used: 2026-06-16
---
# td_execute_python script:
root = op('/project1')
nodes = []
for name, optype in [('bg', noiseTOP), ('fx', levelTOP), ('out', nullTOP)]:
    n = root.create(optype, name)
    nodes.append(n.path)