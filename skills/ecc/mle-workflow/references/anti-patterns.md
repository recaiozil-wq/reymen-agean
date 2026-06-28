---
skill_id: 1d71f6b47202
usage_count: 1
last_used: 2026-06-16
---
## Anti-Patterns

- Notebook state is required to reproduce the model
- Random split leaks future data into validation or test sets
- Feature joins ignore event time and label availability
- Offline metric improves while important slices regress
- Thresholds are tuned on the test set repeatedly
- Training preprocessing is copied manually into serving code
- Model version is missing from prediction logs
- Monitoring only checks service uptime, not data or prediction quality
- Rollback requires retraining instead of switching to a known-good artifact