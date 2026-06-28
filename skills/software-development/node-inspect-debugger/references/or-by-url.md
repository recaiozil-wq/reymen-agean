---
skill_id: 779c125be557
usage_count: 1
last_used: 2026-06-16
---
# or by URL
node inspect ws://127.0.0.1:9229/<uuid>
```

To start a process with the inspector from the beginning:

```bash
node --inspect script.js           # listen on 127.0.0.1:9229, keep running
node --inspect-brk script.js       # listen AND pause on first line
node --inspect=0.0.0.0:9230 script.js   # custom host:port
```

For TypeScript via tsx:

```bash
node --inspect-brk --import tsx script.ts