# Skill: Git Auto Direct Commit (freecodecamp / paul.kinlan)

Copie du pattern open-source de manipulation de Git par l'API REST de GitHub sans clone local ni serveur intermédiaire :
`createBlob (base64) → createTree → createCommit → updateHead`.

## Problème résolu
Permet aux applications statiques servies par GitHub Pages d'écrire directement des fichiers (JSON, audios WebM/M4A) dans le dépôt GitHub sans passer par un serveur intermédiaire vulnérable aux déconnexions.

## Séquence des appels
1. `GET /git/refs/heads/{branch}` : récupère le SHA du dernier commit.
2. `GET /git/commits/{commitSha}` : récupère le SHA de l'arbre (`tree.sha`).
3. `POST /git/blobs` : crée les blobs avec `encoding: "base64"`.
4. `POST /git/trees` : crée l'arbre avec `base_tree: treeSha` et les blobs.
5. `POST /git/commits` : crée le commit avec le message et `parents: [commitSha]`.
6. `PATCH /git/refs/heads/{branch}` : met à jour la référence de la branche.
