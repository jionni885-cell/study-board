#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit « zéro dépendance » du dépôt Study Board.

    python3 tools/audit.py            # contrôle tout, code de sortie 1 si problème
    python3 tools/audit.py --fix-zip  # resynchronise StudyBoard-app.zip

Cet audit tourne aussi en CI (voir tools/audit-workflow.yml, à copier en
.github/workflows/audit.yml).
Il ne remplace pas l'audit fonctionnel (tools/audit-dom.mjs, qui simule le navigateur)
mais il garantit : structure des données, compteurs, contenus interdits, chemins des
audios, cohérence de README.md / REPRISE.md et synchronisation de l'archive ZIP.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
FIX_ZIP = "--fix-zip" in sys.argv

problems = []
warnings = []


def bad(msg):
    problems.append(msg)


def warn(msg):
    warnings.append(msg)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


# --------------------------------------------------------------------------
# 0. Lecture du fichier
# --------------------------------------------------------------------------
if not os.path.exists(HTML):
    print("index.html introuvable — lance l'audit depuis le dépôt.")
    sys.exit(1)

src = open(HTML, encoding="utf-8").read()

if "<!DOCTYPE html>" not in src or "</html>" not in src:
    bad("index.html : document HTML incomplet")
if 'lang="fr"' not in src:
    warn("index.html : attribut lang=\"fr\" absent")
if "viewport" not in src:
    bad("index.html : meta viewport absent (affichage mobile)")
if "data-theme" not in src:
    bad("index.html : thème clair/sombre absent")

scripts = re.findall(r"<script[^>]*>(.*?)</script>", src, re.S)
if len(scripts) != 3:
    bad("index.html : %d blocs <script> (3 attendus)" % len(scripts))

# --------------------------------------------------------------------------
# 1. Syntaxe JavaScript des trois blocs
# --------------------------------------------------------------------------
node = shutil.which("node")
tmp = tempfile.mkdtemp(prefix="sb-audit-")
if node:
    for i, block in enumerate(scripts):
        p = os.path.join(tmp, "block%d.js" % i)
        open(p, "w", encoding="utf-8").write(block)
        r = run([node, "--check", p])
        if r.returncode != 0:
            bad("bloc <script> %d : erreur de syntaxe JS → %s" % (i, (r.stderr or "").strip().splitlines()[:1]))
else:
    warn("node est absent : contrôle de syntaxe JS et lecture des données ignorés")

# --------------------------------------------------------------------------
# 2. Données : D (contenu), DF6 (défis), EX6 (astuces/pièges), AUDIOF (audios)
# --------------------------------------------------------------------------
D = DF6 = EX6 = AUDIOF = None
if node:
    extract = r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
