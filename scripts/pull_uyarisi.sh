#!/bin/sh
# ReYMeN pre-commit pull uyarisi hook
# Birden fazla local kopyada calisirken remote'un gerisinde
# kalmamak icin commit oncesi fetch + uyari.

git fetch origin 2>/dev/null
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null)

if [ -n "$BEHIND" ] && [ "$BEHIND" -gt 0 ] 2>/dev/null; then
    echo ""
    echo "⚠️  UYARI: Remote'ta $BEHIND yeni commit var!"
    echo "   'git pull --rebase' oneriliyor."
    echo ""
fi
exit 0
