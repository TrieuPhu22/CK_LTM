import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
import re


class Colors:
    PRIMARY = "#1e3a8a"
    SECONDARY = "#3b82f6"
    SUCCESS = "#10b981"
    DANGER = "#ef4444"
    MAIN_BG = "#f8fafc"
    CARD_BG = "#ffffff"
    HEADER_BG = "#0f172a"
    WHITE_TEXT = "#ffffff"


class LoginWindow(tk.Tk):
    def __init__(self, on_login_success):
        super().__init__()

        # Lưu callback function để gọi khi đăng nhập thành công
        self.on_login_success = on_login_success

        # Khởi tạo đối tượng Database
        self.db = Database()

        # Thiết lập cửa sổ
        self.title("⚽ Football Hub - Đăng Nhập")
        self.geometry("500x700")
        self.configure(background=Colors.MAIN_BG)
        self.resizable(False, False)

        # Tạo giao diện
        self.create_login_ui()

        # Thêm dòng này để xử lý sự kiện đóng cửa sổ
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_login_ui(self):
        # Frame chính
        main_frame = tk.Frame(self, bg=Colors.MAIN_BG, padx=40, pady=40)
        main_frame.pack(fill="both", expand=True)

        # Logo và tiêu đề
        tk.Label(main_frame, text="⚽", font=("Segoe UI", 50), bg=Colors.MAIN_BG).pack(pady=(0, 10))
        tk.Label(main_frame, text="Football Hub", font=("Segoe UI", 24, "bold"), bg=Colors.MAIN_BG).pack(pady=(0, 5))
        tk.Label(main_frame, text="Đăng nhập để tiếp tục", font=("Segoe UI", 12), bg=Colors.MAIN_BG).pack(pady=(0, 30))

        # Form đăng nhập
        form_frame = tk.Frame(main_frame, bg=Colors.CARD_BG, padx=30, pady=30, relief="flat", bd=1)
        form_frame.pack(fill="x")

        # Username
        tk.Label(form_frame, text="Tên đăng nhập", font=("Segoe UI", 10), bg=Colors.CARD_BG, anchor="w").pack(fill="x",
                                                                                                              pady=(0,
                                                                                                                    5))
        self.username_entry = ttk.Entry(form_frame, font=("Segoe UI", 12))
        self.username_entry.pack(fill="x", pady=(0, 15), ipady=5)

        # Password
        tk.Label(form_frame, text="Mật khẩu", font=("Segoe UI", 10), bg=Colors.CARD_BG, anchor="w").pack(fill="x",
                                                                                                         pady=(0, 5))
        self.password_entry = ttk.Entry(form_frame, font=("Segoe UI", 12), show="•")
        self.password_entry.pack(fill="x", pady=(0, 20), ipady=5)

        # Login button
        login_btn = tk.Button(form_frame, text="Đăng Nhập",
                              command=self.login,
                              font=("Segoe UI", 12, "bold"),
                              bg=Colors.PRIMARY, fg=Colors.WHITE_TEXT,
                              padx=10, pady=8, relief="flat", cursor="hand2")
        login_btn.pack(fill="x", pady=(0, 15))

        # Register link
        register_frame = tk.Frame(form_frame, bg=Colors.CARD_BG)
        register_frame.pack(fill="x")

        tk.Label(register_frame, text="Chưa có tài khoản?",
                 font=("Segoe UI", 10), bg=Colors.CARD_BG).pack(side="left")

        register_link = tk.Label(register_frame, text="Đăng ký ngay",
                                 font=("Segoe UI", 10, "bold"), bg=Colors.CARD_BG,
                                 fg=Colors.SECONDARY, cursor="hand2")
        register_link.pack(side="left", padx=(5, 0))
        register_link.bind("<Button-1>", self.open_register)

        # Thêm key bindings
        self.bind("<Return>", lambda event: self.login())

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        success, result = self.db.authenticate_user(username, password)

        if success:
            messagebox.showinfo("Thành công", f"Chào mừng {result['full_name']} quay trở lại!")
            self.withdraw()  # Ẩn cửa sổ đăng nhập
            # Gọi callback function với thông tin người dùng
            self.on_login_success(result)
        else:
            messagebox.showerror("Lỗi đăng nhập", result)

    def open_register(self, event=None):
        self.withdraw()  # Ẩn cửa sổ đăng nhập
        register_window = RegisterWindow(self)
        register_window.mainloop()

    def on_closing(self):
        """Xử lý sự kiện đóng cửa sổ"""
        self.destroy()
        # Đảm bảo chương trình thoát hoàn toàn
        import sys
        sys.exit(0)


