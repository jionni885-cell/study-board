# Pipeline QA — Study Board (v3)

> ⚠️ **Ce qui tourne ici a remplacé le « swarm » de 2026-09-17** (hermes-builder /
> hermes-critic / hermes-fixer / hermes-meta / hermes-tester / agent-qa / agent-reflect /
> auto-fix / loop.sh). L'architecture précédente est documentée dans l'historique git
> (PR #13) et n'est **plus à relancer** : elle ne terminait jamais.

## Pourquoi le swarm a été remplacé (constats vérifiés)

1. **Boucles infinies** : six processus `while True` (5 à 20 s d'intervalle) qui ne
   s'arrêtaient jamais, spammaient les logs et consommaient la CPU sans fin.
2. **Log spam non productif** : `loop/log.md` contenait 8 fois le même « Cycle 01 —
   DONE » alors que `state.json` indiquait `cycles_run: 1` — le driver relançait le
   runner sans progression vérifiable.
3. **Promesses non vérifiables** : « serveurs actifs », « 5 agents HERMES actifs et
   autonomes » — faux dès la fin de la session, et impossible sur GitHub Pages
   (site 100 % statique).
4. **Risque d'écriture** : `auto-fix.py` et le serveur poussaient du git automatiquement
   (y compris vers `main`) à partir de processus autonomes.
5. **L'échec réel du moment** (le 401 « Gardé en local » sur téléphone) venait d'un
   token GitHub **publié dans `token.json`** — aucun agent ne pouvait le corriger ;
   seule la suppression du token public + un flux privé le pouvait. Voir REPRISE.md.

## La v2 : un pipeline fini, déterministe, vérifiable

Un seul programme, `python3 agents/qa.py`, qui ne tourne qu'une **fois** et
s'arrête (9 pas) :

| Pas | Vérification (récompense = code de sortie) |
|---|---|
| `structure` | `python3 tools/audit.py` (données, compteurs, phrases interdites, ZIP, README/REPRISE) |
| `syntaxe_js` | `node --check` sur les 3 blocs de `index.html` + 1 bloc de `vocal.html` |
| `securite` | pas de `token.json` suivi par git, pas de `.m4a` privé, pas de `ghp_…` dans un fichier suivi, pas de sandbox mort en dur, pas d'URL de token publique |
| `ecosysteme` | `python3 ecosystem/check.py` : registre de l'écosystème lisible, **5 références externes** complètes (`langgraph`, `open-r1`, `trl`, `dspy`, `swarms`), chemins internes réels, invariants déclarés, aucun secret, et ce contrôle bien branché dans le pipeline |
| `audit_complet` | `node tools/audit-complet.mjs` (0 erreur / 0 avertissement) |
| `audit_dom` | `node tools/audit-dom.mjs` (jsdom : défis, quiz, cartes, robustesse) |
| `serveur` | smoke test HTTP sur une **copie isolée** : santé, POST vocal, liste, statique, traversal refusé, 413 > 30 Mo, survie après refus |
| `mobile` | `node tools/audit-mobile.mjs` : **vrai navigateur** (Chromium), 28 écrans × 5 largeurs (320 → 768 px) — débordements, éléments hors écran, cibles tactiles, contrastes WCAG, fenêtre des défis, zoom iOS, marges d'encoche, erreurs JS, **barre d'action basse** mesurée sur chaque écran, + quiz, défi et **geste de balayage** réellement joués |
| `hygiene_git` | `git diff --check`, pas de `token.json` flottant |

Correspondance avec les techniques avancées (voir l'article « Au-delà des Loops et
des Multi-Agents ») :

- **PRM (Process-Supervised Reward Models)** : chaque pas est un point de contrôle
  de processus à lui seul — un pas rouge bloque la livraison, on ne se contente pas
  du résultat final.
- **LATS-lite (recherche bornée + backtracking)** : un pas rouge déclenche un
  correcteur idempotent (`agents/fixers.py`), puis **re-vérification** ; si le pas
  reste rouge, la correction est abandonnée et le pas passe en FAILED (budget :
  2 tentatives/pas, 4 corrections/exécution). Jamais de demi-état.
- **RLVR (récompenses vérifiables)** : le code de sortie du pipeline est 0 **si et
  seulement si** tous les pas sont verts. C'est la seule mesure de « parfait » —
  plus de note subjective.
- **Pas de swarm** : un seul processus, zéro boucle infinie, zéro push automatique,
  zéro écriture git cachée.

## Usage

```bash
python3 agents/qa.py               # tout (jsdom ~2 min + smoke test serveur)
python3 agents/qa.py --fast        # sans les pas lents
python3 agents/qa.py --no-fix      # rapport uniquement
python3 agents/qa.py --step securite
```

Rapport machine : `agents/rapport.json`. Code de sortie : 0 = livraison autorisée.

## Le pas `mobile` (navigateur réel)

Depuis le 21/09/2026, le pipeline ne se contente plus de jsdom : le site est fait
pour être lu **au pouce**. `tools/audit-mobile.mjs` ouvre `index.html` et
`vocal.html` dans Chromium en 320 / 360 / 390 / 414 / 768 px et mesure ce qu'un
œil humain verrait :

- **débordement horizontal** (la page qu'on peut tirer sur le côté) : c'est le
  défaut majeur trouvé le 21/09 — `ul.pills li` en `display:flex` élargissait un
  écran de 320 px à **808 px**, et la phrase partait en colonnes ;
- **éléments hors écran** : un élément qui dépasse est un défaut **sauf** si un
  ancêtre défile (`overflow:auto/scroll`) ou coupe un décor sans texte ;
- **cibles tactiles** : < 24 px = erreur, < 40 px = avertissement (44 px =
  seuil Apple/Google) ;
- **textes** : < 12 px = avertissement ; **contrastes** calculés avec la vraie
  luminance WCAG (transparences cumulées et `color-mix()` composées) ;
- **fenêtre des défis** : doit tenir dans l'écran, bouton fermer atteignable,
  contenu défilable ;
- **zoom iOS** : tout champ < 16 px fait zoomer la page à la saisie ;
- **encoche / barre d'accueil** : `viewport-fit=cover` sans
  `env(safe-area-inset-*)` = erreur ;
- **erreurs JavaScript** et ressources manquantes pendant la navigation
  (les `.m4a` privés, absents par conception, sont exclus) ;
- **parcours réel** : une question de quiz est répondue (l'explication doit
  s'afficher) et un défi est cliqué (l'écran doit avancer). Le nombre
  d'interactions jouées est affiché : si une vérification ne peut pas se faire,
  elle ÉCHOUE au lieu de disparaître en silence.

Navigateur : `CHROME_PATH=/chemin/chrome`, ou l'installation autonome
`npm i --no-save puppeteer-core@23 @sparticuz/chromium@131`. **Sans navigateur,
le pas est SKIP (annoncé comme tel)** : le pipeline reste livrable mais le
rapport dit explicitement que le téléphone n'a pas été vérifié — jamais de faux
vert.

## Rôle des humains (et de la session Arena)

- Le pipeline **ne commit jamais** et **ne push jamais**. Si un correcteur a fait
  `git rm --cached token.json`, la session committe.
- Un pas `syntaxe_js`, `audit_dom`, `serveur` ou `hygiene_git` en FAILED n'a pas de
  correcteur automatique : ça se corrige à la main, puis `python3 agents/qa.py`.
- CI : `.github/workflows/audit.yml` relance le pipeline à chaque push/PR
  (s'il est activé sur le dépôt).
