#!/bin/bash
# Lance les 3 agents indépendants
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
echo "🚀 Lancement agents QA indépendants..."
mkdir -p "$DIR/../agents"
chmod +x "$DIR/agent-qa.py" "$DIR/agent-vocal.sh" "$DIR/agent-fiches.sh" 2>/dev/null || true
# agent principal python (boucle 45s)
nohup python3 "$DIR/agent-qa.py" > "$DIR/../agents/agent-qa.log" 2>&1 &
echo "agent-qa pid $!"
# agents secondaires (optionnels)
nohup bash "$DIR/agent-vocal.sh" > "$DIR/../agents/agent-vocal.log" 2>&1 &
echo "agent-vocal pid $!"
nohup bash "$DIR/agent-fiches.sh" > "$DIR/../agents/agent-fiches.log" 2>&1 &
echo "agent-fiches pid $!"
echo "✅ Agents lancés — logs: agents/critiques.log + agents/status.json"
cat "$DIR/../agents/status.json" 2>/dev/null | head -n 30 || echo "status pas encore prêt (10s)"
