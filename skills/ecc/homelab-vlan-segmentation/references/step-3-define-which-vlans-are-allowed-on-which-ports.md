---
skill_id: 10d6b856c0f7
usage_count: 1
last_used: 2026-06-16
---
# Step 3: Define which VLANs are allowed on which ports
/interface bridge vlan
add bridge=bridge tagged=ether1 untagged=ether2 vlan-ids=10
add bridge=bridge tagged=ether1 untagged=ether3 vlan-ids=20