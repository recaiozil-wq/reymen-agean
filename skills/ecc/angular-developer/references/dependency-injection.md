---
skill_id: c36a3629f6e4
usage_count: 1
last_used: 2026-06-16
---
## Dependency Injection

When implementing dependency injection in Angular, follow these guidelines:

- **Fundamentals**: Overview of Dependency Injection, services, and the `inject()` function. Read [di-fundamentals.md](references/di-fundamentals.md)
- **Creating and Using Services**: Creating services, the `providedIn: 'root'` option, and injecting into components or other services. Read [creating-services.md](references/creating-services.md)
- **Defining Dependency Providers**: Automatic vs manual provision, `InjectionToken`, `useClass`, `useValue`, `useFactory`, and scopes. Read [defining-providers.md](references/defining-providers.md)
- **Injection Context**: Where `inject()` is allowed, `runInInjectionContext`, and `assertInInjectionContext`. Read [injection-context.md](references/injection-context.md)
- **Hierarchical Injectors**: The `EnvironmentInjector` vs `ElementInjector`, resolution rules, modifiers (`optional`, `skipSelf`), and `providers` vs `viewProviders`. Read [hierarchical-injectors.md](references/hierarchical-injectors.md)