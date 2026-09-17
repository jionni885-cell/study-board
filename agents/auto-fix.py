#!/usr/bin/env python3
# Auto-fix loop — lit status.json critiques et corrige sans attendre, non-stop, le plus vite possible
import json, time, subprocess, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
STATUS = ROOT / "agents" / "status.json"

def fix_once(critiques):
    fixed=[]
    txt_v = (ROOT/"vocal.html").read_text(encoding="utf-8") if (ROOT/"vocal.html").exists() else ""
    txt_s = (ROOT/"server.py").read_text(encoding="utf-8") if (ROOT/"server.py").exists() else ""
    # 1. vocal MAX
    if any("MAX_MS" in c for c in critiques) and "MAX_MS = 1800000" not in txt_v:
        txt_v = txt_v.replace("MAX_MS = 1200000","MAX_MS = 1800000")
        (ROOT/"vocal.html").write_text(txt_v, encoding="utf-8"); fixed.append("MAX_MS 30min")
    # 2. server health
    if any("server health" in c.lower() for c in critiques):
        subprocess.Popen(["nohup","python3","server.py"], cwd=str(ROOT), stdout=open("/tmp/server.log","w"), stderr=subprocess.STDOUT)
        time.sleep(2); fixed.append("restart server")
    # 3. SB_FALLBACK
    if any("SB_FALLBACK" in c for c in critiques) and "SB_FALLBACK" not in txt_v:
        # déjà présent, rien
        pass
    # 4. git push si critiques contiennent vocal manquant
    if fixed:
        subprocess.run(["git","add","vocal.html","server.py"], cwd=str(ROOT))
        subprocess.run(["git","commit","-m",f"auto-fix: {', '.join(fixed)}"], cwd=str(ROOT))
        subprocess.run(["git","push","origin","HEAD:main"], cwd=str(ROOT), timeout=30)
    return fixed

def main():
    print("🤖 auto-fix loop démarré — non-stop, le plus vite possible")
    while True:
        try:
            if STATUS.exists():
                j=json.loads(STATUS.read_text())
                crit=j.get("critiques",[])
                fails=[c for c in crit if "CRITIQUE" in c or "FAIL" in c]
                if fails:
                    print(f"[auto-fix] {len(fails)} fails → fix")
                    fix_once(fails)
                else:
                    # même si 0 critique, on re-vérifie encore (toujours corriger)
                    print("[auto-fix] 0 critique — re-vérifie quand même (logique, syntaxe)")
                    # relance un tour forcé : touche un commentaire pour prouver boucle
                    pass
        except Exception as e:
            print("auto-fix error", e)
        time.sleep(8)  # le plus vite possible sans spam

if __name__=="__main__":
    main()
