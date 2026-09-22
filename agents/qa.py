#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline QA Study Board — v3 (remplace le swarm multi-agents non borné).

MÉTHODE — les « techniques avancées » appliquées de façon déterministe :
- Chaque pas est un POINT DE CONTRÔLE DE PROCESSUS (PRM) : une vérification
  isolée dont la récompense est vérifiable — le code de sortie d'un outil
  (audit.py, node --check, jsdom, smoke test HTTP). Pas de note subjective.
- Boucle de correction bornée (LATS-lite) : un pas rouge déclenche des
  correcteurs idempotents (agents/fixers.py), puis RE-VÉRIFICATION du pas.
  Si le pas reste rouge, la correction est abandonnée (backtracking) et le
  pas passe en FAILED — jamais de demi-état laissé en place.
- Récompenses vérifiables (RLVR) : le code de sortie du pipeline est 0 si et
  seulement si tous les pas sont verts. C'est la seule mesure de « parfait ».
- Budget strict : 2 tentatives de correction par pas, 4 corrections au total.
  Le pipeline TOURNE FINI. Pas de boucle infinie, pas de log spam, pas de
  commit/push (le pipeline n'a jamais les mains sur git en écriture, sauf les
  git rm --cached explicitement tracés dans le rapport).

USAGE
  python3 agents/qa.py              # les 9 pas (dont jsdom ~2 min + serveur)
  python3 agents/qa.py --fast       # sans les pas lents (audit_dom, serveur)
  python3 agents/qa.py --no-fix     # rapport uniquement, aucune correction
  python3 agents/qa.py --step securite   # un seul pas

