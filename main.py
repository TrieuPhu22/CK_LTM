import tkinter as tk
import traceback
import sys

try:
    from auth_ui import LoginWindow
    from client import ModernFootballApp


    class FootballHubApp:
        def __init__(self):
            # Bắt đầu với cửa sổ đăng nhập
            self.login_window = LoginWindow(self.on_login_success)
            self.login_window.mainloop()

        def on_login_success(self, user_data):
            """Được gọi khi đăng nhập thành công"""
            # Khởi tạo ứng dụng chính với thông tin người dùng
            self.main_app = ModernFootballApp(user_data)
            self.main_app.mainloop()


    if __name__ == "__main__":
        app = FootballHubApp()
except Exception as e:
    print(f"Lỗi: {e}")
    traceback.print_exc()
    input("Nhấn Enter để thoát...")  # Giữ cửa sổ console mở