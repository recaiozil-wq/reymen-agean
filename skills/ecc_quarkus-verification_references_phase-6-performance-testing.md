---
name: ecc_quarkus-verification_references_phase-6-performance-testing
description: "Phase 6: Performance Testing"
title: "Ecc Quarkus Verification References Phase 6 Performance Testing"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Phase 6: Performance Testing |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Phase 6: Performance Testing

### Load Testing with K6

```javascript
// load-test.js
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 50 },
    { duration: '1m', target: 100 },
    { duration: '30s', target: 0 },
  ],
};

export default function () {
  const res = http.get('http://localhost:8080/api/markets');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });
}
```

Run:
```bash
k6 run load-test.js
```

### Metrics to Monitor

- Response time (p50, p95, p99)
- Throughput (requests/sec)
- Error rate
- Memory usage
- CPU usage
