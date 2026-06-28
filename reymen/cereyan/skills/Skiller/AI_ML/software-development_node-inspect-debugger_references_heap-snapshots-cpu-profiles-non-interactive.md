---
name: software-development_node-inspect-debugger_references_heap-snapshots-cpu-profiles-non-interactive
description: Heap Snapshots & CPU Profiles (Non-interactive)
title: "Software Development Node Inspect Debugger References Heap Snapshots Cpu Profiles Non Interactive"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Heap Snapshots & CPU Profiles (Non-interactive) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Heap Snapshots & CPU Profiles (Non-interactive)

From the CDP driver above, swap Debugger for `HeapProfiler` / `Profiler`:

```javascript
// CPU profile for 5 seconds
await client.Profiler.enable();
await client.Profiler.start();
await new Promise(r => setTimeout(r, 5000));
const { profile } = await client.Profiler.stop();
require('fs').writeFileSync('/tmp/cpu.cpuprofile', JSON.stringify(profile));
// Open /tmp/cpu.cpuprofile in Chrome DevTools → Performance tab
```

```javascript
// Heap snapshot
await client.HeapProfiler.enable();
const chunks = [];
client.HeapProfiler.addHeapSnapshotChunk(({ chunk }) => chunks.push(chunk));
await client.HeapProfiler.takeHeapSnapshot({ reportProgress: false });
require('fs').writeFileSync('/tmp/heap.heapsnapshot', chunks.join(''));
```