function grab(re) { const m = re.exec(src); return m ? m[0] : null; }
function js(src2) { return eval('(' + src2 + ')'); }
const d = grab(/const D=\[[\s\S]*?\nconst AUD=/);
const df6 = grab(/^const DF6 = \{[\s\S]*?\};$/m);
const ex6 = grab(/^const EX6 = \{[\s\S]*?\};$/m);
const audiof = grab(/const AUDIOF=\{[^}]*\}/);
const out = {
  D: js(d.slice('const D='.length).replace(/\nconst AUD=$/, '').replace(/;$/, '')),
  DF6: df6 ? js(df6.replace(/^const DF6 = /, '').replace(/;$/, '')) : null,
  EX6: ex6 ? js(ex6.replace(/^const EX6 = /, '').replace(/;$/, '')) : null,
  AUDIOF: audiof ? js(audiof.replace(/^const AUDIOF=/, '')) : null,
  AUD: js(grab(/const AUD=\[[^\]]*\]/).replace(/^const AUD=/, '')),
};
process.stdout.write(JSON.stringify(out));
"""
    p = os.path.join(tmp, "extract.js")
    open(p, "w", encoding="utf-8").write(extract)
    r = run([node, p, HTML])
    if r.returncode != 0:
        bad("extraction des données impossible → %s" % (r.stderr or "").strip()[:200])
    else:
        data = json.loads(r.stdout)
        D, DF6, EX6, AUDIOF = data["D"], data["DF6"], data["EX6"], data["AUDIOF"]
        AUD = data["AUD"]

if D:
    TYPES = {"texte", "liste", "def", "exemple", "note", "cle", "facts", "schema", "timeline", "table", "probe"}
    FORBIDDEN = ["à vérifier", "a verifier", "transcription", "la voix dit", "selon ton professeur",
                 "à confirmer", "l'essentiel à retenir", "todo", "xxx"]
    fiche_keys = set()
    for mi, m in enumerate(D):
        for fi, f in enumerate(m["fiches"]):
            key = "%d-%d" % (mi, fi)
            fiche_keys.add(key)
            tag = "%s (%s — %s)" % (key, m["nom"], f.get("titre", "?"))
            if not f.get("parties"):
                bad("%s : aucune partie" % tag)
            if not f.get("flashcards"):
                bad("%s : aucune carte" % tag)
            if not f.get("quiz"):
                bad("%s : aucun quiz" % tag)
            titres = [p["titre"] for p in f.get("parties", [])]
            if "Ce qu'il faut retenir" not in titres:
                bad("%s : partie « Ce qu'il faut retenir » manquante" % tag)
            n_def = n_wpw = 0
            for p in f.get("parties", []):
                for b in p.get("blocs", []):
                    if b["type"] not in TYPES:
                        bad("%s : type de bloc inconnu « %s »" % (tag, b["type"]))
                    if b["type"] == "def":
                        n_def += 1
                        n_wpw += 1 if b.get("wpw") else 0
                        if not b.get("terme") or not b.get("texte"):
                            bad("%s : définition incomplète" % tag)
                    blob = json.dumps(b, ensure_ascii=False).lower()
                    for fw in FORBIDDEN:
                        if fw in blob:
                            bad("%s : méta-note interdite « %s »" % (tag, fw))
            for c in f["flashcards"]:
                if not c.get("face") or not c.get("verso"):
                    bad("%s : carte incomplète" % tag)
                blob = json.dumps(c, ensure_ascii=False).lower()
                for fw in FORBIDDEN:
                    if fw in blob:
                        bad("%s : méta-note interdite « %s » (carte)" % (tag, fw))
            for qi, q in enumerate(f["quiz"]):
                opts = q.get("options") or (["Vrai", "Faux"] if q.get("type") == "vf" else [])
                if len(opts) < 2:
                    bad("%s : quiz %d sans options" % (tag, qi + 1))
                if not isinstance(q.get("reponse"), int) or not (0 <= q["reponse"] < len(opts)):
                    bad("%s : quiz %d — index de réponse invalide" % (tag, qi + 1))
                if not q.get("expl"):
                    bad("%s : quiz %d sans explication" % (tag, qi + 1))
                if q.get("type") and q["type"] != "vf":
                    warn("%s : quiz %d — type « %s » non géré par le moteur" % (tag, qi + 1, q["type"]))
                blob = json.dumps(q, ensure_ascii=False).lower()
                for fw in FORBIDDEN:
                    if fw in blob:
                        bad("%s : méta-note interdite « %s » (quiz %d)" % (tag, fw, qi + 1))
            # compteurs _nb de la matière
            if len(m["fiches"]) == 1:
                nb = m.get("_nb", {})
                for champ, attendu in (("fiches", 1), ("def", n_def), ("wpw", n_wpw),
                                       ("fc", len(f["flashcards"])), ("q", len(f["quiz"]))):
                    if nb.get(champ) != attendu:
                        bad("%s : _nb.%s = %s (attendu %s)" % (tag, champ, nb.get(champ), attendu))
            if not (f.get("sources") or []):
                warn("%s : aucune source (.m4a) déclarée" % tag)

    # défis express
    FORMATS = {"vf", "cloze", "order", "intrus", "sort"}
    for key, dd in (DF6 or {}).items():
        if key not in fiche_keys:
            bad("DF6[\"%s\"] ne correspond à aucune fiche" % key)
            continue
        if not dd.get("e") or not dd.get("tag"):
            bad("DF6[%s] : emoji ou phrase d'accroche manquante" % key)
        vus = set()
        for i, g in enumerate(dd.get("ch", [])):
            where = 'DF6[%s] défi %d (%s)' % (key, i + 1, g.get("title", "?"))
            if g.get("t") not in FORMATS:
                bad("%s : format inconnu « %s »" % (where, g.get("t")))
                continue
            vus.add(g["t"])
            if g["t"] == "vf":
                for j, it in enumerate(g.get("items", [])):
                    if not it.get("s") or not isinstance(it.get("v"), bool) or not it.get("e"):
                        bad("%s : item %d incomplet (s / v / e)" % (where, j + 1))
            elif g["t"] == "cloze":
                for j, it in enumerate(g.get("items", [])):
                    if "__" not in it.get("q", "") or not it.get("opt") or not isinstance(it.get("a"), int) \
                            or not (0 <= it["a"] < len(it["opt"])) or not it.get("e"):
                        bad("%s : item %d incomplet (q avec __ / opt / a / e)" % (where, j + 1))
            elif g["t"] == "order":
                if len(g.get("items", [])) < 2:
                    bad("%s : moins de 2 étapes à remettre en ordre" % where)
            elif g["t"] == "intrus":
                if len(g.get("items", [])) < 2 or not isinstance(g.get("a"), int) \
                        or not (0 <= g["a"] < len(g["items"])) or not g.get("e"):
                    bad("%s : intrus incomplet (items / a / e)" % where)
            elif g["t"] == "sort":
                buckets = g.get("buckets") or {}
                if len(buckets) < 2 or sum(len(v) for v in buckets.values()) < 2:
                    bad("%s : classement incomplet (au moins 2 thèmes)" % where)
        for fmt in ("vf", "cloze", "order", "intrus", "sort"):
            if fmt not in vus:
                warn("DF6[%s] : format « %s » absent" % (key, fmt))
        if key not in (EX6 or {}) or len(EX6[key]) < 2:
            bad("EX6[%s] : au moins 2 astuces/pièges sont exigés" % key)
    for key in (EX6 or {}):
        if key not in fiche_keys:
            bad("EX6[\"%s\"] ne correspond à aucune fiche" % key)

    # audios
    for key, slug in (AUDIOF or {}).items():
        if key not in fiche_keys:
            bad("AUDIOF[\"%s\"] ne correspond à aucune fiche" % key)
        p = os.path.join(ROOT, "media", "audio", slug + ".mp3")
        if not os.path.exists(p):
            bad("AUDIOF[%s] → media/audio/%s.mp3 absent" % (key, slug))
        elif os.path.getsize(p) < 20000:
            bad("media/audio/%s.mp3 : fichier suspicieusement petit" % slug)
    for key in fiche_keys:
        if (AUDIOF or {}).get(key) is None:
            bad("fiche %s : aucun récapitulatif MP3 déclaré dans AUDIOF" % key)

# --------------------------------------------------------------------------
# 3. Aucun fichier .m4a dans le dépôt public
# --------------------------------------------------------------------------
r = run(["git", "ls-files"], cwd=ROOT)
if r.returncode == 0:
    tracked = [l.strip() for l in r.stdout.splitlines() if l.strip()]
    for f in tracked:
        if f.lower().endswith(".m4a"):
            bad("fichier .m4a suivi par git (privé, interdit dans le dépôt) : %s" % f)
        if os.path.getsize(os.path.join(ROOT, f)) > 30 * 1024 * 1024:
            bad("fichier trop volumineux pour le dépôt : %s" % f)

# --------------------------------------------------------------------------
# 4. Archive StudyBoard-app.zip synchronisée
# --------------------------------------------------------------------------
ZIP = os.path.join(ROOT, "StudyBoard-app.zip")
if os.path.exists(ZIP):
    z = zipfile.ZipFile(ZIP)
    noms = {i.filename.replace("\\", "/") for i in z.infolist()}
    attendus = ["index.html", "README.md"] + sorted(
        "media/audio/" + f for f in os.listdir(os.path.join(ROOT, "media", "audio")) if f.endswith(".mp3")
    )
    for name in attendus:
        if name not in noms:
            bad("StudyBoard-app.zip : %s manquant" % name)
            continue
        if z.read(name) != open(os.path.join(ROOT, name), "rb").read():
            if FIX_ZIP:
                warn("StudyBoard-app.zip : %s resynchronisé" % name)
            else:
                bad("StudyBoard-app.zip : %s différent du dépôt (relance avec --fix-zip)" % name)
    for name in noms:
        if name.endswith(".m4a"):
            bad("StudyBoard-app.zip : contient un .m4a interdit (%s)" % name)
    if FIX_ZIP:
        with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as out:
            for name in attendus:
                out.write(os.path.join(ROOT, name), name)
        print("→ StudyBoard-app.zip resynchronisé (%d fichiers)" % len(attendus))
else:
    bad("StudyBoard-app.zip absent")

# --------------------------------------------------------------------------
# 5. README.md et REPRISE.md cohérents avec les données
# --------------------------------------------------------------------------
def lit_tableau(chemin):
    """Lit un tableau de fiches en s'appuyant sur la ligne d'en-tête (les colonnes
    ne sont pas dans le même ordre dans README.md et REPRISE.md)."""
    try:
        txt = open(os.path.join(ROOT, chemin), encoding="utf-8").read()
    except FileNotFoundError:
        bad("%s manquant" % chemin)
        return None, None
    lignes, entete = {}, None
    for ligne in txt.splitlines():
        if not ligne.strip().startswith("|"):
            continue
        cells = [c.strip() for c in ligne.strip().strip("|").split("|")]
        if entete is None:
            if cells and cells[0].lower() == "index":
                entete = [c.lower() for c in cells]
            continue
        if not re.match(r"^\d-\d$", cells[0]) or len(cells) < len(entete):
            continue

        def colonne(mot):
            for i, c in enumerate(entete):
                if mot in c:
                    return i
            return None

        def nombre(mot):
            i = colonne(mot)
            if i is None:
                return None
            m = re.search(r"(\d+)", cells[i])
            return int(m.group(1)) if m else None

        def parenth(mot):
            i = colonne(mot)
            if i is None:
                return None
            m = re.search(r"\((\d+)\)", cells[i])
            return int(m.group(1)) if m else None

        lignes[cells[0]] = {
            "parties": nombre("partie"), "def": nombre("définition"),
            "wpw": parenth("définition") if parenth("définition") is not None else nombre("mot pour mot"),
            "cartes": nombre("carte"), "quiz": nombre("quiz"),
        }
    return txt, lignes

if D:
    stats = {}
    for mi, m in enumerate(D):
        for fi, f in enumerate(m["fiches"]):
            n_def = sum(1 for p in f["parties"] for b in p["blocs"] if b["type"] == "def")
            n_wpw = sum(1 for p in f["parties"] for b in p["blocs"] if b["type"] == "def" and b.get("wpw"))
            stats["%d-%d" % (mi, fi)] = {
                "parties": len(f["parties"]), "def": n_def, "wpw": n_wpw,
                "cartes": len(f["flashcards"]), "quiz": len(f["quiz"]),
            }
    totaux = {
        "parties": sum(s["parties"] for s in stats.values()),
        "cartes": sum(s["cartes"] for s in stats.values()),
        "questions": sum(s["quiz"] for s in stats.values()),
        "fiches": len(stats),
    }
    for doc in ("README.md", "REPRISE.md"):
        txt, table = lit_tableau(doc)
        if table is None:
            continue
        for key, ligne in table.items():
            s = stats.get(key)
            if not s:
                bad("%s : ligne %s sans fiche correspondante" % (doc, key))
                continue
            for champ in ("parties", "def", "wpw", "cartes", "quiz"):
                if ligne.get(champ) is not None and ligne[champ] != s[champ]:
                    bad("%s : fiche %s — %s annoncé %s, réel %s" % (doc, key, champ, ligne[champ], s[champ]))
        for ligne in txt.splitlines():
            if "totaux" not in ligne.lower():
                continue
            for cle, valeur in totaux.items():
                for m in re.finditer(r"(\d+)\s+" + cle, ligne):
                    if int(m.group(1)) != valeur:
                        bad("%s : totaux — « %s %s » annoncé(s), %s réel(s)" % (doc, m.group(1), cle, valeur))

# --------------------------------------------------------------------------
# 6. Contrôles de contenu interdits dans le HTML entier
# --------------------------------------------------------------------------
for fw in ["à vérifier", "la voix dit", "selon ton professeur", "transcription :"]:
    if fw in src.lower():
        bad("index.html : expression interdite « %s »" % fw)

# --------------------------------------------------------------------------
# Rapport
# --------------------------------------------------------------------------
shutil.rmtree(tmp, ignore_errors=True)
print("=" * 62)
print("AUDIT STUDY BOARD")
print("=" * 62)
if D:
    print("fiches : %s | défis : %s | astuces : %s | audios : %s" % (
        len(D) if not stats else len(stats), len(DF6 or {}), len(EX6 or {}), len(AUDIOF or {})))
print("\nProblèmes : %d" % len(problems))
for p in problems:
    print("  ✗ %s" % p)
if warnings:
    print("\nAvertissements : %d" % len(warnings))
    for w in warnings:
        print("  ! %s" % w)
if not problems:
    print("\n✅ Tout est cohérent.")
sys.exit(1 if problems else 0)