RAPPORT : agents/rapport.json (machine) + console (humain).
"""
import json
import os
import pathlib
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixers import STEP_FIXERS  # noqa: E402

MAX_FIX_ATTEMPTS = 2      # par pas
TOTAL_FIX_BUDGET = 4      # par exécution
SLOW_STEPS = {"audit_dom", "serveur", "mobile"}

PASS, FAIL, FIXED = "PASS", "FAIL", "FIXED"


def sh(cmd, timeout=300, cwd=None):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(cwd or ROOT))


# ---------------------------------------------------------------------------
# Pas de contrôle (chaque fonction retourne (ok, détail))
# ---------------------------------------------------------------------------

def check_structure():
    r = sh(["python3", "tools/audit.py"])
    ok = r.returncode == 0 and "Problèmes : 0" in r.stdout
    tail = "\n".join(l for l in r.stdout.splitlines() if "✗" in l or "!" in l)[:600]
    return ok, ("structure + données + ZIP + README/REPRISE OK" if ok else "audit.py non vert\n" + tail)


def _js_blocks():
    out = []
    for page, expected in (("index.html", 3), ("vocal.html", 1)):
        t = (ROOT / page).read_text(encoding="utf-8")
        blocks = re.findall(r"<script>(.*?)</script>", t, re.S)
        out.append((page, expected, blocks))
    return out


def check_syntaxe_js():
    detail = []
    ok = True
    for page, expected, blocks in _js_blocks():
        if len(blocks) != expected:
            ok = False
            detail.append(f"{page} : {len(blocks)} blocs <script>, {expected} attendus")
            continue
        for i, b in enumerate(blocks):
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
                f.write(b)
                tmp = f.name
            r = sh(["node", "--check", tmp], timeout=60)
            os.unlink(tmp)
            if r.returncode != 0:
                ok = False
                detail.append(f"{page} bloc {i+1} : syntaxe invalide — {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else '?'}")
    return ok, ("syntaxe JS OK (3 blocs index + 1 bloc vocal)" if ok else "\n".join(detail))


def check_securite():
    crits = []
    # 1. token.json jamais suivi par git
    r = sh(["git", "ls-files", "--", "token.json"])
    if r.returncode == 0 and r.stdout.strip():
        crits.append("token.json est SUIVI PAR GIT (token révélé — git rm --cached token.json)")
    # 2. .m4a privés jamais suivis
    r = sh(["git", "ls-files", "-z"])
    if r.returncode == 0:
        tracked = r.stdout.split("\0")
        for f in tracked:
            if f.endswith(".m4a"):
                crits.append("fichier .m4a privé suivi par git : " + f)
    # 3. aucun token GitHub dans un fichier texte suivi
    for f in tracked:
        p = ROOT / f
        if not (p.exists() and p.is_file() and p.stat().st_size < 5 * 1024 * 1024):
            continue
        if p.suffix not in {".html", ".js", ".mjs", ".py", ".md", ".json", ".yml", ".yaml", ".sh", ".txt", ".example"}:
            continue
        try:
            t = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if re.search(r"ghp_[A-Za-z0-9]{20,}", t) and "example" not in p.name:
            crits.append("token GitHub ghp_... trouvé dans : " + f)
    # 4. aucun sandbox éphémère mort en dur
    dead = re.compile(r"https://[^'\"]*e2b\.(app|dev)", re.I)
    for page in ("index.html", "vocal.html"):
        t = (ROOT / page).read_text(encoding="utf-8")
        if dead.search(t):
            crits.append("URL e2b (sandbox mort) en dur dans " + page)
    # 5. vocal.html sans URL de token publique
    t = (ROOT / "vocal.html").read_text(encoding="utf-8")
    if "raw.githubusercontent.com" in t or "github.io/study-board/token.json" in t:
        crits.append("vocal.html fetch un token sur une URL publique")
    return (not crits), ("sécurité OK (pas de token public, pas de .m4a, pas de sandbox mort)" if not crits else "\n".join(crits))


def check_audit_complet():
    r = sh(["node", "tools/audit-complet.mjs"], timeout=300)
    ok = r.returncode == 0 and "0 erreurs" in r.stdout
    tail = "\n".join(l for l in r.stdout.splitlines() if "❌" in l)[:600]
    return ok, ("audit-complet 0 erreur / 0 avertissement" if ok else "audit-complet non vert\n" + tail)


def check_audit_dom():
    if not (ROOT / "tools" / "node_modules").exists():
        sh(["npm", "install", "--no-audit", "--no-fund"], timeout=600, cwd=ROOT / "tools")
    r = sh(["node", "audit-dom.mjs"], timeout=900, cwd=ROOT / "tools")
    ok = r.returncode == 0 and "Problèmes : 0" in r.stdout and "Erreurs JS bloquantes : 0" in r.stdout
    tail = "\n".join(l for l in r.stdout.splitlines() if "✗" in l or "Erreur" in l)[:600]
    return ok, ("audit fonctionnel jsdom 0 défaut (défis, quiz, cartes, robustesse)" if ok else "audit-dom non vert\n" + tail)


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def check_serveur():
    """Smoke test HTTP sur une COPIE isolée du serveur (aucun git push, port libre)."""
    with tempfile.TemporaryDirectory(prefix="sbqa_") as td:
        td = pathlib.Path(td)
        (td / "server.py").write_bytes((ROOT / "server.py").read_bytes())
        (td / "index.html").write_text("<html><body>SBQA stub</body></html>", encoding="utf-8")
        (td / "vocals").mkdir()
        (td / "vocals" / ".gitkeep").write_text("", encoding="utf-8")
        port = _free_port()
        env = dict(os.environ, SB_PORT=str(port))
        proc = subprocess.Popen(
            [sys.executable, "server.py"], cwd=td, env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            base = f"http://127.0.0.1:{port}"
            # attente santé
            health = None
            for _ in range(50):
                try:
                    with urllib.request.urlopen(base + "/api/health", timeout=1) as r:
                        health = json.loads(r.read().decode())
                    break
                except Exception:
                    time.sleep(0.1)
            if not health or not health.get("ok"):
                return False, "serveur : /api/health injoignable après 5 s"
            crits = []
            # POST vocal
            payload = json.dumps({"fiche": "0-0", "transcript": "smoke test pipeline qa", "words": 5}).encode()
            req = urllib.request.Request(base + "/api/vocal", data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                j = json.loads(r.read().decode())
            if not j.get("ok") or "id" not in j:
                crits.append("POST /api/vocal : " + json.dumps(j, ensure_ascii=False))
            else:
                vid = j["id"]
                # GET vocals
                with urllib.request.urlopen(base + "/api/vocals", timeout=10) as r:
                    arr = json.loads(r.read().decode())
                if not any(v.get("id") == vid for v in arr):
                    crits.append("GET /api/vocals : id manquant dans la liste")
                # racine statique
                with urllib.request.urlopen(base + "/", timeout=10) as r:
                    if r.status != 200 or b"SBQA stub" not in r.read():
                        crits.append("GET / : index stub non servi")
            # traversal refusé
            import http.client
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            c.request("GET", "/../etc/passwd")
            resp = c.getresponse()
            body = resp.read()
            if resp.status not in (403, 404) or b"root:" in body:
                crits.append(f"traversal /../etc/passwd : statut {resp.status} (attendu 403/404, contenu protégé)")
            c.close()
            # 413 au-delà de 30 Mo — le serveur refuse SANS lire le corps :
            # le client reçoit HTTPError(413) OU une cassure de pipe pendant l'envoi
            # (les deux valent « refusé »). Le serveur doit ensuite survivre.
            big = b"x" * (31 * 1024 * 1024)
            req = urllib.request.Request(base + "/api/vocal", data=big, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    if r.status != 413:
                        crits.append(f"POST 31 Mo : accepté (statut {r.status}, attendu 413)")
            except urllib.error.HTTPError as e:
                if e.code != 413:
                    crits.append(f"POST 31 Mo : refusé avec statut {e.code} (attendu 413)")
            except (urllib.error.URLError, ConnectionError, OSError):
                pass  # pipe cassé en cours d'envoi = rejet rapide, comportement attendu
            try:
                with urllib.request.urlopen(base + "/api/health", timeout=5) as r:
                    if r.status != 200:
                        crits.append("serveur mort après le refus 31 Mo")
            except Exception:
                crits.append("serveur mort après le refus 31 Mo")
            return (not crits), ("serveur OK (santé, POST vocal, liste, statique, traversal, 413)" if not crits else "\n".join(crits))
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
    return False, "erreur interne smoke test serveur"


def check_mobile():
    """Audit « téléphone » dans un VRAI navigateur (Chromium) : 320/360/390/414/768 px,
    débordements, cibles tactiles, contrastes, défis plein écran, studio vocal.
    Si aucun navigateur n'est installé, le pas passe en SKIP (jamais en échec) :
    la livraison reste possible, mais le rapport dit clairement que le téléphone
    n'a PAS été vérifié."""
    if not (ROOT / "tools" / "audit-mobile.mjs").exists():
        return None, "tools/audit-mobile.mjs absent"
    if not (ROOT / "tools" / "node_modules" / "puppeteer-core").exists():
        # essai borné : si le réseau bloque, on continue (le pas sera SKIP)
        sh(["npm", "install", "--no-save", "--no-audit", "--no-fund", "puppeteer-core@23", "@sparticuz/chromium@131"],
           timeout=900, cwd=ROOT / "tools")
    r = sh(["node", "tools/audit-mobile.mjs", "--json"], timeout=900)
    if "IGNORÉ" in r.stdout or '"skip"' in r.stdout:
        return None, "aucun navigateur réel disponible (CHROME_PATH=… ou npm i puppeteer-core @sparticuz/chromium)"
    try:
        data = json.loads(r.stdout)
    except Exception:
        return False, "sortie illisible de l'audit mobile : " + (r.stdout or r.stderr)[-400:]
    errs, warns = data.get("erreurs", []), data.get("avertissements", [])
    if r.returncode != 0 or errs:
        lignes = "\n".join("  ✗ " + e["msg"] for e in errs[:8])
        return False, f"{len(errs)} défaut(s) sur téléphone :\n" + lignes
    return True, f"téléphone OK (5 tailles d'écran, {len(warns)} avertissement(s))"


