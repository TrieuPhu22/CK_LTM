import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import List, Dict, Any

# Các module mới từ patch
from client_network import FootballServerClient
from favorites import add_team, add_player, list_favorites, remove_team, remove_player
from export_csv import export_list_of_dicts_csv

HOST = "127.0.0.1"
PORT = 65432

# Một vài giải đấu thường dùng (Football-Data codes)
COMMON_COMPETITIONS = [
    ("PL", "Premier League"),
    ("PD", "La Liga"),
    ("SA", "Serie A"),
    ("BL1", "Bundesliga"),
    ("FL1", "Ligue 1"),
    ("CL", "UEFA Champions League"),
]

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Football Client - LTM")
        self.geometry("1120x680")

        # Kết nối server
        self.api = FootballServerClient(host=HOST, port=PORT)
        try:
            self.api.connect()
            pong = self.api.request("PING", {})
            if not pong.get("ok", False):
                messagebox.showwarning("Warning", "Server connected nhưng PING lỗi.")
        except Exception as ex:
            messagebox.showerror("Không thể kết nối server", str(ex))

        # Thanh trên cùng (competition + days + refresh all)
        self._build_topbar()

        # Notebook tabs
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._build_tab_matches()
        self._build_tab_standings()
        self._build_tab_scorers()
        self._build_tab_search()

        # Status bar
        self.status = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status, anchor="w").pack(fill="x", padx=8, pady=(0, 8))

        # Tải mặc định
        self.refresh_all()

        # Đảm bảo đóng socket khi thoát
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ======= UI builders =======
    def _build_topbar(self):
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=8, pady=8)

        ttk.Label(frame, text="Competition:").pack(side="left")
        self.combo_comp = ttk.Combobox(frame, width=22, state="readonly",
                                       values=[f"{c} - {n}" for c, n in COMMON_COMPETITIONS])
        self.combo_comp.current(0)
        self.combo_comp.pack(side="left", padx=6)

        ttk.Label(frame, text="Days (matches):").pack(side="left", padx=(12, 0))
        self.var_days = tk.IntVar(value=7)
        sp = ttk.Spinbox(frame, from_=1, to=30, width=5, textvariable=self.var_days)
        sp.pack(side="left", padx=6)

        ttk.Button(frame, text="Refresh All", command=self.refresh_all).pack(side="left", padx=10)

        ttk.Separator(frame, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Button(frame, text="Favorites…", command=self.show_favorites_dialog).pack(side="left")

    def _build_tab_matches(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="Matches")

        toolbar = ttk.Frame(tab)
        toolbar.pack(fill="x", padx=8, pady=8)

        ttk.Button(toolbar, text="Load Matches", command=self.load_matches).pack(side="left")
        ttk.Button(toolbar, text="Export CSV", command=self.export_matches_csv).pack(side="left", padx=6)

        cols = ("utcDate", "competition", "homeTeam", "awayTeam", "status", "score_full")
        self.tv_matches = ttk.Treeview(tab, columns=cols, show="headings", height=18)
        for c in cols:
            self.tv_matches.heading(c, text=c)
            self.tv_matches.column(c, width=150 if c != "utcDate" else 180)

        self.tv_matches.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.matches_cache: List[Dict[str, Any]] = []

    def _build_tab_standings(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="Standings")

        toolbar = ttk.Frame(tab)
        toolbar.pack(fill="x", padx=8, pady=8)

        ttk.Button(toolbar, text="Load Standings", command=self.load_standings).pack(side="left")
        ttk.Button(toolbar, text="Export CSV", command=self.export_standings_csv).pack(side="left", padx=6)

        cols = ("position", "team", "playedGames", "won", "draw", "lost", "points", "goalsFor", "goalsAgainst", "goalDifference")
        self.tv_standings = ttk.Treeview(tab, columns=cols, show="headings", height=18)
        for c in cols:
            self.tv_standings.heading(c, text=c)
            self.tv_standings.column(c, width=100 if c != "team" else 220)
        self.tv_standings.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.standings_cache: List[Dict[str, Any]] = []

    def _build_tab_scorers(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="Scorers")

        toolbar = ttk.Frame(tab)
        toolbar.pack(fill="x", padx=8, pady=8)

        ttk.Button(toolbar, text="Load Scorers", command=self.load_scorers).pack(side="left")
        ttk.Button(toolbar, text="Export CSV", command=self.export_scorers_csv).pack(side="left", padx=6)

        cols = ("player", "team", "goals", "assists", "playedMatches", "position")
        self.tv_scorers = ttk.Treeview(tab, columns=cols, show="headings", height=18)
        for c in cols:
            self.tv_scorers.heading(c, text=c)
            self.tv_scorers.column(c, width=150 if c not in ("goals", "assists", "playedMatches") else 110)
        self.tv_scorers.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.scorers_cache: List[Dict[str, Any]] = []

    def _build_tab_search(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="Teams/Players")

        # Left: Teams search
        left = ttk.Labelframe(tab, text="Search Team")
        left.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        row = ttk.Frame(left); row.pack(fill="x", padx=8, pady=6)
        ttk.Label(row, text="Keyword:").pack(side="left")
        self.ent_team_q = ttk.Entry(row, width=28); self.ent_team_q.pack(side="left", padx=6)
        ttk.Button(row, text="Search", command=self.search_team).pack(side="left")
        ttk.Button(row, text="Add to Favorites", command=self.add_selected_team).pack(side="left", padx=6)

        self.tv_teams = ttk.Treeview(left, columns=("id", "name", "shortName", "tla", "area"), show="headings", height=16)
        for c in ("id", "name", "shortName", "tla", "area"):
            self.tv_teams.heading(c, text=c)
            self.tv_teams.column(c, width=120 if c != "name" else 220)
        self.tv_teams.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.teams_cache: List[Dict[str, Any]] = []

        # Right: Players of selected team (optional)
        right = ttk.Labelframe(tab, text="Team Players (by Team ID)")
        right.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        row2 = ttk.Frame(right); row2.pack(fill="x", padx=8, pady=6)
        ttk.Label(row2, text="Team ID:").pack(side="left")
        self.ent_team_id = ttk.Entry(row2, width=12); self.ent_team_id.pack(side="left", padx=6)
        ttk.Button(row2, text="Load Squad", command=self.load_team_players).pack(side="left")
        ttk.Button(row2, text="Add Player to Favorites", command=self.add_selected_player).pack(side="left", padx=6)

        self.tv_players = ttk.Treeview(right, columns=("id", "name", "position", "nationality", "dateOfBirth"), show="headings", height=16)
        for c in ("id", "name", "position", "nationality", "dateOfBirth"):
            self.tv_players.heading(c, text=c)
            self.tv_players.column(c, width=140 if c not in ("name") else 200)
        self.tv_players.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.players_cache: List[Dict[str, Any]] = []

    # ======= Helpers =======
    def _current_competition(self) -> str:
        val = self.combo_comp.get().split(" - ")[0].strip()
        return val or "PL"

    def _set_status(self, text: str):
        self.status.set(text)
        self.update_idletasks()

    # ======= Actions =======
    def refresh_all(self):
        self.load_matches()
        self.load_standings()
        self.load_scorers()

    def load_matches(self):
        comp = self._current_competition()
        days = max(1, int(self.var_days.get() or 7))
        self._set_status(f"Loading matches {comp} ({days} days)…")
        try:
            resp = self.api.request("MATCHES", {"competitionId": comp, "days": days})
            if not resp.get("ok"):
                raise RuntimeError(resp.get("message") or "MATCHES error")
            matches = (resp.get("data") or {}).get("matches", [])
            self.matches_cache = self._normalize_matches(matches)
            self._fill_tree(self.tv_matches, self.matches_cache, ("utcDate","competition","homeTeam","awayTeam","status","score_full"))
            self._set_status(f"Loaded {len(self.matches_cache)} matches.")
        except Exception as ex:
            messagebox.showerror("Matches", str(ex))
            self._set_status("Error while loading matches.")

    def load_standings(self):
        comp = self._current_competition()
        self._set_status(f"Loading standings {comp}…")
        try:
            resp = self.api.request("STANDINGS", {"competitionId": comp})
            if not resp.get("ok"):
                raise RuntimeError(resp.get("message") or "STANDINGS error")
            st = self._extract_standings(resp.get("data") or {})
            self.standings_cache = st
            self._fill_tree(self.tv_standings, st, ("position","team","playedGames","won","draw","lost","points","goalsFor","goalsAgainst","goalDifference"))
            self._set_status(f"Loaded {len(st)} standings rows.")
        except Exception as ex:
            messagebox.showerror("Standings", str(ex))
            self._set_status("Error while loading standings.")

    def load_scorers(self):
        comp = self._current_competition()
        self._set_status(f"Loading scorers {comp}…")
        try:
            resp = self.api.request("SCORERS", {"competitionId": comp})
            if not resp.get("ok"):
                raise RuntimeError(resp.get("message") or "SCORERS error")
            scorers = (resp.get("data") or {}).get("scorers", [])
            self.scorers_cache = self._normalize_scorers(scorers)
            self._fill_tree(self.tv_scorers, self.scorers_cache, ("player","team","goals","assists","playedMatches","position"))
            self._set_status(f"Loaded {len(self.scorers_cache)} scorers.")
        except Exception as ex:
            messagebox.showerror("Scorers", str(ex))
            self._set_status("Error while loading scorers.")

    def search_team(self):
        q = self.ent_team_q.get().strip()
        if not q:
            messagebox.showinfo("Search Team", "Nhập từ khoá team trước.")
            return
        self._set_status(f"Searching team: {q}…")
        try:
            resp = self.api.request("SEARCH_TEAM", {"q": q})
            if not resp.get("ok"):
                raise RuntimeError(resp.get("message") or "SEARCH_TEAM error")
            teams = (resp.get("data") or {}).get("teams", [])
            self.teams_cache = self._normalize_teams(teams)
            self._fill_tree(self.tv_teams, self.teams_cache, ("id","name","shortName","tla","area"))
            self._set_status(f"Found {len(self.teams_cache)} teams for '{q}'.")
        except Exception as ex:
            messagebox.showerror("Search Team", str(ex))
            self._set_status("Error while searching team.")

    def load_team_players(self):
        tid = self.ent_team_id.get().strip()
        if not tid.isdigit():
            messagebox.showinfo("Team Players", "Nhập Team ID (số). Bạn có thể chọn từ danh sách Teams ở trái để xem id.")
            return
        self._set_status(f"Loading players of team {tid}…")
        try:
            resp = self.api.request("TEAM", {"teamId": int(tid)})
            if not resp.get("ok"):
                raise RuntimeError(resp.get("message") or "TEAM error")
            squad = (resp.get("data") or {}).get("squad", [])
            self.players_cache = self._normalize_players(squad)
            self._fill_tree(self.tv_players, self.players_cache, ("id","name","position","nationality","dateOfBirth"))
            self._set_status(f"Loaded {len(self.players_cache)} players of team {tid}.")
        except Exception as ex:
            messagebox.showerror("Team Players", str(ex))
            self._set_status("Error while loading players.")

    # ======= Favorites & Export =======
    def add_selected_team(self):
        sel = self._get_selected_row(self.tv_teams, self.teams_cache)
        if not sel:
            messagebox.showinfo("Favorites", "Chọn một đội trong bảng bên trái.")
            return
        add_team(sel)
        messagebox.showinfo("Favorites", f"Đã thêm đội '{sel.get('name')}' vào favorites.")

    def add_selected_player(self):
        sel = self._get_selected_row(self.tv_players, self.players_cache)
        if not sel:
            messagebox.showinfo("Favorites", "Chọn một cầu thủ trong bảng bên phải.")
            return
        add_player(sel)
        messagebox.showinfo("Favorites", f"Đã thêm cầu thủ '{sel.get('name')}' vào favorites.")

    def show_favorites_dialog(self):
        favs = list_favorites()
        win = tk.Toplevel(self)
        win.title("Favorites")
        win.geometry("640x420")

        nb = ttk.Notebook(win); nb.pack(fill="both", expand=True, padx=8, pady=8)

        # Teams tab
        tab_t = ttk.Frame(nb); nb.add(tab_t, text="Teams")
        cols_t = ("id","name","shortName","tla","area")
        tv_t = ttk.Treeview(tab_t, columns=cols_t, show="headings", height=12)
        for c in cols_t:
            tv_t.heading(c, text=c); tv_t.column(c, width=120 if c != "name" else 220)
        tv_t.pack(fill="both", expand=True, padx=8, pady=(8, 0))

        for row in favs.get("teams", []):
            tv_t.insert("", "end", values=(row.get("id"), row.get("name"), row.get("shortName"), row.get("tla"), row.get("area")))

        def remove_team_action():
            item = tv_t.selection()
            if not item:
                return
            vals = tv_t.item(item, "values")
            if not vals:
                return
            remove_team(int(vals[0]))
            tv_t.delete(item)

        ttk.Button(tab_t, text="Remove Selected", command=remove_team_action).pack(pady=8)

        # Players tab
        tab_p = ttk.Frame(nb); nb.add(tab_p, text="Players")
        cols_p = ("id","name","position","nationality","dateOfBirth")
        tv_p = ttk.Treeview(tab_p, columns=cols_p, show="headings", height=12)
        for c in cols_p:
            tv_p.heading(c, text=c); tv_p.column(c, width=140 if c != "name" else 200)
        tv_p.pack(fill="both", expand=True, padx=8, pady=(8, 0))

        for row in favs.get("players", []):
            tv_p.insert("", "end", values=(row.get("id"), row.get("name"), row.get("position"), row.get("nationality"), row.get("dateOfBirth")))

        def remove_player_action():
            item = tv_p.selection()
            if not item:
                return
            vals = tv_p.item(item, "values")
            if not vals:
                return
            remove_player(int(vals[0]))
            tv_p.delete(item)

        ttk.Button(tab_p, text="Remove Selected", command=remove_player_action).pack(pady=8)

    def export_matches_csv(self):
        if not self.matches_cache:
            messagebox.showinfo("Export", "Chưa có dữ liệu Matches, vui lòng Load trước.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], initialfile="matches.csv")
        if not path:
            return
        export_list_of_dicts_csv(self.matches_cache, path, field_order=["utcDate","competition","homeTeam","awayTeam","status","score_full"])
        messagebox.showinfo("Export", f"Đã xuất {path}")

    def export_standings_csv(self):
        if not self.standings_cache:
            messagebox.showinfo("Export", "Chưa có dữ liệu Standings, vui lòng Load trước.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], initialfile="standings.csv")
        if not path:
            return
        export_list_of_dicts_csv(self.standings_cache, path, field_order=["position","team","playedGames","won","draw","lost","points","goalsFor","goalsAgainst","goalDifference"])
        messagebox.showinfo("Export", f"Đã xuất {path}")

    def export_scorers_csv(self):
        if not self.scorers_cache:
            messagebox.showinfo("Export", "Chưa có dữ liệu Scorers, vui lòng Load trước.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], initialfile="scorers.csv")
        if not path:
            return
        export_list_of_dicts_csv(self.scorers_cache, path, field_order=["player","team","goals","assists","playedMatches","position"])
        messagebox.showinfo("Export", f"Đã xuất {path}")

    # ======= Normalizers & Fillers =======
    def _normalize_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        rows = []
        for m in matches:
            comp = (m.get("competition") or {}).get("name")
            home = (m.get("homeTeam") or {}).get("name")
            away = (m.get("awayTeam") or {}).get("name")
            status = m.get("status")
            full = m.get("score", {}).get("fullTime", {})
            score_full = f"{full.get('home')} - {full.get('away')}"
            utc = m.get("utcDate")
            try:
                # chuẩn hoá date hiển thị
                dt = datetime.fromisoformat(utc.replace("Z", "+00:00"))
                utc_disp = dt.strftime("%Y-%m-%d %H:%M UTC")
            except Exception:
                utc_disp = utc
            rows.append({
                "utcDate": utc_disp,
                "competition": comp,
                "homeTeam": home,
                "awayTeam": away,
                "status": status,
                "score_full": score_full
            })
        return rows

    def _extract_standings(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        # football-data trả standings[0].table
        st = []
        standings = (data.get("standings") or [])
        table = []
        if standings:
            table = standings[0].get("table") or []
        for row in table:
            team_name = (row.get("team") or {}).get("name")
            st.append({
                "position": row.get("position"),
                "team": team_name,
                "playedGames": row.get("playedGames"),
                "won": row.get("won"),
                "draw": row.get("draw"),
                "lost": row.get("lost"),
                "points": row.get("points"),
                "goalsFor": row.get("goalsFor"),
                "goalsAgainst": row.get("goalsAgainst"),
                "goalDifference": row.get("goalDifference"),
            })
        return st

    def _normalize_scorers(self, scorers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        rows = []
        for s in scorers:
            player = (s.get("player") or {}).get("name")
            team = (s.get("team") or {}).get("name")
            goals = s.get("goals")
            assists = s.get("assists")
            played = s.get("playedMatches") or s.get("matches")
            position = (s.get("player") or {}).get("position")
            rows.append({
                "player": player,
                "team": team,
                "goals": goals,
                "assists": assists,
                "playedMatches": played,
                "position": position,
            })
        return rows

    def _normalize_teams(self, teams: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        rows = []
        for t in teams:
            rows.append({
                "id": t.get("id"),
                "name": t.get("name"),
                "shortName": t.get("shortName"),
                "tla": t.get("tla"),
                "area": (t.get("area") or {}).get("name"),
            })
        return rows

    def _normalize_players(self, squad: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        rows = []
        for p in squad:
            rows.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "position": p.get("position"),
                "nationality": p.get("nationality"),
                "dateOfBirth": p.get("dateOfBirth"),
            })
        return rows

    def _fill_tree(self, tv: ttk.Treeview, rows: List[Dict[str, Any]], cols: tuple):
        tv.delete(*tv.get_children())
        for r in rows:
            tv.insert("", "end", values=tuple(r.get(c, "") for c in cols))

    def _get_selected_row(self, tv: ttk.Treeview, cache: List[Dict[str, Any]]):
        sel = tv.selection()
        if not sel:
            return None
        idx = tv.index(sel[0])
        if 0 <= idx < len(cache):
            return cache[idx]
        return None

    # ======= Exit =======
    def on_close(self):
        try:
            self.api.close()
        except Exception:
            pass
        self.destroy()

if __name__ == "__main__":
    App().mainloop()
