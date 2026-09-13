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
| 0-0 | SES — Les sources et les défis de la croissance économique | 6 | 15 (11) | 21 | 20 | 5 formats |
| 1-0 | HGGSP — Faire la guerre, faire la paix : conflits et modes de résolution | 4 | 3 (3) | 12 | 10 | 4 formats |
| 1-1 | HGGSP — Cartographier les guerres et les conflits : limites et enjeux | 3 | 0 (0) | 6 | 4 | 4 formats |
| 2-0 | Histoire — La crise de 1929 : le krach boursier et ses mécanismes | 6 | 3 (3) | 11 | 10 | 4 formats |
| 3-0 | Anglais — Heroes & superheroes : vocabulary + Story vs History | 5 | 4 (0) | 19 | 10 | 4 formats |
| 4-0 | Philosophie — Qu'est-ce que la philosophie ? | 5 | 9 (9) | 12 | 10 | 5 formats |

**Totaux actuels : 29 parties, 81 cartes, 64 questions, 6 récapitulatifs MP3.**

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

Deux outils vérifient le dépôt et bloquent toute régression :

```bash
python3 tools/audit.py          # structure, compteurs, contenus interdits, audios, ZIP, README/REPRISE
python3 tools/audit.py --fix-zip  # resynchronise StudyBoard-app.zip
cd tools && npm install && node audit-dom.mjs   # audit fonctionnel (jsdom) : défis, quiz, cartes, robustesse
```

`tools/audit.py` ne demande rien à installer. Le fichier `tools/audit-workflow.yml`
est prêt à être copié en `.github/workflows/audit.yml` pour lancer les deux audits
automatiquement à chaque `push` / `pull request`.
Les deux audits doivent afficher **0 défaut** avant toute livraison.

La mémoire de reprise complète et l'historique sont dans [`REPRISE.md`](REPRISE.md).
