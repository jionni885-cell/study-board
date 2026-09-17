# Skill: Vocal Long (vocal.html interne)

Gestion des oraux longs jusqu'à 30 minutes (MAX_MS = 1800000 ms / MAX_S = 1800 s) :
- Paliers d'analyse : `<10` trop court / `<60` un peu court / `<600` parfait 2-5 min / `<1500` long 5-12 min / `>=1500` XXL 15-30 min
- Détection d'hésitations : `hesRatio > 0.025` (2.5%)
- Segmentation automatique en chapitres proportionnels (`words/3` ou `words/segN`)
- Génération automatique de plan chronométré + 5 flashcards
