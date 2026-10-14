#!/usr/bin/env bash
# Usage : scripts/sauvegarde.sh "message de commit"
set -euo pipefail
cd "$(dirname "$0")/.."
msg="${1:-Sauvegarde $(date '+%F %H:%M')}"
if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  echo "ERREUR : .env est suivi par git. Lance : git rm --cached .env"; exit 1
fi
git add -A
git diff --cached --quiet && { echo "Rien à sauvegarder."; exit 0; }
git commit -m "$msg"
git push
