---
skill_id: e1b347d1d39b
usage_count: 1
last_used: 2026-06-16
---
## Connection Pools

SQLAlchemy example:

```python
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+mysqlconnector://app:secret@db.internal/app",
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=240,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 5},
)
```

Node.js `mysql2` example:

```javascript
import mysql from 'mysql2/promise';

const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
  enableKeepAlive: true,
  keepAliveInitialDelay: 30000,
});

const [rows] = await pool.execute(
  'SELECT id, total FROM orders WHERE account_id = ? LIMIT 50',
  [accountId],
);
```

Keep application pool recycling below the server `wait_timeout`. If the server
uses `wait_timeout = 300`, a `pool_recycle` around 240 seconds is coherent;
`pool_pre_ping` still helps recover from network and failover events.