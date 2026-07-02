# 📖 Usage Guide

## Basic Usage

### Chat Mode

```
reymen chat
```

You can talk to ReYMeN in natural language. It automatically handles file operations, terminal commands, web search, and more.

### Web Interface

```
reymen web
```

Open http://localhost:5000 in your browser. Use JWT authentication (admin/reymen) to access the panel.

## Advanced Usage

### Changing Models

```
reymen model
reymen model deepseek
reymen model openai/gpt-4
```

### Kanban Board

```
reymen kanban board create "Project X"
reymen kanban add "Backend development" --column backlog --priority high
reymen kanban claim CARD_ID
reymen kanban done CARD_ID
reymen kanban swarm start TASK_DESCRIPTION
```

### Cron Tasks

```
reymen cron add "30m" "System check"
reymen cron add "0 9 * * *" "Daily report"
```

### Plugin Usage

```
reymen plugin list
reymen plugin enable web_search_provider
reymen plugin enable image_gen_provider
```

### MCP Server

```
python -m reymen.core.mcp_server --transport http --port 9000
python -m reymen.core.mcp_server --transport stdio
```

### Open WebUI Integration

In Open WebUI, add a Custom OpenAI API:
URL: http://localhost:5000/v1
API Key: reymen

## Security

### Approvals System
By default, confirmation is required for destructive commands.
Can be bypassed with the --yolo flag.

### Secrets Redaction
Tool outputs automatically mask sensitive information like API keys, tokens, and emails.

## Self-Improvement

```
reymen quality
reymen quality --trend
```