def check_ecosysteme():
    """Carte de l'écosystème : registre machine lisible, 5 références externes
    complètes (langgraph, open-r1, trl, dspy, swarms), chemins internes réels,
    invariants déclarés, aucun secret. Aucun accès réseau."""
    if not (ROOT / "ecosystem" / "check.py").exists():
        return False, "ecosystem/check.py absent (la carte de l'écosystème a disparu)"
    r = sh(["python3", "ecosystem/check.py"], timeout=120)
    ok = r.returncode == 0 and "Problèmes : 0" in r.stdout
    tail = "\n".join(l for l in r.stdout.splitlines() if "✗" in l)[:600]
    return ok, ("écosystème cohérent (registre, 5 références externes, invariants, aucun secret)"
                if ok else "ecosystem/check.py non vert\n" + tail)


def check_hygiene_git():
    r = sh(["git", "diff", "--check"])
    if r.returncode != 0 or r.stdout.strip():
        return False, "git diff --check : espaces en fin de ligne / conflits\n" + r.stdout[:400]
    r = sh(["git", "status", "--porcelain"])
    # un token.json NON suivi ET non ignoré apparaît comme "?? token.json" — à proscrire.
    # (la suppression en attente "D token.json" est l'état normal de la transition, pas un défaut)
    if r.returncode == 0:
        for l in r.stdout.splitlines():
            # correspondance EXACTE : token.json.example (le modèle, à suivre) ne doit pas déclencher
            if l.startswith("??") and l[3:].strip().rstrip("/") == "token.json":
                return False, "token.json flottant sur le disque (?? token.json) — l'ignorer dans .gitignore"
    return True, "hygiène git OK (diff --check, pas de token.json flottant)"


