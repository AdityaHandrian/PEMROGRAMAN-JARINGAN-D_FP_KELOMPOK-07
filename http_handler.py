import os.path
import time
import json
from glob import glob
from datetime import datetime
from urllib.parse import urlparse, parse_qs

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.txt': 'text/plain',
            '.html': 'text/html'
        }
        self.players = set()
        self.reset_game()

    def reset_game(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.turn = 'X'
        self.winner = None
        self.win_time = None
        self.last_winning_board = None
        print("[RESET] Game restarted.")

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = []
        resp.append(f"HTTP/1.0 {kode} {message}\r\n")
        resp.append(f"Date: {tanggal}\r\n")
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append(f"Content-Length: {len(messagebody)}\r\n")
        for kk in headers:
            resp.append(f"{kk}: {headers[kk]}\r\n")
        resp.append("\r\n")

        response_headers = ''.join(resp)
        if type(messagebody) is not bytes:
            messagebody = messagebody.encode()

        return response_headers.encode() + messagebody

    def proses(self, data):
        try:
            requests = data.split("\r\n")
            baris = requests[0]
            all_headers = [n for n in requests[1:] if n != '']
            j = baris.split(" ")
            method = j[0].upper().strip()
            object_address = j[1].strip()

            if method == 'GET':
                return self.http_get(object_address, all_headers)
            elif method == 'POST':
                return self.http_post(object_address, all_headers)
            else:
                return self.response(400, 'Bad Request', '{"status":"INVALID_METHOD"}', {'Content-Type': 'application/json'})
        except:
            return self.response(400, 'Bad Request', '{"status":"ERROR"}', {'Content-Type': 'application/json'})

    def http_get(self, object_address, headers):
        parsed = urlparse(object_address)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == '/register':
            player_id = params.get("id", [""])[0]
            if not player_id:
                return self.response(400, "Bad Request", '{"status": "NO_ID"}', {'Content-Type': 'application/json'})
            self.players.add(player_id)
            print(f"[REGISTER] → {player_id}")
            return self.response(200, "OK", json.dumps({
                "status": "REGISTERED",
                "total_players": len(self.players),
                "turn": self.turn
            }), {'Content-Type': 'application/json'})

        if path == '/status':
            if self.winner and self.win_time and (time.time() - self.win_time > 10):
                self.reset_game()
            board_to_send = self.last_winning_board if self.winner else self.board
            return self.response(200, "OK", json.dumps({
                "board": board_to_send,
                "turn": self.turn,
                "winner": self.winner
            }), {'Content-Type': 'application/json'})

        # fallback static file support
        if path == '/':
            return self.response(200, 'OK', 'TicTacToe HTTP Server', {'Content-Type': 'text/plain'})
        object_address = path[1:]
        files = glob('./*')
        if './' + object_address not in files:
            return self.response(404, 'Not Found', '{"status":"FILE_NOT_FOUND"}', {'Content-Type': 'application/json'})
        with open('./' + object_address, 'rb') as fp:
            isi = fp.read()
        fext = os.path.splitext(object_address)[1]
        content_type = self.types.get(fext, 'application/octet-stream')
        return self.response(200, 'OK', isi, {'Content-Type': content_type})

    def http_post(self, object_address, headers):
        parsed = urlparse(object_address)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/move":
            if self.winner:
                return self.response(200, "OK", '{"status": "GAME_OVER"}', {'Content-Type': 'application/json'})

            player = params.get("player", [""])[0]
            r = params.get("r", [""])[0]
            c = params.get("c", [""])[0]

            if not (player and r and c):
                return self.response(400, "Bad Request", '{"status": "INVALID_PARAM"}', {'Content-Type': 'application/json'})

            try:
                r, c = int(r), int(c)
            except:
                return self.response(400, "Bad Request", '{"status": "INVALID_COORD"}', {'Content-Type': 'application/json'})

            if self.board[r][c] != "":
                return self.response(200, "OK", '{"status": "INVALID_MOVE"}', {'Content-Type': 'application/json'})

            if player != self.turn:
                return self.response(200, "OK", '{"status": "NOT_YOUR_TURN"}', {'Content-Type': 'application/json'})

            self.board[r][c] = player
            print(f"[MOVE] {player} → ({r},{c})")

            winner = self.check_winner()
            if winner:
                self.winner = winner
                self.win_time = time.time()
                self.last_winning_board = [row.copy() for row in self.board]
                print(f"[WINNER] {winner}")
            else:
                self.turn = "O" if self.turn == "X" else "X"

            return self.response(200, "OK", '{"status": "OK"}', {'Content-Type': 'application/json'})

        return self.response(404, 'Not Found', '{"status": "UNKNOWN_ENDPOINT"}', {'Content-Type': 'application/json'})

    def check_winner(self):
        b = self.board
        for p in ['X', 'O']:
            for i in range(3):
                if all(b[i][j] == p for j in range(3)): return p
                if all(b[j][i] == p for j in range(3)): return p
            if all(b[i][i] == p for i in range(3)): return p
            if all(b[i][2 - i] == p for i in range(3)): return p
        if all(cell != '' for row in b for cell in row):
            return 'DRAW'
        return None
