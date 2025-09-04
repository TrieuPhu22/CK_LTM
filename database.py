import sqlite3
import hashlib
import os


class Database:
    def __init__(self, db_file="football_hub.db"):
        self.db_file = db_file
        self.create_tables()

    def create_tables(self):
        """Tạo bảng users nếu chưa tồn tại"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Tạo bảng users với các trường cần thiết
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           username
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           password
                           TEXT
                           NOT
                           NULL,
                           email
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           full_name
                           TEXT,
                           favorite_team
                           TEXT,
                           registration_date
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        conn.commit()
        conn.close()

    def hash_password(self, password):
        """Mã hóa mật khẩu bằng SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, email, full_name, favorite_team=None):
        """Đăng ký người dùng mới"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            hashed_password = self.hash_password(password)

            cursor.execute('''
                           INSERT INTO users (username, password, email, full_name, favorite_team)
                           VALUES (?, ?, ?, ?, ?)
                           ''', (username, hashed_password, email, full_name, favorite_team))

            conn.commit()
            conn.close()
            return True, "Đăng ký thành công!"
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                return False, "Tên đăng nhập đã tồn tại!"
            elif "email" in str(e):
                return False, "Email đã được sử dụng!"
            else:
                return False, f"Lỗi: {str(e)}"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def authenticate_user(self, username, password):
        """Xác thực người dùng đăng nhập"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            hashed_password = self.hash_password(password)

            cursor.execute('''
                           SELECT *
                           FROM users
                           WHERE username = ?
                             AND password = ?
                           ''', (username, hashed_password))

            user = cursor.fetchone()
            conn.close()

            if user:
                # Chuyển từ tuple thành dictionary để dễ sử dụng
                columns = ['id', 'username', 'password', 'email', 'full_name',
                           'favorite_team', 'registration_date']
                user_dict = {columns[i]: user[i] for i in range(len(columns))}
                return True, user_dict
            else:
                return False, "Tên đăng nhập hoặc mật khẩu không đúng!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def get_user_by_username(self, username):
        """Lấy thông tin người dùng theo username"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            conn.close()

            if user:
                columns = ['id', 'username', 'password', 'email', 'full_name',
                           'favorite_team', 'registration_date']
                user_dict = {columns[i]: user[i] for i in range(len(columns))}
                return user_dict
            else:
                return None
        except Exception:
            return None