#!/usr/bin/env bash
# Injecte la mémoire court terme au démarrage (stdout = contexte pour Claude).
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
if [ -f cerveau/memoire/maintenant.md ]; then
  echo "## Mémoire court terme (cerveau/memoire/maintenant.md)"
  head -n 40 cerveau/memoire/maintenant.md
fi
echo "## Projets"
ls -1 projets 2>/dev/null | grep -v '^_' | sed 's/^/- /'
if [ -x scripts/verifier-trader-skills.sh ] && ! scripts/verifier-trader-skills.sh >/dev/null 2>&1; then
  echo "## ⚠️ Skills trader-* modifiés ou incomplets : lancer scripts/verifier-trader-skills.sh et ne pas les utiliser avant relecture."
fi
exit 0
