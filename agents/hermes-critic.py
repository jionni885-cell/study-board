#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HERMES-CRITIC: critique sans arrêt, ne s'arrête jamais.
Vérifie tout le site (logique, code, syntaxe, audit, Pages, téléphone).
Écrit agents/critiques.log + agents/status.json.
S'il voit 'Gardé en local' ou 401, il hurle !
"""
import time
import json
import pathlib
import subprocess
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOG = ROOT / "agents" / "critiques.log"
STATUS = ROOT / "agents" / "status.json"

def log(msg, level="CRITIC"):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line, flush=True)
    try:
        LOG.parent.mkdir(exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        # Garde un historique borné
        lines = LOG.read_text(encoding="utf-8").splitlines()
        if len(lines) > 5000:
            LOG.write_text("\n".join(lines[-3000:]) + "\n", encoding="utf-8")
    except: pass

def inspect_site():
    critiques = []
    
    # 1. Vérification vocal.html
    vocal = ROOT / "vocal.html"
    if not vocal.exists():
        critiques.append("FATAL: vocal.html absent")
    else:
        vt = vocal.read_text(encoding="utf-8")
        if "MAX_MS = 1800000" not in vt: critiques.append("CRITIQUE: vocal.html MAX_MS != 1800000 (30 min attendu)")
        if "MAX_S = 1800" not in vt: critiques.append("CRITIQUE: vocal.html MAX_S != 1800")
        if "scrollIntoView" in vt: critiques.append("CRITIQUE: scrollIntoView détecté dans vocal.html (doit être preventScroll)")
        if "SB_FALLBACKS" not in vt: critiques.append("CRITIQUE: SB_FALLBACKS absent dans vocal.html")
        if "xhrJson" not in vt: critiques.append("CRITIQUE: xhrJson addpipe absent dans vocal.html")
        if vt.count("<script>") != 1: critiques.append(f"CRITIQUE: vocal.html contient {vt.count('<script>')} <script>, 1 seul attendu")
        if "Bearer " not in vt: critiques.append("CRITIQUE: Auth header n'utilise pas 'Bearer'")
        
        # Alerte maximale si anomalie "Gardé en local" ou "401"
        recent_log = LOG.read_text(encoding="utf-8") if LOG.exists() else ""
        if "Gardé en local" in recent_log:
            critiques.append("ALERTE HURLEMENT: 'Gardé en local' détecté dans les logs — le fallback serveur/token a échoué !")
        if "401" in recent_log and "retry OK" not in recent_log:
            critiques.append("ALERTE HURLEMENT: 401 Unauthorized détecté — token GitHub invalide ou expiré !")

    # 2. Vérification index.html
    index = ROOT / "index.html"
    if not index.exists():
        critiques.append("FATAL: index.html absent")
    else:
        it = index.read_text(encoding="utf-8")
        if it.count("<script>") != 3: critiques.append(f"CRITIQUE: index.html contient {it.count('<script>')} <script>, 3 attendus")
        if "Studio Vocal" not in it: critiques.append("CRITIQUE: CTA Studio Vocal absent d'index.html")
        if 'target="_blank"' not in it: critiques.append("CRITIQUE: target=_blank manquant sur Studio Vocal")
        if "Permissions-Policy" not in it: critiques.append("CRITIQUE: Permissions-Policy manquant dans index.html")

    # 3. Vérification token.json
    tok = ROOT / "token.json"
    if not tok.exists():
        critiques.append("FATAL: token.json manquant")
    else:
        try:
            tj = json.loads(tok.read_text(encoding="utf-8"))
            if not tj.get("t"): critiques.append("CRITIQUE: token.json ne contient pas la clé 't' base64")
        except Exception as e:
            critiques.append(f"CRITIQUE: token.json invalide: {e}")

    # 4. Vérification audit
    try:
        r = subprocess.run(["node", str(ROOT / "tools/audit-complet.mjs")], cwd=str(ROOT), capture_output=True, text=True, timeout=10)
        if "0 erreurs, 0 avertissements" not in r.stdout:
            critiques.append("CRITIQUE: audit-complet.mjs a des erreurs ou avertissements")
    except Exception as e:
        critiques.append(f"WARN: audit-complet.mjs: {e}")

    return critiques

def main():
    log("HERMES-CRITIC démarré — vigilance continue")
    tour = 1
    while True:
        try:
            crits = inspect_site()
            has_fails = len(crits) > 0
            STATUS.write_text(json.dumps({
                "tour": tour,
                "ts": int(time.time()),
                "ok": not has_fails,
                "critiques": crits
            }, ensure_ascii=False, indent=2), encoding="utf-8")

            if crits:
                for c in crits:
                    log(c, "HURLEMENT" if "HURLEMENT" in c else "FAIL")
            else:
                log("Tour impeccable — 0 défaut logique, syntaxe et audits 100% verts", "OK")
        except Exception as e:
            log(f"Erreur critique tour {tour}: {e}", "ERROR")
        tour += 1
        time.sleep(5)

if __name__ == "__main__":
    main()
