---
skill_id: 0382b30a0834
usage_count: 1
last_used: 2026-06-16
---
## Pitfalls

- **VM locked error**: `VBoxManage modifyvm` fails if VM is running (locked for session). Always power off first: `VBoxManage controlvm <name> acpipowerbutton` or disable from GUI.
- **Stale lock after GUI crash**: If modify/start still fails after closing VirtualBox, kill `VirtualBoxVM.exe`, wait a few seconds, then retry. This clears orphaned session locks.
- **USB passthrough breaks VM networking**: Passing a USB WiFi adapter to a Kali VM can destabilize the VM's network stack. Kali's NetworkManager may try to use the USB WiFi as the primary interface and drop the host-only/NAT connection. Symptoms: SSH/ping stop responding even after removing the USB filter. VBox.log shows "Attached" for the USB device but VM becomes unreachable.
  - **Fix**: Remove USB filter physically from the VM settings (`VBoxManage usbfilter remove 0 --target <vm>`), poweroff cleanly, restart, wait for boot, then SSH in via host-only. If still unreachable after 60s boot, use VirtualBox GUI console to diagnose: `sudo dhclient eth1 && systemctl restart ssh` from the VM console.
- **Multiple poweroff/startup cycles corrupting VDI lock**: Rapid `controlvm poweroff` → `startvm` cycles can leave VDI in a read-only locked state with `VERR_VD_IMAGE_READ_ONLY`. Fix: `Stop-Process -Name VBoxSVC -Force`, wait 5s, then retry. The VDI file's filesystem attributes may show `False` for IsReadOnly but VBoxSVC still holds a stale lock.
- **VBoxManage hostonlyif commands hanging**: `VBoxManage hostonlyif remove` and `hostonlyif create` can hang indefinitely if VBoxSVC is in a bad state. Kill VBoxSVC first, then retry. If still hangs, the host-only adapter is fine — the problem is inside the VM's network config, not VirtualBox's.
- **Kali black screen after boot**: Common with Kali + GNOME + older VirtualBox graphics defaults. Preferred fix: set `--graphicscontroller vboxvga`, `--vram 128`, `--accelerate3d off`, and append `nomodeset` to GRUB. See [kali-grub-nomodeset.md](references/kali-grub-nomodeset.md).
- **SSH refused**: VM may not have sshd running. On Kali: `sudo systemctl enable --now ssh`. If NAT only, port forwarding must be configured **before** VM boot.
- **NAT port forwarding rules**: Set with `--natpf1 "ssh,tcp,127.0.0.1,2222,10.0.2.15,22"`. Note guest IP (right side) must be the VM's actual NAT IP (usually 10.0.2.15).
- **VRDP port conflicts**: Default 3389 may conflict with Windows RDP. Use high port (e.g. 5000).
- **Host-Only DHCP**: May be disabled. Set static IP in VM or enable DHCP on host-only network.
- **GuestInfo IP may be unavailable**: `VBoxManage guestproperty get <vm> "/VirtualBox/GuestInfo/Net/*/V4/IP"` can return `No value set!` even on an otherwise healthy VM. When GuestInfo IP retrieval fails, use alternative discovery methods: try SSH with the expected NAT default (10.0.2.15), inspect host-only lease tables, or use network scanning from the host.
- **PATH-less VBoxManage on Windows**: `VBoxManage.exe` is usually under `C:\Program Files\Oracle\VirtualBox\VBoxManage.exe`, not on PATH by default. Use that path explicitly.
- **Elevated execution quoting failure**: PowerShell quoting through `-ArgumentList '...'` often fails (`positional parameter cannot be found`). Running elevated through `cmd.exe` avoids this class of quoting bug.
- **UAC elevation cannot capture stdout directly**: UAC-spawned elevated processes do not return stdout through the invoking shell. Use a file-redirection strategy instead of trying to capture output inline.\n- **Keyboardputstring race condition**: Chaining `keyboardputstring` commands without sufficient `sleep` between them causes the next command to be typed before the previous one finishes executing (e.g. typing `sudo nmap -sn` then immediately typing `echo bitti` on the same prompt line). Always sleep 1-2s between simple commands, 3-8s for longer scans.
- **Long compound commands silently drop text**: Shell constructs like `echo '...' && echo '...' && echo '...'` sent as a single `keyboardputstring` call can truncate or drop characters because VirtualBox's keyboard buffer is limited. **Split every logical command into its own call** with sleep between:
  ```bash