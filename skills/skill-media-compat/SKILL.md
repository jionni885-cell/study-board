# Skill: Media Compatibility (streamproc/MediaStreamRecorder)

Copie du pattern de `streamproc/MediaStreamRecorder` :
Sélection robuste et dynamique du type MIME audio pour `MediaRecorder` avec cascade de fallbacks multi-navigateurs.

## Problème résolu
Chrome et Firefox supportent `audio/webm;codecs=opus`. iOS Safari supporte `audio/mp4` ou `audio/aac`. Les anciens Android supportent `audio/ogg` ou `audio/wav`. Si une option unsupported est passée à `MediaRecorder`, le constructeur lève une exception immédiate.

## Cascade de détection
1. `audio/webm;codecs=opus`
2. `audio/webm`
3. `audio/mp4`
4. `audio/ogg;codecs=opus`
5. `audio/wav`
6. `audio/aac`
7. Options vides `{}` (laisse le navigateur choisir son format par défaut)
