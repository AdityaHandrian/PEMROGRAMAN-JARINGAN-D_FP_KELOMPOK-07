import sys, pygame, threading, requests, time

HOST = 'http://localhost:8881'  # load balancer
WIDTH, HEIGHT = 340, 420
BG_COLOR = (224, 241, 244)
LINE_COLOR = (0, 55, 61)
X_COLOR = (219, 50, 54)
O_COLOR = (66, 133, 244)
TEXT_COLOR = (0, 55, 61)
HOVER_COLOR = (200, 230, 235)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe Multiplayer via Load Balancer")
font = pygame.font.Font(None, 32)

board = [['' for _ in range(3)] for _ in range(3)]
my_symbol = 'X'
room_id = None
turn = None
winner_text = ""
game_over = False

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

    text_surf = font.render(f"Room: {room_id} | Turn: {turn or '?'}", True, TEXT_COLOR)
    screen.blit(text_surf, (20, 340))

    if winner_text:
        win_surf = font.render(winner_text, True, (255, 82, 3))
        screen.blit(win_surf, (20, 370))

    pygame.display.update()

def register_room():
    global room_id
    r = requests.post(f"{HOST}/register")
    room_id = r.json()['room']

def move(row, col):
    try:
        requests.post(f"{HOST}/move/{room_id}", json={
            "row": row,
            "col": col,
            "player": my_symbol
        })
    except:
        pass

def poll_status():
    global board, turn, winner_text, game_over
    while True:
        try:
            r = requests.get(f"{HOST}/status/{room_id}")
            if r.status_code == 200:
                data = r.json()
                board = data['board']
                turn = data['turn']
                winner = data['winner']
                if winner:
                    winner_text = "Draw!" if winner == "DRAW" else f"Pemenang: {winner}"
                    game_over = True
            draw_board()
        except:
            pass
        time.sleep(0.8)

register_room()
threading.Thread(target=poll_status, daemon=True).start()

draw_board()
clock = pygame.time.Clock()

running = True
while running:
    hover_pos = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            x, y = pygame.mouse.get_pos()
            if 20 <= x < 320 and 20 <= y < 320:
                row, col = (y-20)//100, (x-20)//100
                if board[row][col] == '' and turn == my_symbol:
                    move(row, col)

    mx, my = pygame.mouse.get_pos()
    if 20 <= mx < 320 and 20 <= my < 320:
        row, col = (my-20)//100, (mx-20)//100
        if board[row][col] == '' and not game_over:
            hover_pos = (row, col)

    draw_board(hover_pos)
    clock.tick(60)

pygame.quit()
