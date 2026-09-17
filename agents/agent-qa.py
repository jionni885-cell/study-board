#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent QA principal — tourne en boucle, teste l'entièreté du site, critique sans arrêt.
Indépendant, ne s'arrête jamais. Logue dans agents/critiques.log + status.json
"""
import json, time, subprocess, urllib.request, urllib.error, re, pathlib, sys, os

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOG = ROOT / "agents" / "critiques.log"
STATUS = ROOT / "agents" / "status.json"
VOCAL = ROOT / "vocal.html"
INDEX = ROOT / "index.html"
SERVER = ROOT / "server.py"

def log(msg, level="INFO"):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {level} {msg}"
    print(line, flush=True)
    try:
        LOG.parent.mkdir(exist_ok=True)
        LOG.write_text((LOG.read_text(encoding="utf-8") if LOG.exists() else "") + line + "\n", encoding="utf-8")
        # garde 5000 lignes max
        lines = LOG.read_text(encoding="utf-8").splitlines()
        if len(lines) > 5000:
            LOG.write_text("\n".join(lines[-3000:])+"\n", encoding="utf-8")
    except: pass

def check_vocal():
    critiques=[]
    try:
        txt=VOCAL.read_text(encoding="utf-8")
        if "MAX_MS = 1800000" not in txt: critiques.append("CRITIQUE vocal: MAX_MS pas 30min (1800000)")
        if "MAX_S = 1800" not in txt: critiques.append("CRITIQUE vocal: MAX_S pas 1800")
        if 'SB_FALLBACK' not in txt: critiques.append("CRITIQUE vocal: SB_FALLBACK manquant → GO Pages cassé")
        if 'blobToDataURL' not in txt: critiques.append("CRITIQUE vocal: audioBase64 manquant → GO n'envoie pas l'audio")
        if 'preventScroll' not in txt: critiques.append("CRITIQUE vocal: no-scroll fix manquant → page qui saute")
        if 'restartChoice' not in txt: critiques.append("CRITIQUE vocal: bouton Choisir manquant")
        if 'restartVocal' not in txt: critiques.append("CRITIQUE vocal: bouton Restart manquant")
        if 'vu' not in txt.lower() or 'Analyser' not in txt: critiques.append("WARN vocal: vu-mètre manquant")
        if txt.count("30:00")<2: critiques.append("WARN vocal: timer 30:00 pas partout")
        if "transcription :" in txt.lower(): critiques.append("FAIL vocal: contient 'transcription :' interdit")
        if 'fetchWithFallback' not in txt: critiques.append("CRITIQUE vocal: fallback Pages→sandbox manquant")
        # script blocks
        m=re.findall(r'<script>', txt)
        if len(m)!=1: critiques.append(f"CRITIQUE vocal: attendu 1 <script>, trouvé {len(m)}")
    except Exception as e:
        critiques.append(f"FAIL vocal read: {e}")
    return critiques

def check_index():
    critiques=[]
    try:
        txt=INDEX.read_text(encoding="utf-8")
        if "Studio Vocal" not in txt: critiques.append("CRITIQUE index: CTA Studio Vocal manquant")
        if 'target="_blank"' not in txt: critiques.append("CRITIQUE index: target=_blank manquant sur CTA")
        # 3 blocs script
        blocks=re.findall(r'<script>', txt)
        if len(blocks)!=3: critiques.append(f"CRITIQUE index: attendu 3 <script>, trouvé {len(blocks)}")
        # fiches
        for fid in ["0-0","1-0","1-1","2-0","3-0","4-0","yemen"]:
            if fid not in txt: critiques.append(f"WARN index: fiche {fid} absente")
        if "transcription :" in txt.lower(): critiques.append("FAIL index: contient 'transcription :' interdit")
    except Exception as e:
        critiques.append(f"FAIL index read: {e}")
    return critiques

def check_server():
    critiques=[]
    # health
    try:
        with urllib.request.urlopen("http://127.0.0.1:4173/api/health", timeout=5) as r:
            j=json.loads(r.read())
            if not j.get("ok"): critiques.append("CRITIQUE server: /api/health not ok")
            # headers
            if r.headers.get("Permissions-Policy") != "microphone=*, camera=*":
                critiques.append("CRITIQUE server: Permissions-Policy manquant")
            if r.headers.get("Access-Control-Allow-Origin") != "*":
                critiques.append("CRITIQUE server: CORS manquant")
    except Exception as e:
        critiques.append(f"FAIL server health: {e}")
    # POST vocal audio
    try:
        import base64
        fake=base64.b64encode(b"AGENTTEST"*500).decode()
        payload={"fiche":"0-0","transcript":"agent test critique","words":3,"audioBase64":"data:audio/webm;base64,"+fake,"audioMime":"audio/webm"}
        data=json.dumps(payload).encode()
        req=urllib.request.Request("http://127.0.0.1:4173/api/vocal", data=data, headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            j=json.loads(r.read())
            if not j.get("ok"): critiques.append(f"CRITIQUE server: POST /api/vocal fail {j}")
            if not j.get("audio"): critiques.append("WARN server: POST n'a pas sauvé audio")
    except Exception as e:
        critiques.append(f"FAIL server POST: {e}")
    # check server.py content
    try:
        s=SERVER.read_text(encoding="utf-8")
        if "30 * 1024 * 1024" not in s: critiques.append("CRITIQUE server.py: MAX_BODY pas 30Mo")
        if "audioBase64" not in s: critiques.append("CRITIQUE server.py: audioBase64 non géré")
        if "git push" not in s: critiques.append("CRITIQUE server.py: auto git push manquant")
        if "MAX_BODY" not in s: critiques.append("CRITIQUE server.py: MAX_BODY manquant")
    except Exception as e:
        critiques.append(f"FAIL server.py read: {e}")
    return critiques

def check_audit():
    critiques=[]
    try:
        r=subprocess.run(["python3","tools/audit.py"], cwd=str(ROOT), capture_output=True, text=True, timeout=15)
        out=r.stdout+r.stderr
        if "Problèmes : 0" not in out: critiques.append(f"CRITIQUE audit: Problèmes !=0 → {out[:300]}")
        if "transcription" in out.lower(): critiques.append("WARN audit: mention transcription")
    except Exception as e:
        critiques.append(f"FAIL audit: {e}")
    return critiques

def check_pages_api():
    critiques=[]
    try:
        # via gh api si dispo, sinon skip
        r=subprocess.run(["gh","api","repos/jionni885-cell/study-board/contents/vocal.html","--jq",".size"], capture_output=True, text=True, timeout=10)
        if r.returncode==0:
            sz=int(r.stdout.strip() or 0)
            if sz < 50000: critiques.append(f"WARN pages: vocal.html size petit {sz}")
        else:
            critiques.append("WARN pages: gh api vocal.html fail")
        r2=subprocess.run(["gh","api","repos/jionni885-cell/study-board/pages","--jq",".status"], capture_output=True, text=True, timeout=10)
        if r2.returncode==0 and "built" not in r2.stdout:
            critiques.append(f"CRITIQUE pages: status {r2.stdout.strip()} != built")
    except Exception as e:
        critiques.append(f"WARN pages api: {e}")
    return critiques

def run_once(n):
    log(f"— Tour #{n} — test entier du site —", "CYCLE")
    all_crit=[]
    for name, fn in [("VOCAL",check_vocal),("INDEX",check_index),("SERVER",check_server),("AUDIT",check_audit),("PAGES",check_pages_api)]:
        try:
            c=fn()
            if c:
                for x in c: log(x, "CRITIQUE" if "CRITIQUE" in x or "FAIL" in x else "WARN")
                all_crit.extend(c)
            else:
                log(f"{name} OK", "OK")
        except Exception as e:
            log(f"{name} exception {e}", "FAIL")
            all_crit.append(str(e))
    # status.json
    try:
        STATUS.write_text(json.dumps({"tour":n,"ts":int(time.time()),"critiques":all_crit,"ok":len([x for x in all_crit if "CRITIQUE" in x or "FAIL" in x])==0}, ensure_ascii=False, indent=2), encoding="utf-8")
    except: pass
    if not all_crit:
        log("✅ Tour parfait — 0 critique", "OK")
    elif any("CRITIQUE" in x or "FAIL" in x for x in all_crit):
        log(f"❌ {len(all_crit)} critiques — je ne m'arrête pas, je re-teste", "FAIL")
    else:
        log(f"⚠️ {len(all_crit)} warns", "WARN")
    return all_crit

def main():
    LOG.parent.mkdir(exist_ok=True)
    log("🤖 Agent QA démarré — indépendant, critique en boucle", "START")
    n=1
    while True:
        try:
            run_once(n)
        except Exception as e:
            log(f"agent crash tour {n}: {e}", "FAIL")
        n+=1
        time.sleep(15)  # 45s entre tours, critique non-stop

if __name__=="__main__":
    main()
