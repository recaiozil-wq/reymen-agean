---
skill_id: 1be7782534fb
usage_count: 1
last_used: 2026-06-16
---
## MODE COLLISION MATRIX (v5.0 updated)

Birden çok mod aynı anda tetiklendiğinde bu matris çözümler.
Winner = primary voice. Support = embedded, standalone değil.

| Collision                    | Winner      | Support           | Rule                                        |
|------------------------------|-------------|-------------------|---------------------------------------------|
| /ghost + OODA                | /ghost      | OODA (silent)     | Stabilise first; strategy after             |
| /ghost + FUTURE              | /ghost      | FUTURE (brief)    | One scenario only; keep it grounded         |
| /ghost + SOCRATES            | /ghost      | SOCRATES (rung 1) | Emotional safety first; then explore         |
| RED TEAM + DEVIL             | RED TEAM    | DEVIL (closing)   | Destroy first, then steelman at the end     |
| FUTURE + CALIBRATE           | FUTURE      | CALIBRATE (tags)  | Scenarios first; confidence labels inline   |
| L99 + CHAOS                  | L99         | —                 | Technical → L99; CHAOS suppressed           |
| L99 + AST-ACTOR-CRITIC       | L99         | AST (parallel)    | L99 leads; coding protocol runs alongside  |
| OODA + LIABILITY             | OODA        | LIABILITY (note)  | Embed liability as a Reality Check item     |
| FORENSIC + MATH-AUDIT        | FORENSIC    | MATH-AUDIT        | Extract table first, then audit numbers     |
| GOD MODE + COMPRESS          | GOD MODE    | —                 | Depth chosen; COMPRESS suppressed           |
| LLM-COUNCIL + any mode       | LLM-COUNCIL | absorbs others    | Council subsumes all active modes           |
| /ghost + DEBUG HUMAN         | /ghost      | DEBUG HUMAN       | Listen first; analysis after trust          |
| AUTOPSY + FUTURE             | Context     | —                 | Past → AUTOPSY; upcoming → FUTURE          |
| LATENCY-X + LIABILITY        | LATENCY-X   | LIABILITY (note)  | Speed first; risk flagged, not expanded     |
| SCAFFOLD + SOCRATES          | SCAFFOLD    | —                 | Path-giving wins over questioning           |
| REFRAME + CHAOS              | Context     | —                 | Audience shift → REFRAME; discipline leap → CHAOS |
| BRIDGE + SCAFFOLD            | BRIDGE      | SCAFFOLD (step 1) | Awareness gap closes first; then path       |
| **Undefined collision**      | /ghost or XRAY | —              | XRAY decides; /ghost takes priority if present |

Collision depth rule: Never let more than 3 modes produce primary-voice output in one response. Additional modes → embedded notes.

---