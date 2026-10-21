#!/usr/bin/env bash
# Installe les 5 outils du reel sur TA machine (niveau utilisateur, tous projets).
# Usage : scripts/installer-plugins.sh
#   1. OmniRoute          (passerelle multi-fournisseurs, utilisée seulement via `omniroute run claude`)
#   2. claude-mem         (plugin, mémoire entre sessions)
#   3. Headroom           (proxy de compression, utilisé seulement via `headroom wrap claude`)
#   4. claude-code-setup  (plugin officiel Anthropic)
#   5. task-observer      (skill)
set -euo pipefail
cd "$(dirname "$0")/.."
command -v claude >/dev/null || { echo "Claude Code introuvable (commande 'claude')."; exit 1; }
command -v npm >/dev/null || { echo "npm introuvable : installe Node.js 20+ (https://nodejs.org)."; exit 1; }
node_major=$(node -v | sed 's/^v//;s/\..*//')
[ "$node_major" -ge 20 ] || { echo "Node.js 20+ requis (trouvé : $(node -v))."; exit 1; }

echo "== 1/5 OmniRoute"
npm install -g omniroute

echo "== 2/5 claude-mem"
claude plugin marketplace add thedotmack/claude-mem || true
claude plugin install claude-mem@thedotmack

echo "== 3/5 Headroom"
if command -v pipx >/dev/null; then pipx install "headroom-ai[all]"
elif command -v pip3 >/dev/null; then pip3 install --user "headroom-ai[all]"
else echo "Python/pip introuvable : Headroom ignoré (installe Python 3 puis relance)."; fi

echo "== 4/5 claude-code-setup"
claude plugin marketplace add anthropics/claude-plugins-official || true
claude plugin install claude-code-setup@claude-plugins-official

echo "== 5/5 task-observer"
mkdir -p "$HOME/.claude/skills"
cp -r .claude/skills/task-observer "$HOME/.claude/skills/"

cat <<'MSG'

Terminé. Redémarre Claude Code.
- Claude normal (recommandé pour ton vrai travail) : claude
- Avec OmniRoute : lance `omniroute` (tableau de bord http://localhost:20128),
  connecte tes fournisseurs, puis : omniroute run claude
- Avec Headroom : headroom wrap claude
Détails et risques : workflows/plugins.md
MSG
