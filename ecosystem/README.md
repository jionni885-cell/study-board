# 🧩 Écosystème complet — Study Board

> **L'écosystème « jiojio »** : l'ensemble des pièces du projet — les **agents**
> (pipeline QA), les **skills** (savoir-faire documentés), les **outils**
> (audits) et cette **carte** (`ecosystem/`). Tout est dans ce dépôt, tout est
> vérifiable, rien ne tourne sans fin.
>
> Contrôle automatique : `python3 ecosystem/check.py` (hors ligne, code de
> sortie 0 = cohérent). Ce contrôle est aussi le **pas `ecosysteme`** de
> `python3 agents/qa.py`. Carte mise à jour le **23/09/2026** (guide de réussite).

## 1. Pourquoi une carte ?

Le projet a déjà payé cher l'absence de carte : le 17/09/2026, un « swarm » de
six agents (`while True`) tournait sans s'arrêter, spammait les logs et
annonçait des serveurs « actifs » qui ne l'étaient pas. La leçon est simple :
**un écosystème doit être décrit, borné et vérifié par un code de sortie.**
C'est le rôle de ce dossier.

```
ecosystem/
├─ README.md      ← cette carte (humaine)
├─ registry.json  ← le registre (machine : interne + externe + invariants)
└─ check.py       ← le contrôle hors ligne (lancé par le pipeline QA)
```

## 2. L'écosystème interne (ce qui tourne ici)

| Pièce | Fichier | Rôle |
|---|---|---|
| Application | `index.html` | Fiches (`D`), défis (`DF6`), astuces (`EX6`), repères (`EXTRA`), audios (`AUDIOF`), exposés (`EXPOSES`), **guide de réussite** (lecture active) |
| Studio Vocal | `vocal.html` | Oral de 1 à 30 min : micro, import audio, collage de texte |
| Serveur local | `server.py` | Statique + `/api/vocal`, `/api/vocals`, `/api/health` (port 4173) |
| Pipeline QA | `agents/qa.py` | **9 pas** de contrôle finis + correcteurs bornés + `agents/rapport.json` |
| Correcteurs | `agents/fixers.py` | Corrections idempotentes (jamais de commit, jamais de push) |
| Audits | `tools/audit.py`, `audit-dom.mjs`, `audit-mobile.mjs`, `audit-complet.mjs` | Structure, navigateur simulé, vrai navigateur (5 tailles d'écran), transverse |
| Savoir-faire | `skills/` | 7 patterns documentés (audio, audit, déploiement, git, média, no-scroll, vocal long) |
| Carte | `ecosystem/` | Ce dossier |
| Mémoire | `REPRISE.md` | État réel du projet, règles, historique |

## 3. Les 5 références externes demandées (22/09/2026)

Elles sont **documentées, jamais installées** : le site reste autonome et hors
ligne, et aucune dépendance n'est téléchargée automatiquement.

| Référence | Licence | Ce qu'elle est | Ce qu'on en a gardé dans Study Board |
|---|---|---|---|
| [langgraph](https://github.com/langchain-ai/langgraph) | MIT | Orchestrateur d'agents en **graphe** (nœuds, état, transitions) | La forme « graphe borné » : un pas = un nœud, une récompense = un code de sortie (`agents/qa.py`) |
| [open-r1](https://github.com/huggingface/open-r1) | Apache-2.0 | Reproduction ouverte de DeepSeek-R1, recettes de raisonnement | Les **récompenses vérifiables** : on ne juge pas « à l'œil », on exécute (audit, `node --check`, jsdom, HTTP) |
| [trl](https://github.com/huggingface/trl) | Apache-2.0 | Entraînement par renforcement (SFT, DPO, GRPO…) | Le **budget borné** : 2 tentatives par pas, 4 corrections par exécution, puis backtracking propre |
| [dspy](https://github.com/stanfordnlp/dspy) | MIT | Programmer les modèles : modules, signatures, mesures | La discipline **signature + mesure** : `(ok, détail)`, et des mesures chiffrées au navigateur réel |
| [swarms](https://github.com/kyegomez/swarms) | Apache-2.0 | Orchestration multi-agents (rôles spécialisés) | La **séparation des rôles** (structure, syntaxe, sécurité, DOM, serveur, téléphone, git) — mais dans **un seul processus fini**, sans `while True` |

> ⚠️ `langgraph-api` (le serveur d'agent) est sous **Elastic License 2.0** :
> seule la bibliothèque `langgraph` est sous MIT. Comme rien n'est installé ici,
> la question ne se pose pas — mais il faut le savoir avant de copier du code.

## 4. Les invariants (ce qui est interdit, pour toujours)

1. **Aucun processus qui ne se termine pas** — jamais de `while True`, jamais de boucle d'agent autonome.
2. **Aucun secret dans le dépôt** — `token.json` reste gitignoré et local (le token publié le 17/09/2026 reste à révoquer).
3. **Aucun push automatique** — le pipeline QA ne commit ni ne pousse ; c'est la session qui décide.
4. **Rien à installer pour le site** — `index.html` et `vocal.html` fonctionnent hors ligne.
5. **Aucune dépendance téléchargée automatiquement** — les références externes sont documentées, pas importées.
6. **Toute affirmation passe par un code de sortie** — `python3 agents/qa.py` et `python3 ecosystem/check.py`.

## 5. Utilisation

```bash
python3 ecosystem/check.py            # la carte est-elle cohérente ? (hors ligne, < 1 s)
python3 ecosystem/check.py --detail   # + le détail de chaque vérification
python3 agents/qa.py                  # les 9 pas du pipeline (dont ce contrôle)
```

Le pas `ecosysteme` vérifie : registre lisible, **les 5 références présentes et
complètes**, chemins internes réels (aucun fichier fantôme), invariants
déclarés, aucun secret et aucune URL de sandbox morte dans `ecosystem/`, et
enfin que ce contrôle est bien **branché** dans le pipeline (sinon la carte se
périmerait en silence).
