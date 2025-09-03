import tkinter as tk
from tkinter import ttk, messagebox
import socket, json, time, csv
from datetime import datetime
from pathlib import Path
from modern_theme import HOST, PORT, FORMAT, COMPETITIONS, ModernTheme, EXPORT_DIR, DARK_MODE_DEFAULT

# ==================== Utils & Mixins ====================
FAV_FILE = Path("favorites.json")

def safe_send(sock, text: str):
    try:
        sock.sendall(text.encode(FORMAT))
        return True
    except Exception:
        return False

def safe_recv(sock, buf=65536):
    try:
        data = sock.recv(buf).decode(FORMAT)
        return json.loads(data) if data else {}
    except Exception:
        return {"error": True, "message": "Failed to parse or receive data"}

def ensure_export_dir():
    Path(EXPORT_DIR).mkdir(parents=True, exist_ok=True)

def export_csv(filename, rows, headers):
    ensure_export_dir()
    path = Path(EXPORT_DIR) / filename
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    return str(path)

class ConnectionMixin:
    def connect_with_retry(self, attempts=3, delay=0.8):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        last = None
        for i in range(attempts):
            try:
                self.client.connect((HOST, PORT))
                ready = self.client.recv(1024).decode(FORMAT)
                if ready == "READY":
                    return True
            except Exception as e:
                last = e
                time.sleep(delay * (i+1))
        messagebox.showerror("Connection", f"Không thể kết nối server: {last}")
        return False

class FavoritesMixin:
    def load_favorites(self):
        if FAV_FILE.exists():
            try:
                return json.loads(FAV_FILE.read_text(encoding="utf-8"))
            except Exception:
                return {"teams": [], "players": []}
        return {"teams": [], "players": []}

    def save_favorites(self):
        FAV_FILE.write_text(json.dumps(self.favorites, ensure_ascii=False, indent=2), encoding="utf-8")

    def toggle_favorite_team(self, team_name):
        arr = self.favorites.setdefault("teams", [])
        if team_name in arr:
            arr.remove(team_name)
        else:
            arr.append(team_name)
        self.save_favorites()
        messagebox.showinfo("Favorites", f"Đội yêu thích: {', '.join(arr) or '—'}")


# ==================== Main App ====================
class ModernFootballApp(ConnectionMixin, FavoritesMixin, tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("⚽ Football Hub - Modern Edition")
        self.geometry("1400x900")
        self.configure(background=ModernTheme.MAIN_BG)
        self.minsize(1200, 800)

        # Data
        self.teams = {}
        self.players = {}
        self.favorites = self.load_favorites()

        # UI
        self.create_header()
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()

        # Connect
        self.connect_with_retry()
