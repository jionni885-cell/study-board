# Study Board — fiches de révision

> ♻️ **Agent IA : avant tout travail sur ce dépôt, lis [`REPRISE.md`](REPRISE.md).**

Application de révision **100 % autonome** (un seul fichier : `index.html` + dossier `media`).
SES · HGGSP · Histoire · Anglais · Philosophie — fiches de cours détaillées, cartes façon Quizlet,
mode Écrire, mode Associer, quiz, **défis express** (vrai/faux, phrases à trous,
remise en ordre, intrus, classement), **révision audio**, thème clair/sombre,
responsive mobile.

---

## ▶ Comment l'ouvrir

### Sur ton téléphone (le plus simple)
1. Télécharge ce dépôt : bouton vert **Code → Download ZIP** (ou le fichier
   `StudyBoard-app.zip`), puis décompresse-le sur ton téléphone.
2. Touche `index.html` → il s'ouvre dans ton navigateur.
   *(Sur iPhone : dans l'app « Fichiers », touche `index.html` → Partager →
   « Ouvrir dans Safari » si besoin.)*
3. Tout fonctionne hors-ligne. Garde le dossier tel quel : l'app a besoin de
   `media/` (audios) à côté d'`index.html`.

### Sur un ordinateur
Double-clique sur `index.html` (Chrome, Firefox, Safari, Edge…).

> 💡 Ton avancement (cartes mémorisées, étoiles des défis, thème) est conservé
> **localement dans le navigateur** de l'appareil où tu ouvres le fichier.

---

## 📱 Sur téléphone (vérifié au navigateur réel)

Le site est fait pour être ouvert **au pouce, sur téléphone**. Une session de
correction complète (21 septembre 2026) a mesuré le site sur un **vrai
navigateur** (Chromium) en 320, 360, 390, 414 et 768 px de large, et a corrigé
tout ce qui gênait :

| Problème constaté | Correction |
|---|---|
| La page était **élargie à 808 px** sur un écran de 320 px (il fallait tirer le site sur le côté) : les puces des listes étaient en `flex`, chaque bout de phrase devenait une colonne | Puces en position absolue : le texte reprend toute la largeur (320 px = 320 px) |
| Bouton **« Ouvrir le studio »** et **« Synchroniser »** du tableau de bord des vocaux **ne faisaient rien** (caractères Unicode en clair dans le code → script invalide) | Handlers réécrits, apostrophes échappées ; **tous** les handlers sont désormais compilés un par un à l'audit |
| Fenêtre des **défis express** plus large et plus haute que l'écran (fermeture hors champ) | Largeur/hauteur bornées (`92dvh`), marges de sécurité, tout reste atteignable |
| Contenu **sous l'encoche** et sous la barre d'accueil iPhone (`viewport-fit=cover` sans marge) | `env(safe-area-inset-*)` posés (haut, bas, gauche, droite) |
| Boutons d'**onglets** (30 px), fil d'Ariane (16 px), compteur d'onglets : trop petits pour un doigt | Cibles tactiles **44 px** (seuil Apple/Google) partout |
| **Zoom automatique iOS** dès qu'on touchait un champ du Studio Vocal (< 16 px) | Champs à 16 px minimum |
| Textes à **10,9 px** illisibles, **contrastes sous la norme** (2,6:1 au lieu de 4,5:1) | Tailles ≥ 12 px sur téléphone, gris secondaire assombri (palette AA), boutons bleus corrigés en thème sombre |
| En-tête « Study Board » qui se cassait en **4 lignes** sur 320 px | En-tête compact sur petit écran (le libellé du studio se raccourcit, le thème reste accessible) |
| Tableaux et grilles qui débordaient | Colonnes `minmax(0,1fr)`, tableaux défilables, mots longs non coupés |
| Studio Vocal : bouton « Retour fiches » énorme, en-tête sur deux lignes, les 3 onglets (Enregistrer / Import / Coller) hors écran | En-tête sur une ligne, bouton normal, onglets en grille de 3 égale |

