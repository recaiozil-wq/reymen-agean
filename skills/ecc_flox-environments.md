---
name: flox-environments
description: Bu skill modüler bir yönlendiricidir. İhtiyacınız olan bölümü seçin ve
  ilgili reference dosyasını yükleyin.
title: Flox Environments
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

# Flox Environments

Bu skill modüler bir yönlendiricidir. İhtiyacınız olan bölümü seçin ve ilgili reference dosyasını yükleyin.

## 📂 Bölümler

| Bölüm | Reference Dosyası |
|-------|------------------|
| Flox Environments | `references/flox-environments.md` |
| When to Activate | `references/when-to-activate.md` |
| Core Concepts | `references/core-concepts.md` |
| Essential Commands | `references/essential-commands.md` |
| Manifest Structure | `references/manifest-structure.md` |
| .flox/env/manifest.toml | `references/flox-env-manifest-toml.md` |
| Packages to install — the core of the environment | `references/packages-to-install-the-core-of-the-environment.md` |
| Static environment variables | `references/static-environment-variables.md` |
| Non-interactive setup scripts (run every activation) | `references/non-interactive-setup-scripts-run-every-activation.md` |
| Shell functions and aliases (available in interactive shell) | `references/shell-functions-and-aliases-available-in-interactive-shell.md` |
| Supported platforms | `references/supported-platforms.md` |
| Package Installation Patterns | `references/package-installation-patterns.md` |
| Linux-only tools | `references/linux-only-tools.md` |
| macOS frameworks | `references/macos-frameworks.md` |
| GNU tools on macOS (where BSD defaults differ) | `references/gnu-tools-on-macos-where-bsd-defaults-differ.md` |
| Language-Specific Recipes | `references/language-specific-recipes.md` |
| IMPORTANT: gcc alone doesn't expose libstdc++ headers — you need gcc-unwrapped | `references/important-gcc-alone-doesn-t-expose-libstdc-headers-you-need-.md` |
| Hooks and Profile | `references/hooks-and-profile.md` |
| Anti-Patterns | `references/anti-patterns.md` |
| BAD — breaks on other machines | `references/bad-breaks-on-other-machines.md` |
| GOOD — use Flox environment variables | `references/good-use-flox-environment-variables.md` |
| BAD — kills the shell | `references/bad-kills-the-shell.md` |
| GOOD — return from hook, don't exit | `references/good-return-from-hook-don-t-exit.md` |
| BAD — manifest is committed to git | `references/bad-manifest-is-committed-to-git.md` |
| Use: API_KEY="<your-api-key>" flox activate | `references/use-api_key-your-api-key-flox-activate.md` |
| BAD — reinstalls every activation | `references/bad-reinstalls-every-activation.md` |
| GOOD — skip if already installed | `references/good-skip-if-already-installed.md` |
| BAD — hook functions aren't available in the interactive shell | `references/bad-hook-functions-aren-t-available-in-the-interactive-shell.md` |
| GOOD — use [profile] for user-invokable functions | `references/good-use-profile-for-user-invokable-functions.md` |
| Full-Stack Example | `references/full-stack-example.md` |
| Environment Sharing | `references/environment-sharing.md` |
| Teammates just run: | `references/teammates-just-run.md` |
| Project-specific additions on top of base | `references/project-specific-additions-on-top-of-base.md` |
| AI-Assisted and Vibe Coding | `references/ai-assisted-and-vibe-coding.md` |
| Agent discovers it needs a tool (e.g., jq for JSON processing) | `references/agent-discovers-it-needs-a-tool-e-g-jq-for-json-processing.md` |
| Or for more control, edit the manifest directly | `references/or-for-more-control-edit-the-manifest-directly.md` |
| Add the package to [install] section, then apply | `references/add-the-package-to-install-section-then-apply.md` |
| Run a command with the tool available | `references/run-a-command-with-the-tool-available.md` |
| Debugging | `references/debugging.md` |
| Related Skills | `references/related-skills.md` |

## Kullanım

1. İhtiyacın olan bölümü belirle
2. `skill_view(name="...", file_path="references/...")` ile yükle