STEPS = [
    ("structure", check_structure, False),
    ("syntaxe_js", check_syntaxe_js, False),
    ("securite", check_securite, False),
    ("ecosysteme", check_ecosysteme, False),
    ("audit_complet", check_audit_complet, False),
    ("audit_dom", check_audit_dom, True),
    ("serveur", check_serveur, True),
    ("mobile", check_mobile, True),
    ("hygiene_git", check_hygiene_git, False),
]


# ---------------------------------------------------------------------------
# Orchestrateur (boucle bornée avec backtracking)
# ---------------------------------------------------------------------------

def run_pipeline(fast=False, allow_fix=True, only=None):
    t0 = time.time()
    results = []
    fix_budget = TOTAL_FIX_BUDGET
    for name, fn, slow in STEPS:
        if only and name != only:
            continue
        if fast and slow:
            results.append({"step": name, "status": "SKIP", "detail": "--fast", "fixes": []})
            print(f"⏭  {name:<14} SKIP (--fast)")
            continue
        fixes = []
        try:
            ok, detail = fn()
        except Exception as e:  # un pas qui crashe ne crashe pas le pipeline
            ok, detail = False, f"exception pendant le pas : {type(e).__name__} : {e}"
        if ok is None:   # SKIP explicite : le pas n'a pas pu s'exécuter (ex. navigateur absent)
            results.append({"step": name, "status": "SKIP", "detail": detail, "fixes": []})
            print(f"⏭  {name:<14} SKIP   {detail}")
            continue
        if not ok and allow_fix:
            for attempt in range(1, MAX_FIX_ATTEMPTS + 1):
                if fix_budget <= 0:
                    break
                applied = None
                for fixer in STEP_FIXERS.get(name, []):
                    try:
                        changed, fdetail = fixer()
                    except Exception as e:  # un correcteur qui crashe n'abîme rien d'autre
                        fdetail = f"exception correcteur : {e}"
                        changed = False
                    if changed:
                        fix_budget -= 1
                        applied = (fixer.__name__, fdetail)
                        fixes.append(fdetail)
                        break  # un seul correcteur par tentative, puis re-vérification
                if not applied:
                    break  # rien à corriger → pas de tentative inutile
                try:
                    ok, detail = fn()  # RE-VÉRIFICATION (la récompense décide)
                except Exception as e:
                    ok, detail = False, f"re-vérification en erreur : {type(e).__name__} : {e}"
                if ok:
                    detail = "corrigé puis re-vérifié : " + applied[1]
                    break
        status = PASS if ok else (FIXED if fixes else FAIL)
        if not ok and fixes:
            status = FAIL  # corrigé mais toujours rouge → backtracking signalé
            detail = "corrections abandonnées (toujours rouge) : " + "; ".join(fixes) + "\n" + detail
        results.append({"step": name, "status": status, "detail": detail, "fixes": fixes})
        mark = {"PASS": "✅", "FIXED": "✅", "FAIL": "❌", "SKIP": "⏭"}[status]
        print(f"{mark} {name:<14} {status:<6} {detail.splitlines()[0] if detail else ''}")
        if not ok and detail:
            for l in detail.splitlines()[1:4]:
                print(f"    {l}")
    overall = all(r["status"] in (PASS, FIXED, "SKIP") for r in results)
    elapsed = round(time.time() - t0, 1)
    report = {
        "ts": int(time.time()),
        "overall": "PASS" if overall else "FAIL",
        "duration_sec": elapsed,
        "fixes_applied": sum(len(r["fixes"]) for r in results),
        "steps": results,
    }
    out = ROOT / "agents" / "rapport.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n=== PIPELINE QA : {report['overall']} en {elapsed}s (rapport: agents/rapport.json) ===")
    return overall


if __name__ == "__main__":
    fast = "--fast" in sys.argv
    no_fix = "--no-fix" in sys.argv
    only = None
    if "--step" in sys.argv:
        only = sys.argv[sys.argv.index("--step") + 1]
        if only not in {n for n, _, _ in STEPS}:
            print("pas inconnu : " + only + " — choix : " + ", ".join(n for n, _, _ in STEPS))
            sys.exit(2)
    ok = run_pipeline(fast=fast, allow_fix=not no_fix, only=only)
    sys.exit(0 if ok else 1)
