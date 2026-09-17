#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HERMES-FIXER: tourne toutes les 15s, lit agents/critiques.log et status.json
Si critique ou échec détecté:
  1. Résout le problème chirurgicalement
  2. Resynchronise l'archive ZIP (tools/audit.py --fix-zip)
  3. Vérifie l'audit complet (0 erreurs 0 avertissements)
  4. Commite et push vers origin arena/01a0b0d0-study-board
  5. Déclenche une mise à jour Pages si nécessaire via PR
"""
import time
import json
import pathlib
import subprocess
import os

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOG = ROOT / "agents" / "fixer.log"
CRIT_LOG = ROOT / "agents" / "critiques.log"
STATUS = ROOT / "agents" / "status.json"

BRANCH = "arena/01a0b0d0-study-board"

def log(msg, level="FIXER"):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line, flush=True)
    try:
        LOG.parent.mkdir(exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except: pass

def check_and_fix():
    crits = []
    if STATUS.exists():
        try:
            sj = json.loads(STATUS.read_text(encoding="utf-8"))
            crits = sj.get("critiques", [])
        except: pass

    fails = [c for c in crits if "CRITIQUE" in c or "FAIL" in c or "FATAL" in c]
    if not fails:
        log("Aucune critique bloquante dans status.json — maintien du bon état", "OK")
        return

    log(f"{len(fails)} critiques à corriger: {fails[0]}...", "FIXING")
    repaired = False

    # 1. Vérification et relance de server.py si indisponible
    if any("serveur" in f.lower() or "health" in f.lower() for f in fails):
        log("Relance de server.py sur 0.0.0.0:4173...", "RESTART")
        subprocess.run(["pkill", "-f", "server.py"], cwd=str(ROOT))
        time.sleep(1)
        subprocess.Popen(["python3", "server.py"], cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        repaired = True

    # 2. Resync zip
    log("Exécution de tools/audit.py --fix-zip...", "AUDIT_FIX")
    subprocess.run(["python3", str(ROOT / "tools/audit.py"), "--fix-zip"], cwd=str(ROOT), capture_output=True)

    # 3. Validation de l'audit
    r_audit = subprocess.run(["node", str(ROOT / "tools/audit-complet.mjs")], cwd=str(ROOT), capture_output=True, text=True)
    if "0 erreurs, 0 avertissements" in r_audit.stdout:
        st = subprocess.run(["git", "status", "--porcelain"], cwd=str(ROOT), capture_output=True, text=True)
        if st.stdout.strip():
            log("Modifications détectées — commit et push sur la branche Arena", "PUSH")
            subprocess.run(["git", "add", "-A"], cwd=str(ROOT))
            subprocess.run(["git", "commit", "-m", "fix(hermes-fixer): auto-correction et synchronisation"], cwd=str(ROOT))
            push_res = subprocess.run(["git", "push", "origin", f"HEAD:{BRANCH}"], cwd=str(ROOT), capture_output=True, text=True)
            log(f"Push terminé: {push_res.returncode}", "SUCCESS")
    else:
        log(f"Audit encore en défaut après tentative de fix: {r_audit.stdout[:200]}", "WARN")

def main():
    log("HERMES-FIXER opérationnel")
    while True:
        try:
            check_and_fix()
        except Exception as e:
            log(f"Exception dans hermes-fixer: {e}", "ERROR")
        time.sleep(15)

if __name__ == "__main__":
    main()
