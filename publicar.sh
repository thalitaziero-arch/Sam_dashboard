#!/bin/bash
# Publica a atualizacao semanal do dashboard da Sam.
# Uso: ./publicar.sh  (pega automaticamente o ultimo tzr_sam_dashboard.html baixado em ~/Downloads)
#      ./publicar.sh /caminho/para/arquivo.html  (usa um arquivo especifico)
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$REPO_DIR/tzr_sam_dashboard.html"

if [ -n "$1" ]; then
  SRC="$1"
else
  SRC=$(ls -t ~/Downloads/tzr_sam_dashboard*.html 2>/dev/null | head -n 1)
fi

if [ -z "$SRC" ] || [ ! -f "$SRC" ]; then
  echo "Nao encontrei o arquivo baixado. Baixe primeiro pelo botao 'Download updated file to send Sam' no painel do coach,"
  echo "ou rode: ./publicar.sh /caminho/do/arquivo.html"
  exit 1
fi

echo "Usando arquivo: $SRC"
cp "$SRC" "$DEST"

cd "$REPO_DIR"
git add tzr_sam_dashboard.html
if git diff --cached --quiet; then
  echo "Nada novo para publicar (o arquivo e igual ao que ja esta no repositorio)."
  exit 0
fi

git commit -m "Update dashboard - $(date +%Y-%m-%d)"
git push origin main

echo "Publicado! O Streamlit Cloud vai atualizar o site em 1-2 minutos."
