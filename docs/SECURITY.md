# Security Policy

## 🛡️ Supported Versions

| Version | Support |
|:--------|:--------|
| 0.9.x (beta) | ✅ Security patches |
| < 0.9 | ❌ Not supported |

## 🔐 Reporting a Vulnerability

If you find a security vulnerability in ReYMeN:

1. **DO NOT open a public issue**
2. **Contact via Telegram:** @Pasa_38
3. Or email: (coming soon)

### Expected response time

- First response: within 48 hours
- Fix: within 7 days

## ⚠️ Known Security Warnings

### API Keys

- **Never** commit `.env` file to git
- Edit `.env.example` and use as `.env`
- On Linux: `chmod 600 .env`
- API keys are not written to logs (protected by filter)

### Token Security

- Telegram bot tokens are stored in `.env`
- Use a separate token for each bot
- If a token is leaked: revoke via BotFather with `/revoke`

### Execution Security

- `approvals.mode: smart` — asks for approval on dangerous operations
- Sandbox mode: File access can be limited to project directory
- PII redaction: Sensitive data is automatically sanitized
