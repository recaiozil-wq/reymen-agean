---
skill_id: ae055c9eb740
usage_count: 1
last_used: 2026-06-16
---
## 4. Widget Architecture

### Extract to Classes, Not Methods

```dart
// BAD — private method returning widget, prevents optimization
Widget _buildHeader() {
  return Container(
    padding: const EdgeInsets.all(16),
    child: Text(title, style: Theme.of(context).textTheme.headlineMedium),
  );
}

// GOOD — separate widget class, enables const, element reuse
class _PageHeader extends StatelessWidget {
  const _PageHeader(this.title);
  final String title;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Text(title, style: Theme.of(context).textTheme.headlineMedium),
    );
  }
}
```

### const Propagation

```dart
// BAD — new instances every rebuild
child: Padding(
  padding: EdgeInsets.all(16.0),       // not const
  child: Icon(Icons.home, size: 24.0), // not const
)

// GOOD — const stops rebuild propagation
child: const Padding(
  padding: EdgeInsets.all(16.0),
  child: Icon(Icons.home, size: 24.0),
)
```

### Scoped Rebuilds

```dart
// BAD — entire page rebuilds on every counter change
class CounterPage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(counterProvider); // rebuilds everything
    return Scaffold(
      body: Column(children: [
        const ExpensiveHeader(), // unnecessarily rebuilt
        Text('$count'),
        const ExpensiveFooter(), // unnecessarily rebuilt
      ]),
    );
  }
}

// GOOD — isolate the rebuilding part
class CounterPage extends StatelessWidget {
  const CounterPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Column(children: [
        ExpensiveHeader(),        // never rebuilt (const)
        _CounterDisplay(),        // only this rebuilds
        ExpensiveFooter(),        // never rebuilt (const)
      ]),
    );
  }
}

class _CounterDisplay extends ConsumerWidget {
  const _CounterDisplay();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(counterProvider);
    return Text('$count');
  }
}
```

---