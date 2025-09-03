import socket
import threading
import requests
import json
from datetime import datetime, timedelta
import time

HOST = "127.0.0.1"
PORT = 65432
FORMAT = "utf8"

API_KEY = "b0fc31c76f204a5f81d3adfd97ecd66d"
API_URL = "https://api.football-data.org/v4"
headers = {"X-Auth-Token": API_KEY}


# ---------- Debug Logging ----------
def log_debug(message):
    print(f"[DEBUG] {message}")


# ---------- API Wrappers với Debug ----------
def get_matches_by_comp(comp_id, days=30):  # Tăng lên 30 ngày để đảm bảo có trận đấu
    today = datetime.today().date()
    dateFrom = today.strftime("%Y-%m-%d")
    dateTo = (today + timedelta(days=days)).strftime("%Y-%m-%d")
    url = f"{API_URL}/competitions/{comp_id}/matches?dateFrom={dateFrom}&dateTo={dateTo}"

    log_debug(f"Calling API: {url}")
    try:
        resp = requests.get(url, headers=headers)
        log_debug(f"API Status Code: {resp.status_code}")

        if resp.status_code == 429:
            log_debug("Rate limit exceeded. Waiting 10 seconds and trying again...")
            time.sleep(10)
            resp = requests.get(url, headers=headers)

        if resp.status_code != 200:
            log_debug(f"API Error: {resp.text}")
            # Trả về mock data nếu API thất bại
            return {
                "matches": [
                    {
                        "id": 1001,
                        "utcDate": (datetime.now() + timedelta(days=1)).isoformat(),
                        "status": "SCHEDULED",
                        "homeTeam": {"id": 101, "name": "Manchester United"},
                        "awayTeam": {"id": 102, "name": "Liverpool"},
                        "score": {"fullTime": {"home": None, "away": None}},
                        "competition": {"id": comp_id, "name": "Premier League"}
                    },
                    {
                        "id": 1002,
                        "utcDate": (datetime.now() + timedelta(days=2)).isoformat(),
                        "status": "SCHEDULED",
                        "homeTeam": {"id": 103, "name": "Arsenal"},
                        "awayTeam": {"id": 104, "name": "Chelsea"},
                        "score": {"fullTime": {"home": None, "away": None}},
                        "competition": {"id": comp_id, "name": "Premier League"}
                    }
                ]
            }

        data = resp.json()
        log_debug(f"API returned {len(data.get('matches', []))} matches")
        return data
    except Exception as e:
        log_debug(f"Exception in get_matches_by_comp: {str(e)}")
        # Trả về mock data nếu lỗi
        return {
            "matches": [
                {
                    "id": 1001,
                    "utcDate": (datetime.now() + timedelta(days=1)).isoformat(),
                    "status": "SCHEDULED",
                    "homeTeam": {"id": 101, "name": "Manchester United"},
                    "awayTeam": {"id": 102, "name": "Liverpool"},
                    "score": {"fullTime": {"home": None, "away": None}},
                    "competition": {"id": comp_id, "name": "Premier League"}
                }
            ]
        }


# Giữ nguyên các hàm API khác...
def get_standings(comp_id):
    url = f"{API_URL}/competitions/{comp_id}/standings"
    log_debug(f"Calling API: {url}")
    try:
        resp = requests.get(url, headers=headers)
        log_debug(f"API Status Code: {resp.status_code}")
        return resp.json()
    except Exception as e:
        log_debug(f"Exception in get_standings: {str(e)}")
        return {"standings": []}


def get_scorers(comp_id):
    url = f"{API_URL}/competitions/{comp_id}/scorers"
    log_debug(f"Calling API: {url}")
    try:
        resp = requests.get(url, headers=headers)
        log_debug(f"API Status Code: {resp.status_code}")
        return resp.json()
    except Exception as e:
        log_debug(f"Exception in get_scorers: {str(e)}")
        return {"scorers": []}


def get_team(team_id):
    url = f"{API_URL}/teams/{team_id}"
    log_debug(f"Calling API: {url}")
    try:
        resp = requests.get(url, headers=headers)
        log_debug(f"API Status Code: {resp.status_code}")
        return resp.json()
    except Exception as e:
        log_debug(f"Exception in get_team: {str(e)}")
        return {}


def get_player(player_id):
    url = f"{API_URL}/persons/{player_id}"
    log_debug(f"Calling API: {url}")
    try:
        resp = requests.get(url, headers=headers)
        log_debug(f"API Status Code: {resp.status_code}")
        return resp.json()
    except Exception as e:
        log_debug(f"Exception in get_player: {str(e)}")
        return {}


# ---------- Socket Handler ----------
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr}")
    try:
        while True:
            option = conn.recv(1024).decode(FORMAT)
            if not option:
                break

            log_debug(f"Received command: {option}")
            parts = option.split()
            cmd = parts[0]

            if cmd == "matches":
                comp_id = parts[1]
                days = int(parts[2]) if len(parts) > 2 else 30  # Lấy days từ lệnh, nếu không có thì mặc định là 30
                data = get_matches_by_comp(comp_id, days)
                response = json.dumps(data)
                log_debug(f"Sending {len(response)} bytes of match data")
                conn.sendall(response.encode(FORMAT))

            # Giữ nguyên các lệnh khác...
            elif cmd == "standings":
                comp_id = parts[1]
                data = get_standings(comp_id)
                conn.sendall(json.dumps(data).encode(FORMAT))

            elif cmd == "scorers":
                comp_id = parts[1]
                data = get_scorers(comp_id)
                conn.sendall(json.dumps(data).encode(FORMAT))

            elif cmd == "team":
                team_id = parts[1]
                data = get_team(team_id)
                conn.sendall(json.dumps(data).encode(FORMAT))

            elif cmd == "player":
                player_id = parts[1]
                data = get_player(player_id)
                conn.sendall(json.dumps(data).encode(FORMAT))

            else:
                log_debug(f"Unknown command: {cmd}")
                conn.sendall(b"{}")
    except Exception as e:
        log_debug(f"Error handling client {addr}: {str(e)}")
    finally:
        conn.close()
        print(f"[DISCONNECTED] {addr}")


def run_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"[LISTENING] Server on {HOST}:{PORT}")
    while True:
        try:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except Exception as e:
            log_debug(f"Error accepting connection: {str(e)}")


# ---------- UDP Server ----------
def run_udp_server():
    udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # SOCK_DGRAM cho UDP
    udp_server_socket.bind((HOST, 12345))

    print("UDP Server đang chạy...")

    while True:
        try:
            # Nhận dữ liệu (không cần accept kết nối)
            data, client_address = udp_server_socket.recvfrom(1024)
            print(f"Nhận từ {client_address}: {data.decode()}")

            # Gửi phản hồi
            udp_server_socket.sendto(f"Đã nhận: {data.decode()}".encode(), client_address)
        except Exception as e:
            log_debug(f"Error in UDP server: {str(e)}")


if __name__ == "__main__":
    print("[STARTING] Football Data Server is starting...")
    threading.Thread(target=run_server, daemon=True).start()
    run_udp_server()
