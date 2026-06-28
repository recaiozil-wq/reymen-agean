---
skill_id: e528a02e90ab
usage_count: 1
last_used: 2026-06-16
---
# Or with specific registry
mvn package \
  -Dquarkus.container-image.build=true \
  -Dquarkus.container-image.registry=docker.io \
  -Dquarkus.container-image.group=myorg \
  -Dquarkus.container-image.tag=1.0.0