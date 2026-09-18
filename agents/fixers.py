#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stratégies de correction du pipeline QA Study Board (v2).

Chaque correcteur est :
- IDEMPOTENT : appliqué deux fois de suite, le second n'a aucun effet ;
- ATOMIQUE : une seule modification ciblée, aucune réécriture globale ;
- SANS EFFET DE BORD DANGEREUX : jamais de commit, jamais de push, jamais de
  suppression de contenu pédagogique ;
- Suivi d'une RE-VÉRIFICATION du pas concerné par agents/qa.py (si le pas est
  toujours rouge, la correction est abandonnée — backtracking).

Les correcteurs retournent (changé: bool, détail: str).
"""
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _run(cmd, timeout=120):
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)


def fix_zip_sync():
    """Resynchronise StudyBoard-app.zip avec le dépôt (index, vocal, README, media)."""
    r = _run(["python3", "tools/audit.py", "--fix-zip"])
    out = (r.stdout or "") + (r.stderr or "")
    if "resynchronisé" in out:
        return True, "StudyBoard-app.zip resynchronisé"
    if r.returncode == 0:
        return False, "ZIP déjà synchronisé"
    return False, "fix-zip échoué : " + out.strip().splitlines()[-1] if out.strip() else "inconnu"


def fix_permissions_index():
    """Ajoute le meta Permissions-Policy à index.html s'il manque."""
    p = ROOT / "index.html"
    t = p.read_text(encoding="utf-8")
    if "Permissions-Policy" in t:
        return False, "Permissions-Policy déjà présent"
    if "<meta charset=\"utf-8\">" not in t:
        return False, "point d'ancrage <meta charset> introuvable — intervention humaine requise"
    t = t.replace(
        '<meta charset="utf-8">',
        '<meta charset="utf-8">\n<meta http-equiv="Permissions-Policy" content="microphone=*, camera=*">',
        1,
    )
    p.write_text(t, encoding="utf-8")
    return True, "meta Permissions-Policy ajouté à index.html"


def fix_vocal_max_ms():
    """Rend le plafond 30 min de vocal.html si un ancien plafond (20 min) subsiste."""
    p = ROOT / "vocal.html"
    if not p.exists():
        return False, "vocal.html absent — intervention humaine requise"
    t = p.read_text(encoding="utf-8")
    changed = []
    if "MAX_MS = 1200000" in t:
        t = t.replace("MAX_MS = 1200000", "MAX_MS = 1800000")
        changed.append("MAX_MS 30 min")
    if "MAX_S = 1200" in t:
        t = t.replace("MAX_S = 1200", "MAX_S = 1800")
        changed.append("MAX_S 1800")
    if changed:
        p.write_text(t, encoding="utf-8")
        return True, "plafond vocal corrigé : " + ", ".join(changed)
    if "MAX_MS = 1800000" in t:
        return False, "plafond 30 min déjà correct"
    return False, "MAX_MS inattendu — intervention humaine requise"


def fix_gitignore_token():
    """Assure que token.json est gitignoré (sécurité)."""
    p = ROOT / ".gitignore"
    lines = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
    if any(l.strip() == "token.json" for l in lines):
        return False, "token.json déjà gitignoré"
    lines.append("token.json")
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True, "token.json ajouté à .gitignore"


def fix_token_untrack():
    """Dé-suit token.json de l'index git (git rm --cached) SANS toucher au fichier local.

    Le commit de cette suppression est fait par la session (le pipeline ne commit jamais).
    """
    r = _run(["git", "ls-files", "--", "token.json"])
    if r.returncode != 0 or not r.stdout.strip():
        return False, "token.json n'est pas suivi par git"
    _run(["git", "rm", "--cached", "-q", "--", "token.json"])
    return True, "token.json dé-suivi de git (git rm --cached) — à committer par la session"


# Registre : pas du pipeline -> correcteurs à essayer (dans l'ordre)
STEP_FIXERS = {
    "structure": [fix_zip_sync, fix_permissions_index, fix_vocal_max_ms],
    "audit_complet": [fix_zip_sync],
    "securite": [fix_gitignore_token, fix_token_untrack],
    "syntaxe_js": [],    # une erreur de syntaxe se corrige à la main (pas de devin machine)
    "audit_dom": [],     # un défaut fonctionnel se corrige à la main
    "serveur": [],       # un défaut serveur se corrige à la main
    "hygiene_git": [],   # un défaut git se corrige à la main
}
