---
skill_id: a680e8454992
usage_count: 1
last_used: 2026-06-16
---
## 9. Error Handling Architecture

```dart
// Global error capture — set up in main()
void main() {
  FlutterError.onError = (details) {
    FlutterError.presentError(details);
    crashlytics.recordFlutterFatalError(details);
  };

  PlatformDispatcher.instance.onError = (error, stack) {
    crashlytics.recordError(error, stack, fatal: true);
    return true;
  };

  runApp(const App());
}

// Custom ErrorWidget for production
class App extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    ErrorWidget.builder = (details) => ProductionErrorWidget(details);
    return MaterialApp.router(routerConfig: router);
  }
}
```

---