# Skill: Audit (tools/audit-complet.mjs + tools/audit.py)

Vérification stricte de non-régression avant tout push :
`0 erreurs, 0 avertissements`.

## Outils d'audit
1. `tools/audit.py --fix-zip` : vérifie la cohérence des fiches (6 fiches, 6 défis, 6 astuces, 6 audios) et maintient l'archive `StudyBoard-app.zip` synchronisée avec le dépôt.
2. `tools/audit-complet.mjs` : vérifie `index.html`, `vocal.html`, `server.py`, `token.json`, les headers, les timers 30 min, les fallbacks, le token base64, etc.

## Règle d'or
Avant TOUT `git commit` ou `git push`, exécuter systématiquement :
```bash
python3 tools/audit.py --fix-zip && node tools/audit-complet.mjs
```
Aucun avertissement ni aucune erreur ne doivent subsister.
