---
skill_id: 47409708274b
usage_count: 1
last_used: 2026-06-16
---
# Find by network class
Get-PnpDevice | Where-Object { $_.Class -eq 'Net' } | Select-Object FriendlyName,InstanceId | Format-List
```

Add USB filter (VM must be off or device not yet captured):
```bash
VBoxManage usbfilter add 0 --target "<vm-name>" \
  --name "RT73 USB Wireless" \
  --vendorid 148F \
  --productid 2573 \
  --revision 0001
```

Verify filter and attachment:
```bash