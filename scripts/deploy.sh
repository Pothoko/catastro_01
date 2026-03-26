#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# deploy.sh — Script de actualización Odoo Catastro en WSL
# Uso: bash /opt/catastro/deploy.sh
# Equivalente a: git push → GitHub Actions buildea → este script actualiza
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

COMPOSE_DIR="/opt/catastro"
IMAGE="ghcr.io/jpvargassoruco/catastro:latest"

echo "🔄 [$(date '+%Y-%m-%d %H:%M:%S')] Iniciando deploy de Catastro..."
cd "$COMPOSE_DIR"

# 1. Pull de la última imagen desde GHCR
echo "📦 Descargando imagen $IMAGE ..."
docker pull "$IMAGE"

# 2. Recrear el contenedor Odoo (cero downtime en DB y Traefik)
echo "🚀 Recreando contenedor Odoo..."
docker compose up -d --no-deps --force-recreate odoo

# 3. Verificar salud
echo "⏳ Esperando que Odoo esté disponible (máx 60s)..."
for i in {1..12}; do
  if curl -sf http://127.0.0.1 > /dev/null 2>&1; then
    echo "✅ Odoo disponible en http://catastro.local"
    break
  fi
  sleep 5
  echo "   ... esperando ($((i*5))s)"
done

echo ""
echo "📋 Contenedores activos:"
docker compose ps

echo ""
echo "✅ Deploy completado: $(date '+%Y-%m-%d %H:%M:%S')"
