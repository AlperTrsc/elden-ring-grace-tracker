import http.server
import json
import os
import sys
import threading
import time
import urllib.parse
import webbrowser

PORT = 8088
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'graces.json')
BOSS_FILE = os.path.join(BASE_DIR, 'data', 'bosses.json')
USER_SAVE_FILE = os.path.join(BASE_DIR, 'data', 'user_progress.json')
WEB_DIR = os.path.join(BASE_DIR, 'web')

def load_graces_raw():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_bosses_raw():
    if not os.path.exists(BOSS_FILE):
        return []
    with open(BOSS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_user_progress():
    default_p = {"discovered": [], "favorites": [], "notes": {}, "custom_markers": [], "defeated_bosses": []}
    if not os.path.exists(USER_SAVE_FILE):
        return default_p
    try:
        with open(USER_SAVE_FILE, 'r', encoding='utf-8') as f:
            p = json.load(f)
            for k, v in default_p.items():
                if k not in p:
                    p[k] = v
            return p
    except Exception as e:
        print(f"Error loading user progress: {e}")
        return default_p

def save_user_progress(data):
    os.makedirs(os.path.dirname(USER_SAVE_FILE), exist_ok=True)
    tmp_path = USER_SAVE_FILE + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, USER_SAVE_FILE)

class GraceHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/api/graces':
            graces = load_graces_raw()
            progress = load_user_progress()
            disc_set = set(progress.get("discovered", []))
            fav_set = set(progress.get("favorites", []))
            notes_dict = progress.get("notes", {})

            for g in graces:
                gid = g["id"]
                g["discovered"] = gid in disc_set
                g["favorite"] = gid in fav_set
                g["notes"] = notes_dict.get(gid, "")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(graces, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/bosses':
            bosses = load_bosses_raw()
            progress = load_user_progress()
            def_set = set(progress.get("defeated_bosses", []))
            for b in bosses:
                b["defeated"] = b["id"] in def_set

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(bosses, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/progress' or path == '/api/custom-markers':
            progress = load_user_progress()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(progress, ensure_ascii=False).encode('utf-8'))
            return

        # Serve static web files
        if path == '/' or path == '':
            self.path = '/index.html'

        try:
            return super().do_GET()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def copyfile(self, source, outputfile):
        try:
            super().copyfile(source, outputfile)
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/api/save':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode('utf-8'))
                save_user_progress(data)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                resp = {"status": "ok", "saved_at": time.time()}
                self.wfile.write(json.dumps(resp).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        elif path == '/api/reset':
            empty_progress = {"discovered": [], "favorites": [], "notes": {}}
            save_user_progress(empty_progress)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "reset_ok"}).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        # Keep console output clean
        pass

def run_server(port=PORT, open_browser=True):
    # Try specified port or next available
    server = None
    cur_port = port
    for _ in range(10):
        try:
            server = http.server.ThreadingHTTPServer(('127.0.0.1', cur_port), GraceHandler)
            break
        except OSError:
            cur_port += 1

    if not server:
        print(f"Error: Could not bind to port {port} or next 10 ports.")
        sys.exit(1)

    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    url = f"http://127.0.0.1:{cur_port}"
    print(f"\n=======================================================")
    print(f"  [+] ELDEN RING: SITES OF GRACE EXPLORER & TRACKER")
    print(f"  Sunucu basariyla baslatildi: {url}")
    print(f"  Durdurmak icin: Ctrl+C")
    print(f"=======================================================\n")

    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSunucu kapatılıyor...")
        server.shutdown()

if __name__ == '__main__':
    run_server()
