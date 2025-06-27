import sys, pygame, socket, threading

HOST = '192.168.43.144'  # ganti ke IP server kamu
PORT = 65432

WIDTH, HEIGHT = 340, 420
BG_COLOR = (224, 241, 244)
LINE_COLOR = (0, 55, 61)
X_COLOR = (219, 50, 54)
O_COLOR = (66, 133, 244)
TEXT_COLOR = (0, 55, 61)
HOVER_COLOR = (200, 230, 235)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe Multiplayer")

font = pygame.font.Font(None, 32)

board = [['' for _ in range(3)] for _ in range(3)]
my_symbol = None
current_turn = None
game_over = False
winner_text = ""

def draw_board(hover_pos=None):
    screen.fill(BG_COLOR)

    for i in range(1, 3):
        pygame.draw.line(screen, LINE_COLOR, (20, i*100+20), (320, i*100+20), 3)
        pygame.draw.line(screen, LINE_COLOR, (i*100+20, 20), (i*100+20, 320), 3)

    for r in range(3):
        for c in range(3):
            x = 20 + c*100 + 50
            y = 20 + r*100 + 50
            if board[r][c] == 'X':
                pygame.draw.line(screen, X_COLOR, (x-25, y-25), (x+25, y+25), 6)
                pygame.draw.line(screen, X_COLOR, (x+25, y-25), (x-25, y+25), 6)
            elif board[r][c] == 'O':
                pygame.draw.circle(screen, O_COLOR, (x, y), 30, 6)
            elif hover_pos == (r, c):
                pygame.draw.rect(screen, HOVER_COLOR, (20 + c*100, 20 + r*100, 100, 100), border_radius=6)

    info = f"Your: {my_symbol or '?'} | Turn: {current_turn or '?'}"
    text_surf = font.render(info, True, TEXT_COLOR)
    screen.blit(text_surf, (20, 340))

    if winner_text:
        win_surf = font.render(winner_text, True, (255, 82, 3))
        screen.blit(win_surf, (20, 370))

    pygame.display.update()

def recv_server(sock):
    global my_symbol, current_turn, board, game_over, winner_text
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                break
            lines = data.strip().split('\n')
            for line in lines:
                if line.startswith('ROLE:'):
                    my_symbol = line.split(':')[1]
                    print(f"You are {my_symbol}")
                elif line.startswith('TURN:'):
                    current_turn = line.split(':')[1]
                    print(f"Giliran: {current_turn}")
                elif line.startswith('UPDATE:'):
                    sym, r, c = line.split(':')[1].split(',')
                    board[int(r)][int(c)] = sym
                    draw_board()
                elif line.startswith('WIN:'):
                    pemenang = line.split(':')[1]
                    if pemenang == 'DRAW':
                        winner_text = "Hasil: Draw!"
                    else:
                        winner_text = f"Pemenang: {pemenang}"
                    game_over = True
                    draw_board()
        except:
            break

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
threading.Thread(target=recv_server, args=(sock,), daemon=True).start()

draw_board()
clock = pygame.time.Clock()

running = True
while running:
    hover_pos = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sock.close()
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            x, y = pygame.mouse.get_pos()
            if 20 <= x < 320 and 20 <= y < 320:
                row, col = (y-20)//100, (x-20)//100
                if board[row][col] == '' and my_symbol == current_turn:
                    sock.sendall(f"MOVE:{row},{col}\n".encode())

    # Hover detection
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if 20 <= mouse_x < 320 and 20 <= mouse_y < 320:
        row, col = (mouse_y-20)//100, (mouse_x-20)//100
        if board[row][col] == '':
            hover_pos = (row, col)

    draw_board(hover_pos)
    clock.tick(60)

pygame.quit()
