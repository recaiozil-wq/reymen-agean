---
skill_id: d238e557eed1
usage_count: 1
last_used: 2026-06-16
---
## Integration with ReYMeN Agent

The integration point is **nexus-core-omega-v5** execution sequence step 9.5 (ZORUNLU RL SKILL LOG). Every message response ends with a call to the CLI bridge.

### CLI Integration Bridge

Every user message should log the selected skill. Use the integration script:

```bash
python /c/Users/marko/AppData/Local/hermes/rl_observation/rl_integration.py \
  --query "<user query, 100 chars max>" \
  --skill "<skill name or 'none'>" \
  --mode "<active mode>" \
  --rule-based
```

With user feedback (auto-reward):
```bash
python /c/Users/marko/AppData/Local/hermes/rl_observation/rl_integration.py \
  --query "<query>" \
  --skill "<skill>" \
  --user-reply "<user's reply to previous response>"
```

Get stats:
```bash
python /c/Users/marko/AppData/Local/hermes/rl_observation/rl_integration.py --action stats
python /c/Users/marko/AppData/Local/hermes/rl_observation/rl_integration.py --action mab-data
```

### Cron Monitoring Pattern

Two cron jobs run daily for RL system health:

| Time | Job | Purpose |
|------|-----|---------|
| 20:00 | RL Günlük Rapor | Toplu istatistik + karşılaştırmalı analiz |
| 21:00 | GitHub Push | RL kod değişikliklerini yedekleme |