Rien d'autre à faire de ton côté : ces corrections sont dans le site, et
l'audit `tools/audit-mobile.mjs` rejoue **20 écrans × 5 tailles** (plus une partie
de quiz et un défi réellement joués) à chaque livraison pour que ces défauts ne
reviennent jamais.

---

## 🎧 Révision audio

Sur chaque fiche, un lecteur **« Réviser en écoutant »** lance un récapitulatif
audio complet du cours, lu par une voix claire : définitions à répéter, chiffres
clés, mécanismes, pièges et mini auto-test final.

- `media/audio/ses-croissance.mp3` — La croissance économique
- `media/audio/hggsp-guerre.mp3` — Conflits et modes de résolution
- `media/audio/hggsp-cartographier.mp3` — Cartographier les guerres
- `media/audio/histoire-1929.mp3` — La crise de 1929
- `media/audio/anglais-heroes.mp3` — Heroes & superheroes (vocabulaire anglais)
- `media/audio/philo-intro.mp3` — Qu'est-ce que la philosophie ?

### Notes vocales d'origine (.m4a)
Les enregistrements d'origine (`.m4a`) **ne doivent jamais être ajoutés au dépôt**.
Le dépôt est public et ces vocaux restent privés. Les lecteurs « prise de notes
originale » se masquent automatiquement si le fichier est absent ; ils se
réactivent uniquement si l'utilisateur place localement le fichier correspondant
dans `media/`.

---

## 🎙️ Studio Vocal (oraux jusqu'à 30 min)

`vocal.html` (accessible depuis l'accueil, bouton **🎙️ Studio Vocal**) enregistre
un oral de **1 à 30 min** (micro, import audio ou texte collé), l'analyse (mots,
hésitations, plan chronométré, 5 flashcards) et l'envoie dans le dépôt.

- **Sur ordinateur** : lance `python3 server.py` (port 4173) puis ouvre
  `http://localhost:4173/vocal.html` — l'envoi passe par `POST /api/vocal` et le
  serveur committe/pousse le vocal dans ta branche active.
- **Sur téléphone (site en ligne)** : l'envoi direct dans GitHub demande **une
  seule fois** un token GitHub personnel (`ghp_…`, droit `repo`) collé dans la
  petite fenêtre du studio. Il reste **dans ton navigateur uniquement**
  (localStorage), jamais dans le dépôt.
- **Sans rien de tout ça** : le vocal est **gardé en local** dans le navigateur
  (badge 💾), il enrichit ta fiche et reste disponible dans le studio.

