#!/usr/bin/env bash
# Usage : scripts/nouveau-projet.sh <nom-du-projet>
set -euo pipefail
cd "$(dirname "$0")/.."
nom="${1:?Usage: $0 <nom-du-projet>}"
[[ "$nom" =~ ^[a-z0-9][a-z0-9-]*$ ]] || { echo "Nom invalide (minuscules, chiffres, tirets)"; exit 1; }
dest="projets/$nom"
[[ -e "$dest" ]] && { echo "Le projet $nom existe déjà"; exit 1; }
mkdir -p "$dest"
date_j=$(date +%F)
sed -e "s/{{NOM}}/$nom/g" -e "s/{{DATE}}/$date_j/g" projets/_modele/contexte.md > "$dest/contexte.md"
echo "- \`projets/$nom/\` — créé le $date_j" >> cerveau/index.md
echo "Projet créé : $dest"
