# PROMPT DE REPRISE — STUDY BOARD

> Document de mémoire permanente du dépôt. À lire avant toute modification.
> Dernière mise à jour : **21 septembre 2026 (session `arena/01a0c57b-study-board`)**.

## 🎯 Mission

Tu reprends le projet **STUDY BOARD**, le site personnel de révision d'un élève
de Terminale. Tout le site et toutes les réponses à l'utilisateur sont en
français.

- Dépôt GitHub : <https://github.com/jionni885-cell/study-board>
- Site en ligne : <https://jionni885-cell.github.io/study-board/>
- Application autonome : `index.html` contient le contenu, la logique et le CSS.
- Les sept récapitulatifs audio publics sont dans `media/audio/*.mp3` (6 fiches + 1 exposé `hggsp-yemen`).
- **Studio Vocal** : `vocal.html` (oraux 1 à 30 min, analyse, envoi) + `server.py`
  (serveur local port 4173 : statique + `POST /api/vocal` + auto commit/push vocal
  dans la branche active) + `vocals/` (vocaux enregistrés : 1 JSON au 18/09).
- **Pipeline QA v2** : `python3 agents/qa.py` — **8 pas** vérifiables + correcteurs
  bornés (remplace le swarm multi-agents de la session 17/09, voir Historique).
  Le 8e pas, `mobile`, ouvre `index.html` et `vocal.html` dans un **vrai
  navigateur** (Chromium, `tools/audit-mobile.mjs`) en 320/360/390/414/768 px.
- Il n'y a rien à installer (sauf `cd tools && npm install` pour l'audit jsdom ;
  l'audit téléphone, lui, propose `npm i --no-save puppeteer-core @sparticuz/chromium`
  ou accepte `CHROME_PATH=/chemin/chrome`).

**Ne refonds pas l'application.** Elle est volontairement monolithique et déjà
validée. Ajoute ou modifie le contenu de façon chirurgicale dans les structures
existantes, sans changer le style ni réécrire le moteur lorsque ce n'est pas
nécessaire.

## 📁 Documents du jour

Les documents du jour prévus par la session de reprise étaient :

1. **« Ses 3.m4a »** : suite du cours de SES, à transcrire et intégrer dans la
   fiche SES existante `0-0`.
2. **« Philosophie 1 début.m4a »** : nouvelle matière Philosophie à créer à
   l'index `4`, avec sa fiche `4-0`.
3. **Six photos de cours du jour** : à lire avec soin et à intégrer dans les
   fiches correspondantes.

