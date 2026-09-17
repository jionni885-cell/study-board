# Skill: Deploy Check (gh api pages/builds)

Surveillance et polling du statut de déploiement GitHub Pages :
Vérification que le dernier commit déployé a le statut `built`.

## Commande GitHub CLI
```bash
gh api repos/jionni885-cell/study-board/pages/builds --jq .[0].status
```

## Attente active
Lors d'un nouveau commit sur `main`, l'état passe de `queued` / `building` à `built`.
Si l'état est `errored`, l'agent notifie l'anomalie avec l'erreur retournée par l'API.
