#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HERMES-BUILDER: implémente et renforce en continu
Lit vocal.html, index.html, server.py, copie et sécurise les patterns open-source
(addpipe/simple-recorderjs-demo, streamproc/MediaStreamRecorder, cwilso/AudioRecorder).
Commite chirurgicalement si nécessaire après vérification de l'audit.
"""
import time
import pathlib
import subprocess
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOG = ROOT / "agents" / "builder.log"
CRIT_LOG = ROOT / "agents" / "critiques.log"

def log(msg, level="BUILDER"):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line, flush=True)
    try:
        LOG.parent.mkdir(exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except: pass

def check_and_build():
    vocal_path = ROOT / "vocal.html"
    index_path = ROOT / "index.html"
    server_path = ROOT / "server.py"
    modified = False

    # 1. Vérification vocal.html
    if vocal_path.exists():
        vocal_txt = vocal_path.read_text(encoding="utf-8")
        # Vérifie scrollIntoView
        if "scrollIntoView" in vocal_txt:
            log("Remplacement de scrollIntoView résiduel par preventScroll", "REFLEXION")
            vocal_txt = re.sub(
                r'document\.getElementById\(([\'"][^\'"]+[\'"])\)\.scrollIntoView\([^)]*\)',
                r"const el=document.getElementById(\1);if(el){el.tabIndex=-1;try{el.focus({preventScroll:true});}catch{el.focus();}}",
                vocal_txt
            )
            vocal_path.write_text(vocal_txt, encoding="utf-8")
            modified = True

        # Vérifie pattern addpipe xhrJson
        if "xhrJson" not in vocal_txt or "XMLHttpRequest" not in vocal_txt:
            log("Pattern xhrJson absent ou corrompu dans vocal.html !", "CRITIQUE")

    # 2. Vérification index.html
    if index_path.exists():
        index_txt = index_path.read_text(encoding="utf-8")
        if "Permissions-Policy" not in index_txt:
            log("Ajout Permissions-Policy manquant dans index.html", "FIX")
            index_txt = index_txt.replace(
                '<meta charset="utf-8">',
                '<meta charset="utf-8">\n<meta http-equiv="Permissions-Policy" content="microphone=*, camera=*">'
            )
            index_path.write_text(index_txt, encoding="utf-8")
            modified = True

    # 3. Synchronisation zip et audit
    if modified:
        log("Fichiers modifiés, synchronisation de l'archive...", "SYNC")
        subprocess.run(["python3", str(ROOT / "tools/audit.py"), "--fix-zip"], cwd=str(ROOT), capture_output=True)
        r = subprocess.run(["node", str(ROOT / "tools/audit-complet.mjs")], cwd=str(ROOT), capture_output=True, text=True)
        if "0 erreurs" in r.stdout:
            log("Audit validé, commit des améliorations", "COMMIT")
            subprocess.run(["git", "add", "vocal.html", "index.html", "StudyBoard-app.zip"], cwd=str(ROOT))
            subprocess.run(["git", "commit", "-m", "fix(hermes-builder): renforcement patterns open-source & no-scroll"], cwd=str(ROOT))
        else:
            log(f"Audit échoué après build: {r.stdout[:200]}", "WARN")

def main():
    log("HERMES-BUILDER initialisé et actif")
    tour = 1
    while True:
        try:
            check_and_build()
        except Exception as e:
            log(f"Exception dans le cycle {tour}: {e}", "ERROR")
        tour += 1
        time.sleep(5)

if __name__ == "__main__":
    main()
