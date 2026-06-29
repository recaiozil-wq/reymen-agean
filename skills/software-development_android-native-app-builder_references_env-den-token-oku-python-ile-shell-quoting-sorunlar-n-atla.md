---
name: software-development_android-native-app-builder_references_env-den-token-oku-python-ile-shell-quoting-sorunlar-n-atla
description: .env'den token oku (Python ile, shell quoting sorunlarını atla)
title: "Software Development Android Native App Builder References Env Den Token Oku Python Ile Shell Quoting Sorunlar N Atla"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | .env'den token oku (Python ile, shell quoting sorunlarını atla) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# .env'den token oku (Python ile, shell quoting sorunlarını atla)
with open(r'C:\Users\marko\AppData\Local\hermes\.env') as f:
    content = f.read()
match = re.search(r'^TELEGRAM_BOT_TOKEN=*** content, re.MULTILINE)
token = match.group(1).strip()
chat_id = "6328823909"  # kullanıcının chat_id'si
