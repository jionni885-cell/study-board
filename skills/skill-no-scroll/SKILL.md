# Skill: No-Scroll (interne)

Prévention des sauts d'écran intempestifs sur smartphone et dans les iframes :
Remplacement de `scrollIntoView()` par `focus({preventScroll:true})`.

## Problème résolu
Sur iOS Safari et dans les iframes intégrées, l'appel à `.scrollIntoView()` provoque des saccades ou repositionne brusquement la page parente.
L'utilisation de `.focus({ preventScroll: true })` permet de cibler l'élément pour l'accessibilité sans déplacer arbitrairement la vue de l'utilisateur.
