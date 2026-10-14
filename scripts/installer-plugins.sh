#!/usr/bin/env bash
# Installe les plugins Claude Code sur TA machine (niveau utilisateur, tous projets).
# Usage : scripts/installer-plugins.sh            → claude-mem + claude-code-setup + task-observer
#         scripts/installer-plugins.sh --headroom → ajoute Headroom (optionnel, gain faible)
set -euo pipefail
cd "$(dirname "$0")/.."
command -v claude >/dev/null || { echo "Claude Code n'est pas installé (commande 'claude' introuvable)."; exit 1; }
node_major=$(node -v 2>/dev/null | sed 's/^v//;s/\..*//' || echo 0)
[ "${node_major:-0}" -ge 20 ] || echo "Attention : claude-mem demande Node.js 20+ (trouvé : $(node -v 2>/dev/null || echo aucun))."

claude plugin marketplace add anthropics/claude-plugins-official || true
claude plugin marketplace add thedotmack/claude-mem || true
claude plugin install claude-code-setup@claude-plugins-official
claude plugin install claude-mem@thedotmack

# task-observer : skill personnelle, disponible dans tous tes projets
mkdir -p "$HOME/.claude/skills"
cp -r .claude/skills/task-observer "$HOME/.claude/skills/"
echo "task-observer copié dans ~/.claude/skills/"

if [ "${1:-}" = "--headroom" ]; then
  pip install "headroom-ai[all]"
  echo "Headroom installé. Lance Claude avec : headroom wrap claude"
fi
echo "Terminé. Redémarre Claude Code."
