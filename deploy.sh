#!/bin/bash
# Deploy gastro mapy na GitHub Pages. Token číta z kanonického miesta.
set -e
TOKFILE="/home/michal/API/github.txt"
USER="mixall11"
REPO="gastro-ba-kraj"
DIR="/home/michal/gastro-ba-kraj"

[ -f "$TOKFILE" ] || { echo "CHYBA: token súbor $TOKFILE neexistuje"; exit 1; }
TOK=$(grep -oE 'ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}' "$TOKFILE" | head -1)
[ -z "$TOK" ] && TOK=$(tr -d ' \t\r\n' < "$TOKFILE")

# overenie tokenu
LOGIN=$(curl -s -H "Authorization: token $TOK" https://api.github.com/user | grep -oE '"login": *"[^"]+"' | cut -d'"' -f4)
[ -z "$LOGIN" ] && { echo "CHYBA: token neplatný (GitHub API nevrátilo login)"; exit 1; }
echo "Token OK, prihlásený ako: $LOGIN"

# 1) vytvor verejné repo (ak existuje, pokračuj)
echo "== Vytváram repo $USER/$REPO (public)…"
curl -s -H "Authorization: token $TOK" https://api.github.com/user/repos \
  -d "{\"name\":\"$REPO\",\"private\":false,\"description\":\"Interaktivna mapa tackarni a vyvarovni v Bratislavskom kraji\",\"homepage\":\"https://$USER.github.io/$REPO/\"}" \
  | grep -oE '"full_name": *"[^"]+"|"message": *"[^"]+"' | head -2

# ak repo je private (existovalo), prepni na public
curl -s -X PATCH -H "Authorization: token $TOK" \
  https://api.github.com/repos/$USER/$REPO -d '{"private":false}' >/dev/null || true

# 2) push
echo "== Push…"
cd "$DIR"
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$USER/$REPO.git"
git branch -M main
git -c credential.helper="!f(){ echo username=x-access-token; echo password=$TOK; };f" push -u origin main

# 3) zapni Pages (main / root)
echo "== Zapínam GitHub Pages…"
curl -s -X POST -H "Authorization: token $TOK" -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/$USER/$REPO/pages \
  -d '{"source":{"branch":"main","path":"/"}}' \
  | grep -oE '"html_url": *"[^"]+"|"message": *"[^"]+"' | head -1 || true

echo ""
echo "HOTOVO. Mapa nabehne o ~1 min na: https://$USER.github.io/$REPO/"
