import socket
import threading

HOST = '0.0.0.0'
PORT = 65432

clients = {}
current_turn = 'X'
board_state = [['' for _ in range(3)] for _ in range(3)]
lock = threading.Lock()

def broadcast(msg):
    for c in clients.values():
        try:
            c.sendall(f"{msg}\n".encode())
        except:
            pass

def check_winner():
    for mark in ['X', 'O']:
        for i in range(3):
            if all(cell == mark for cell in board_state[i]): return mark
            if all(board_state[j][i] == mark for j in range(3)): return mark
        if all(board_state[i][i] == mark for i in range(3)): return mark
        if all(board_state[i][2-i] == mark for i in range(3)): return mark
    if all(cell != '' for row in board_state for cell in row):
        return 'DRAW'
    return None

def reset_game():
    global board_state, current_turn
    print("Resetting game...")
    board_state = [['' for _ in range(3)] for _ in range(3)]
    current_turn = 'X'
    broadcast("RESET")
    broadcast(f"TURN:{current_turn}")

def handle_client(conn, mark):
    global current_turn
    try:
        conn.sendall(f"ROLE:{mark}\n".encode())
        conn.sendall(f"TURN:{current_turn}\n".encode())
        while True:
            data = conn.recv(1024)
            if not data:
                break
            lines = data.decode().strip().split('\n')
            for line in lines:
                if line.startswith('MOVE:'):
                    r, c = map(int, line[5:].split(','))
                    with lock:
                        if board_state[r][c] != '' or mark != current_turn:
                            continue
                        board_state[r][c] = mark
                        broadcast(f"UPDATE:{mark},{r},{c}")
                        winner = check_winner()
                        if winner:
                            broadcast(f"WIN:{winner}")
                            reset_game()
                        else:
                            current_turn = 'O' if current_turn == 'X' else 'X'
                            broadcast(f"TURN:{current_turn}")
    except:
        pass
    finally:
        print(f"Player {mark} disconnected.")
        with lock:
            if mark in clients:
                del clients[mark]
        conn.close()

# Buat socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(2)
print(f"Server listening on {HOST}:{PORT}")

while True:
    conn, addr = s.accept()
    with lock:
        if 'X' not in clients:
            mark = 'X'
        elif 'O' not in clients:
            mark = 'O'
        else:
            conn.sendall("FULL\n".encode())
            conn.close()
            continue

        clients[mark] = conn
        print(f"Player {mark} connected from {addr}")
        threading.Thread(target=handle_client, args=(conn, mark), daemon=True).start()

        if len(clients) == 2:
            broadcast(f"TURN:{current_turn}")
