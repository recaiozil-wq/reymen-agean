---
name: autonomous-ai-agents_kanban-codex-lane_references_overview
description: Overview
title: "Autonomous Ai Agents Kanban Codex Lane References Overview"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Overview |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Overview

This skill defines the lightweight Hermes+Codex dual-lane convention for Kanban workers. Hermes is always the task owner: it calls `kanban_show`, decides whether Codex is appropriate, creates or selects an isolated workspace, starts and monitors Codex, reconciles any diff, runs verification, and writes the final `kanban_complete` or `kanban_block` handoff. Codex is an input lane only. Codex output is not a task completion signal, not a trusted reviewer, and not allowed to write durable Kanban state directly.

The convention exists so a Hermes worker can use Codex for bounded implementation help without changing the dispatcher. The dispatcher must still spawn Hermes workers. A worker may optionally spawn Codex inside its own run, then accept, partially accept, or reject the lane after independent review and tests.
