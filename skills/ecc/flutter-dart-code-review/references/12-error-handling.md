---
skill_id: 074688655b6f
usage_count: 1
last_used: 2026-06-16
---
## 12. Error Handling

### Framework error handling:
- [ ] `FlutterError.onError` overridden to capture framework errors (build, layout, paint)
- [ ] `PlatformDispatcher.instance.onError` set for async errors not caught by Flutter
- [ ] `ErrorWidget.builder` customized for release mode (user-friendly instead of red screen)
- [ ] Global error capture wrapper around `runApp` (e.g., `runZonedGuarded`, Sentry/Crashlytics wrapper)

### Error reporting:
- [ ] Error reporting service integrated (Firebase Crashlytics, Sentry, or equivalent)
- [ ] Non-fatal errors reported with stack traces
- [ ] State management error observer wired to error reporting (e.g., BlocObserver, ProviderObserver, or equivalent for your solution)
- [ ] User-identifiable info (user ID) attached to error reports for debugging

### Graceful degradation:
- [ ] API errors result in user-friendly error UI, not crashes
- [ ] Retry mechanisms for transient network failures
- [ ] Offline state handled gracefully
- [ ] Error states in state management carry error info for display
- [ ] Raw exceptions (network, parsing) are mapped to user-friendly, localized messages before reaching the UI — never show raw exception strings to users

---