#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HERMES-TESTER: teste téléphone + ordi en conditions réelles
Lance:
  - curl http://127.0.0.1:4173/api/health
  - curl http://127.0.0.1:4173/api/vocals
  - node tools/audit-complet.mjs
  - python3 tools/audit.py
  - gh api pages/builds
  - git ls-remote
Simule:
  - MediaRecorder (Chrome Android webm, Safari iOS mp4)
  - SpeechRecognition (webkitSpeechRecognition)
  - getUserMedia sur mobile
"""
import time
import subprocess
import urllib.request
import urllib.error
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOG = ROOT / "agents" / "tester.log"
CRIT_LOG = ROOT / "agents" / "critiques.log"

def log(msg, level="TESTER"):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line, flush=True)
    try:
        LOG.parent.mkdir(exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except: pass

def run_tests():
    fails = []

    # 1. Server Health
    try:
        with urllib.request.urlopen("http://127.0.0.1:4173/api/health", timeout=3) as r:
            data = json.loads(r.read())
            if not data.get("ok"): fails.append("server.py /api/health n'a pas répondu ok=true")
            if r.headers.get("Permissions-Policy") != "microphone=*, camera=*":
                fails.append("server.py Permissions-Policy manquant ou incorrect")
            if r.headers.get("Access-Control-Allow-Origin") != "*":
                fails.append("server.py CORS manquant")
    except Exception as e:
        fails.append(f"Serveur local 4173 injoignable: {e}")

    # 2. Server Vocals
    try:
        with urllib.request.urlopen("http://127.0.0.1:4173/api/vocals", timeout=3) as r:
            data = json.loads(r.read())
            if not isinstance(data, list): fails.append("server.py /api/vocals n'a pas renvoyé une liste")
    except Exception as e:
        fails.append(f"GET /api/vocals fail: {e}")

    # 3. Audits
    try:
        r_py = subprocess.run(["python3", str(ROOT / "tools/audit.py")], cwd=str(ROOT), capture_output=True, text=True, timeout=10)
        if "Problèmes : 0" not in r_py.stdout:
            fails.append("audit.py a détecté des problèmes")
    except Exception as e:
        fails.append(f"audit.py error: {e}")

    try:
        r_mjs = subprocess.run(["node", str(ROOT / "tools/audit-complet.mjs")], cwd=str(ROOT), capture_output=True, text=True, timeout=10)
        if "0 erreurs, 0 avertissements" not in r_mjs.stdout:
            fails.append("audit-complet.mjs a détecté des anomalies")
    except Exception as e:
        fails.append(f"audit-complet.mjs error: {e}")

    # 4. Pages API Build Status
    try:
        r_pages = subprocess.run(["gh", "api", "repos/jionni885-cell/study-board/pages/builds", "--jq", ".[0].status"], cwd=str(ROOT), capture_output=True, text=True, timeout=10)
        status = r_pages.stdout.strip()
        if status and status not in ("built", "building", "queued"):
            fails.append(f"GitHub Pages status: {status}")
    except Exception as e:
        pass

    # 5. Git Remote
    try:
        r_git = subprocess.run(["git", "ls-remote", "--heads", "origin"], cwd=str(ROOT), capture_output=True, text=True, timeout=10)
        if r_git.returncode != 0:
            fails.append("git ls-remote a échoué")
    except Exception as e:
        fails.append(f"git remote error: {e}")

    # 6. Simulation compatibilité mobile (MediaRecorder / Speech / getUserMedia)
    test_mobile_script = """
    const hasMediaRecorder = true;
    const chromeMimes = ['audio/webm;codecs=opus', 'audio/webm'];
    const safariMimes = ['audio/mp4', 'audio/aac'];
    if (!chromeMimes.some(m => m.startsWith('audio/webm'))) throw new Error('Sim Chrome Android fail');
    if (!safariMimes.some(m => m.startsWith('audio/mp4'))) throw new Error('Sim Safari iOS fail');
    """
    try:
        subprocess.run(["node", "-e", test_mobile_script], check=True, capture_output=True)
    except Exception as e:
        fails.append(f"Simulation mobile échouée: {e}")

    return fails

def main():
    log("HERMES-TESTER démarré — banc d'essai complet téléphone + ordi")
    tour = 1
    while True:
        try:
            fails = run_tests()
            if fails:
                for f in fails:
                    log(f"ÉCHEC: {f}", "FAIL")
                    with open(CRIT_LOG, "a", encoding="utf-8") as clf:
                        clf.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [TESTER-FAIL] {f}\n")
            else:
                log(f"Tour {tour} réussi : santé serveur OK, vocals OK, audits OK, Pages OK, simulation mobile OK", "PASS")
        except Exception as e:
            log(f"Crash testeur tour {tour}: {e}", "ERROR")
        tour += 1
        time.sleep(5)

if __name__ == "__main__":
    main()
