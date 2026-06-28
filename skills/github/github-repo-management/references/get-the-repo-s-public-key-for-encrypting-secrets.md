---
skill_id: d026095756e0
usage_count: 1
last_used: 2026-06-16
---
# Get the repo's public key for encrypting secrets
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/secrets/public-key