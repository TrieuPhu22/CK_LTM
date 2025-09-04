import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import threading
from modern_theme import ModernTheme

class ChatWindow(tk.Toplevel):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.username = username
        self.parent = parent
        self.is_running = True
        
        # Thiết lập cửa sổ chat
        self.title(f"Chat - {username}")
        self.geometry("400x500")
        self.configure(bg=ModernTheme.MAIN_BG)
        
        # Khởi tạo UDP socket và kết nối
        self.setup_udp_connection()
        
        self.create_widgets()
        self.start_receive_thread()
        
        # Gửi tin nhắn thông báo kết nối
        self.send_join_message()
        
        # Ping server định kỳ để giữ kết nối
        self.ping_interval = 5000  # 5 giây
        self.ping_server()

    def setup_udp_connection(self):
        """Thiết lập kết nối UDP mới"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
            self.server_address = ('127.0.0.1', 12345)
            self.sock.bind(('', 0))  # Bind vào port ngẫu nhiên
            self.sock.settimeout(1.0)  # Thêm timeout 1 giây
            print(f"Chat socket bound to {self.sock.getsockname()}")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Không thể kết nối đến server chat: {e}")
            self.destroy()

    def ping_server(self):
        """Gửi ping định kỳ đến server để giữ kết nối"""
        if self.is_running:
            try:
                ping_message = f"PING|{self.username}"
                self.sock.sendto(ping_message.encode(), self.server_address)
            except:
                pass
            self.after(self.ping_interval, self.ping_server)

    def receive_messages(self):
        """Nhận tin nhắn từ server"""
        while self.is_running:
            try:
                data, _ = self.sock.recvfrom(1024)
                message = data.decode()
                
                # Bỏ qua tin nhắn PING
                if message.startswith("PING|"):
                    continue
                    
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, message + '\n')
                self.chat_area.config(state='disabled')
                self.chat_area.see(tk.END)
            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:
                    print(f"Lỗi nhận tin nhắn: {e}")
                break

    def send_message(self):
        """Gửi tin nhắn"""
        message = self.msg_entry.get().strip()
        if message:
            full_message = f"{self.username}: {message}"
            try:
                self.sock.sendto(full_message.encode(), self.server_address)
                # Hiển thị tin nhắn của chính mình
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, full_message + '\n')
                self.chat_area.config(state='disabled')
                self.chat_area.see(tk.END)
                self.msg_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Không thể gửi tin nhắn: {e}")

    def send_join_message(self):
        """Gửi tin nhắn thông báo tham gia chat"""
        try:
            join_message = f"{self.username} đã tham gia chat"
            self.sock.sendto(join_message.encode(), self.server_address)
            
            # Hiển thị tin nhắn tham gia trong chat area
            self.chat_area.config(state='normal')
            self.chat_area.insert(tk.END, join_message + '\n')
            self.chat_area.config(state='disabled')
            self.chat_area.see(tk.END)
        except Exception as e:
            print(f"Lỗi khi gửi tin nhắn tham gia: {e}")

    def on_closing(self):
        """Xử lý đóng cửa sổ chat"""
        self.is_running = False  # Dừng thread nhận tin nhắn
        try:
            # Gửi tin nhắn thông báo ngắt kết nối
            leave_message = f"{self.username} đã rời chat"
            self.sock.sendto(leave_message.encode(), self.server_address)
            self.sock.close()
        except:
            pass
        finally:
            # Reset parent's chat window and enabled state
            if hasattr(self.parent, 'chat_window'):
                self.parent.chat_window = None
            if hasattr(self.parent, 'chat_enabled'):
                self.parent.chat_enabled.set(False)
            self.destroy()

    def create_widgets(self):
        """Tạo giao diện chat"""
        # Chat area
        self.chat_area = scrolledtext.ScrolledText(
            self, 
            wrap=tk.WORD,
            width=40, 
            height=20,
            font=ModernTheme.BODY_FONT,
            bg=ModernTheme.CARD_BG
        )
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_area.config(state='disabled')

        # Message input frame
        self.input_frame = ttk.Frame(self)
        self.input_frame.pack(padx=10, pady=(0,10), fill=tk.X)

        # Message entry
        self.msg_entry = ttk.Entry(
            self.input_frame,
            font=ModernTheme.BODY_FONT
        )
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Send button
        self.send_btn = ttk.Button(
            self.input_frame,
            text="Gửi",
            command=self.send_message
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(5,0))

        # Bind Enter key to send message
        self.msg_entry.bind('<Return>', lambda e: self.send_message())

    def start_receive_thread(self):
        """Khởi động thread nhận tin nhắn"""
        self.receive_thread = threading.Thread(
            target=self.receive_messages, 
            daemon=True
        )
        self.receive_thread.start()