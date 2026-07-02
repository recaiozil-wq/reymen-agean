# 🛠️ CLI Reference

`reymen` command line interface.

## General Usage

```
reymen [command] [parameters]
```

## Commands

### `reymen chat`

Interactive or single-query chat.

```
# Interactive
reymen chat

# Single query
reymen chat -q "What is the capital of Turkey?"

# Select model
reymen chat -m deepseek
```

### `reymen web`

Web UI (http://localhost:5000).

```
reymen web
reymen web --port 8080
```

### `reymen kanban`

Kanban board management.

```
reymen kanban boards
reymen kanban add "New task" --column backlog
reymen kanban move KART_ID in_progress
reymen kanban done KART_ID
```

### `reymen cron`

Scheduled tasks.

```
reymen cron list
reymen cron add "30m" "Check every 30 minutes"
reymen cron pause JOB_ID
```

### `reymen plugin`

Plugin management.

```
reymen plugin list
reymen plugin install PLUGIN_NAME
reymen plugin remove PLUGIN_NAME
```

### `reymen model`

Model/provider management.

```
reymen model
reymen model deepseek
reymen model providers
```

### `reymen session`

Session management.

```
reymen session list
reymen session search "keyword"
reymen session delete SESSION_ID
```

### `reymen backup`

Backup.

```
reymen backup create
reymen backup restore FILE.zip
reymen backup list
```

### `reymen gateway`

Gateway management.

```
reymen gateway start
reymen gateway stop
reymen gateway status
```

### `reymen skill`

Skill management.

```
reymen skill list
reymen skill search "keyword"
reymen skill install SKILL_NAME
```

### `reymen config`

Configuration.

```
reymen config show
reymen config set key.value
reymen config edit
```

## Exit Codes

| Code | Meaning |
|:----:|---------|
| 0 | Success |
| 1 | General error |
| 2 | Parameter error |
| 3 | Authorization error |
| 4 | Connection error |