> 🔒 **Sécurité — lecture obligatoire (18/09/2026)** : un token GitHub a été
> **erronément publié** dans ce dépôt public le 17/09/2026 (fichier `token.json`,
> retiré le 18/09/2026). Il est considéré **révélé** :
> **révoque-le immédiatement** dans
> [github.com/settings/tokens](https://github.com/settings/tokens) (ou
> [github.com/settings/personal-access-tokens](https://github.com/settings/personal-access-tokens)
> si c'est un token granulaire). N'utilise plus ce token nulle part.
> Le fichier `token.json` est désormais ignoré par git : s'il est recréé sur ta
> machine (optionnel, via `token.json.example`), il restera local.

---

## ☁ Ce dépôt GitHub (public)

Le site en ligne est disponible à l'adresse :
<https://jionni885-cell.github.io/study-board/>.

- Pour récupérer l'app sur un nouvel appareil : ouvre le dépôt → **Code →
  Download ZIP** → décompresse → ouvre `index.html`.
- Les mises à jour (nouveaux cours, corrections) arrivent par les commits et les
  pull requests.

---

## 📚 Contenu (état au 10 septembre 2026)

| Index | Matière / fiche | Parties | Définitions (dont mot pour mot) | Cartes | Quiz | Défis |
|---|---|---:|---:|---:|---:|---:|
| 0-0 | SES — Les sources et les défis de la croissance économique | 6 | 15 (11) | 23 | 21 | 5 formats |
| 1-0 | HGGSP — Faire la guerre, faire la paix : conflits et modes de résolution | 4 | 3 (3) | 12 | 10 | 4 formats |
| 1-1 | HGGSP — Cartographier les guerres et les conflits : limites et enjeux | 3 | 0 (0) | 6 | 4 | 4 formats |
| 2-0 | Histoire — La crise de 1929 : le krach boursier et ses mécanismes | 6 | 3 (3) | 11 | 10 | 4 formats |
| 3-0 | Anglais — Heroes & superheroes : vocabulary + Story vs History | 5 | 4 (0) | 19 | 10 | 4 formats |
| 4-0 | Philosophie — Qu'est-ce que la philosophie ? | 5 | 9 (9) | 12 | 10 | 5 formats |

**Totaux actuels : 29 parties, 83 cartes, 65 questions, 6 récapitulatifs MP3.**

La matière **Philosophie** (index 4) a été ajoutée le 13 septembre 2026 à partir
des documents sources fournis (audio « Philosophie 1 début » + photos de cours).
La fiche SES a également été complétée avec la voix 3 et les exercices du jour.

Chaque fiche propose des parties détaillées, une synthèse finale
**« Ce qu'il faut retenir »**, des définitions « mot pour mot » 🎯, des exemples,
repères (faits clés, schémas, frises, tableaux, mini-questions), des astuces et
pièges, des cartes, les modes Étudier/Écrire/Associer/Grille, un quiz, des défis
express et un récapitulatif audio.

---

## 🧪 Vérifications automatiques

Un seul point d'entrée — le **pipeline QA v2** (8 pas vérifiables, correcteurs
bornés, smoke test serveur isolé, audit téléphone au navigateur réel ; le détail
est dans [`agents/README.md`](agents/README.md)) :

```bash
python3 agents/qa.py            # TOUT : structure, syntaxe JS, sécurité token,
                                # audit-complet, audit fonctionnel jsdom,
                                # smoke test serveur, audit téléphone,
                                # hygiène git
python3 agents/qa.py --fast     # idem sans les pas lents (jsdom, serveur, téléphone)
python3 tools/audit.py --fix-zip  # à la main : resynchronise StudyBoard-app.zip
```

### 📱 Audit téléphone (navigateur réel)

```bash
cd tools
npm run audit:mobile            # 20 écrans × 5 largeurs (320 → 768 px)
npm run audit:mobile -- --shots=/tmp/captures   # + captures PNG par écran
```

Il utilise un **vrai navigateur** (Chromium) : débordements, éléments hors écran,
cibles tactiles, contrastes WCAG calculés, fenêtres plein écran, zoom iOS,
marges d'encoche, erreurs JavaScript — et il joue réellement une question de quiz
et un défi. Deux façons de lui donner un navigateur : `CHROME_PATH=/chemin/chrome`
(ou Chrome/Chromium installé), ou `npm i --no-save puppeteer-core@23 @sparticuz/chromium@131`
(téléchargement autonome). Sans navigateur, l'audit s'annonce **ignoré** (il ne
fait jamais semblant d'avoir testé le téléphone).

`tools/audit.py` ne demande rien à installer. Le CI est prêt dans
[`tools/audit-workflow.yml`](tools/audit-workflow.yml) : il faut une **seule
fois** le copier dans `.github/workflows/audit.yml` depuis l'interface GitHub
(dépôt → `Add file` → `Create new file`) — les jetons des sessions Arena n'ont
pas la permission « workflows », d'où ce geste manuel. Il relance alors le
pipeline à chaque `push` / `pull request`.
Le code de sortie du pipeline (0) est l'unique autorisation de livraison.

La mémoire de reprise complète et l'historique sont dans [`REPRISE.md`](REPRISE.md).
