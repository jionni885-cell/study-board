#!/bin/bash
# Agent vocal — tourne seul, teste vocal.html en boucle
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
while true; do
  echo "[vocal-agent] $(date) test vocal..."
  # node check
  python3 -c "import re; t=open('$ROOT/vocal.html').read(); js=re.search(r'<script>(.*?)</script>',t,re.S).group(1); open('/tmp/v.js','w').write(js)" 2>&1
  node --check /tmp/v.js 2>&1 && echo "vocal js OK" || echo "CRITIQUE vocal js FAIL"
  grep -q "MAX_MS = 1800000" "$ROOT/vocal.html" || echo "CRITIQUE vocal MAX_MS pas 30min"
  grep -q "SB_FALLBACK" "$ROOT/vocal.html" || echo "CRITIQUE vocal SB_FALLBACK manquant"
  grep -q "restartChoice" "$ROOT/vocal.html" || echo "CRITIQUE restartChoice manquant"
  sleep 60
done
