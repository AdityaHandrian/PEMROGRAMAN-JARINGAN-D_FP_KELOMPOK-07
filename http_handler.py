import os.path
import time
import json
from glob import glob
from datetime import datetime
from urllib.parse import urlparse, parse_qs

class HttpServer:
    def __init__(self):
        self.sessions={}
        self.types={}
        self.types['.pdf']='application/pdf'
        self.types['.jpg']='image/jpeg'
        self.types['.txt']='text/plain'
        self.types['.html']='text/html'
        self.games = {}  # key: room name

    def new_game(self):
        return {
            "board": [['' for _ in range(3)] for _ in range(3)],
            "turn": 'X',
            "winner": None,
            "win_time": None,
            "last_winning_board": None,
            "players": set()
        }

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = []
        resp.append("HTTP/1.0 {} {}\r\n" . format(kode,message))
        resp.append("Date: {}\r\n" . format(tanggal))
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append("Content-Length: {}\r\n" . format(len(messagebody)))
        for kk in headers:
            resp.append("{}:{}\r\n" . format(kk,headers[kk]))
        resp.append("\r\n")

        response_headers = ''
        for i in resp:
            response_headers="{}{}" . format(response_headers,i)
        #menggabungkan resp menjadi satu string dan menggabungkan dengan messagebody yang berupa bytes
		#response harus berupa bytes
		#message body harus diubah dulu menjadi bytes
        if type(messagebody) is not bytes:
            messagebody = messagebody.encode()

        response = response_headers.encode() + messagebody
        #response adalah bytes
        return response

    def proses(self, data):
        requests = data.split("\r\n")
		#print(requests)
        
        baris = requests[0]
		#print(baris)
        all_headers = [n for n in requests[1:] if n != '']

        j = baris.split(" ")
        try:
            method = j[0].upper().strip()
            if method == 'GET':
                object_address = j[1].strip()
                return self.http_get(object_address, all_headers)
            elif method == 'POST':
                object_address = j[1].strip()
                return self.http_post(object_address, all_headers)
            else:
                return self.response(400,'Bad Request','',{})
        except IndexError:
            return self.response(400,'Bad Request','',{})

    def http_get(self, object_address, headers):
        parsed = urlparse(object_address)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == '/register':
            player_id = params.get("id", [""])[0]
            room = params.get("room", [""])[0]

            if not player_id or not room:
                return self.response(400, "Bad Request", '{"status": "NO_ID_OR_ROOM"}',
                                     {'Content-Type': 'application/json'})
            if player_id not in ['X', 'O']:
                return self.response(400, "Bad Request", '{"status": "INVALID_ID"}',
                                     {'Content-Type': 'application/json'})

            if room not in self.games:
                self.games[room] = self.new_game()

            self.games[room]["players"].add(player_id)
            print(f"[{room}] REGISTER → {player_id}")
            return self.response(200, "OK", json.dumps({
                "status": "REGISTERED",
                "total_players": len(self.games[room]["players"]),
                "turn": self.games[room]["turn"]
            }), {'Content-Type': 'application/json'})

        if path == '/status':
            room = params.get("room", [""])[0]
            if not room or room not in self.games:
                return self.response(404, 'Not Found', '{"status":"ROOM_NOT_FOUND"}',
                                     {'Content-Type': 'application/json'})
            g = self.games[room]
            if g["winner"] and g["win_time"] and time.time() - g["win_time"] > 10:
                self.games[room] = self.new_game()
                g = self.games[room]

            board = g["last_winning_board"] if g["winner"] else g["board"]
            return self.response(200, "OK", json.dumps({
                "board": board,
                "turn": g["turn"],
                "winner": g["winner"]
            }), {'Content-Type': 'application/json'})

        #fallback static file
        if path == '/':
            return self.response(200, 'OK', 'TicTacToe HTTP Server', {'Content-Type': 'text/plain'})

        object_address = path[1:]
        files = glob('./*')
        if './' + object_address not in files:
            return self.response(404, 'Not Found', '{"status":"FILE_NOT_FOUND"}',
                                 {'Content-Type': 'application/json'})
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
            player = params.get("player", [""])[0]
            r = params.get("r", [""])[0]
            c = params.get("c", [""])[0]
            room = params.get("room", [""])[0]

            if not (player and r and c and room):
                return self.response(400, "Bad Request", '{"status": "INVALID_PARAM"}',
                                     {'Content-Type': 'application/json'})

            if room not in self.games:
                return self.response(404, 'Not Found', '{"status":"ROOM_NOT_FOUND"}',
                                     {'Content-Type': 'application/json'})

            g = self.games[room]

            if g["winner"]:
                return self.response(200, "OK", '{"status": "GAME_OVER"}',
                                     {'Content-Type': 'application/json'})

            try:
                r, c = int(r), int(c)
            except:
                return self.response(400, "Bad Request", '{"status": "INVALID_COORD"}',
                                     {'Content-Type': 'application/json'})

            if g["board"][r][c] != "":
                return self.response(200, "OK", '{"status": "INVALID_MOVE"}',
                                     {'Content-Type': 'application/json'})

            if player != g["turn"]:
                return self.response(200, "OK", '{"status": "NOT_YOUR_TURN"}',
                                     {'Content-Type': 'application/json'})

            g["board"][r][c] = player
            print(f"[{room}] MOVE {player} → ({r},{c})")

            winner = self.check_winner(g["board"])
            if winner:
                g["winner"] = winner
                g["win_time"] = time.time()
                g["last_winning_board"] = [row.copy() for row in g["board"]]
                print(f"[{room}] WINNER: {winner}")
            else:
                g["turn"] = "O" if player == "X" else "X"

            return self.response(200, "OK", '{"status": "OK"}',
                                 {'Content-Type': 'application/json'})

        return self.response(404, 'Not Found', '{"status": "UNKNOWN_ENDPOINT"}',
                             {'Content-Type': 'application/json'})

    def check_winner(self, b):
        for p in ['X', 'O']:
            for i in range(3):
                if all(b[i][j] == p for j in range(3)): return p
                if all(b[j][i] == p for j in range(3)): return p
            if all(b[i][i] == p for i in range(3)): return p
            if all(b[i][2 - i] == p for i in range(3)): return p
        if all(cell != '' for row in b for cell in row):
            return 'DRAW'
        return None
