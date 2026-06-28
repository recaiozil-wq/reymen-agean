---
skill_id: 68ee081f72e8
usage_count: 1
last_used: 2026-06-16
---
## Quick Paths

### 1. Check VM status
```bash
VBoxManage = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
subprocess.run([VBoxManage, "showvminfo", VM_NAME, "--machinereadable"])