#!/bin/bash
#
# ReYMeN Hook Kurulum Scripti
# Kullanim: bash scripts/install-hooks.sh
#
# .git/hooks/pre-commit dosyasini proje kokunden kopyalar
# ve calistirilabilir yapar.
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJE_KOKU="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOK_KAYNAK="$PROJE_KOKU/scripts/pre-commit.sh"
HOOK_HEDEF="$PROJE_KOKU/.git/hooks/pre-commit"

# Oncelikle scripts/ altindaki kaynak dosyayi kontrol et
if [ ! -f "$HOOK_KAYNAK" ]; then
    echo "[!!] $HOOK_KAYNAK bulunamadi!"
    echo "    scripts/pre-commit.sh dosyasinin mevcut oldugundan emin olun."
    exit 1
fi

# .git/hooks/ var mi?
if [ ! -d "$PROJE_KOKU/.git/hooks" ]; then
    echo "[!!] .git/hooks/ klasoru bulunamadi!"
    echo "    Bu bir Git reposu degil veya .git/ eksik."
    exit 1
fi

cp "$HOOK_KAYNAK" "$HOOK_HEDEF"
chmod +x "$HOOK_HEDEF"

echo "[OK] Pre-commit hook kuruldu: $HOOK_HEDEF"
echo "    Her commit oncesi 'git fetch origin' calisir."
echo "    Remote'ta yeni commit varsa uyari basar, commit engellenmez."
