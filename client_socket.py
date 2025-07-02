import pygame
import socket
import time
import json

#konfigurasi server
HOST = '10.8.195.10'
PORT = 8881

PLAYER_ID = input("Masukkan ID kamu (X atau O): ").strip().upper()
ROOM_ID = input("Masukkan nama room: ").strip()

#untuk tampilan pygame
pygame.init()
WIDTH, HEIGHT = 500, 510
BG_COLOR = (224, 241, 244)
LINE_COLOR = (0, 55, 61)
X_COLOR = (219, 50, 54)
O_COLOR = (66, 133, 244)
TEXT_COLOR = (0, 55, 61)
HOVER_COLOR = (200, 230, 235)
WIN_LINE_COLOR = (255, 0, 0)

BOARD_TOP = 105
BOARD_SIZE = 300
CELL_SIZE = 100
GRID_LEFT = (WIDTH - BOARD_SIZE) // 2
INFO_TOP = BOARD_TOP + BOARD_SIZE + 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe Multiplayer")

title_font = pygame.font.Font("assets/backup/SuperMario256.ttf", 38)
info_font  = pygame.font.Font("assets/backup/Display Plan.ttf", 26)
small_font = pygame.font.Font("assets/backup/Display Plan.ttf", 22)
xo_font    = pygame.font.Font("assets/backup/BaksoSapi.otf", 90)

board = [['' for _ in range(3)] for _ in range(3)]
current_turn = None
winner_text = ""
winner_coords = None

def make_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    return sock

def send_http_request(request_str):
    try:
        sock = make_socket()
        sock.sendall(request_str.encode())
        data_received = b""
        while True:
            data = sock.recv(4096)
            if not data:
                break
            data_received += data
        sock.close()

        response_body = data_received.split(b'\r\n\r\n', 1)[-1]
        return response_body.decode()
    except Exception as e:
        print(f"[!] Error socket: {e}")
        return ""

def register():
    global current_turn
    req = f"GET /register?id={PLAYER_ID}&room={ROOM_ID} HTTP/1.0\r\nHost: {HOST}\r\n\r\n"
    resp = send_http_request(req)
    if resp:
        try:
            data = json.loads(resp)
            current_turn = data.get("turn")
            print(f"Terdaftar sebagai {PLAYER_ID} di room {ROOM_ID}")
        except:
            print("Gagal parsing JSON response register")

def get_status():
    global board, current_turn, winner_text, winner_coords
    req = f"GET /status?room={ROOM_ID} HTTP/1.0\r\nHost: {HOST}\r\n\r\n"
    resp = send_http_request(req)
    if resp:
        try:
            data = json.loads(resp)
            board[:] = data["board"]
            current_turn = data["turn"]
            winner = data.get("winner")
            if winner:
                winner_text = "Draw!" if winner == "DRAW" else f"Pemenang: {winner}"
                winner_coords = get_winning_line(board)
            else:
                winner_text = ""
                winner_coords = None
        except:
            print("Gagal parsing JSON status")

def send_move(row, col):
    req = f"POST /move?player={PLAYER_ID}&r={row}&c={col}&room={ROOM_ID} HTTP/1.0\r\nHost: {HOST}\r\nContent-Length: 0\r\n\r\n"
    resp = send_http_request(req)
    print("RESP:", resp)

