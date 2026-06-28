---
skill_id: 5c6f38f68b47
usage_count: 1
last_used: 2026-06-16
---
# Run on the client, or on the server and transfer the private key securely — never in plaintext
umask 077
wg genkey | tee phone_private.key | wg pubkey > phone_public.key