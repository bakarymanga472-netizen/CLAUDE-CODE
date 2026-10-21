#!/usr/bin/env bash
# Vérifie que les 11 skills trader-* n'ont pas été modifiés depuis leur relecture
# (source : dan-ai-lab/day-trader-fr, commit 756e4f5, fork MIT de Jakeschincariol/day-trader-skill).
# Usage : scripts/verifier-trader-skills.sh   → code 0 si intact, 1 sinon.
set -euo pipefail
racine="$(cd "$(dirname "$0")/.." && pwd)"
cd "$racine/.claude/skills"

attendus=11
presents=$(ls -d trader-*/ 2>/dev/null | wc -l)
if [ "$presents" -ne "$attendus" ]; then
  echo "ÉCHEC : $presents skills trader-* trouvés, $attendus attendus." >&2
  exit 1
fi

if sha256sum --quiet -c "$racine/scripts/trader-skills.sha256"; then
  echo "OK : 11 skills trader-* intacts."
else
  echo "ÉCHEC : fichiers modifiés depuis la relecture. Relis le diff avant usage." >&2
  exit 1
fi

# Tout fichier ajouté non relu est suspect.
nouveaux=$(comm -13 <(awk '{print $2}' "$racine/scripts/trader-skills.sha256" | sort) \
                    <(find trader-* -type f ! -name '*.pyc' ! -path '*/__pycache__/*' | sort))
if [ -n "$nouveaux" ]; then
  echo "ÉCHEC : fichiers non relus ajoutés :" >&2
  echo "$nouveaux" >&2
  exit 1
fi
