#!/bin/sh
#
# ReYMeN pre-commit hook — pull uyarisi
# Kaynak: scripts/pre-commit.sh
# Kurulum: bash scripts/install-hooks.sh
#
# Birden fazla local kopyada calisirken remote'un gerisinde
# kalmamak icin commit oncesi fetch + uyari.
#

# Sessiz fetch — remote ref'leri guncelle
git fetch origin 2>/dev/null

# Remote'un kac commit onde oldugunu hesapla
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null)

if [ -n "$BEHIND" ] && [ "$BEHIND" -gt 0 ] 2>/dev/null; then
    echo ""
    echo "⚠️  UYARI: Remote'ta $BEHIND yeni commit var!"
    echo "   Bu commit'i atmadan once 'git pull --rebase' oneriliyor."
    echo "   Yine de devam ediliyor..."
    echo ""
fi

# Commit'i her durumda onayla
exit 0
