---
skill_id: 970cc1548691
usage_count: 1
last_used: 2026-06-16
---
# Check attachment in boot log (after VM started)
grep -i "USB\|<vendorid>\|<productid>\|attach" "C:/Users/<user>/VirtualBox VMs/<vm>/Logs/VBox.log"
```

**Known good config for RT73 (Ralink) USB WiFi:**
- VID 148F, PID 2573
- HighSpeed on RootHub (OHCI/EHCI controller)
- xHCI (USB 3.0) controller NOT needed — RT73 is USB 2.0 HighSpeed
- Works with VirtualBox default OHCI+EHCI controllers

**⚠️ WiFi passthrough danger**: USB WiFi passthrough can destabilize the VM's own networking (see Pitfalls). Best practice: set up USB filter while VM is off, start VM, expect it to take slightly longer on first boot as the new USB device is detected. If the VM becomes unreachable, the fix is removing the filter + console recovery.