class RegisterWindow(tk.Toplevel):
    def __init__(self, login_window):
        super().__init__()

        # Lưu tham chiếu đến cửa sổ đăng nhập
        self.login_window = login_window

        # Khởi tạo đối tượng Database
        self.db = Database()

        # Thiết lập cửa sổ
        self.title("⚽ Football Hub - Đăng Ký")
        self.geometry("500x800")
        self.configure(background=Colors.MAIN_BG)
        self.resizable(False, False)

        # Tạo giao diện
        self.create_register_ui()

        # Xử lý khi đóng cửa sổ
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_register_ui(self):
        # Frame chính
        main_frame = tk.Frame(self, bg=Colors.MAIN_BG, padx=40, pady=30)
        main_frame.pack(fill="both", expand=True)

        # Tiêu đề
        tk.Label(main_frame, text="⚽ Đăng Ký Tài Khoản", font=("Segoe UI", 20, "bold"), bg=Colors.MAIN_BG).pack(
            pady=(0, 20))

        # Form đăng ký
        form_frame = tk.Frame(main_frame, bg=Colors.CARD_BG, padx=30, pady=30, relief="flat", bd=1)
        form_frame.pack(fill="x")

        # Username
        tk.Label(form_frame, text="Tên đăng nhập", font=("Segoe UI", 10), bg=Colors.CARD_BG, anchor="w").pack(fill="x",
                                                                                                              pady=(0,
                                                                                                                    5))
        self.username_entry = ttk.Entry(form_frame, font=("Segoe UI", 12))
        self.username_entry.pack(fill="x", pady=(0, 15), ipady=5)

        # Email
        tk.Label(form_frame, text="Email", font=("Segoe UI", 10), bg=Colors.CARD_BG, anchor="w").pack(fill="x",
                                                                                                      pady=(0, 5))
        self.email_entry = ttk.Entry(form_frame, font=("Segoe UI", 12))
        self.email_entry.pack(fill="x", pady=(0, 15), ipady=5)

        # Full Name
        tk.Label(form_frame, text="Họ và tên", font=("Segoe UI", 10), bg=Colors.CARD_BG, anchor="w").pack(fill="x",
                                                                                                          pady=(0, 5))
        self.fullname_entry = ttk.Entry(form_frame, font=("Segoe UI", 12))
        self.fullname_entry.pack(fill="x", pady=(0, 15), ipady=5)

        # Favorite Team
        tk.Label(form_frame, text="Đội bóng yêu thích (không bắt buộc)", font=("Segoe UI", 10), bg=Colors.CARD_BG,
                 anchor="w").pack(fill="x", pady=(0, 5))
        self.team_entry = ttk.Entry(form_frame, font=("Segoe UI", 12))
        self.team_entry.pack(fill="x", pady=(0, 15), ipady=5)

        # Password
        tk.Label(form_frame, text="Mật khẩu", font=("Segoe UI", 10), bg=Colors.CARD_BG, anchor="w").pack(fill="x",
                                                                                                         pady=(0, 5))
        self.password_entry = ttk.Entry(form_frame, font=("Segoe UI", 12), show="•")
        self.password_entry.pack(fill="x", pady=(0, 15), ipady=5)

        # Confirm Password
        tk.Label(form_frame, text="Xác nhận mật khẩu", font=("Segoe UI", 10), bg=Colors.CARD_BG, anchor="w").pack(
            fill="x", pady=(0, 5))
        self.confirm_password_entry = ttk.Entry(form_frame, font=("Segoe UI", 12), show="•")
        self.confirm_password_entry.pack(fill="x", pady=(0, 20), ipady=5)

        # Register button
        register_btn = tk.Button(form_frame, text="Đăng Ký",
                                 command=self.register,
                                 font=("Segoe UI", 12, "bold"),
                                 bg=Colors.PRIMARY, fg=Colors.WHITE_TEXT,
                                 padx=10, pady=8, relief="flat", cursor="hand2")
        register_btn.pack(fill="x", pady=(0, 15), ipady=5)

        # Login link
        login_frame = tk.Frame(form_frame, bg=Colors.CARD_BG)
        login_frame.pack(fill="x")

        tk.Label(login_frame, text="Đã có tài khoản?",
                 font=("Segoe UI", 10), bg=Colors.CARD_BG).pack(side="left")

        login_link = tk.Label(login_frame, text="Đăng nhập",
                              font=("Segoe UI", 10, "bold"), bg=Colors.CARD_BG,
                              fg=Colors.SECONDARY, cursor="hand2")
        login_link.pack(side="left", padx=(5, 0))
        login_link.bind("<Button-1>", self.back_to_login)

    def register(self):
        # Lấy dữ liệu từ form
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        full_name = self.fullname_entry.get().strip()
        favorite_team = self.team_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        # Kiểm tra đầy đủ thông tin
        if not username or not email or not full_name or not password or not confirm_password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        # Kiểm tra định dạng email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Lỗi", "Email không hợp lệ!")
            return

        # Kiểm tra độ dài username
        if len(username) < 4:
            messagebox.showerror("Lỗi", "Tên đăng nhập phải có ít nhất 4 ký tự!")
            return

        # Kiểm tra mật khẩu khớp nhau
        if password != confirm_password:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
            return

        # Kiểm tra độ dài mật khẩu
        if len(password) < 6:
            messagebox.showerror("Lỗi", "Mật khẩu phải có ít nhất 6 ký tự!")
            return

        # Thực hiện đăng ký
        success, message = self.db.register_user(username, password, email, full_name, favorite_team)

        if success:
            messagebox.showinfo("Thành công", message)
            self.back_to_login()
        else:
            messagebox.showerror("Lỗi đăng ký", message)

    def back_to_login(self, event=None):
        self.destroy()
        self.login_window.deiconify()  # Hiện lại cửa sổ đăng nhập

    def on_close(self):
        self.login_window.deiconify()  # Hiện lại cửa sổ đăng nhập khi đóng
        self.destroy()