import socket
import threading
import requests
import json
import time
from datetime import datetime

# ---- Basic settings ----
HOST = "127.0.0.1"
PORT = 65432
FORMAT = "utf8"

API_KEY = "b0fc31c76f204a5f81d3adfd97ecd66d"
API_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}

REQUEST_TIMEOUT = 8  # seconds
MAX_RETRIES = 3
RETRY_BACKOFF = 0.7  # seconds
CACHE_TTL = 60  # seconds

_cache = {}  # key -> (expires_at_ts, data)


# ====== Cache helpers ======
def _cache_get(key):
    item = _cache.get(key)
    if not item:
        return None
    expires_at, data = item
    if time.time() > expires_at:
        _cache.pop(key, None)
        return None
    return data


def _cache_set(key, data, ttl=CACHE_TTL):
    _cache[key] = (time.time() + ttl, data)


def http_get(path, params=None, ttl=CACHE_TTL):
    """GET with retry + timeout + cache"""
    key = ("GET", path, json.dumps(params or {}, sort_keys=True))
    cached = _cache_get(key)
    if cached is not None:
        return cached

    url = f"{API_URL}{path}"
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            _cache_set(key, data, ttl=ttl)
            return data
        except Exception as e:
            last_err = e
            time.sleep(RETRY_BACKOFF * attempt)

    return {"error": True, "message": f"API request failed: {last_err}"}


# ====== API wrappers ======
def get_competitions():
    return http_get("/competitions", params={"plan": "TIER_ONE"}, ttl=3600)


def get_matches_by_comp(comp_id):
    return http_get(f"/competitions/{comp_id}/matches", params={"season": datetime.now().year})


def get_standings(comp_id):
    return http_get(f"/competitions/{comp_id}/standings")


def search_teams(name):
    return http_get("/teams", params={"name": name})


# ====== Socket server ======
def handle_client(conn, addr):
    try:
        conn.sendall("READY".encode(FORMAT))
        while True:
            option = conn.recv(4096).decode(FORMAT)
            if not option:
                break

            parts = option.split()
            cmd = parts[0].lower()

            if cmd == "health":
                conn.sendall(json.dumps({"ok": True, "time": datetime.utcnow().isoformat() + "Z"}).encode(FORMAT))

            elif cmd == "competitions":
                data = get_competitions()
                conn.sendall(json.dumps(data).encode(FORMAT))

            elif cmd == "matches" and len(parts) >= 2:
                comp_id = parts[1]
                data = get_matches_by_comp(comp_id)
                conn.sendall(json.dumps(data).encode(FORMAT))

            elif cmd == "standings" and len(parts) >= 2:
                comp_id = parts[1]
                data = get_standings(comp_id)
                conn.sendall(json.dumps(data).encode(FORMAT))

            elif cmd == "teams" and len(parts) >= 2:
                name = " ".join(parts[1:])
                data = search_teams(name)
                conn.sendall(json.dumps(data).encode(FORMAT))

            else:
                conn.sendall(json.dumps({"error": True, "message": "Unknown command"}).encode(FORMAT))

    except Exception as e:
        try:
            conn.sendall(json.dumps({"error": True, "message": f"Server error: {e}"}).encode(FORMAT))
        except Exception:
            pass
    finally:
        conn.close()


def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"[{datetime.now().isoformat()}] Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    run_server()
