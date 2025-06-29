import pygame
import requests
import time

# Ganti IP dan port sesuai server kamu
BASE_URL = "http://10.8.195.69:8881"

PLAYER_ID = input("Masukkan ID kamu (X atau O): ").strip().upper()
ROOM_ID = input("Masukkan nama room: ").strip()

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
xo_font = pygame.font.Font("assets/backup/BaksoSapi.otf", 90)


board = [['' for _ in range(3)] for _ in range(3)]
current_turn = None
winner_text = ""
winner_coords = None

def register():
    global current_turn
    try:
        url = f"{BASE_URL}/register?id={PLAYER_ID}&room={ROOM_ID}"
        r = requests.get(url)
        if r.ok:
            data = r.json()
            current_turn = data.get("turn", None)
            print(f"Terdaftar sebagai {PLAYER_ID} di room {ROOM_ID}")
        else:
            print("Gagal register:", r.text)
    except Exception as e:
        print("Error saat register:", e)

def get_status():
    global board, current_turn, winner_text, winner_coords
    try:
        url = f"{BASE_URL}/status?room={ROOM_ID}"
        r = requests.get(url)
        if r.ok:
            data = r.json()
            board[:] = data["board"]
            current_turn = data["turn"]
            winner = data.get("winner")
            if winner:
                winner_text = "Draw!" if winner == "DRAW" else f"Pemenang: {winner}"
                winner_coords = get_winning_line(board)
            else:
                winner_text = ""
                winner_coords = None
        else:
            print("Gagal status:", r.text)
    except Exception as e:
        print("Error:", e)

def send_move(row, col):
    try:
        url = f"{BASE_URL}/move?player={PLAYER_ID}&r={row}&c={col}&room={ROOM_ID}"
        r = requests.post(url)
        print("Kirim langkah:", r.text)
    except Exception as e:
        print("Gagal kirim:", e)

def draw_board(hover_pos=None):
    screen.fill(BG_COLOR)

    # Grid lines
    for i in range(1, 3):
        pygame.draw.line(screen, LINE_COLOR, (GRID_LEFT, BOARD_TOP + i*CELL_SIZE),
                         (GRID_LEFT+BOARD_SIZE, BOARD_TOP + i*CELL_SIZE), 3)
        pygame.draw.line(screen, LINE_COLOR, (GRID_LEFT + i*CELL_SIZE, BOARD_TOP),
                         (GRID_LEFT + i*CELL_SIZE, BOARD_TOP+BOARD_SIZE), 3)

    # XO & hover
    for r in range(3):
        for c in range(3):
            x = GRID_LEFT + c*CELL_SIZE + CELL_SIZE//2
            y = (BOARD_TOP + r*CELL_SIZE + CELL_SIZE//2) + 10  # Offset for centering text
            if board[r][c] in ['X', 'O']:
                color = X_COLOR if board[r][c] == 'X' else O_COLOR
                xo_surf = xo_font.render(board[r][c], True, color)
                xo_rect = xo_surf.get_rect(center=(x, y))
                screen.blit(xo_surf, xo_rect)
            elif hover_pos == (r, c):
                pygame.draw.rect(screen, HOVER_COLOR, (GRID_LEFT + c*CELL_SIZE, BOARD_TOP + r*CELL_SIZE, CELL_SIZE, CELL_SIZE), border_radius=6)
    
    # Winner line
    if winner_coords:
        draw_win_line(winner_coords)

    # Title
    title_surf = title_font.render("Tic Tac Toe", True, (0, 55, 61))
    title_rect = title_surf.get_rect(center=(WIDTH//2, 40))
    screen.blit(title_surf, title_rect)

    # Giliran
    turn_info = f"Giliran: {current_turn or '?'}"
    turn_surf = info_font.render(turn_info, True, (255, 82, 3))
    turn_rect = turn_surf.get_rect(center=(WIDTH//2, INFO_TOP+20))
    screen.blit(turn_surf, turn_rect)

    # Room & player info
    info_y = INFO_TOP + 50
    room_surf = small_font.render(f"Room: {ROOM_ID}", True, TEXT_COLOR)
    player_surf = small_font.render(f"Kamu: {PLAYER_ID}", True, TEXT_COLOR)
    screen.blit(room_surf, (20, info_y))
    screen.blit(player_surf, (WIDTH - player_surf.get_width() - 20, info_y))

    # Winner banner
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

# Main Loop
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
