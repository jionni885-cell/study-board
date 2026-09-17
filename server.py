#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Study Board — serveur statique + API vocaux
  POST /api/vocal  -> {fiche, transcript, words, missing, ficheLabel, date} -> vocals/*.json
  GET  /api/vocals -> 50 derniers (merge serveur)
  GET  /api/health -> ok
Headers: Permissions-Policy microphone=*, camera=* + CORS:*
Port: 0.0.0.0:4173
Long vocaux 1-20min supportés (payload jusqu'à 20 Mo)
"""
import json
import os
import time
import base64
import subprocess
import threading
import urllib.parse
import mimetypes
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
VOCALS_DIR = ROOT / "vocals"
VOCALS_DIR.mkdir(exist_ok=True)

# s'assurer que .gitkeep existe
gitkeep = VOCALS_DIR / ".gitkeep"
if not gitkeep.exists():
    try:
        gitkeep.write_text("", encoding="utf-8")
    except: pass

MAX_BODY = 30 * 1024 * 1024  # 30 Mo (audio+json 20min ~19Mo webm)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # log discret
        try:
            print(f"[{time.strftime('%H:%M:%S')}] {format % args}")
        except: pass

    def end_headers(self):
        # Permissions + CORS pour tous
        self.send_header("Permissions-Policy", "microphone=*, camera=*")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "ts": int(time.time())}, ensure_ascii=False).encode())
            return
        if path == "/api/vocals":
            items = []
            try:
                for p in VOCALS_DIR.glob("*.json"):
                    if p.name == ".gitkeep":
                        continue
                    try:
                        d = json.loads(p.read_text(encoding="utf-8"))
                        # normalise
                        d["_file"] = p.name
                        if "date" not in d:
                            d["date"] = int(p.stat().st_mtime * 1000)
                        items.append(d)
                    except: pass
                # tri date desc
                items.sort(key=lambda x: x.get("date", 0), reverse=True)
                items = items[:50]
            except Exception as e:
                items = []
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(items, ensure_ascii=False).encode())
            return

        # fichier statique
        # décode
        rel = urllib.parse.unquote(path).lstrip("/")
        if rel == "" or rel.endswith("/"):
            rel = rel + "index.html" if rel == "" else rel + "index.html"
            # si path = "/" -> index.html
            if rel.startswith("/"):
                rel = rel.lstrip("/")
            if rel == "index.html" or rel == "":
                rel = "index.html"
        # sécurité: pas de ..
        target = (ROOT / rel).resolve()
        try:
            target.relative_to(ROOT)
        except:
            self.send_error(403, "Forbidden")
            return
        if target.is_dir():
            target = target / "index.html"
        if not target.exists() or not target.is_file():
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Not found")
            return
        ctype, _ = mimetypes.guess_type(str(target))
        if not ctype:
            ctype = "application/octet-stream"
        if ctype.startswith("text/"):
            ctype += "; charset=utf-8"
        try:
            data = target.read_bytes()
        except:
            self.send_error(500)
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        # éviter cache agressif pour html
        if target.suffix == ".html":
            self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/vocal":
            self.send_error(404, "Not found")
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            self.send_response(413)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "payload trop volumineux (max 20Mo)"}).encode())
            return
        try:
            raw = self.rfile.read(length) if length else b"{}"
        except:
            raw = b"{}"
        try:
            data = json.loads(raw.decode("utf-8") if raw else "{}")
        except:
            data = {}
        # normalisation
        fiche = str(data.get("fiche") or "0-0").strip()
        # fiche format mi-fi, fallback 0-0
        if not fiche or "-" not in fiche:
            fiche = "0-0"
        transcript = str(data.get("transcript") or data.get("text") or "").strip()
        words = data.get("words")
        if not isinstance(words, int):
            try:
                words = len(transcript.split())
            except:
                words = 0
        missing = data.get("missing") if isinstance(data.get("missing"), list) else []
        ficheLabel = str(data.get("ficheLabel") or data.get("fiche_label") or fiche).strip()[:200]
        date = data.get("date")
        if not isinstance(date, int):
            date = int(time.time()*1000)
        # durée estimée (mots / 130 * 60)
        duree = round(words/130*60) if words else 0
        # hesRatio si fourni sinon calcul simple
        hes = data.get("hesRatio")
        # id unique
        ts = int(time.time()*1000)
        safe_fiche = fiche.replace("/", "-").replace("..", "")
        fname = f"{ts}_{safe_fiche}.json"
        payload = {
            "fiche": fiche,
            "ficheLabel": ficheLabel or fiche,
            "transcript": transcript[:100000],  # garde tout mais limite 100k chars
            "words": words,
            "missing": missing[:50],
            "date": date,
            "ts": ts,
            "dureeSec": duree,
            "hesRatio": hes,
        }
        # copie aussi les champs optionnels utiles
        for k in ("niveau", "duree", "niveauLabel"):
            if k in data:
                payload[k] = data[k]
        # ajoute id
        payload["id"] = fname.replace(".json", "")
        # --- audio optionnel (base64) ---
        audio_b64 = data.get("audioBase64") or data.get("audio") or ""
        audio_mime = str(data.get("audioMime") or data.get("audioType") or "").strip()
        audio_ext = "webm"
        if "mp4" in audio_mime: audio_ext="m4a"
        elif "ogg" in audio_mime: audio_ext="ogg"
        elif "wav" in audio_mime: audio_ext="wav"
        elif "webm" in audio_mime: audio_ext="webm"
        # si data URL, strip prefix
        if isinstance(audio_b64, str) and audio_b64.startswith("data:"):
            try:
                # data:audio/webm;base64,XXXX
                header, b64 = audio_b64.split(",",1)
                audio_b64=b64
                if "mp4" in header: audio_ext="m4a"
                elif "ogg" in header: audio_ext="ogg"
            except: pass
        audio_fname = None
        audio_path = None
        if isinstance(audio_b64, str) and len(audio_b64) > 100:
            try:
                # nettoie espaces/newlines
                b64clean = "".join(audio_b64.split())
                audio_bytes = base64.b64decode(b64clean)
                if 100 < len(audio_bytes) < 28*1024*1024:
                    audio_fname = f"{payload['id']}.{audio_ext}"
                    audio_path = VOCALS_DIR / audio_fname
                    audio_path.write_bytes(audio_bytes)
                    payload["audioFile"] = audio_fname
                    payload["audioMime"] = audio_mime or f"audio/{audio_ext}"
                    payload["audioBytes"] = len(audio_bytes)
                    print(f"[vocal] audio saved {audio_fname} {len(audio_bytes)} bytes")
            except Exception as e:
                print(f"[vocal] audio decode fail: {e}")
        out = VOCALS_DIR / fname
        try:
            out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
            return
        # --- auto git commit+push en arrière-plan (pour GO) — gère le rebase si remote a bougé (ex: push direct GitHub API) ---
        def _git_push():
            try:
                files = [str(out)]
                if audio_path and audio_path.exists():
                    files.append(str(audio_path))
                subprocess.run(["git","add"]+files, cwd=str(ROOT), timeout=10)
                st = subprocess.run(["git","status","--porcelain"]+files, cwd=str(ROOT), capture_output=True, text=True, timeout=10)
                if not st.stdout.strip():
                    print("[vocal] nothing to commit")
                    return
                msg = f"vocal: {fiche} {words} mots {payload['id']}"
                if audio_fname: msg += f" +audio {audio_ext}"
                subprocess.run(["git","commit","-m",msg], cwd=str(ROOT), timeout=10)
                # tente push, si non-fast-forward → fetch + rebase puis repush
                r = subprocess.run(["git","push","origin","HEAD:main"], cwd=str(ROOT), capture_output=True, text=True, timeout=30)
                if r.returncode != 0 and "non-fast-forward" in (r.stderr or "") + (r.stdout or ""):
                    print("[vocal] push non-fast-forward, fetch+rebase")
                    subprocess.run(["git","fetch","origin","main"], cwd=str(ROOT), timeout=15)
                    subprocess.run(["git","rebase","origin/main"], cwd=str(ROOT), timeout=15)
                    subprocess.run(["git","push","origin","HEAD:main"], cwd=str(ROOT), timeout=30)
                print(f"[vocal] git push done {payload['id']}")
            except Exception as e:
                print(f"[vocal] git push fail: {e}")
        try:
            threading.Thread(target=_git_push, daemon=True).start()
        except: pass
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "id": payload["id"], "words": words, "audio": bool(audio_path)}).encode())

def run():
    # mimetypes
    mimetypes.add_type("text/html", ".html")
    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("application/javascript", ".js")
    mimetypes.add_type("audio/mpeg", ".mp3")
    mimetypes.add_type("audio/mp4", ".m4a")
    addr = ("0.0.0.0", 4173)
    httpd = ThreadingHTTPServer(addr, Handler)
    httpd.timeout = 30
    print(f"Study Board server → http://0.0.0.0:4173/  (root={ROOT})")
    print(f"  POST /api/vocal  (max {MAX_BODY//1024//1024}Mo)  → vocals/*.json")
    print(f"  GET  /api/vocals (50 derniers)")
    print(f"  GET  /api/health")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run()
