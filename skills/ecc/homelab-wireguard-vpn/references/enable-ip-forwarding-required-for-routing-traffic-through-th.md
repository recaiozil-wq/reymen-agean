---
skill_id: 727ae33da89f
usage_count: 1
last_used: 2026-06-16
---
# Enable IP forwarding (required for routing traffic through the server)
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-wireguard.conf
sudo sysctl --system