**20:00 job structure (self-contained skill prompt):**
1. `rl_integration.py --action stats` + `--action mab-data` → ham veri
2. session_search ile önceki günün raporunu bul
3. Karşılaştırmalı rapor hazırla (MAB karar oranı, negatif trend, threshold değeri, en başarılı/en sorunlu skill'ler)
4. **Format kuralı: Telegram uyumlu, tablo kullanma.** Rapor şu yapıda olmalı:
   ```
   **RL SİSTEMİ — GÜNLÜK RAPOR [GG.AA.YYYY HH:MM]**

   Toplam: X | Kural: X | MAB: X
   Pozitif: X | Negatif: X | Nötr: X
   MAB karar oranı: X%

   En başarılı skill'ler (alpha/beta):
   - skill1 — α:X/β:X (%XX) ✅
   - skill2 — α:X/β:X (%XX) ✅

   En sorunlu skill'ler (yüksek beta):
   - skill3 — α:X/β:X (%XX) ⚠️

   Threshold: X (auto_tune)

   Önceki güne göre değişim:
   + MAB karar sayısı: X → X
   + Negatif reward: X → X
   + Toplam kayıt artışı: X

   Değerlendirme: 1-2 cümlelik yorum
   ```

**21:00 job structure (workdir: hermes-backup):**
1. RL kod dosyalarını `AppData/Local/hermes/rl_observation/` → `hermes-backup/rl_observation/` e kopyala
2. `git status` + `git diff --stat`
3. Değişiklik varsa → add, commit ("auto-sync YYYY-MM-DD_HH:MM"), push
4. Raporu Telegram'a gönder

### Log Maintenance

A cron job runs daily at 04:00:
- Rotates log file at 5MB (skill_log_YYYYMMDD.jsonl)
- Prunes to keep only last 1000 entries
- 30-day half-life exponential decay on old weights

### For ReYMeN Agent specifically:

1. **Logger installed at:** `C:\Users\marko\AppData\Local\hermes\rl_observation\rl_skill_logger.py`
2. **Log file:** `C:\Users\marko\AppData\Local\hermes\rl_observation\skill_log.jsonl`
3. **Integration point:** nexus-core-omega-v5 execution sequence step 9.5 (after task completion, before daily log write)
4. **Call from agent response (PREFERRED):**
   ```bash
   python /c/Users/marko/AppData/Local/hermes/rl_observation/rl_integration.py \
     --query "..." --skill "..." --mode "..."
   ```
5. **Reward update on user correction:**
   ```bash
   python /c/Users/marko/AppData/Local/hermes/rl_observation/rl_integration.py \
     --update-reward "<log_id>" --new-reward -1
   ```

### Generic integration pattern (any agent framework):
1. Hook into the agent's post-decision lifecycle
2. Log: {timestamp, query_context, action_taken, decision_source, initial_reward}
3. Hook into the post-response lifecycle
4. Update reward based on user feedback signal
5. Periodically train/recalibrate MAB from accumulated log

### Reward Validation (Required Before Any MAB Training)

Before touching MAB thresholds, seed data, or shadow mode, **validate the reward function.** A reward function with <70% accuracy on a labeled test set will corrupt MAB faster than no reward function at all.

**Method:** Build a 15-message golden set covering positive, negative, and neutral cases. Run auto_reward against manual labels. Gate at 70% accuracy. See `references/reward-validation-methodology.md` for the exact golden set and procedure.

**Current state (14 June 2026):** auto_reward v1 (keyword-only) validated at 93% on the 15-case golden set. Known limitation: measures tone, not outcome. reward_v2 (behavioral) in development — adds correction/progression/silence signals.

### Pitfalls

- **Reward function is everything.** A bad reward function is worse than no RL at all. The system will optimize whatever you measure — measure the wrong thing and you get pathological behavior.
- **Full Deep RL (DQN/PPO) is overkill** for skill selection. The state space is small (current query features → skill choice). MAB handles this with zero neural network complexity.
- **Don't log full query text** — use hashes. The log file grows indefinitely and PII is a concern.
- **Shadow mode is not optional.** Never flip the switch without knowing what the MAB would have done differently.
- **Manual override must always exist.** The user should be able to say "use skill X, forget what MAB says."
- **MAB needs minimum data.** With fewer than 10-20 data points per arm, Thompson Sampling is essentially random. Start logging before you start optimizing.
- **auto_reward keyword list is a silent data corruption vector.** Single-word negative keywords ("degil", "hayir", "olmaz", "tekrar") in auto_reward trigger -1 on normal conversational speech, inflating beta values across multiple skills. Symptoms: 5+ skills show beta=7+ while alpha stays 1-3. Fix: use phrase-level patterns ("yanlis oldu", "calismadi", "hata verdi") instead of single words, or implement a confirmation gate before applying negative rewards.
- **Monitor MAB data health regularly.** Check `rl_integration.py --action mab-data` weekly. Look for: (a) skills where beta > alpha+3 — likely false negatives, (b) skills with <3 total pulls — not enough data, (c) MAB decision ratio <15% — threshold may be too high. Run stats every 3-5 days after any auto_reward changes to catch drift early.
- **Never seed all skills at once in a single context.** Seeding 622 skills (or more) into one "genel" context with neutral priors (alpha=1, beta=1) turns MAB into a random selector. With all arms equal, Thompson Sampling produces uniform random picks. Result: 4.3% accuracy on a 23-query shadow test. Strategy: seed one category at a time (e.g. "windows-shortcuts" first, ~10-15 skills), shadow-test for 50+ queries, then expand to the next category. A narrow but proven set beats a wide but flat set.
- **Tone-based reward does not measure skill success.** auto_reward at 93% accuracy still only tells you if the user's next message sounds happy, not whether the selected skill actually solved the problem. A user can say "thanks" out of politeness (false positive) or "no" to an unrelated question (false negative). reward_v2 adds behavioral signals (correction/progression/silence) to bridge this gap. Do not promote a skill based on tone alone — wait for behavioral confirmation.
- **A test that modifies the system it's testing produces invalid results.** If you discover a bug mid-test (max→min, empty-message correction, missing prev_skill), STOP the test. Record the failure. Fix the bug as a SEPARATE task. Re-freeze the system. Re-run from scratch. Running patches mid-test means the final result measures a system that never existed at any single point in the window. Three concrete rules: (1) Take a frozen snapshot before the first test run (copy the module, point the test import at the copy). (2) The test script is READ-ONLY: calls functions, never writes files, never patches imports at runtime. (3) If a bug is found during testing, the fix goes into the SOURCE module. The frozen copy is updated after the fix, then the test is re-run. The test NEVER modifies its own subject.
- **Empty/correction hazard with null next_msg.** When `next_msg` is empty/None (user is silent), do NOT fall back to `prev_msg` as `current_query` inside the test harness or reward_v2. The fallback creates false hash equality with the previous entry, triggering an incorrect -0.6 correction signal. Fix: let empty `next_msg` pass through as-is; reward_v2 handles it by setting `current_hash = ""` so no hash match can occur. ALSO gate the entire correction block: when `is_empty_message=True`, skip the correction for-loop entirely (not just the hash check). Silence is a SEPARATE signal (silence_seconds), not a subtype of correction. Verify with: reward(13) and reward(14) must show corr=0.00, not -0.30 from stale skill-level correction.
- **Cron/background entries create neutral-only streaks.** When the system runs unattended (cron jobs, background maintenance), every decision logs with reward=0 because there's no user reply to auto_reward. This inflates the neutral count without providing learning signal. Don't mistake "growing total entries" for "growing training data." Monitor positive+negative count separately from total count. If neutral entries grow but pos/neg stays flat, the streak is cron noise, not learning progress. Current baseline (14 June 2026): ~16 neutral entries per 76 minutes during unattended operation.
- **max/min trap in correction logic.** `max(current_correction, -0.3)` returns `0.0` because `0.0 > -0.3`. The debug print shows the assignment happening, but the value is silently clobbered. Use `min(current_correction, -0.3)` instead — the more negative (stronger signal) survives. Root-cause pattern: `components["correction"]` appears 0.0 in the final dict despite skill-match code path being entered. Test by: log both `components["correction"]` before and after the assignment, or add a direct `print(f"correction after: {components['correction']}")` right after the min/max line.