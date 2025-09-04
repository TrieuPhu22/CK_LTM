import tkinter as tk
from tkinter import ttk, messagebox
import socket
import json
from datetime import datetime


# Theme colors
class Colors:
    PRIMARY = "#1e3a8a"
    SECONDARY = "#3b82f6"
    SUCCESS = "#10b981"
    DANGER = "#ef4444"
    MAIN_BG = "#f8fafc"
    CARD_BG = "#ffffff"
    SIDEBAR_BG = "#1e293b"
    HEADER_BG = "#0f172a"
    WHITE_TEXT = "#ffffff"


# Connection settings
HOST = "127.0.0.1"
PORT = 65432
FORMAT = "utf8"

COMPETITIONS = {
    "All Competitions": "all",
    "Premier League": "2021",
    "La Liga": "2014",
    "Bundesliga": "2002",
    "Serie A": "2019",
    "Champions League": "2001",
}


class ModernFootballApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("⚽ Football Hub - Modern Edition")
        self.geometry("1400x900")
        self.configure(background=Colors.MAIN_BG)
        self.minsize(1200, 800)

        # Initialize variables
        self.teams = {}
        self.players = {}

        # Create UI
        self.create_header()
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()

        # Connect to server
        self.connect_to_server()

        # Tự động gửi UDP message sau 2 giây
        self.after(2000, self.send_udp_message)

    def create_header(self):
        """Create modern header"""
        header = tk.Frame(self, background=Colors.HEADER_BG, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Title
        title_frame = tk.Frame(header, background=Colors.HEADER_BG)
        title_frame.pack(side="left", padx=20, pady=20)

        tk.Label(title_frame, text="⚽ Football Hub",
                 font=("Segoe UI", 24, "bold"),
                 background=Colors.HEADER_BG,
                 foreground=Colors.WHITE_TEXT).pack(side="left")

        tk.Label(title_frame, text="Real-time Football Data & Analytics",
                 font=("Segoe UI", 12),
                 background=Colors.HEADER_BG,
                 foreground="#94a3b8").pack(side="left", padx=(10, 0))

        # Controls
        controls_frame = tk.Frame(header, background=Colors.HEADER_BG)
        controls_frame.pack(side="right", padx=20, pady=20)

        tk.Label(controls_frame, text="Competition:",
                 font=("Segoe UI", 11),
                 background=Colors.HEADER_BG,
                 foreground=Colors.WHITE_TEXT).pack(side="left", padx=(0, 10))

        self.comp_var = tk.StringVar(value="Premier League")
        self.comp_combo = ttk.Combobox(controls_frame, textvariable=self.comp_var,
                                       values=list(COMPETITIONS.keys()),
                                       state="readonly", width=15)
        self.comp_combo.pack(side="left", padx=(0, 20))

        refresh_btn = tk.Button(controls_frame, text="🔄 Refresh",
                                command=self.refresh_all,
                                font=("Segoe UI", 11, "bold"),
                                background=Colors.SECONDARY,
                                foreground=Colors.WHITE_TEXT,
                                relief="flat", cursor="hand2")
        refresh_btn.pack(side="left")

    def create_sidebar(self):
        """Create navigation sidebar"""
        sidebar = tk.Frame(self, background=Colors.SIDEBAR_BG, width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        nav_buttons = [
            ("📅 Matches", self.show_matches),
            ("🏆 Standings", self.show_standings),
            ("⚽ Scorers", self.show_scorers),
            ("👥 Teams", self.show_teams),
            ("👤 Players", self.show_players),
        ]

        for text, command in nav_buttons:
            btn = tk.Button(sidebar, text=text, command=command,
                            font=("Segoe UI", 11),
                            background=Colors.SIDEBAR_BG,
                            foreground=Colors.WHITE_TEXT,
                            relief="flat", cursor="hand2",
                            anchor="w", padx=20, pady=15)
            btn.pack(fill="x", padx=10, pady=2)

            # Hover effects
            btn.bind("<Enter>", lambda e, b=btn: b.configure(background=Colors.PRIMARY))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(background=Colors.SIDEBAR_BG))

    def create_main_content(self):
        """Create main content area"""
        self.main_frame = tk.Frame(self, background=Colors.MAIN_BG)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Create notebook
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True)

        # Create tabs
        self.create_matches_tab()
        self.create_standings_tab()
        self.create_scorers_tab()
        self.create_teams_tab()
        self.create_players_tab()

    def create_matches_tab(self):
        """Create matches tab"""
        self.tab_matches = tk.Frame(self.notebook, background=Colors.MAIN_BG)
        self.notebook.add(self.tab_matches, text="📅 Matches")

        # Filter frame
        filter_frame = tk.Frame(self.tab_matches, background=Colors.CARD_BG, relief="flat", bd=1)
        filter_frame.pack(fill="x", padx=10, pady=(0, 20))

        tk.Label(filter_frame, text="Match Filters",
                 font=("Segoe UI", 14, "bold"),
                 background=Colors.CARD_BG).pack(anchor="w", padx=15, pady=(15, 10))

        controls = tk.Frame(filter_frame, background=Colors.CARD_BG)
        controls.pack(fill="x", padx=15, pady=(0, 15))

        # Filters
        tk.Label(controls, text="Date Range:", background=Colors.CARD_BG).pack(side="left", padx=(0, 10))

        self.days_var = tk.StringVar(value="7")
        ttk.Combobox(controls, textvariable=self.days_var,
                     values=["1", "3", "7", "14", "30"],
                     width=8, state="readonly").pack(side="left", padx=(0, 20))

        tk.Label(controls, text="Status:", background=Colors.CARD_BG).pack(side="left", padx=(0, 10))

        self.status_var = tk.StringVar(value="All")
        ttk.Combobox(controls, textvariable=self.status_var,
                     values=["All", "Live", "Finished", "Scheduled"],
                     width=12, state="readonly").pack(side="left", padx=(0, 20))

        load_btn = tk.Button(controls, text="📥 Load Matches",
                             command=self.load_matches,
                             font=("Segoe UI", 11, "bold"),
                             background=Colors.PRIMARY,
                             foreground=Colors.WHITE_TEXT,
                             relief="flat", cursor="hand2")
        load_btn.pack(side="right")

        # Matches table
        self.create_matches_table()

    def create_matches_table(self):
        """Create matches table"""
        table_frame = tk.Frame(self.tab_matches, background=Colors.CARD_BG, relief="flat", bd=1)
        table_frame.pack(fill="both", expand=True, padx=10)

        tk.Label(table_frame, text="Match Results",
                 font=("Segoe UI", 14, "bold"),
                 background=Colors.CARD_BG).pack(anchor="w", padx=15, pady=(15, 10))

        # Treeview frame
        tree_frame = tk.Frame(table_frame, background=Colors.CARD_BG)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame)
        v_scroll.pack(side="right", fill="y")

        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal")
        h_scroll.pack(side="bottom", fill="x")

        # Treeview
        # Thêm cột "league" vào danh sách columns
        columns = ("date", "time", "home", "score", "away", "status", "league")
        self.matches_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                         yscrollcommand=v_scroll.set,
                                         xscrollcommand=h_scroll.set)

        # Configure columns - Thêm cột "league" vào headers
        headers = [("date", "Date", 100), ("time", "Time", 80), ("home", "Home Team", 200),
                   ("score", "Score", 80), ("away", "Away Team", 200), ("status", "Status", 120),
                   ("league", "League", 150)]  # Thêm cột League

        for col, heading, width in headers:
            self.matches_tree.heading(col, text=heading)
            self.matches_tree.column(col, width=width, minwidth=width)

        self.matches_tree.pack(fill="both", expand=True)

        v_scroll.config(command=self.matches_tree.yview)
        h_scroll.config(command=self.matches_tree.xview)

    def create_standings_tab(self):
        """Create standings tab"""
        self.tab_standings = tk.Frame(self.notebook, background=Colors.MAIN_BG)
        self.notebook.add(self.tab_standings, text="🏆 Standings")

        # Control frame
        control_frame = tk.Frame(self.tab_standings, background=Colors.CARD_BG, relief="flat", bd=1)
        control_frame.pack(fill="x", padx=10, pady=(0, 20))

        tk.Label(control_frame, text="League Standings",
                 font=("Segoe UI", 14, "bold"),
                 background=Colors.CARD_BG).pack(anchor="w", padx=15, pady=15)

        load_standings_btn = tk.Button(control_frame, text="📥 Load Standings",
                                       command=self.load_standings,
                                       font=("Segoe UI", 11, "bold"),
                                       background=Colors.PRIMARY,
                                       foreground=Colors.WHITE_TEXT,
                                       relief="flat", cursor="hand2")
        load_standings_btn.pack(anchor="e", padx=15, pady=(0, 15))

        # Standings table
        self.create_standings_table()

    def create_standings_table(self):
        """Create standings table"""
        table_frame = tk.Frame(self.tab_standings, background=Colors.CARD_BG, relief="flat", bd=1)
        table_frame.pack(fill="both", expand=True, padx=10)

        tree_frame = tk.Frame(table_frame, background=Colors.CARD_BG)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=15)

        v_scroll = ttk.Scrollbar(tree_frame)
        v_scroll.pack(side="right", fill="y")

        columns = ("pos", "team", "played", "won", "draw", "lost", "gf", "ga", "gd", "points")
        self.standings_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                           yscrollcommand=v_scroll.set)

        headers = [("pos", "Pos", 50), ("team", "Team", 200), ("played", "P", 60),
                   ("won", "W", 60), ("draw", "D", 60), ("lost", "L", 60),
                   ("gf", "GF", 60), ("ga", "GA", 60), ("gd", "GD", 60), ("points", "Pts", 60)]

        for col, heading, width in headers:
            self.standings_tree.heading(col, text=heading)
            self.standings_tree.column(col, width=width, minwidth=width)

        self.standings_tree.pack(fill="both", expand=True)
        v_scroll.config(command=self.standings_tree.yview)

    def create_scorers_tab(self):
        """Create scorers tab"""
        self.tab_scorers = tk.Frame(self.notebook, background=Colors.MAIN_BG)
        self.notebook.add(self.tab_scorers, text="⚽ Scorers")

        # Similar structure to standings
        control_frame = tk.Frame(self.tab_scorers, background=Colors.CARD_BG, relief="flat", bd=1)
        control_frame.pack(fill="x", padx=10, pady=(0, 20))

        tk.Label(control_frame, text="Top Scorers",
                 font=("Segoe UI", 14, "bold"),
                 background=Colors.CARD_BG).pack(anchor="w", padx=15, pady=15)

        load_scorers_btn = tk.Button(control_frame, text="📥 Load Scorers",
                                     command=self.load_scorers,
                                     font=("Segoe UI", 11, "bold"),
                                     background=Colors.PRIMARY,
                                     foreground=Colors.WHITE_TEXT,
                                     relief="flat", cursor="hand2")
        load_scorers_btn.pack(anchor="e", padx=15, pady=(0, 15))

        self.create_scorers_table()

    def create_scorers_table(self):
        """Create scorers table"""
        table_frame = tk.Frame(self.tab_scorers, background=Colors.CARD_BG, relief="flat", bd=1)
        table_frame.pack(fill="both", expand=True, padx=10)

        tree_frame = tk.Frame(table_frame, background=Colors.CARD_BG)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=15)

        v_scroll = ttk.Scrollbar(tree_frame)
        v_scroll.pack(side="right", fill="y")

        columns = ("rank", "player", "team", "goals", "assists", "position", "nationality")
        self.scorers_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                         yscrollcommand=v_scroll.set)

        headers = [("rank", "Rank", 60), ("player", "Player", 200), ("team", "Team", 150),
                   ("goals", "Goals", 80), ("assists", "Assists", 80),
                   ("position", "Position", 100), ("nationality", "Nationality", 100)]

        for col, heading, width in headers:
            self.scorers_tree.heading(col, text=heading)
            self.scorers_tree.column(col, width=width, minwidth=width)

        self.scorers_tree.pack(fill="both", expand=True)
        v_scroll.config(command=self.scorers_tree.yview)

    def create_teams_tab(self):
        """Create teams tab"""
        self.tab_teams = tk.Frame(self.notebook, background=Colors.MAIN_BG)
        self.notebook.add(self.tab_teams, text="👥 Teams")

        # Team selector
        selector_frame = tk.Frame(self.tab_teams, background=Colors.CARD_BG, relief="flat", bd=1)
        selector_frame.pack(fill="x", padx=10, pady=(0, 20))

        tk.Label(selector_frame, text="Team Information",
                 font=("Segoe UI", 14, "bold"),
                 background=Colors.CARD_BG).pack(anchor="w", padx=15, pady=(15, 10))

        controls = tk.Frame(selector_frame, background=Colors.CARD_BG)
        controls.pack(fill="x", padx=15, pady=(0, 15))

        tk.Label(controls, text="Select Team:", background=Colors.CARD_BG).pack(side="left", padx=(0, 10))

        self.team_var = tk.StringVar()
        self.team_combo = ttk.Combobox(controls, textvariable=self.team_var,
                                       values=[], state="readonly", width=30)
        self.team_combo.pack(side="left", padx=(0, 10))

        load_team_btn = tk.Button(controls, text="📥 Load Team Info",
                                  command=self.load_team_info,
                                  font=("Segoe UI", 11, "bold"),
                                  background=Colors.PRIMARY,
                                  foreground=Colors.WHITE_TEXT,
                                  relief="flat", cursor="hand2")
        load_team_btn.pack(side="left")

        # Team info display
        info_frame = tk.Frame(self.tab_teams, background=Colors.CARD_BG, relief="flat", bd=1)
        info_frame.pack(fill="both", expand=True, padx=10)

        self.team_info_text = tk.Text(info_frame, font=("Segoe UI", 11),
                                      background=Colors.CARD_BG,
                                      relief="flat", wrap="word")
        self.team_info_text.pack(fill="both", expand=True, padx=15, pady=15)

    def create_players_tab(self):
        """Create players tab"""
        self.tab_players = tk.Frame(self.notebook, background=Colors.MAIN_BG)
        self.notebook.add(self.tab_players, text="👤 Players")

        # Similar to teams tab
        selector_frame = tk.Frame(self.tab_players, background=Colors.CARD_BG, relief="flat", bd=1)
        selector_frame.pack(fill="x", padx=10, pady=(0, 20))

        tk.Label(selector_frame, text="Player Information",
                 font=("Segoe UI", 14, "bold"),
                 background=Colors.CARD_BG).pack(anchor="w", padx=15, pady=(15, 10))

        controls = tk.Frame(selector_frame, background=Colors.CARD_BG)
        controls.pack(fill="x", padx=15, pady=(0, 15))

        tk.Label(controls, text="Select Player:", background=Colors.CARD_BG).pack(side="left", padx=(0, 10))

        self.player_var = tk.StringVar()
        self.player_combo = ttk.Combobox(controls, textvariable=self.player_var,
                                         values=[], state="readonly", width=30)
        self.player_combo.pack(side="left", padx=(0, 10))

        load_player_btn = tk.Button(controls, text="📥 Load Player Info",
                                    command=self.load_player_info,
                                    font=("Segoe UI", 11, "bold"),
                                    background=Colors.PRIMARY,
                                    foreground=Colors.WHITE_TEXT,
                                    relief="flat", cursor="hand2")
        load_player_btn.pack(side="left")

        info_frame = tk.Frame(self.tab_players, background=Colors.CARD_BG, relief="flat", bd=1)
        info_frame.pack(fill="both", expand=True, padx=10)

        self.player_info_text = tk.Text(info_frame, font=("Segoe UI", 11),
                                        background=Colors.CARD_BG,
                                        relief="flat", wrap="word")
        self.player_info_text.pack(fill="both", expand=True, padx=15, pady=15)

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = tk.Frame(self, background=Colors.HEADER_BG, height=30)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)

        self.status_label = tk.Label(self.status_bar, text="Ready",
                                     font=("Segoe UI", 10),
                                     background=Colors.HEADER_BG,
                                     foreground=Colors.WHITE_TEXT,
                                     anchor="w")
        self.status_label.pack(side="left", padx=10, pady=5)

        # Thêm nút UDP
        udp_btn = tk.Button(self.status_bar, text="Send UDP",
                            command=self.send_udp_message,
                            font=("Segoe UI", 9),
                            background=Colors.SECONDARY,
                            foreground=Colors.WHITE_TEXT,
                            relief="flat", cursor="hand2")
        udp_btn.pack(side="left", padx=10, pady=2)

        self.connection_label = tk.Label(self.status_bar, text="🟢 Connected",
                                         font=("Segoe UI", 10),
                                         background=Colors.HEADER_BG,
                                         foreground=Colors.SUCCESS,
                                         anchor="e")
        self.connection_label.pack(side="right", padx=10, pady=5)

    # Navigation methods
    def show_matches(self):
        self.notebook.select(0)

    def show_standings(self):
        self.notebook.select(1)

    def show_scorers(self):
        self.notebook.select(2)

    def show_teams(self):
        self.notebook.select(3)

    def show_players(self):
        self.notebook.select(4)

    # Server connection
    def connect_to_server(self):
        """Connect to server"""
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((HOST, PORT))
            self.update_status("Connected to server")
            self.connection_label.configure(text="🟢 Connected", foreground=Colors.SUCCESS)
        except Exception as e:
            self.update_status(f"Connection failed: {str(e)}")
            self.connection_label.configure(text="🔴 Disconnected", foreground=Colors.DANGER)
            messagebox.showerror("Connection Error", f"Could not connect to server:\n{str(e)}")

    def safe_recv(self):
        """Safely receive data"""
        try:
            data = self.client.recv(65535).decode(FORMAT)
            return json.loads(data)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid data received from server")
            return {}
        except Exception as e:
            messagebox.showerror("Error", f"Communication error: {str(e)}")
            return {}

    def update_status(self, message):
        """Update status bar"""
        self.status_label.configure(text=message)

    def get_competition_id(self):
        """Get competition ID"""
        selected = self.comp_var.get()
        return COMPETITIONS.get(selected, "2021")

    # Data loading methods
    def load_matches(self):
        """Load matches"""
        self.update_status("Loading matches...")

        try:
            comp_id = self.get_competition_id()
            days = self.days_var.get()

            # Clear existing data
            self.matches_tree.delete(*self.matches_tree.get_children())

            if comp_id == "all":
                # Nếu chọn "All Competitions", tải trận đấu từ tất cả các giải
                all_matches = []
                comp_count = 0

                for comp_name, comp_code in COMPETITIONS.items():
                    if comp_code == "all":  # Bỏ qua tùy chọn "All Competitions"
                        continue

                    self.update_status(f"Loading matches from {comp_name}...")
                    self.client.sendall(f"matches {comp_code} {days}".encode(FORMAT))
                    data = self.safe_recv()

                    if data and "matches" in data:
                        all_matches.extend(data["matches"])
                        comp_count += 1

                # Xử lý và hiển thị dữ liệu trận đấu
                self.display_matches({"matches": all_matches})
                self.update_status(f"Loaded matches from {comp_count} competitions")

            else:
                # Tải trận đấu từ một giải cụ thể
                self.client.sendall(f"matches {comp_id} {days}".encode(FORMAT))
                data = self.safe_recv()
                self.display_matches(data)

        except Exception as e:
            self.update_status(f"Error loading matches: {str(e)}")
            messagebox.showerror("Error", f"Failed to load matches:\n{str(e)}")

    def load_standings(self):
        """Load standings"""
        self.update_status("Loading standings...")

        try:
            comp_id = self.get_competition_id()
            self.client.sendall(f"standings {comp_id}".encode(FORMAT))
            data = self.safe_recv()

            self.standings_tree.delete(*self.standings_tree.get_children())

            if not data.get("standings"):
                self.standings_tree.insert("", "end", values=("No standings data", "", "", "", "", "", "", "", "", ""))
                return

            for table in data.get("standings", []):
                if "group" in table:
                    self.standings_tree.insert("", "end", values=(
                        f"--- GROUP {table['group']} ---", "", "", "", "", "", "", "", "", ""
                    ))

                for row in table.get("table", []):
                    team_name = row.get("team", {}).get("name", "Unknown")
                    self.standings_tree.insert("", "end", values=(
                        row.get("position", ""),
                        team_name,
                        row.get("playedGames", ""),
                        row.get("won", ""),
                        row.get("draw", ""),
                        row.get("lost", ""),
                        row.get("goalsFor", ""),
                        row.get("goalsAgainst", ""),
                        row.get("goalDifference", ""),
                        row.get("points", "")
                    ))
                    self.teams[team_name] = row.get("team", {}).get("id")

            self.team_combo["values"] = list(self.teams.keys())
            self.update_status("Standings loaded successfully")

        except Exception as e:
            self.update_status(f"Error loading standings: {str(e)}")
            messagebox.showerror("Error", f"Failed to load standings:\n{str(e)}")

    def load_scorers(self):
        """Load scorers"""
        self.update_status("Loading scorers...")

        try:
            comp_id = self.get_competition_id()
            self.client.sendall(f"scorers {comp_id}".encode(FORMAT))
            data = self.safe_recv()

            self.scorers_tree.delete(*self.scorers_tree.get_children())

            if not data.get("scorers"):
                self.scorers_tree.insert("", "end", values=("No scorers data", "", "", "", "", "", ""))
                return

            for i, scorer in enumerate(data.get("scorers", []), 1):
                player = scorer.get("player", {})
                team = scorer.get("team", {})

                self.scorers_tree.insert("", "end", values=(
                    i,
                    player.get("name", "Unknown"),
                    team.get("name", "Unknown"),
                    scorer.get("goals", ""),
                    scorer.get("assists", ""),
                    player.get("position", ""),
                    player.get("nationality", "")
                ))

                self.players[player.get("name", "")] = player.get("id")
                self.teams[team.get("name", "")] = team.get("id")

            self.player_combo["values"] = list(self.players.keys())
            self.team_combo["values"] = list(self.teams.keys())
            self.update_status(f"Loaded {len(data.get('scorers', []))} scorers")

        except Exception as e:
            self.update_status(f"Error loading scorers: {str(e)}")
            messagebox.showerror("Error", f"Failed to load scorers:\n{str(e)}")

    def load_team_info(self):
        """Load team info"""
        team_name = self.team_var.get()
        if not team_name:
            messagebox.showwarning("Warning", "Please select a team first")
            return

        self.update_status(f"Loading team info for {team_name}...")

        try:
            team_id = self.teams.get(team_name)
            if not team_id:
                messagebox.showerror("Error", "Team ID not found")
                return

            self.client.sendall(f"team {team_id}".encode(FORMAT))
            data = self.safe_recv()

            self.team_info_text.delete("1.0", tk.END)

            if not data or "errorCode" in data:
                self.team_info_text.insert("end", "Could not load team information")
                return

            # Format team info
            info = f"""👥 TEAM INFORMATION

Name: {data.get('name', 'N/A')}
Short Name: {data.get('tla', 'N/A')}
Country: {data.get('area', {}).get('name', 'N/A')}
Founded: {data.get('founded', 'N/A')}
Venue: {data.get('venue', 'N/A')}
Colors: {data.get('clubColors', 'N/A')}
Website: {data.get('website', 'N/A')}

👥 SQUAD MEMBERS:
"""

            squad = data.get("squad", [])
            if squad:
                info += f"\nTotal Players: {len(squad)}\n\n"
                for i, player in enumerate(squad, 1):
                    info += f"{i}. {player.get('name', 'N/A')} - {player.get('position', 'N/A')} ({player.get('nationality', 'N/A')})\n"
                    self.players[player.get('name', '')] = player.get('id')
            else:
                info += "No squad information available"

            self.team_info_text.insert("end", info)
            self.player_combo["values"] = list(self.players.keys())
            self.update_status(f"Team info loaded for {team_name}")

        except Exception as e:
            self.update_status(f"Error loading team info: {str(e)}")
            messagebox.showerror("Error", f"Failed to load team info:\n{str(e)}")

    def load_player_info(self):
        """Load player info"""
        player_name = self.player_var.get()
        if not player_name:
            messagebox.showwarning("Warning", "Please select a player first")
            return

        self.update_status(f"Loading player info for {player_name}...")

        try:
            player_id = self.players.get(player_name)
            if not player_id:
                messagebox.showerror("Error", "Player ID not found")
                return

            self.client.sendall(f"player {player_id}".encode(FORMAT))
            data = self.safe_recv()

            self.player_info_text.delete("1.0", tk.END)

            if not data or "errorCode" in data:
                self.player_info_text.insert("end", "Could not load player information")
                return

            # Format player info
            info = f"""👤 PLAYER INFORMATION

Name: {data.get('name', 'N/A')}
Date of Birth: {data.get('dateOfBirth', 'N/A')}
Nationality: {data.get('nationality', 'N/A')}
Position: {data.get('position', 'N/A')}
Shirt Number: {data.get('shirtNumber', 'N/A')}

👥 CURRENT TEAM:
"""

            current_team = data.get('currentTeam', {})
            if current_team:
                info += f"Team: {current_team.get('name', 'N/A')}\n"
                contract = current_team.get('contract', {})
                info += f"Contract: {contract.get('startDate', 'N/A')} to {contract.get('endDate', 'N/A')}\n"

            self.player_info_text.insert("end", info)
            self.update_status(f"Player info loaded for {player_name}")

        except Exception as e:
            self.update_status(f"Error loading player info: {str(e)}")
            messagebox.showerror("Error", f"Failed to load player info:\n{str(e)}")

    def refresh_all(self):
        """Refresh all data"""
        self.update_status("Refreshing data...")
        messagebox.showinfo("Refresh", "Data refreshed successfully!")
        self.update_status("Ready")

    def display_matches(self, data):
        """Display matches in the treeview"""
        if not data or not data.get("matches"):
            self.matches_tree.insert("", "end", values=("No matches found", "", "", "", "", "",
                                                        ""))  # Thêm một giá trị rỗng cho cột league
            self.update_status("No matches available for this period")
            return

        # Process matches
        for match in data.get("matches", []):
            try:
                home_team = match.get("homeTeam", {}).get("name", "Unknown")
                away_team = match.get("awayTeam", {}).get("name", "Unknown")

                # Process score
                score_data = match.get("score", {}).get("fullTime", {})
                home_score = score_data.get("home", "-")
                away_score = score_data.get("away", "-")
                score = f"{home_score}-{away_score}"

                # Process date and time
                try:
                    match_date = datetime.fromisoformat(match.get("utcDate", "").replace("Z", "+00:00"))
                    date_str = match_date.strftime("%d/%m/%Y")
                    time_str = match_date.strftime("%H:%M")
                except:
                    date_str = "Unknown"
                    time_str = "Unknown"

                # Process status
                status = match.get("status", "UNKNOWN")
                status_display = {
                    "FINISHED": "✅ Finished",
                    "LIVE": "🔴 LIVE",
                    "IN_PLAY": "🔴 Playing",
                    "PAUSED": "⏸️ Paused",
                    "TIMED": "⏰ Scheduled",
                    "SCHEDULED": "📅 Scheduled"
                }.get(status, status)

                # Lấy tên giải đấu
                league_name = match.get("competition", {}).get("name", "Unknown League")

                # Thêm league_name vào values
                self.matches_tree.insert("", "end", values=(
                    date_str, time_str, home_team, score, away_team, status_display, league_name
                ))

                # Store team IDs
                self.teams[home_team] = match.get("homeTeam", {}).get("id")
                self.teams[away_team] = match.get("awayTeam", {}).get("id")

            except Exception as e:
                print(f"Error processing match: {e}")
                continue

        # Update team combo
        self.team_combo["values"] = list(self.teams.keys())
        self.update_status(f"Loaded {len(data.get('matches', []))} matches")

    def send_udp_message(self):
        """Gửi tin nhắn UDP và hiển thị phản hồi"""
        try:
            # Tạo UDP socket
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Chuẩn bị và gửi tin nhắn
            message = "Hello My Friend!"
            self.update_status(f"Gửi tin nhắn UDP: {message}")
            udp_socket.sendto(message.encode(), ('127.0.0.1', 12345))

            # Thiết lập timeout để tránh chờ mãi mãi
            udp_socket.settimeout(5)

            # Nhận phản hồi
            try:
                data, server = udp_socket.recvfrom(1024)
                response = data.decode()
                messagebox.showinfo("UDP Response", f"Phản hồi từ server: {response}")
                self.update_status(f"UDP: Nhận phản hồi từ {server[0]}:{server[1]}")
            except socket.timeout:
                messagebox.showwarning("UDP Timeout", "Không nhận được phản hồi từ server UDP")
                self.update_status("UDP: Timeout - không nhận được phản hồi")
        except Exception as e:
            messagebox.showerror("UDP Error", f"Lỗi khi gửi tin nhắn UDP: {str(e)}")
            self.update_status(f"UDP Error: {str(e)}")
        finally:
            # Đóng socket
            udp_socket.close()


if __name__ == "__main__":
    app = ModernFootballApp()
    app.mainloop()


