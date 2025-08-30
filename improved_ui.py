import tkinter as tk
from tkinter import ttk, font, messagebox
import socket
import json
from datetime import datetime

# Định nghĩa các màu sắc chính của ứng dụng
MAIN_BG = "#f0f0f0"  # Màu nền chính
HEADER_BG = "#1a237e"  # Màu nền header - xanh đậm
HEADER_FG = "white"  # Màu chữ header
BUTTON_BG = "#1976d2"  # Màu nút - xanh dương
BUTTON_FG = "white"  # Màu chữ nút
TREEVIEW_BG = "white"  # Màu nền bảng
TREEVIEW_SELECT = "#bbdefb"  # Màu chọn dòng - xanh nhạt
LABEL_FG = "#0d47a1"  # Màu chữ nhãn - xanh đậm

# Thông tin kết nối
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
        self.title("Lịch Bóng Đá 24/7")
        self.geometry("1000x700")
        self.configure(bg=MAIN_BG)
        self.minsize(900, 650)  # Đặt kích thước tối thiểu

        # Thiết lập style
        self.setup_styles()

        # Kết nối socket
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((HOST, PORT))
        except Exception as e:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối đến server: {str(e)}")
            self.destroy()
            return

        self.teams = {}  # {team_name: team_id}
        self.players = {}  # {player_name: player_id}

        # Tabs
        self.notebook = ttk.Notebook(self)
        self.tab_matches = tk.Frame(self.notebook, bg=MAIN_BG)
        self.tab_standings = tk.Frame(self.notebook, bg=MAIN_BG)
        self.tab_scorers = tk.Frame(self.notebook, bg=MAIN_BG)
        self.tab_team = tk.Frame(self.notebook, bg=MAIN_BG)
        self.tab_player = tk.Frame(self.notebook, bg=MAIN_BG)

        self.notebook.add(self.tab_matches, text="Trận Đấu")
        self.notebook.add(self.tab_standings, text="Bảng Xếp Hạng")
        self.notebook.add(self.tab_scorers, text="Ghi Bàn")
        self.notebook.add(self.tab_team, text="Thông Tin Đội")
        self.notebook.add(self.tab_player, text="Thông Tin Cầu Thủ")
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

    def setup_styles(self):
        """Thiết lập style cho các widget"""
        self.style = ttk.Style()
        self.style.theme_use('clam')  # sử dụng theme clam làm nền tảng

        # Style cho Treeview
        self.style.configure("Treeview",
                             background=TREEVIEW_BG,
                             rowheight=25,
                             font=('Segoe UI', 10))
        self.style.configure("Treeview.Heading",
                             font=('Segoe UI', 10, 'bold'),
                             background=HEADER_BG,
                             foreground=HEADER_FG)
        self.style.map('Treeview',
                       background=[('selected', TREEVIEW_SELECT)],
                       foreground=[('selected', 'black')])

        # Style cho Button
        self.style.configure("TButton",
                             font=('Segoe UI', 10, 'bold'),
                             background=BUTTON_BG,
                             foreground=BUTTON_FG)

        # Style cho Combobox
        self.style.configure("TCombobox",
                             font=('Segoe UI', 10))

        # Style cho Label
        self.style.configure("TLabel",
                             font=('Segoe UI', 10),
                             foreground=LABEL_FG)

    def safe_recv(self):
        """Nhận dữ liệu từ server an toàn"""
        data = self.client.recv(65535).decode(FORMAT)
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            messagebox.showerror("Lỗi", "Dữ liệu không hợp lệ từ server")
            return {}

    # Các phương thức khác sẽ được thêm ở phần sau


if __name__ == "__main__":
    app = SoccerApp()
    app.mainloop()