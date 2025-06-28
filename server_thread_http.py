import http.server
import socketserver
import threading
import json

PORT = 8889  # bisa 8889 / 8890 / 8891 tergantung instance

rooms = {}
lock = threading.Lock()

class GameHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parts = self.path.strip('/').split('/')
        if len(parts) == 2 and parts[0] == 'status':
            room_id = parts[1]
            with lock:
                if room_id in rooms:
                    self.respond_json(rooms[room_id])
                else:
                    self.respond_json({"error": "Room not found"}, 404)
        else:
            self.respond_json({"error": "Invalid GET path"}, 400)

    def do_POST(self):
        parts = self.path.strip('/').split('/')
        length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(length)
        try:
            data = json.loads(post_data.decode())
        except:
            data = {}

        if self.path == '/register':
            with lock:
                new_room = str(len(rooms) + 1)
                rooms[new_room] = {
                    "board": [['' for _ in range(3)] for _ in range(3)],
                    "turn": 'X',
                    "winner": None
                }
            self.respond_json({"room": new_room})

        elif len(parts) == 2 and parts[0] == 'move':
            room_id = parts[1]
            row = data.get("row")
            col = data.get("col")
            player = data.get("player")

            with lock:
                if room_id not in rooms:
                    self.respond_json({"error": "Room not found"}, 404)
                    return

                room = rooms[room_id]
                if room["winner"]:
                    self.respond_json({"error": "Game over"}, 400)
                    return

                if room["turn"] != player:
                    self.respond_json({"error": "Not your turn"}, 400)
                    return

                if room["board"][row][col] != '':
                    self.respond_json({"error": "Cell occupied"}, 400)
                    return

                room["board"][row][col] = player
                room["winner"] = self.check_winner(room["board"])

                if not room["winner"]:
                    room["turn"] = 'O' if player == 'X' else 'X'

            self.respond_json({"status": "ok", "room": room})

        else:
            self.respond_json({"error": "Invalid POST path"}, 400)

    def check_winner(self, board):
        for p in ['X', 'O']:
            for i in range(3):
                if all(board[i][j] == p for j in range(3)):
                    return p
                if all(board[j][i] == p for j in range(3)):
                    return p
            if all(board[j][j] == p for j in range(3)):
                return p
            if all(board[j][2-j] == p for j in range(3)):
                return p
        if all(board[i][j] != '' for i in range(3) for j in range(3)):
            return "DRAW"
        return None

    def respond_json(self, data, code=200):
        response = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
        return  # disable default logging to clean console

def run_server():
    with socketserver.ThreadingTCPServer(("", PORT), GameHandler) as httpd:
        print(f"Game Server running on port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