def draw_board(hover_pos=None):
    screen.fill(BG_COLOR)
    for i in range(1, 3):
        pygame.draw.line(screen, LINE_COLOR, (GRID_LEFT, BOARD_TOP + i*CELL_SIZE),
                         (GRID_LEFT+BOARD_SIZE, BOARD_TOP + i*CELL_SIZE), 3)
        pygame.draw.line(screen, LINE_COLOR, (GRID_LEFT + i*CELL_SIZE, BOARD_TOP),
                         (GRID_LEFT + i*CELL_SIZE, BOARD_TOP+BOARD_SIZE), 3)

    for r in range(3):
        for c in range(3):
            x = GRID_LEFT + c*CELL_SIZE + CELL_SIZE//2
            y = (BOARD_TOP + r*CELL_SIZE + CELL_SIZE//2) + 10
            if board[r][c] in ['X', 'O']:
                color = X_COLOR if board[r][c] == 'X' else O_COLOR
                xo_surf = xo_font.render(board[r][c], True, color)
                xo_rect = xo_surf.get_rect(center=(x, y))
                screen.blit(xo_surf, xo_rect)
            elif hover_pos == (r, c):
                pygame.draw.rect(screen, HOVER_COLOR, (GRID_LEFT + c*CELL_SIZE, BOARD_TOP + r*CELL_SIZE, CELL_SIZE, CELL_SIZE), border_radius=6)

    if winner_coords:
        draw_win_line(winner_coords)

    title_surf = title_font.render("Tic Tac Toe", True, (0, 55, 61))
    title_rect = title_surf.get_rect(center=(WIDTH//2, 40))
    screen.blit(title_surf, title_rect)

    turn_info = f"Giliran: {current_turn or '?'}"
    turn_surf = info_font.render(turn_info, True, (255, 82, 3))
    turn_rect = turn_surf.get_rect(center=(WIDTH//2, INFO_TOP+20))
    screen.blit(turn_surf, turn_rect)

    info_y = INFO_TOP + 50
    room_surf = small_font.render(f"Room: {ROOM_ID}", True, TEXT_COLOR)
    player_surf = small_font.render(f"Kamu: {PLAYER_ID}", True, TEXT_COLOR)
    screen.blit(room_surf, (20, info_y))
    screen.blit(player_surf, (WIDTH - player_surf.get_width() - 20, info_y))

    if winner_text:
        win_surf = info_font.render(winner_text, True, (255, 0, 0))
        win_rect = win_surf.get_rect(center=(WIDTH//2, 65))
        screen.blit(win_surf, win_rect)

    pygame.display.update()

def get_winning_line(b):
    for i in range(3):
        if b[i][0] != "" and b[i][0] == b[i][1] == b[i][2]:
            y = BOARD_TOP + CELL_SIZE//2 + i*CELL_SIZE
            return ((GRID_LEFT, y), (GRID_LEFT+BOARD_SIZE, y))
        if b[0][i] != "" and b[0][i] == b[1][i] == b[2][i]:
            x = GRID_LEFT + CELL_SIZE//2 + i*CELL_SIZE
            return ((x, BOARD_TOP), (x, BOARD_TOP+BOARD_SIZE))
    if b[0][0] != "" and b[0][0] == b[1][1] == b[2][2]:
        return ((GRID_LEFT, BOARD_TOP), (GRID_LEFT+BOARD_SIZE, BOARD_TOP+BOARD_SIZE))
    if b[0][2] != "" and b[0][2] == b[1][1] == b[2][0]:
        return ((GRID_LEFT+BOARD_SIZE, BOARD_TOP), (GRID_LEFT, BOARD_TOP+BOARD_SIZE))
    return None

def draw_win_line(coords):
    pygame.draw.line(screen, WIN_LINE_COLOR, coords[0], coords[1], 6)

#mainloop
register()
draw_board()
clock = pygame.time.Clock()
last_poll = 0
running = True

while running:
    hover_pos = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not winner_text:
            x, y = pygame.mouse.get_pos()
            if GRID_LEFT <= x < GRID_LEFT+BOARD_SIZE and BOARD_TOP <= y < BOARD_TOP+BOARD_SIZE:
                row, col = (y-BOARD_TOP)//CELL_SIZE, (x-GRID_LEFT)//CELL_SIZE
                if board[row][col] == '' and PLAYER_ID == current_turn:
                    send_move(row, col)

    x, y = pygame.mouse.get_pos()
    if GRID_LEFT <= x < GRID_LEFT+BOARD_SIZE and BOARD_TOP <= y < BOARD_TOP+BOARD_SIZE:
        row, col = (y-BOARD_TOP)//CELL_SIZE, (x-GRID_LEFT)//CELL_SIZE
        if board[row][col] == '':
            hover_pos = (row, col)

    if time.time() - last_poll >= 1:
        get_status()
        last_poll = time.time()

    draw_board(hover_pos)
    clock.tick(60)

pygame.quit()
