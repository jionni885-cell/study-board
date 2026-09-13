# PROMPT DE REPRISE — STUDY BOARD

> Document de mémoire permanente du dépôt. À lire avant toute modification.
> Dernière mise à jour : **13 septembre 2026 (PR #6)**.

## 🎯 Mission

Tu reprends le projet **STUDY BOARD**, le site personnel de révision d'un élève
de Terminale. Tout le site et toutes les réponses à l'utilisateur sont en
français.

- Dépôt GitHub : <https://github.com/jionni885-cell/study-board>
- Site en ligne : <https://jionni885-cell.github.io/study-board/>
- Application autonome : `index.html` contient le contenu, la logique et le CSS.
- Les six récapitulatifs audio publics sont dans `media/audio/*.mp3`.
- Il n'y a rien à installer.

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
| 0-0 | SES — Les sources et les défis de la croissance économique | 6 | 15 | 11 | 21 | 20 | `ses-croissance` |
| 1-0 | HGGSP — Faire la guerre, faire la paix : conflits et modes de résolution | 4 | 3 | 3 | 12 | 10 | `hggsp-guerre` |
| 1-1 | HGGSP — Cartographier les guerres et les conflits : limites et enjeux | 3 | 0 | 0 | 6 | 4 | `hggsp-cartographier` |
| 2-0 | Histoire — La crise de 1929 : le krach boursier et ses mécanismes | 6 | 3 | 3 | 11 | 10 | `histoire-1929` |
| 3-0 | Anglais — Heroes & superheroes : vocabulary + Story vs History | 5 | 4 | 0 | 19 | 10 | `anglais-heroes` |
| 4-0 | Philosophie — Qu'est-ce que la philosophie ? | 5 | 9 | 9 | 12 | 10 | `philo-intro` |

**Totaux : 5 matières, 6 fiches, 29 parties, 81 cartes, 64 questions et
6 fichiers MP3.**

La matière Philosophie est créée (index 4) à partir de l'audio « Philosophie 1
début » ; la fiche SES 0-0 est complétée (voix 3, facteurs de production,
fonction de production, croissance extensive, FBCF, règle des 70, exercices).

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

## 🧪 Audits automatiques du dépôt

Deux outils rejouent le GAUNTLET LOOP ; ils sont la référence, pas l'œil :

- `python3 tools/audit.py` — zéro dépendance : structure de `index.html` et des
  trois blocs `<script>`, syntaxe JavaScript via `node --check`, données `D`,
  `DF6`, `EX6`, `AUDIOF` (extraction puis `eval`), cohérence des `_nb`, phrases
  interdites, fichiers `.m4a` suivis par git, fichiers > 30 Mo, tables du
  `README.md` et de `REPRISE.md`, synchronisation de `StudyBoard-app.zip`.
  `python3 tools/audit.py --fix-zip` resynchronise l'archive. Code de sortie 1
  dès qu'un problème est détecté ; les formats de défi absents ne sont que des
  avertissements (chaque fiche doit garder plusieurs formats, pas les cinq).
- `cd tools && npm install && node audit-dom.mjs` — audit fonctionnel jsdom :
  joue **tous** les défis express (5 bonnes réponses + 3 erronées par fiche,
  transitions animées comprises), les 50 questions de quiz avec reprise, les
  4 modes de cartes × 2 filtres × 5 fiches, le mode Écrire, la visibilité des
  boîtes `.m4a`, puis la robustesse (8 états `localStorage` abîmés, 6 adresses
  invalides, thème). Code de sortie 1 en cas de défaut ou d'erreur JS.
- `tools/audit-workflow.yml` est le modèle de CI à copier en
  `.github/workflows/audit.yml` (une seule fois) : il exécute les deux audits à
  chaque `push` et chaque `pull request`. Le jeton GitHub App des sessions
  Arena n'a pas la permission « workflows » : créer ce fichier à la main depuis
  l'interface GitHub si besoin, sans bloquer la livraison.
- `tools/node_modules/` n'est jamais committé (`tools/.gitignore`).

Les deux audits doivent afficher **0 problème** avant toute livraison.

## 🧪 GAUNTLET LOOP — obligatoire avant livraison

Avant de livrer une modification :

- lancer `python3 tools/audit.py` puis `node tools/audit-dom.mjs` et corriger
  chaque problème jusqu'à **0 défaut** ;
- auditer la structure complète de `D`, `EXTRA`, `DF6` et `EX6` ;
- vérifier chaque type de bloc et chaque clé de fiche ;
- vérifier chaque quiz : options, index de réponse valide et explication ;
- vérifier les défis : données complètes, bonnes réponses, progression et écran
  final ;
- vérifier les quatre modes de cartes ;
- vérifier le thème clair/sombre et les petits écrans ;
- vérifier les chemins des MP3 et le masquage des `.m4a` absents ;
- vérifier la syntaxe des trois blocs `<script>` ;
- vérifier `git diff --check` ;
- synchroniser `StudyBoard-app.zip` avec `index.html`, `README.md` et `media/` ;
- corriger chaque défaut trouvé : **0 défaut exigé**.

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

## 🕘 Historique des mises à jour

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
