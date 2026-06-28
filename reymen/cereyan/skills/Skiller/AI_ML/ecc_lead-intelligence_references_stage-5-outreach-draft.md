---
name: ecc_lead-intelligence_references_stage-5-outreach-draft
description: "Stage 5: Outreach Draft"
title: "Ecc Lead Intelligence References Stage 5 Outreach Draft"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_lead-intelligence_references_stage-5-outreach-draft.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Stage 5: Outreach Draft

Generate personalized outreach for each lead. The draft should match the source-derived voice profile and the target channel.

### Channel Rules

#### Email

- Use for the highest-value cold outreach, warm intros, investor outreach, and partnership asks
- Default to drafting in Apple Mail / Mail.app when local desktop control is available
- Create drafts first, do not send automatically unless the user explicitly asks
- Subject line should be plain and specific, not clever

#### LinkedIn

- Use when the target is active there, when mutual graph context is stronger on LinkedIn, or when email confidence is low
- Prefer API access if available
- Otherwise use browser control to inspect profiles, recent activity, and draft the message
- Keep it shorter than email and avoid fake professional warmth

#### X

- Use for high-context operator, builder, or investor outreach where public posting behavior matters
- Prefer API access for search, timeline, and engagement analysis
- Fall back to browser control when needed
- DMs and public replies should be much tighter than email and should reference something real from the target's timeline

#### Channel Selection Heuristic

Pick one primary channel in this order:

1. warm intro by email
2. direct email
3. LinkedIn DM
4. X DM or reply

Use multi-channel only when there is a strong reason and the cadence will not feel spammy.

### Warm Intro Request (to mutual)

Goal:

- one clear ask
- one concrete reason this intro makes sense
- easy-to-forward blurb if needed

Avoid:

- overexplaining your company
- social-proof stacking
- sounding like a fundraiser template

### Direct Cold Outreach (to target)

Goal:

- open from something specific and recent
- explain why the fit is real
- make one low-friction ask

Avoid:

- generic admiration
- feature dumping
- broad asks like "would love to connect"
- forced rhetorical questions

### Execution Pattern

For each target, produce:

1. the recommended channel
2. the reason that channel is best
3. the message draft
4. optional follow-up draft
5. if email is the chosen channel and Apple Mail is available, create a draft instead of only returning text

If browser control is available:

- LinkedIn: inspect target profile, recent activity, and mutual context, then draft or prepare the message
- X: inspect recent posts or replies, then draft DM or public reply language

If desktop automation is available:

- Apple Mail: create draft email with subject, body, and recipient

Do not send messages automatically without explicit user approval.

### Anti-Patterns

- generic templates with no personalization
- long paragraphs explaining your whole company
- multiple asks in one message
- fake familiarity without specifics
- bulk-sent messages with visible merge fields
- identical copy reused for email, LinkedIn, and X
- platform-shaped slop instead of the author's actual voice
