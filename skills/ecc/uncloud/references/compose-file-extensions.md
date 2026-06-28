---
skill_id: 3d0a3d3160f2
usage_count: 1
last_used: 2026-06-16
---
## Compose File Extensions

Uncloud adds these extensions on top of Docker Compose:

### `x-ports` — publish ports with domains

```yaml
services:
  app:
    image: app:latest
    x-ports:
      - example.com:8000/https
      - www.example.com:8000/https
      - api.example.com:9000/https
```

### `x-caddy` — custom Caddy config for service

```yaml
services:
  app:
    image: app:latest
    x-caddy: |
      example.com {
        redir https://www.example.com{uri} permanent
      }
      www.example.com {
        reverse_proxy {{upstreams 8000}} {
          import common_proxy
        }
        basic_auth /admin/* {
          admin $2a$14$...
        }
      }
```

Template functions available inside `x-caddy`:
- `{{upstreams [service] [port]}}` — healthy container IPs
- `{{.Name}}` — service name
- `{{.Upstreams}}` — map of all services → IPs

### `x-machines` — placement constraints

```yaml
services:
  db:
    image: postgres:18
    x-machines: db-machine          # Single machine name
  app:
    image: app:latest
    x-machines:
      - machine-1
      - machine-2
```

### Full multi-service example

```yaml
services:
  api:
    build: ./api
    x-ports:
      - api.example.com:3000/https
    environment:
      DATABASE_URL: postgres://db:5432/mydb

  web:
    build: ./web
    x-ports:
      - example.com:8000/https
      - www.example.com:8000/https
    environment:
      API_URL: http://api:3000

  db:
    image: postgres:18
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db-data:/var/lib/postgresql/data
    x-machines: db-machine

volumes:
  db-data:
```

---