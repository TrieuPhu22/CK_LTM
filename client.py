import socket
import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

HOST = "127.0.0.1"
PORT = 65432
FORMAT = "utf8"

COMPETITIONS = {
    "Premier League": "2021",
    "La Liga": "2014",
    "Bundesliga": "2002",
    "Serie A": "2019",
    "Champions League": "2001",
}


class SoccerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Soccer Data (football-data.org)")
        self.geometry("950x650")

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((HOST, PORT))

        self.teams = {}  # {team_name: team_id}
        self.players = {}  # {player_name: player_id}

        # Tabs
        self.notebook = ttk.Notebook(self)
        self.tab_matches = tk.Frame(self.notebook)
        self.tab_standings = tk.Frame(self.notebook)
        self.tab_scorers = tk.Frame(self.notebook)
        self.tab_team = tk.Frame(self.notebook)
        self.tab_player = tk.Frame(self.notebook)
        self.notebook.add(self.tab_matches, text="Matches")
        self.notebook.add(self.tab_standings, text="Standings")
        self.notebook.add(self.tab_scorers, text="Scorers")
        self.notebook.add(self.tab_team, text="Team Info")
        self.notebook.add(self.tab_player, text="Player Info")
        self.notebook.pack(expand=True, fill="both")

        # Matches tab
        self.comp_combo = ttk.Combobox(self.tab_matches, values=list(COMPETITIONS.keys()), state="readonly")
        self.comp_combo.current(0)
        self.comp_combo.pack()

        self.filter_combo = ttk.Combobox(
            self.tab_matches, values=["All", "Finished", "Live", "Upcoming"], state="readonly"
        )
        self.filter_combo.current(0)
        self.filter_combo.pack()

        tk.Button(self.tab_matches, text="Load Matches", command=self.load_matches).pack()

        self.tree_matches = ttk.Treeview(
            self.tab_matches, columns=("home", "away", "score", "status", "date"), show="headings"
        )
        for col in ("home", "away", "score", "status", "date"):
            self.tree_matches.heading(col, text=col)
        self.tree_matches.pack(fill="both", expand=True)

        # Standings tab
        self.tree_standings = ttk.Treeview(
            self.tab_standings, columns=("pos", "team", "played", "points"), show="headings"
        )
        for col in ("pos", "team", "played", "points"):
            self.tree_standings.heading(col, text=col)
        self.tree_standings.pack(fill="both", expand=True)
        tk.Button(self.tab_standings, text="Load Standings", command=self.load_standings).pack()

        # Scorers tab
        self.tree_scorers = ttk.Treeview(
            self.tab_scorers, columns=("player", "team", "goals"), show="headings"
        )
        for col in ("player", "team", "goals"):
            self.tree_scorers.heading(col, text=col)
        self.tree_scorers.pack(fill="both", expand=True)
        tk.Button(self.tab_scorers, text="Load Scorers", command=self.load_scorers).pack()

        # Team Info tab
        tk.Label(self.tab_team, text="Select Team:").pack()
        self.team_combo = ttk.Combobox(self.tab_team, values=[], state="readonly")
        self.team_combo.pack(pady=5)
        tk.Button(self.tab_team, text="Load Team Info", command=self.load_team).pack()
        self.team_text = tk.Text(self.tab_team, height=20)
        self.team_text.pack(fill="both", expand=True)

        # Player Info tab
        tk.Label(self.tab_player, text="Select Player:").pack()
        self.player_combo = ttk.Combobox(self.tab_player, values=[], state="readonly")
        self.player_combo.pack(pady=5)
        tk.Button(self.tab_player, text="Load Player Info", command=self.load_player).pack()
        self.player_text = tk.Text(self.tab_player)
        self.player_text.pack(fill="both", expand=True)

    def safe_recv(self):
        data = self.client.recv(65535).decode(FORMAT)
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Dữ liệu không hợp lệ từ server")
            return {}

    def load_matches(self):
        try:
            # Lấy ID giải đấu từ dropdown
            comp = COMPETITIONS[self.comp_combo.get()]
            self.client.sendall(f"matches {comp}".encode(FORMAT))
            data = self.safe_recv()

            # Xóa dữ liệu cũ
            self.tree_matches.delete(*self.tree_matches.get_children())
            self.teams.clear()

            # Lọc theo trạng thái
            filter_mode = self.filter_combo.get()

            # Hiển thị thông báo nếu không có trận đấu
            if not data.get("matches"):
                self.tree_matches.insert("", "end", values=("Không có dữ liệu", "", "", "", ""))
                return

            # Xử lý từng trận đấu
            for m in data.get("matches", []):
                status = m["status"]

                # Lọc theo trạng thái
                if filter_mode == "Finished" and status != "FINISHED":
                    continue
                if filter_mode == "Upcoming" and status != "TIMED":
                    continue
                if filter_mode == "Live" and status not in ("LIVE", "IN_PLAY", "PAUSED"):
                    continue

                # Xử lý trường hợp không có điểm số
                home_score = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else "-"
                away_score = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else "-"
                score = f"{home_score}-{away_score}"

                # Định dạng ngày giờ
                try:
                    date_time = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
                    formatted_date = date_time.strftime("%d/%m/%Y %H:%M")
                except:
                    formatted_date = m["utcDate"]

                # Hiển thị trạng thái rõ ràng hơn
                status_display = {
                    "FINISHED": "Kết thúc",
                    "LIVE": "LIVE",
                    "IN_PLAY": "Đang đấu",
                    "PAUSED": "Tạm dừng",
                    "TIMED": "Sắp diễn ra",
                    "SCHEDULED": "Đã lên lịch"
                }.get(status, status)

                # Thêm vào bảng
                self.tree_matches.insert(
                    "", "end",
                    values=(m["homeTeam"]["name"], m["awayTeam"]["name"], score, status_display, formatted_date)
                )
                self.teams[m["homeTeam"]["name"]] = m["homeTeam"]["id"]
                self.teams[m["awayTeam"]["name"]] = m["awayTeam"]["id"]

            # Cập nhật danh sách đội
            self.team_combo["values"] = list(self.teams.keys())

            # Tự động làm mới nếu đang xem trận đấu trực tiếp
            if filter_mode == "Live":
                self.after(30000, self.load_matches)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách trận đấu: {str(e)}")

    def load_standings(self):
        try:
            # Lấy ID giải đấu từ dropdown
            comp = COMPETITIONS[self.comp_combo.get()]
            self.client.sendall(f"standings {comp}".encode(FORMAT))
            data = self.safe_recv()
            self.tree_standings.delete(*self.tree_standings.get_children())

            # Kiểm tra dữ liệu trả về
            if not data.get("standings"):
                self.tree_standings.insert("", "end", values=("Không có dữ liệu bảng xếp hạng", "", "", ""))
                return

            # Thêm cột mới vào bảng
            if len(self.tree_standings["columns"]) == 4:  # Nếu chỉ có 4 cột mặc định
                self.tree_standings["columns"] = ("pos", "team", "played", "won", "draw", "lost", "gf", "ga", "gd",
                                                  "points")
                for col in self.tree_standings["columns"]:
                    self.tree_standings.heading(col, text=col.upper())

            # Hiển thị từng bảng đấu (với giải đấu có nhiều bảng như Champions League)
            for table in data.get("standings", []):
                # Hiển thị tên bảng đấu (nếu có)
                if "group" in table:
                    self.tree_standings.insert("", "end",
                                               values=(f"--- BẢNG {table['group']} ---", "", "", "", "", "", "", "", "",
                                                       ""))

                # Hiển thị từng đội trong bảng
                for row in table.get("table", []):
                    self.tree_standings.insert(
                        "", "end",
                        values=(
                            row["position"],
                            row["team"]["name"],
                            row["playedGames"],
                            row["won"],
                            row["draw"],
                            row["lost"],
                            row["goalsFor"],
                            row["goalsAgainst"],
                            row["goalDifference"],
                            row["points"]
                        )
                    )
                    self.teams[row["team"]["name"]] = row["team"]["id"]

            # Cập nhật danh sách đội
            self.team_combo["values"] = list(self.teams.keys())

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải bảng xếp hạng: {str(e)}")

    def load_scorers(self):
        try:
            comp = COMPETITIONS[self.comp_combo.get()]
            self.client.sendall(f"scorers {comp}".encode(FORMAT))
            data = self.safe_recv()

            self.tree_scorers.delete(*self.tree_scorers.get_children())

            if not data.get("scorers"):
                self.tree_scorers.insert("", "end", values=("Không có dữ liệu", "", ""))
                return

            # Mở rộng cột để hiển thị thêm thông tin
            if len(self.tree_scorers["columns"]) == 3:
                self.tree_scorers["columns"] = ("player", "team", "position", "nationality", "goals", "assists")
                for col in self.tree_scorers["columns"]:
                    self.tree_scorers.heading(col, text=col.upper())

            for idx, s in enumerate(data.get("scorers", []), 1):
                # Lấy thông tin bổ sung nếu có
                position = s["player"].get("position", "N/A")
                nationality = s["player"].get("nationality", "N/A")
                assists = s.get("assists", "N/A")

                # Hiển thị thông tin
                self.tree_scorers.insert(
                    "", "end",
                    values=(
                        s["player"]["name"],
                        s["team"]["name"],
                        position,
                        nationality,
                        s["goals"],
                        assists
                    )
                )

                # Lưu ID cầu thủ để sử dụng sau này
                self.players[s["player"]["name"]] = s["player"]["id"]
                self.teams[s["team"]["name"]] = s["team"]["id"]

            # Cập nhật danh sách cầu thủ cho tab Player Info
            self.player_combo["values"] = list(self.players.keys())
            self.team_combo["values"] = list(self.teams.keys())

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách ghi bàn: {str(e)}")

    def load_team(self):
        try:
            team_name = self.team_combo.get()
            if not team_name:
                messagebox.showerror("Lỗi", "Vui lòng chọn một đội")
                return

            team_id = self.teams[team_name]
            self.client.sendall(f"team {team_id}".encode(FORMAT))
            data = self.safe_recv()

            # Xóa thông tin cũ
            self.team_text.delete("1.0", tk.END)

            if not data or "errorCode" in data:
                self.team_text.insert("end", "Không thể tải thông tin đội bóng")
                return

            # Hiển thị thông tin đội bóng theo cấu trúc
            self.team_text.insert("end", f"ĐỘI BÓNG: {data.get('name', 'N/A')}\n\n", "header")
            self.team_text.insert("end", f"Tên viết tắt: {data.get('tla', 'N/A')}\n")
            self.team_text.insert("end", f"Quốc gia: {data.get('area', {}).get('name', 'N/A')}\n")
            self.team_text.insert("end", f"Năm thành lập: {data.get('founded', 'N/A')}\n")
            self.team_text.insert("end", f"Sân nhà: {data.get('venue', 'N/A')}\n")
            self.team_text.insert("end", f"Màu áo: {data.get('clubColors', 'N/A')}\n")
            self.team_text.insert("end", f"Website: {data.get('website', 'N/A')}\n\n")

            # Hiển thị danh sách cầu thủ
            self.team_text.insert("end", "DANH SÁCH CẦU THỦ:\n\n", "header")

            # Cập nhật danh sách cầu thủ
            self.players.clear()
            squad = data.get("squad", [])

            # Tạo bảng hiển thị danh sách cầu thủ
            fmt = "{:<3} {:<25} {:<20} {:<15}\n"
            self.team_text.insert("end", fmt.format("STT", "Tên cầu thủ", "Vị trí", "Quốc tịch"))
            self.team_text.insert("end", "-" * 70 + "\n")

            for i, p in enumerate(squad, 1):
                self.players[p["name"]] = p["id"]
                position = p.get("position", "N/A")
                nationality = p.get("nationality", "N/A")
                self.team_text.insert("end", fmt.format(i, p["name"], position, nationality))

            # Định dạng văn bản
            self.team_text.tag_configure("header", font=("Arial", 12, "bold"))

            # Cập nhật danh sách cầu thủ cho tab Player Info
            self.player_combo["values"] = list(self.players.keys())

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải thông tin đội bóng: {str(e)}")

    def load_player(self):
        player_name = self.player_combo.get()
        if not player_name:
            messagebox.showerror("Error", "Please select a player")
            return
        player_id = self.players[player_name]
        self.client.sendall(f"player {player_id}".encode(FORMAT))
        data = self.safe_recv()
        self.player_text.delete("1.0", tk.END)
        self.player_text.insert("end", json.dumps(data, indent=2))


if __name__ == "__main__":
    app = SoccerApp()
    app.mainloop()
