#!/bin/bash
# Agent fiches — teste index.html + audit
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
while true; do
  echo "[fiches-agent] $(date) test fiches..."
  python3 "$ROOT/tools/audit.py" 2>&1 | head -n 20
  grep -q "Studio Vocal" "$ROOT/index.html" || echo "CRITIQUE index CTA manquant"
  cnt=$(grep -c "<script>" "$ROOT/index.html"); [ "$cnt" = "3" ] || echo "CRITIQUE index 3 scripts attendu, got $cnt"
  sleep 60
done
