---
skill_id: 84d762edd5f3
usage_count: 1
last_used: 2026-06-16
---
# Then PUT the encrypted secret
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/secrets/API_KEY \
  -d '<output from python script above>'