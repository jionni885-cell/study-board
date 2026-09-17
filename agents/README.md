# Agents QA — Study Board

3 agents indépendants qui tournent en boucle, critiquent sans arrêt et loguent.

- **agent-vocal** : teste `vocal.html` (timer 30min, paliers, hesRatio, audio 30Mo, GO push, no-scroll, restart choix, vu-mètre, fallback)
- **agent-fiches** : teste `index.html` (6 fiches, 3 blocs <script>, render, audit 0, nav)
- **agent-infra** : teste `server.py` (4173 health, Permissions-Policy, CORS, 30Mo, git push) + Pages `built`

Logs : `agents/critiques.log` (append) + `agents/status.json`

Lancer : `bash agents/runner.sh` ou `python3 agents/agent-qa.py`
