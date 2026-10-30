#!/bin/bash
# Crée l'empreinte du mot de passe HTTP (utilisateur « mathieu ») pour la communauté wow4ever.
# Le mot de passe est saisi sans écho (deux fois) et n'est jamais affiché ni stocké en clair.
set -euo pipefail
F="${W5_ROOT:-}/root/wow4ever-basicauth.hash"
CADDY="${W5_CADDY:-caddy}"
command -v "$CADDY" >/dev/null || { echo "ERREUR: caddy introuvable." >&2; exit 1; }
echo "Utilisateur : mathieu. Choisir un mot de passe simple à taper (minuscules + chiffres, clavier QWERTY/AZERTY)."
umask 077
H=$("$CADDY" hash-password) || { echo "ERREUR: les deux saisies ne correspondent pas. Relancer." >&2; exit 1; }
case "$H" in '$2'?'$'*|'$argon2'*) ;; *) echo "ERREUR: empreinte inattendue." >&2; exit 1;; esac
mkdir -p "$(dirname "$F")"
printf '%s\n' "$H" > "$F.tmp" && chmod 600 "$F.tmp" && mv -f "$F.tmp" "$F"
echo "OK: empreinte enregistrée dans $F (0600). Mot de passe non affiché."
