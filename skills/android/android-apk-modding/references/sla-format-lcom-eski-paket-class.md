---
skill_id: c2b44a2578f9
usage_count: 1
last_used: 2026-06-16
---
# Slaş format (Lcom/eski/paket/Class;)
grep -rl "com/eski/paket/yolu" smali/ smali_classes2/ | \
  xargs sed -i 's|com/eski/paket/yolu|com/yeni/paket/yolu|g'