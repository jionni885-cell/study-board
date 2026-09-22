#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contrôle de l'écosystème Study Board — HORS LIGNE, FINI, VÉRIFIABLE.

    python3 ecosystem/check.py            # contrôle, code de sortie 0 ou 1
    python3 ecosystem/check.py --detail   # + listing complet

Ce que le contrôle garantit :
  1. registry.json est un JSON valide, complet et lisible ;
  2. les 5 références externes demandées sont présentes (langgraph, open-r1,
     trl, dspy, swarms), chacune avec URL, licence, rôle, apport et usage ;
  3. chaque élément INTERNE pointe vers un chemin qui existe réellement
     (aucun fichier fantôme dans la carte de l'écosystème) ;
  4. les invariants de sécurité tiennent : aucun secret (ghp_…), aucun .m4a
     privé, aucune URL de sandbox morte (e2b.app) dans ecosystem/ ;
  5. le pipeline QA déclare bien le pas « ecosysteme » (la carte est branchée
     sur le contrôle automatique, sinon elle se périmerait en silence).

Aucune écriture, aucun accès réseau, aucun processus qui ne se termine.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REG = ROOT / "ecosystem" / "registry.json"
DETAIL = "--detail" in sys.argv

# Les références externes demandées par l'utilisateur (22/09/2026). Si l'une
# disparaît du registre, le contrôle échoue : c'est le garde-fou « sans rien
# oublier ».
EXTERNES_ATTENDUS = {"langgraph", "open-r1", "trl", "dspy", "swarms"}

problemes = []
infos = []


def bad(msg):
    problemes.append(msg)


def ok(msg):
    infos.append(msg)


# --------------------------------------------------------------------------
# 1. Registre lisible
# --------------------------------------------------------------------------
if not REG.exists():
    bad("ecosystem/registry.json absent")
    data = None
else:
    try:
        data = json.loads(REG.read_text(encoding="utf-8"))
        ok("registry.json lisible (version %s, maj %s)" % (data.get("version", "?"), data.get("maj", "?")))
    except Exception as e:
        bad("registry.json illisible : %s" % e)
        data = None

if data:
    # ----------------------------------------------------------------------
    # 2. Références externes
    # ----------------------------------------------------------------------
    externes = {e.get("id"): e for e in data.get("externe", [])}
    manquants = sorted(EXTERNES_ATTENDUS - set(externes))
    if manquants:
        bad("références externes absentes du registre : " + ", ".join(manquants))
    superflus = sorted(set(externes) - EXTERNES_ATTENDUS)
    if superflus:
        bad("références externes non prévues (à documenter explicitement) : " + ", ".join(superflus))
    for ident in sorted(EXTERNES_ATTENDUS & set(externes)):
        e = externes[ident]
        for champ in ("url", "licence", "role", "apport", "retenu", "usage_dans_study_board"):
            if not str(e.get(champ, "")).strip():
                bad("externe « %s » : champ « %s » vide" % (ident, champ))
        if not str(e.get("url", "")).startswith("https://github.com/"):
            bad("externe « %s » : URL GitHub attendue, trouvée « %s »" % (ident, e.get("url")))
        if re.search(r"e2b\.(app|dev)", json.dumps(e)) or re.search(r"ghp_[A-Za-z0-9]{20,}", json.dumps(e)):
            bad("externe « %s » : secret ou URL de sandbox morte dans la fiche" % ident)
    if not manquants and not superflus:
        ok("%d références externes complètes (langgraph, open-r1, trl, dspy, swarms)" % len(externes))

    # ----------------------------------------------------------------------
    # 3. Écosystème interne : aucun chemin fantôme
    # ----------------------------------------------------------------------
    internes = data.get("interne", [])
    if not internes:
        bad("aucun élément interne décrit dans le registre")
    for it in internes:
        chemin = str(it.get("chemin", "")).strip()
        if not chemin:
            bad("interne « %s » : chemin vide" % it.get("id", "?"))
            continue
        if not (ROOT / chemin).exists():
            bad("interne « %s » : chemin inexistant → %s" % (it.get("id", "?"), chemin))
        if not str(it.get("role", "")).strip():
            bad("interne « %s » : rôle manquant" % it.get("id", "?"))
    if internes:
        ok("%d éléments internes vérifiés (tous les chemins existent)" % len(internes))

    # ----------------------------------------------------------------------
    # 4. Invariants
    # ----------------------------------------------------------------------
    inv = data.get("invariants", [])
    if len(inv) < 4:
        bad("moins de 4 invariants déclarés : l'écosystème doit dire ce qui est interdit")
    else:
        ok("%d invariants déclarés (processus finis, aucun secret, aucun push automatique…)" % len(inv))
    if not data.get("tags_utilisateur", {}).get("jiojio"):
        bad("le nom d'usage de l'écosystème (jiojio) n'est pas documenté dans tags_utilisateur")

# --------------------------------------------------------------------------
# 5. Aucun secret, aucun .m4a, aucune sandbox morte dans ecosystem/
# --------------------------------------------------------------------------
for p in sorted((ROOT / "ecosystem").rglob("*")):
    if not p.is_file():
        continue
    if p.suffix.lower() == ".m4a":
        bad("fichier .m4a privé dans ecosystem/ : %s" % p.name)
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    if re.search(r"ghp_[A-Za-z0-9]{20,}", txt):
        bad("secret GitHub (ghp_…) dans ecosystem/%s" % p.name)
    if re.search(r"https://[^'\"\s]*e2b\.(app|dev)", txt):
        bad("URL de sandbox morte (e2b) dans ecosystem/%s" % p.name)

# --------------------------------------------------------------------------
# 6. Le pipeline branche bien ce contrôle
# --------------------------------------------------------------------------
QA = ROOT / "agents" / "qa.py"
if not QA.exists():
    bad("agents/qa.py absent : le contrôle de l'écosystème n'est branché nulle part")
else:
    qa = QA.read_text(encoding="utf-8")
    if "ecosystem/check.py" not in qa or '"ecosysteme"' not in qa:
        bad("agents/qa.py ne déclare pas le pas « ecosysteme » (ecosystem/check.py)")
    else:
        ok("pas « ecosysteme » branché dans agents/qa.py")

# --------------------------------------------------------------------------
# Rapport
# --------------------------------------------------------------------------
print("=" * 62)
print("ÉCOSYSTÈME STUDY BOARD — contrôle hors ligne")
print("=" * 62)
if DETAIL:
    for i in infos:
        print("  · " + i)
else:
    for i in infos:
        print("  ✅ " + i)
print("\nProblèmes : %d" % len(problemes))
for p in problemes:
    print("  ✗ " + p)
print("\n✅ Écosystème cohérent." if not problemes else "\n❌ Écosystème incohérent — à corriger.")
sys.exit(1 if problemes else 0)
