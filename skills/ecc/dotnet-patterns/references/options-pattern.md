---
skill_id: 07203d6584ad
usage_count: 1
last_used: 2026-06-16
---
## Options Pattern

Bind configuration sections to strongly-typed objects.

```csharp
public sealed class SmtpOptions
{
    public const string SectionName = "Smtp";

    public required string Host { get; init; }
    public required int Port { get; init; }
    public required string Username { get; init; }
    public bool UseSsl { get; init; } = true;
}

// Registration
builder.Services.Configure<SmtpOptions>(
    builder.Configuration.GetSection(SmtpOptions.SectionName));

// Usage via injection
public class EmailService(IOptions<SmtpOptions> options)
{
    private readonly SmtpOptions _smtp = options.Value;
}
```