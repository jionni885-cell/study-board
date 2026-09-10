# PROMPT DE REPRISE — STUDY BOARD

> Document de mémoire permanente du dépôt. À lire avant toute modification.
> Dernière mise à jour : **10 septembre 2026**.

## 🎯 Mission

Tu reprends le projet **STUDY BOARD**, le site personnel de révision d'un élève
de Terminale. Tout le site et toutes les réponses à l'utilisateur sont en
français.

- Dépôt GitHub : <https://github.com/jionni885-cell/study-board>
- Site en ligne : <https://jionni885-cell.github.io/study-board/>
- Application autonome : `index.html` contient le contenu, la logique et le CSS.
- Les cinq récapitulatifs audio publics sont dans `media/audio/*.mp3`.
- Il n'y a rien à installer.

**Ne refonds pas l'application.** Elle est volontairement monolithique et déjà
validée. Ajoute ou modifie le contenu de façon chirurgicale dans les structures
existantes, sans changer le style ni réécrire le moteur lorsque ce n'est pas
nécessaire.

## 📁 Documents du jour

Les documents du jour prévus par la session de reprise sont :

1. **« Ses 3.m4a »** : suite du cours de SES, à transcrire et intégrer dans la
   fiche SES existante `0-0`.
2. **« Philosophie 1 début.m4a »** : nouvelle matière Philosophie à créer à
   l'index `4`, avec sa fiche `4-0`.
3. **Six photos de cours du jour** : à lire avec soin et à intégrer dans les
   fiches correspondantes.
4. Si les fichiers ne sont pas accessibles dans Drive ou dans le sandbox,
   demander à l'utilisateur de les joindre en pièces jointes.

À la date de ce document, ces fichiers sources ne sont **pas présents dans le
checkout**. Les captures d'écran du prompt ne remplacent ni les vocaux ni les
photos. Il est donc interdit d'inventer leur contenu : demander les fichiers
avant de créer la fiche Philosophie ou de compléter les cours concernés.

**Important : ne jamais ajouter les fichiers `.m4a` au dépôt public.** Ils
restent privés. Les lecteurs de prise de notes originale doivent disparaître
automatiquement si le fichier local correspondant est absent.

## 📚 État actuel du site

Les données vivent dans `const D` dans `index.html`.

| Index | Matière / fiche | Parties | Définitions | Mot pour mot | Cartes | Quiz | MP3 |
|---|---|---:|---:|---:|---:|---:|---|
| 0-0 | SES — Les sources et les défis de la croissance économique | 5 | 9 | 8 | 16 | 16 | `ses-croissance` |
| 1-0 | HGGSP — Faire la guerre, faire la paix : conflits et modes de résolution | 4 | 3 | 3 | 12 | 10 | `hggsp-guerre` |
| 1-1 | HGGSP — Cartographier les guerres et les conflits : limites et enjeux | 3 | 0 | 0 | 6 | 4 | `hggsp-cartographier` |
| 2-0 | Histoire — La crise de 1929 : le krach boursier et ses mécanismes | 6 | 3 | 3 | 11 | 10 | `histoire-1929` |
| 3-0 | Anglais — Heroes & superheroes : vocabulary + Story vs History | 5 | 4 | 0 | 19 | 10 | `anglais-heroes` |

**Totaux : 4 matières, 5 fiches, 23 parties, 64 cartes, 50 questions et
5 fichiers MP3.**

La matière Philosophie n'est pas encore créée : elle attend le fichier source.

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

## 🕘 Historique des mises à jour

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
