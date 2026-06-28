---
skill_id: bfebe34154a0
usage_count: 1
last_used: 2026-06-16
---
## Examples

### Trigger Examples

- "Optimize this prompt for ECC"
- "Rewrite this prompt so Claude Code uses the right commands"
- "帮我优化这个指令"
- "How should I prompt ECC for this task?"

### Example 1: Vague Chinese Prompt (Project Detected)

**User input:**
```
帮我写一个用户登录页面
```

**Phase 0 detects:** `package.json` with Next.js 15, TypeScript, Tailwind CSS

**Optimized Prompt (Full):**
```
使用项目现有技术栈（Next.js 15 + TypeScript + Tailwind CSS）实现用户登录页面。

技术要求：
- 沿用项目现有的组件结构和路由约定
- 表单验证使用项目中已有的验证方案（检查是否已用 Zod/Yup/其他）
- 认证方式：沿用项目现有认证方案（如无，默认 JWT）
- 包含：邮箱/密码登录表单、表单验证、错误提示、加载状态、响应式布局

工作流：
1. /plan 先规划组件结构和认证流程，参考现有页面的模式
2. /tdd 测试先行：编写登录表单的单元测试和认证流程的集成测试
3. 实现登录页面和认证逻辑
4. /code-review 审查实现
5. /verify 验证所有测试通过且页面正常渲染

安全要求：
- 密码不明文传输
- 防止暴力破解（rate limiting）
- XSS 防护
- CSRF token

验收标准：
- 所有测试通过，覆盖率 80%+
- 页面在移动端和桌面端正常渲染
- 登录成功跳转到 dashboard，失败显示错误信息

不要做：
- 不要实现注册页面
- 不要实现忘记密码功能
- 不要修改现有的路由结构
```

### Example 2: Moderate English Prompt

**User input:**
```
Add a REST API endpoint for user profile updates with validation
```

**Phase 0 detects:** `go.mod` with Go 1.22, Chi router

**Optimized Prompt (Full):**
```
Add a REST API endpoint for user profile updates (PATCH /api/users/:id).

Tech stack: Go 1.22 + Chi router (detected from project)

Requirements:
- PATCH /api/users/:id — partial update of user profile
- Input validation for fields: name, email, avatar_url, bio
- Auth: require valid token, users can only update own profile
- Return 200 with updated user on success
- Return 400 with validation errors on invalid input
- Return 401/403 for auth failures
- Follow existing API patterns in the codebase

Workflow:
1. /plan the endpoint structure, middleware chain, and validation logic
2. /tdd — write table-driven tests for success, validation failure, auth failure, not-found
3. Implement following existing handler patterns
4. /go-review
5. /verify — run full test suite, confirm no regressions

Do not:
- Modify existing endpoints
- Change the database schema (use existing user table)
- Add new dependencies without checking existing ones first (use search-first skill)
```

### Example 3: EPIC Project

**User input:**
```
Migrate our monolith to microservices
```

**Optimized Prompt (Full):**
```
Use the blueprint skill to plan: "Migrate monolith to microservices architecture"

Before executing, answer these questions in the blueprint:
1. Which domain boundaries exist in the current monolith?
2. Which service should be extracted first (lowest coupling)?
3. Communication pattern: REST APIs, gRPC, or event-driven (Kafka/RabbitMQ)?
4. Database strategy: shared DB initially or database-per-service from start?
5. Deployment target: Kubernetes, Docker Compose, or serverless?

The blueprint should produce phases like:
- Phase 1: Identify service boundaries and create domain map
- Phase 2: Set up infrastructure (API gateway, service mesh, CI/CD per service)
- Phase 3: Extract first service (strangler fig pattern)
- Phase 4: Verify with integration tests, then extract next service
- Phase N: Decommission monolith

Each phase = 1 PR, with /verify gates between phases.
Use /save-session between phases. Use /resume-session to continue.
Use git worktrees for parallel service extraction when dependencies allow.

Recommended: Opus 4.6 for blueprint planning, Sonnet 4.6 for phase execution.
```

---