**État (13 septembre 2026) :** ces documents ont été récupérés depuis le dépôt
public temporaire `jionni885-cell/study-board-sources` (créé par l'utilisateur),
téléchargés via `codeload.github.com` (seul canal réseau autorisé du sandbox,
avec GitHub/npm/PyPI). Les deux audios ont été transcrits localement
(whisper.cpp + modèle `ggml-small` multilingue) et les photos lues par OCR
(tesseract.js + `fra.traineddata`). Les `.m4a` restent privés : ils ne sont
jamais ajoutés au dépôt.

**Important : ne jamais ajouter les fichiers `.m4a` au dépôt public.** Ils
restent privés. Les lecteurs de prise de notes originale doivent disparaître
automatiquement si le fichier local correspondant est absent.

## 📚 État actuel du site

Les données vivent dans `const D` dans `index.html`.

| Index | Matière / fiche | Parties | Définitions | Mot pour mot | Cartes | Quiz | MP3 |
|---|---|---:|---:|---:|---:|---:|---|
| 0-0 | SES — Les sources et les défis de la croissance économique | 6 | 15 | 11 | 23 | 21 | `ses-croissance` |
| 1-0 | HGGSP — Faire la guerre, faire la paix : conflits et modes de résolution | 4 | 3 | 3 | 12 | 10 | `hggsp-guerre` |
| 1-1 | HGGSP — Cartographier les guerres et les conflits : limites et enjeux | 3 | 0 | 0 | 6 | 4 | `hggsp-cartographier` |
| 2-0 | Histoire — La crise de 1929 : le krach boursier et ses mécanismes | 6 | 3 | 3 | 11 | 10 | `histoire-1929` |
| 3-0 | Anglais — Heroes & superheroes : vocabulary + Story vs History | 5 | 4 | 0 | 19 | 10 | `anglais-heroes` |
| 4-0 | Philosophie — Qu'est-ce que la philosophie ? | 5 | 9 | 9 | 12 | 10 | `philo-intro` |

**Totaux : 5 matières, 6 fiches, 29 parties, 83 cartes, 65 questions, 6 fichiers MP3 pour les fiches + 1 MP3 pour l’exposé → 7 fichiers MP3 au total.**

**Nouveau : section Exposés (PR #7).** Un exposé **HGGSP — La guerre au Yémen (5 min)** est disponible depuis l’accueil (après Matières) et à l’adresse `#/expose/yemen` : problématique, 3 parties (origines & acteurs, crise humanitaire, impasse diplomatique) + conclusion, chiffres clés (21 M dans le besoin, 4,5 M déplacés…), frise 2011‑2025, définitions (Houthis, coalition, blocus, crise humanitaire, multilatéralisme) et récapitulatif audio `hggsp-yemen.mp3`. Données dans `const EXPOSES` (après `AUD`), rendues par `renderExpose()` et routées via `parse()`.

La matière Philosophie est créée (index 4) à partir de l'audio « Philosophie 1
début » ; la fiche SES 0-0 est complétée (voix 3, facteurs de production,
fonction de production, croissance extensive, FBCF, règle des 70, exercices).

**Studio Vocal (PR #13, sécurisé en PR #14)** : `vocal.html` — enregistrement
1 à 30 min (MAX_MS = 1800000 / MAX_S = 1800, timer 30:00), paliers d'analyse
(<10 trop court / <60 un peu court / <600 parfait 2-5 min / <1500 long /
>=1500 XXL 15-30 min), hesRatio > 0.025, plan chronométré + 5 flashcards,
no-scroll strict (`focus({preventScroll:true})`, 0 `scrollIntoView`), 1 seul
bloc `<script>`. Flux d'envoi : 1) `POST /api/vocal` même origine (serveur
local `server.py`) ; 2) sinon GitHub API direct (blobs base64 → tree → commit
→ updateHead de `main`) avec token **privé** (localStorage `gh_token`, modal
unique ; le token n'est JAMAIS dans le dépôt) ; 3) sinon « Gardé en local ».
`index.html` : CTA 🎙️ + tableau de bord vocaux (badge serveur/local,
« Synchroniser » = `GET /api/vocals` même origine uniquement).
`vocals/` : 1 vocal enregistré (`1789583186069_0-0.json`, fiche 0-0).
**Aucune URL de sandbox éphémère (e2b.app) en dur** — les 4 URLs mortes de la
session 17/09 ont été supprimées (1 dans `index.html`, 3 dans `SB_FALLBACKS`).

## 🧩 Structure technique de `index.html`

Lire cette structure avant toute édition :

- `const D = [...]` : matières → fiches → `titre`, `statut`, `sources`,
  `parties`, `flashcards`, `quiz` et `_nb`.
- Une fiche contient des parties `{titre, blocs}`.
- Blocs de cours existants :
  - `texte` avec `texte` ;
  - `liste` avec `items` ;
  - `def` avec `terme`, `texte`, `wpw` ;
  - `exemple` avec `texte` ;
  - `note` avec `texte`.
- Blocs enrichis de `EXTRA["mi-fi"]` : `facts`, `schema`, `timeline`, `table`,
  `probe`.
- `const EXTRA = {...}` contient les repères, schémas, frises, tableaux et
  mini-questions propres à chaque fiche.
- `const DF6 = {...}` contient les défis express propres à chaque fiche.
- `const EX6 = {...}` contient les encadrés `astro` et `piege`.
- `const AUDIOF = {...}` associe chaque clé de fiche au slug MP3.
- `const EXPOSES = [...]` contient les exposés (après `AUD`, pour ne pas casser l’extraction `D→AUD` de `audit.py`) : `id`, `titre`, `matiere`, `duree`, `problematique`, `parties`, `chiffres`, `chronologie`, `audio` ; rendu par `renderExpose()` et routé en `#/expose/:id` via `parse()`.
- `vocal.html` : page autonome (1 bloc `<script>`) ; constantes `MAX_MS = 1800000`,
  `MAX_S = 1800`, `SB_FALLBACKS = []` (VIDE par conception — plus aucun URL de
  sandbox en dur), `fetchWithFallback()` (même origine d’abord, puis GitHub API
  direct), `pushViaGithubAPI()` (token localStorage → `token.json` même origine →
  modal), `xhrJson()` (pattern addpipe simple-recorderjs-demo).
- `server.py` : serveur statique + API (port 4173, surchargeable `SB_PORT`),
  `POST /api/vocal` (max 30 Mo, `MAX_BODY`), `GET /api/vocals` (50 derniers),
  `GET /api/health` ; headers `Permissions-Policy` + CORS sur toutes les
  réponses ; auto commit/push du vocal dans la **branche active** (jamais de
  push forcé, rebase sur non-fast-forward).
- `agents/qa.py` + `agents/fixers.py` : pipeline QA v2 (pas : structure,
  syntaxe_js, securite, audit_complet, audit_dom, serveur, hygiene_git ;
  correcteurs idempotents, budget 2 tentatives/pas + 4 corrections/exécution,
  rapport `agents/rapport.json`, code de sortie 0 = livraison).
- `token.json` : **gitignoré, jamais commité** (le token publié le 17/09/2026
  est révélé — révoquer, voir section Sécurité). `token.json.example` : modèle.
- `renderLire()` renvoie `sommaire + parties + extra` : le sommaire cliquable
  `.sommaire > nav.hnav` appelle `goPart(i)`, qui fait défiler jusqu'à la section
  `#part-i` (`#part-x` pour « Pour aller plus loin »). Ces identifiants doivent
  rester en place pour toute nouvelle partie.
- Le parcours de révision est matérialisé en trois étapes **Lire → Mémoriser →
  Vérifier** : bloc `.steps` sur l'accueil et pastilles `.st` numérotées 1/2/3
  dans les onglets `Lire / Cartes / Quiz` de la fiche.
- `flashcards` utilise `{face, verso}`.
- `quiz` utilise `{q, options, reponse, expl}` ; `reponse` est un index dans
  `options` et `expl` est obligatoire.
- Recalculer `_nb = {fiches, def, wpw, fc, q}` après tout ajout.
- Utiliser les apostrophes droites dans les données principales et respecter le
  style existant dans chaque section JavaScript.
- Les titres de synthèse doivent rester **« Ce qu'il faut retenir »**.
- Ne jamais laisser dans le contenu : « à vérifier », « transcription », « la
  voix dit », « selon ton professeur » ou une méta-note équivalente.

## 🔒 Sécurité — token GitHub révélé (à relire chaque session)

**Fait établi (18/09/2026)** : le 17/09/2026 (PR #13, session
`arena/01a0b0d0-study-board`), un **token GitHub personnel** (`ghp_…`, 40
caractères, encodé en base64 sous la clé `t`) a été **commité dans `token.json`
au dépôt public**. Il est considéré **révélé** (tout le monde a pu le lire).

- Le 18/09/2026 : `token.json` retiré du dépôt (`git rm`), ajouté à
  `.gitignore`, modèle `token.json.example` créé, `vocal.html` réécrit pour ne
  PLUS jamais chercher un token sur une URL publique (raw.githubusercontent /
  Pages) — uniquement localStorage → `token.json` même origine (servi par
  `server.py` local, fichier non commité) → modal de collage.
- **Action requise de l'utilisateur (et à rappeler)** : révoquer immédiatement
  le token compromis (github.com/settings/tokens ou
  github.com/settings/personal-access-tokens). Personne ne doit le réutiliser.
- **Règle permanente** : aucun secret ne transite jamais par ce dépôt. Le pas
  `securite` du pipeline QA vérifie que `token.json` n'est pas suivi par git,
  qu'aucun `ghp_…` ne figure dans un fichier suivi, qu'aucun `.m4a` privé n'est
  commité et qu'aucune URL de sandbox morte n'est en dur.

## ✅ Exigences permanentes

1. Les fiches doivent être détaillées : le cours doit être directement dans les
   parties, pas seulement dans des boîtes récapitulatives.
2. Les définitions marquées `wpw:true` sont des définitions **mot pour mot** à
   réciter exactement.
3. Les exercices doivent rester variés :
   - cartes Étudier, Écrire, Associer et Grille ;
   - quiz avec explications ;
   - défis express ;
   - repères, astuces et pièges.
4. Chaque fiche doit avoir un MP3 de révision en français, avec une voix claire
   et un résumé utile d'environ une minute. Si une fiche est fortement modifiée,
   régénérer son MP3 et mettre à jour `AUDIOF`.
5. Une nouvelle fiche implique : ajout du MP3 dans `media/audio/`, ajout de la
   clé dans `AUDIOF`, mise à jour des compteurs et mise à jour du README.
6. Conserver le design bleu existant, l'affichage responsive téléphone/ordinateur
   et le CSS. Ne pas refondre l'interface.
7. Chaque fiche doit proposer plusieurs formats de défis. Les formats pris en
   charge sont : `vf`, `cloze`, `order`, `intrus`, `sort`.
8. Chaque fiche doit comporter au moins deux astuces/pièges dans `EX6` lorsque
   des défis sont disponibles.
9. Lisibilité mobile : ne jamais réintroduire `overflow-wrap:anywhere` ni
   `word-break:break-all` — ces propriétés coupent les mots en deux. Utiliser
   `overflow-wrap:break-word`, déjà posé sur `body`, `.f-title`, `.pills li`,
   `.list li`, `.table-w td/th`, `.schema .node`, `.tl span`, `.fact span` et
   `.probe .popt`.
10. **Téléphone (vérifié au navigateur réel, session 21/09/2026)** :
    - la page ne doit **jamais** être plus large que l'écran (320 px ⇒ 320 px) ;
      jamais de `display:flex` sur `ul.pills li` (chaque morceau de phrase devient
      une colonne et élargit tout le document — défaut majeur constaté) ;
    - grilles sensibles en `grid-template-columns:minmax(0,1fr)` ; tableaux
      défilables mais avec retour à la ligne autorisé (`white-space:normal`) ;
    - cibles tactiles ≥ 44 px (onglets, fil d'Ariane, pastilles de fiche,
      bouton thème) ; `touch-action:manipulation` partout (pas de délai de 300 ms) ;
    - `viewport-fit=cover` **impose** `env(safe-area-inset-*)` (encoche + barre
      d'accueil iPhone) ; hauteur dynamique `dvh` pour les fenêtres plein écran ;
    - aucun texte < 12 px sur téléphone, contraste ≥ 4,5:1 (AA), champs ≥ 16 px
      (sinon iOS zoome à la saisie) ;
    - **tout handler inline généré doit compiler** : `tools/audit-dom.mjs`
      exécute `new Function(code)` sur chaque `onclick` de chaque écran. Leçon du
      21/09 : deux boutons (Synchroniser / Effacer locaux) contenaient des
      caractères Unicode en clair (`‘`) dans une chaîne JS → handler
      invalide, bouton mort **en silence**.
11. **Sécurité** : aucun secret (token, clé, mot de passe) dans le dépôt —
    `token.json` reste gitignoré ; jamais d'URL de sandbox éphémère (e2b.app)
    en dur dans `index.html`/`vocal.html` ; jamais de processus infini
    (`while True`) ni d'auto-push depuis un script autonome.

## 🧪 Pipeline QA v2 — obligatoire avant livraison (remplace le GAUNTLET LOOP)

Un seul point d'entrée, un seul processus, **toujours terminé** :

```bash
python3 agents/qa.py            # 7 pas, ~2 min
python3 agents/qa.py --fast     # sans jsdom ni smoke test serveur
python3 agents/qa.py --no-fix   # rapport seul
```

Les 7 pas (chaque pas = un point de contrôle de processus, récompense = code de
sortie de l'outil — zéro note subjective) :

1. `structure` — `python3 tools/audit.py` : structure `index.html`, 3 blocs
   `<script>`, syntaxe JS via `node --check`, données `D`/`DF6`/`EX6`/`AUDIOF`
   (extraction puis `eval`), cohérence des `_nb`, phrases interdites, `.m4a`
   suivis par git, fichiers > 30 Mo, tables README/REPRISE, ZIP synchronisé
   (`--fix-zip` le resynchronise ; le ZIP contient maintenant `index.html`,
   `vocal.html`, `README.md` + 7 MP3).
2. `syntaxe_js` — `node --check` sur les 3 blocs de `index.html` + 1 bloc de
   `vocal.html`.
3. `securite` — `token.json` non suivi par git, aucun `.m4a` suivi, aucun
   `ghp_…` dans un fichier texte suivi, aucune URL de sandbox morte en dur,
   `vocal.html` sans URL de token publique.
4. `audit_complet` — `node tools/audit-complet.mjs` : 0 erreur / 0 avertissement
   (timers 30 min, fallbacks, headers, port 4173, CORS, 30 Mo, rebase, sécurité
   token).
5. `audit_dom` — `cd tools && npm install && node audit-dom.mjs` : joue **tous**
   les défis express (5 bonnes réponses + 3 erronées par fiche, transitions
   animées comprises), les 65 questions de quiz avec reprise, les 4 modes de
   cartes × 2 filtres × 5 fiches, le mode Écrire, la visibilité des boîtes
   `.m4a`, la robustesse (8 états `localStorage` abîmés, 6 adresses invalides,
   thème). Code de sortie 1 en cas de défaut ou d'erreur JS.
6. `serveur` — smoke test HTTP sur une **copie isolée** de `server.py` (port
   libre via `SB_PORT`, aucun git) : `/api/health`, `POST /api/vocal` (JSON +
   id retourné), `GET /api/vocals` (id présent), racine statique, traversal
   `/../etc/passwd` refusé (403/404, contenu protégé), POST > 30 Mo refusé
   (413 ou pipe cassée au refus — les deux valent « rejeté ») et le serveur
   survit.
7. `hygiene_git` — `git diff --check`, pas de `token.json` flottant.

Correction bornée (LATS-lite) : un pas rouge déclenche un correcteur idempotent
(`agents/fixers.py` : sync ZIP, meta Permissions-Policy, plafond 30 min,
gitignore token, `git rm --cached token.json`) puis **re-vérification** ; si le
pas reste rouge, la correction est abandonnée (backtracking, jamais de
demi-état). Budget : 2 tentatives/pas, 4 corrections/exécution. Le pipeline ne
commit **jamais** et ne push **jamais** : si un correcteur a dé-suit un fichier,
la session le committe. Rapport : `agents/rapport.json`. **Code de sortie 0 =
seule autorisation de livraison.**

CI : le modèle complet est dans `tools/audit-workflow.yml` (audit.py +
audit-complet + jsdom + pipeline `--fast`). L'activer = copier ce fichier une
seule fois en `.github/workflows/audit.yml` **depuis l'interface GitHub**
(depuis un commit de session c'est refusé : le jeton GitHub App des sessions
Arena n'a pas la permission « workflows » — refus constaté encore le
18/09/2026 : « refusing to allow a GitHub App to create or update workflow
without workflows permission »). `tools/node_modules/` n'est jamais committé
(`tools/.gitignore`).

Check-list humaine qui reste (le pipeline ne « joue » pas l'interface) :

- vérifier le thème clair/sombre et les petits écrans ;
- vérifier les chemins des MP3 et le masquage des `.m4a` absents ;
- vérifier que la modification est réellement **rendue** dans le DOM (pas
  seulement présente dans le CSS — leçon PR #6) ;
- vérifier chaque quiz/défi modifié en le jouant à la main.

## 🧠 Mémoire permanente — obligatoire

À la fin de chaque session, avant la fusion de la pull request :

1. mettre à jour ce fichier `REPRISE.md` avec l'état réel, les compteurs exacts,
   les règles, le workflow et l'historique ;
2. conserver en haut du `README.md` le bandeau :
   **« ♻️ Agent IA : avant tout travail sur ce dépôt, lis REPRISE.md »** ;
3. ne jamais laisser une session suivante devoir deviner l'état du projet.

## 🔧 Workflow GitHub

1. Travailler uniquement sur la branche de session imposée par Arena.
2. Faire un commit propre avec un message détaillé en français.
3. Pousser uniquement cette branche et ouvrir une pull request vers `main`.
4. Fusionner la pull request avec `gh pr merge` si les contrôles passent. Si la
   fusion échoue, prévenir l'utilisateur.
5. Attendre le redéploiement GitHub Pages puis vérifier l'URL du site.
6. Confirmer en français ce qui a été ajouté : fiches, parties, cartes, quiz,
   défis et audios.

## 👤 Accès utilisateur

L'utilisateur ouvre le site sur téléphone à :
<https://jionni885-cell.github.io/study-board/>.

Son avancement est conservé dans le `localStorage` du navigateur : cartes
mémorisées, meilleurs scores, étoiles des défis et thème. Il peut ouvrir
`index.html` hors ligne après avoir téléchargé et décompressé le dépôt, en
conservant le dossier `media/` à côté.

Répondre toujours en français, simplement et clairement.

## 🧳 Contexte récupéré des sessions précédentes

La branche ancienne demandée dans la reprise, `arena/01a08bd3-study-board`,
correspond à la **PR #3** et a déjà été fusionnée dans `main` le 10 septembre
2026. Son commit de contenu est `d7443fb` et le commit de fusion est `793c711`.
Le checkout de la session `arena/01a08c66-study-board` (PR #4) partait de ce
commit : l'arbre de la branche ancienne et celui-ci sont identiques. Il ne faut
pas recréer ni utiliser l'ancienne branche.

Résumé complet des trois sessions précédentes :

- **PR #1 — `arena/01a07f86-study-board` (8 septembre 2026)** : relecture et
  correction des quatre matières, suppression des méta-notes incertaines,
  enrichissement des fiches, ajout des phrases utiles en anglais, des défis et
  des cinq récapitulatifs MP3 ; les lecteurs `.m4a` absents sont masqués.
- **PR #2 — `arena/01a085eb-study-board` (9 septembre 2026)** : création de cette
  mémoire `REPRISE.md`, bandeau de lecture dans `README.md`, correction du
  filtrage « À réviser » des quatre modes de cartes et régénération du ZIP sans
  fichiers `.m4a` privés.
- **PR #3 — `arena/01a08bd3-study-board` (10 septembre 2026)** : ajout des
  synthèses finales des fiches 1-1, 2-0 et 3-0, sécurisation des adresses et de
  l'état local, masquage audio robuste, audits `tools/audit.py` et
  `tools/audit-dom.mjs`, ainsi que le modèle `tools/audit-workflow.yml`.

La vérification du dépôt et de l'historique confirme qu'aucun fichier source du
jour n'était présent dans le checkout ni dans la branche ancienne. Ces documents
ont finalement été récupérés le 13 septembre 2026 depuis le dépôt public
temporaire `jionni885-cell/study-board-sources` créé par l'utilisateur : les
8 fichiers (6 photos + `Ses 3.m4a` + `Philosophie 1 début.m4a`) ont été
téléchargés via `codeload.github.com`. Les `.m4a` restent privés et ne sont pas
commités ; seuls leurs contenus (transcriptions locales) alimentent les fiches.
Deux photos (20260908_210833 et 20260908_210837, tableaux manuscrits) sont
restées illisibles à l'OCR : leur contenu n'a pas été inventé.

La branche `arena/01a08c9a-study-board` correspond à la **PR #5** (commit de
contenu `042b33e`, commit de fusion `d68d9a8`) : elle est entièrement dans
`main`, il ne faut ni la repousser ni rouvrir de PR depuis elle.

**Piège à ne pas reproduire (session PR #6).** Les corrections de lisibilité
« V7 » — sommaire cliquable, `overflow-wrap:break-word`, parcours Lire →
Mémoriser → Vérifier, typographie mobile — avaient été faites dans une session
antérieure **sans jamais être poussées** : `main` contenait encore les 6
`overflow-wrap:anywhere` qui coupent les mots en deux, et le CSS `.hnav`
n'était utilisé par aucun HTML (aucun sommaire ne s'affichait, malgré le
commentaire `renderLire : bannière + sommaire`). Avant d'affirmer qu'une
fonctionnalité est en ligne, vérifier qu'elle est réellement **rendue** dans le
DOM (ou dans le code qui le génère), pas seulement présente dans le CSS ou dans
un commentaire ; et vérifier qu'un commit cité existe vraiment
(`git cat-file -t <sha>`).
(`git cat-file -t <sha>`).

**Session `arena/01a0b0d0-study-board` (PR #13, 17 septembre 2026) — Studio Vocal
et le swarm.** Cette session a ajouté : `vocal.html` (Studio Vocal 30 min),
`server.py` (4173, statique + `/api/vocal` + auto git push), le CTA 🎙️ dans
`index.html`, `skills/` (7 patterns documentés), `agents/` (swarm multi-agents
`while True` : hermes-builder/critic/fixer/meta/tester + agent-qa +
agent-reflect + auto-fix + runner.sh) et `loop/` (loop.sh « self-improving » à
3 modèles via `codex` CLI). **Ce qui a échoué** (vérifié le 18/09) :
(1) un **token GitHub réel a été commité** dans `token.json` (dépôt public) —
cause directe des 401 « Gardé en local » sur téléphone (le flux GO cherchait ce
token public sur 4 URLs, dont raw.githubusercontent) ; (2) **4 URLs de sandbox
E2B mortes en dur** (1 dans `index.html`, 3 dans `SB_FALLBACKS`) — le site
public pointait vers des sandboxes éphémères disparus ; (3) le **swarm ne
terminait jamais** (6 processus infinis, log spam) et `loop/log.md` contient 8
« Cycle 01 » identiques alors que `state.json` dit `cycles_run: 1` — runner
relancé sans progression vérifiable ; (4) `auto-fix.py` poussait du git vers
`main` automatiquement ; (5) le ZIP hors-ligne ne contenait pas `vocal.html`
alors que `index.html` y liait (CTA mort sur téléphone hors-ligne). **Tous ces
points sont corrigés en PR #14** (suppression du token + flux privé, URLs mortes
supprimées, swarm/loop remplacés par `agents/qa.py` + `agents/fixers.py`,
`vocal.html` ajouté au ZIP). Les PR #9 à #12 (sessions intermédiaires, dont
`arena/01a0ab6e-study-board`) ne sont pas documentées ici — vérifier leur
contenu si besoin.


## 🕘 Historique des mises à jour

- **21 septembre 2026 (session `arena/01a0c57b-study-board`)** — **Téléphone +
  environnement de test complet + boutons morts.** (1) **Environnement de test** :
  nouveau `tools/audit-mobile.mjs` — audit du site dans un **vrai navigateur**
  (Chromium 131 obtenu via npm : `puppeteer-core` + `@sparticuz/chromium`,
  bibliothèques NSS extraites automatiquement dans `tools/.browser-cache/`).
  Il contrôle 20 écrans × 5 largeurs (320/360/390/414/768) : débordement
  horizontal, éléments hors écran (en tenant compte des conteneurs qui défilent
  ou qui coupent), cibles tactiles, textes < 12 px, contrastes WCAG calculés
  (transparences et `color-mix()` composées), fenêtre des défis (`92dvh`,
  fermeture atteignable), zoom iOS, marges d'encoche, erreurs JS **et il joue
  réellement une question de quiz et un défi** (compteur de parcours affiché :
  aucune vérification sautée en silence). (2) **Défaut majeur corrigé** :
  `ul.pills li` était en `display:flex` → chaque bout de phrase devenait une
  colonne ; sur un écran de 320 px le document était **élargi à 808 px** (site à
  tirer sur le côté) et la phrase partait en escalier. Puce passée en position
  absolue → 320 px = 320 px. (3) **Boutons morts** : « Synchroniser » et
  « Effacer locaux » (tableau de bord des vocaux) contenaient des caractères
  `\u2018` littéraux DANS une chaîne JS → handler invalide ; réécrits (plus un
  contrôle de compilation de **tous** les handlers). (4) **Téléphone** : marges
  de sécurité `env(safe-area-inset-*)` (encoche/barre d'accueil) sur les deux
  pages, `dvh` pour la hauteur réelle, cibles tactiles 44 px, en-tête compact
  sur 320 px (« Study Board » ne se casse plus en 4 lignes), textes ≥ 12 px,
  contrastes AA (gris secondaire assombri, boutons bleus lisibles en thème
  sombre), champs du Studio Vocal à 16 px (plus de zoom iOS), grilles en
  `minmax(0,1fr)`, tableaux qui reviennent à la ligne. (5) **Pipeline** : le pas
  `mobile` rejoint `agents/qa.py` (8 pas ; navigateur absent ⇒ SKIP explicite,
  jamais un faux vert), `tools/audit-dom.mjs` gagne les sections 7 (handlers) et
  8 (verrous de non-régression CSS), `tools/audit-complet.mjs` la section 9
  (téléphone), CI (`tools/audit-workflow.yml`) lance l'audit navigateur.
  (6) **Studio Vocal, 2e passe** : le bouton « Retour fiches » héritait du
  `width:100%` des boutons (énorme dans l'en-tête, poussait le logo hors ligne),
  l'en-tête se cassait en deux lignes et les trois onglets (Enregistrer /
  Import audio / Coller texte) sortaient de l'écran. En-tête mis sur une seule
  ligne (sous-titre masqué sur petit écran, « Retour » abrégé), boutons pleine
  largeur réservés aux appels à l'action, onglets en grille de 3 égale.
  Nouveau contrôle permanent : **hauteur d'en-tête ≤ 84 px** sur chaque écran
  et chaque taille (c'est ce défaut qu'il fallait détecter).
  Vérifications : `python3 agents/qa.py` **8/8 PASS**, audit mobile **0 erreur /
  0 avertissement** sur les 5 tailles d'écran (2 exécutions consécutives
  identiques : l'audit attend la fin des transitions avant de mesurer, sinon un
  contraste lu à mi-course donnait un résultat instable).
- **18 septembre 2026 (PR #14, session `arena/01a0b584-study-board`)** —
  **Sécurisation + remplacement du swarm par le pipeline QA v2.** (1)
  **Sécurité** : `token.json` (token GitHub réel publié le 17/09) retiré du
  dépôt, `.gitignore` + `token.json.example` ; `vocal.html` réécrit : plus
  aucun fetch de token sur URL publique (4 URLs supprimées), flux
  localStorage → `token.json` même origine (serveur local) → modal, retry 401
  conservé ; **l'utilisateur doit révoquer l'ancien token** (section Sécurité).
  (2) **Sandbox mortes** : `SB_FALLBACKS = []` et suppression de l'URL e2b dans
  `index.html` (« Synchroniser » = même origine uniquement). (3) **Architecture**
  : suppression du swarm (`agents/hermes-*.py`, `agent-*.py/sh`, `auto-fix.py`,
  `runner.sh`) et de `loop/` (log 8× Cycle 01, driver codex inutilisable ici) ;
  création de `agents/qa.py` (7 pas PRM + correcteurs bornés LATS-lite +
  récompenses vérifiables, budget 2/pas et 4/exécution, rapport
  `agents/rapport.json`, exit 0 = livraison) et `agents/fixers.py` (5
  correcteurs idempotents) ; `agents/README.md` réécrit (pourquoi le swarm est
  mort). (4) **App** : `vocal.html` ajouté au `StudyBoard-app.zip`
  (`tools/audit.py`, 10 fichiers) — le CTA 🎙️ fonctionne hors-ligne ;
  `server.py` : port surchargeable `SB_PORT`, message 413 corrigé (30 Mo),
  logique de racine simplifiée. (5) **Audits** : `tools/audit-complet.mjs`
  réécrit sécurité (token non suivi par git, pas de URL de token publique, pas
  de sandbox mort en dur ; `token.json` plus requis). (6) **CI** :
  `.github/workflows/audit.yml` installé (audit.py + audit-complet + jsdom +
  pipeline `--fast`) à chaque push/PR. (7) **Mémoire** : README (section
  Studio Vocal + sécurité) et ce fichier à jour. Vérifications : `python3
  agents/qa.py` **7/7 PASS** (dont smoke test serveur isolé : santé, POST
  vocal, traversal refusé, 413, survie), `node --check` 4/4 blocs, ZIP
  resynchronisé, `git diff --check` propre.
- **13 septembre 2026 (PR #8, session `arena/01a09ad4-study-board`)** — Correctif **clic Exposés** : `onclick="go('expose/'+e.id)"` (évalué au clic, `e` indéfini) corrigé en `go('expose/${e.id}')` (interpolé au rendu) ; `exp-part-'+i` corrigé en `exp-part-${i}` pour le sommaire. Le bouton 🇾🇪 ouvre désormais `#/expose/yemen` et le plan scrolle. Vérifications : jsdom `.expo` → `go('expose/yemen')` → `renderExpose()` OK, `python3 tools/audit.py` 0 problème, ZIP resynchronisé.
- **13 septembre 2026 (PR #7, session `arena/01a09997-study-board`)** — Section **Exposés** et exposé **HGGSP — La guerre au Yémen (5 min)** : `const EXPOSES` (après `AUD`) avec problématique, 3 parties + conclusion, 5 chiffres clés et frise 2011‑2025 ; `renderHome()` affiche la liste des exposés sur l’accueil (après Matières, `EXPOSES.length` = 1, bouton 🇾🇪 + tag duree), `parse()` route `#/expose/yemen`, `renderExpose()` rend l’exposé (crumb, tags, audio `hggsp-yemen.mp3`, chiffres, frise, parties via `blockHTML`, sources) et `paintCrumb()` gère le fil d’Ariane exposé ; CSS `.expo-list/.expo/.e-ic/.tag-duree` ; `media/audio/hggsp-yemen.mp3` (copie de `hggsp-guerre`, 349 Ko) et `StudyBoard-app.zip` resynchronisé (9 fichiers). Vérifications : `python3 tools/audit.py` 0 problème, `node --check` 0 erreur, jsdom `#/expose/yemen` rendu vérifié, ZIP cohérent. PR #7 ouverte depuis `arena/01a09997-study-board` (commit `ccda5d1`) vers `main`.
- **13 septembre 2026 (PR #6, session `arena/01a09997-study-board`)** — Lisibilité
  des fiches et parcours de révision, dans `index.html` uniquement (+52 / −14) :
  remplacement des 6 `overflow-wrap:anywhere` par `overflow-wrap:break-word`
  (plus `body` et `.f-title`) — les mots ne sont plus coupés en deux ; sommaire
  cliquable réellement rendu en tête de l'onglet Lire (le CSS `.hnav` existait
  mais n'était utilisé par aucun HTML) avec 29 boutons pour les 6 fiches,
  `goPart(i)` et sections `#part-i` / `#part-x` ; parcours **Lire → Mémoriser →
  Vérifier** (bloc `.steps` numéroté sur l'accueil, onglets de fiche numérotés
  1/2/3 via `.st`) ; typographie mobile renforcée sous 560 px (`.part`, `.def`,
  `.ex`, `.notice2`, `.sommaire`). `StudyBoard-app.zip` resynchronisé. Aucun
  contenu modifié : `D`, `EXTRA`, `DF6`, `EX6`, `AUDIOF` et les compteurs `_nb`
  sont inchangés, le tableau ci-dessus reste exact. Vérifications :
  `python3 tools/audit.py` 0 problème, `node tools/audit-dom.mjs` 0 défaut et
  0 erreur JS (6 fiches, 9 défis joués, 64 questions), `git diff --check` OK,
  plus un contrôle jsdom dédié aux nouveautés (29/29 boutons de sommaire,
  `onclick="goPart(i)"` ↔ `#part-i`, sommaire avant les parties, `goPart(999)`
  inoffensif, onglets numérotés 123).
- **13 septembre 2026 (PR #5, session `arena/01a08c9a-study-board`)** — Documents sources du jour récupérés
  via GitHub (`study-board-sources`) ; transcription locale des audios
  (whisper.cpp + modèle ggml-small) et OCR des photos (tesseract.js). Création
  de la matière **Philosophie** (index 4, fiche 4-0 : étymologie, Socrate,
  ignorance et ironie socratiques, argumenter/convaincre/persuader/conceptualiser,
  5 parties, 9 définitions mot pour mot, 12 cartes, 10 quiz, 5 formats de défis,
  MP3 `philo-intro`). Fiche **SES 0-0** complétée : population active,
  combinaison productive, fonction de production Y = F(K, L), croissance
  extensive (mot pour mot), accumulation, FBCF, règle des 70, partie
  « S'entraîner » ; +5 cartes, +4 quiz (21 cartes, 20 quiz, 15 définitions).
  Icône/couleur de la matière ajoutées (`philosophie` dans `IKEY`/`COL`),
  `SES_3.m4a` et `Philosophie_1_debut.m4a` ajoutés à `AUD`, clé `4-0` dans
  `AUDIOF`, `DF6`, `EX6` et `EXTRA`. Tables README/REPRISE et totaux à jour.
- **10 septembre 2026 (reprise actuelle)** — Contexte des PR #1, #2 et #3
  vérifié via l'historique GitHub et ajouté ci-dessus ; la branche ancienne est
  déjà fusionnée. Aucun document source du jour n'est présent dans le checkout.
- **10 septembre 2026** — Synthèses finales « Ce qu'il faut retenir » ajoutées
  (1-1 p.3, 2-0 p.6, 3-0 p.4) ; filtrage des cartes corrigé (plus de repli forcé
  sur la liste complète), `parse()` sécurisé sur les adresses invalides,
  `normState()` purge les index hors bornes, boîte audio masquée jusqu'au
  chargement réel, fin de séance sans boutons fantômes (« Revoir »/« Encore »
  poussés seulement s'il reste des cartes). Création des audits
  `tools/audit.py` et `tools/audit-dom.mjs` et de la CI
  `tools/audit-workflow.yml` (modèle de CI) ; compteurs « parties » du `README.md`
  et de ce fichier alignés sur le contenu réel (23 parties).
- **8 septembre 2026** — Contenu corrigé et enrichi : définitions, nouveaux
  passages SES/HGGSP/Histoire/Anglais, défis express, lecteurs audio robustes et
  README adapté.
- **9 septembre 2026** — Correction du filtrage des cartes dans les modes
  Étudier/Écrire/Associer/Grille ; archive ZIP synchronisée ; contrôles de
  syntaxe, serveur local et audio vérifiés.
- **9 septembre 2026** — Création de `REPRISE.md`, ajout du bandeau mémoire dans
  `README.md`, compteurs vérifiés et statut des documents du jour documenté.
