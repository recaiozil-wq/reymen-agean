---
name: user-preferences-hersona-skills-hersona-initializer
description: プロフィール初回使用時にhersonaを自動適用し、会話中に口調が崩れかけた場合の辅助も行うスキルです。
title: User Preferences Hersona Skills Hersona Initializer
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

# hersona-initializer

## 概要
プロフィール初回使用時にhersonaを自動適用し、会話中に口調が崩れかけた場合の辅助も行うスキルです。

## 主な機能
- 初回メッセージ時に自動でデフォルトペルソナを適用
- 口調の崩れを辅助的に检知・修正する機能（将来的な拡張含む）
- 手動での再適用コマンドを提供

## コマンド
```bash
/hersona init          # 手動でペルソナを再適用・強化
/hersona init --force  # 強制的に再適用
```

## 推奨設定
プロフィールの `SOUL.md` に以下を記述してください：

```markdown
## Hersona Default Settings
Default command: /hersona personality/tsundere speech/keigo multi --weight moderate
```

この記述を読み取り、初回適用および必要に応じた再適用を行います。
