import time
from kandinsky import fill_rect, draw_string, color
from ion import keydown, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_OK, KEY_BACKSPACE
from random import choice

# --- Game Settings ---
FPS_DELAY = 0.025
CW = 7        
OX = 62       
OY = 2        

BLACK = color(0,0,0)
BLUE = color(33,33,255)
YELLOW = color(255,255,0)
WHITE = color(255,255,255)
DOT_C = color(255,184,174)
FRIGHT_C = color(33,33,255)

G_COLORS = [color(255,0,0), color(255,184,255), color(0,255,255), color(255,184,82)]

RAW_MAP = [
"╔════════════╦╦════════════╗",
"║............║║............║",
"║.╔══╗.╔═══╗.║║.╔═══╗.╔══╗.║",
"║o║  ║.║   ║.║║.║   ║.║  ║o║",
"║.╚══╝.╚═══╝.╚╝.╚═══╝.╚══╝.║",
"║..........................║",
"║.╔══╗.╔╗.╔══════╗.╔╗.╔══╗.║",
"║.╚══╝.║║.╚══╗╔══╝.║║.╚══╝.║",
"║......║║....║║....║║......║",
"╚════╗.║╚══╗ ║║ ╔══╝║.╔════╝",
"     ║.║╔══╝ ╚╝ ╚══╗║.║     ",
"     ║.║║          ║║.║     ",
"     ║.║║ ╔══--══╗ ║║.║     ",
"═════╝.╚╝ ║      ║ ╚╝.╚═════",
"      .   ║      ║   .      ",
"═════╗.╔╗ ║      ║ ╔╗.╔═════",
"     ║.║║ ╚══════╝ ║║.║     ",
"     ║.║║          ║║.║     ",
"     ║.║║ ╔══════╗ ║║.║     ",
"╔════╝.╚╝ ╚══╗╔══╝ ╚╝.╚════╗",
"║............║║............║",
"║.╔══╗.╔═══╗.║║.╔═══╗.╔══╗.║",
"║.╚═╗║.╚═══╝.╚╝.╚═══╝.║╔═╝.║",
"║o..║║.......  .......║║..o║",
"══╗.║║.╔╗.╔══════╗.╔╗.║║.╔══",
"══╝.╚╝.║║.╚══╗╔══╝.║║.╚╝.╚══",
"║......║║....║║....║║......║",
"║.╔════╝╚══╗.║║.╔══╝╚════╗.║",
"║.╚════════╝.╚╝.╚════════╝.║",
"║..........................║",
"╚══════════════════════════╝"
]

grid = [list(r) for r in RAW_MAP]

def draw_cell(x, y):
    real_x = x
    x = x % 28
    if not (0 <= y < 31): return
    c = grid[y][x]
    px, py = OX + real_x * CW, OY + y * CW
    
    fill_rect(px, py, CW, CW, BLACK)
    if c == ' ': return
    
    mx, my = px + 3, py + 3
    if c in '═╔╚╦╩╠╬': fill_rect(mx, my, 4, 1, BLUE)
    if c in '═╗╝╦╩╣╬': fill_rect(px, my, 4, 1, BLUE)
    if c in '║╚╝╠╣╩╬': fill_rect(mx, py, 1, 4, BLUE)
    if c in '║╔╗╠╣╦╬': fill_rect(mx, my, 1, 4, BLUE)
    
    if c == '-': fill_rect(px, my, CW, 1, color(255,184,255))
    elif c == '.': fill_rect(mx, my, 2, 2, DOT_C)
    elif c == 'o': fill_rect(mx-1, my-1, 4, 4, DOT_C)

fill_rect(0, 0, 320, 222, BLACK)
dots_total = 0
for y in range(31):
    for x in range(28):
        if grid[y][x] in ['.', 'o']: dots_total += 1
        draw_cell(x, y)

class Ent:
    def __init__(self, x, y, col):
        self.x = x * CW
        self.y = y * CW
        self.old_x, self.old_y = self.x, self.y
        self.dx, self.dy = 0, 0
        self.col = col
        self.state = 0
        self.state_changed = False

    def set_state(self, s):
        if self.state != s:
            self.state = s
            self.state_changed = True

def draw_pac(e):
    px, py = OX + e.x, OY + e.y
    fill_rect(px+2, py+1, 3, 5, YELLOW)
    fill_rect(px+1, py+2, 5, 3, YELLOW)
    if (e.x + e.y) % 4 < 2:
        if e.dx > 0: fill_rect(px+4, py+2, 3, 3, BLACK)
        elif e.dx < 0: fill_rect(px, py+2, 3, 3, BLACK)
        elif e.dy > 0: fill_rect(px+2, py+4, 3, 3, BLACK)
        elif e.dy < 0: fill_rect(px+2, py, 3, 3, BLACK)

def draw_ghost(e):
    px, py = OX + e.x, OY + e.y
    if e.state == 2:
        fill_rect(px+2, py+2, 1, 1, WHITE)
        fill_rect(px+4, py+2, 1, 1, WHITE)
        return
    c = e.col
    if e.state == 1:
        if fright_timer < 60 and (fright_timer // 8) % 2 == 0: c = WHITE
        else: c = FRIGHT_C
            
    fill_rect(px+2, py+1, 3, 1, c)
    fill_rect(px+1, py+2, 5, 1, c)
    fill_rect(px+1, py+3, 5, 3, c)
    
    if e.state != 1:
        ex, ey = 0, 0
        if e.dx > 0: ex = 1
        elif e.dx < 0: ex = -1
        elif e.dy > 0: ey = 1
        elif e.dy < 0: ey = -1
        fill_rect(px+2+ex, py+2+ey, 1, 1, BLACK)
        fill_rect(px+4+ex, py+2+ey, 1, 1, BLACK)
    else:
        fill_rect(px+2, py+2, 1, 1, DOT_C)
        fill_rect(px+4, py+2, 1, 1, DOT_C)
        fill_rect(px+2, py+4, 3, 1, DOT_C)

pac = Ent(13, 23, YELLOW)
ghosts = [Ent(13, 11, G_COLORS[0]), Ent(13, 14, G_COLORS[1]), Ent(11, 14, G_COLORS[2]), Ent(16, 14, G_COLORS[3])]
ghosts[0].dx = -1

entities = [pac] + ghosts
score = 0
lives = 3
ghost_mult = 200
fright_timer = 0
ndx, ndy = 0, 0
dead = False
frame_count = 0

def draw_ui():
    draw_string("SCORE", 2, 10, WHITE, BLACK)
    draw_string(str(score), 2, 30, YELLOW, BLACK)
    draw_string("LIVES", 260, 10, WHITE, BLACK)
    fill_rect(260, 30, 60, 20, BLACK)
    for i in range(lives):
        fill_rect(260 + i*15, 30, 10, 10, YELLOW)

def reset_entities():
    pac.x, pac.y = 13*CW, 23*CW
    pac.dx, pac.dy = 0, 0
    ghosts[0].x, ghosts[0].y = 13*CW, 11*CW
    ghosts[1].x, ghosts[1].y = 13*CW, 14*CW
    ghosts[2].x, ghosts[2].y = 11*CW, 14*CW
    ghosts[3].x, ghosts[3].y = 16*CW, 14*CW
    for gh in ghosts: gh.set_state(0)

draw_ui()

while not dead:
    frame_count += 1
    if keydown(KEY_BACKSPACE): break
    
    ku, kd, kl, kr = keydown(KEY_UP), keydown(KEY_DOWN), keydown(KEY_LEFT), keydown(KEY_RIGHT)
    if ku: ndx, ndy = 0, -1
    elif kd: ndx, ndy = 0, 1
    elif kl: ndx, ndy = -1, 0
    elif kr: ndx, ndy = 1, 0

    if (ndx == -pac.dx and ndy == -pac.dy) and (pac.dx != 0 or pac.dy != 0):
        pac.dx, pac.dy = ndx, ndy

    if pac.x % CW == 0 and pac.y % CW == 0:
        cx, cy = pac.x // CW, pac.y // CW
        c = grid[cy][cx]
        
        if c in ['.', 'o']:
            dots_total -= 1
            if c == 'o':
                score += 50
                fright_timer = 250
                ghost_mult = 200
                for g in ghosts:
                    if g.state == 0:
                        g.set_state(1)
                        if g.dx != 0 or g.dy != 0: g.dx, g.dy = -g.dx, -g.dy
            else:
                score += 10
            grid[cy][cx] = ' '
            draw_ui()
            draw_cell(cx, cy)
            
        if dots_total <= 0: dead = True; break
            
        nx, ny = (cx + ndx) % 28, cy + ndy
        if grid[ny][nx] in [' ', '.', 'o']: pac.dx, pac.dy = ndx, ndy
            
        nx, ny = (cx + pac.dx) % 28, cy + pac.dy
        if grid[ny][nx] not in [' ', '.', 'o']: pac.dx, pac.dy = 0, 0
            
    pac.x += pac.dx
    pac.y += pac.dy
    
    if pac.x < 0: pac.x = 28*CW - 1
    elif pac.x >= 28*CW: pac.x = 0
    
    if fright_timer > 0:
        fright_timer -= 1
        if fright_timer == 0:
            for g in ghosts:
                if g.state == 1: g.set_state(0)

    for i, g in enumerate(ghosts):
        # Frame-skip slows down frightened ghosts to exactly 50% speed
        if g.state == 1 and frame_count % 2 == 0: continue 
        
        if g.x % CW == 0 and g.y % CW == 0:
            cx, cy = g.x // CW, g.y // CW
            
            if g.state == 2 and cx in [13, 14] and 13 <= cy <= 14:
                g.set_state(0)
                g.dx, g.dy = 0, 0 
                
            dirs = []
            for dx, dy in [(0,-1), (-1,0), (0,1), (1,0)]:
                if dx == -g.dx and dy == -g.dy and (g.dx!=0 or g.dy!=0): continue
                nx, ny = (cx + dx) % 28, cy + dy
                if 0 <= ny < 31:
                    c = grid[ny][nx]
                    if c in [' ', '.', 'o']: dirs.append((dx, dy))
                    elif c == '-':
                        if g.state == 2 or cy >= 12: dirs.append((dx, dy))
                            
            if dirs:
                if g.state == 1 and not (cy >= 12 and 11 <= cx <= 16):
                    tx, ty = pac.x // CW, pac.y // CW
                    best_d, best_dist = dirs[0], -1
                    for d in dirs:
                        nx, ny = cx + d[0], cy + d[1]
                        dist = (nx - tx)**2 + (ny - ty)**2
                        if dist > best_dist: best_dist, best_d = dist, d
                    g.dx, g.dy = best_d
                else:
                    if g.state == 2:
                        if cx in [13, 14] and 11 <= cy <= 14: tx, ty = 13, 14
                        else: tx, ty = 13, 11
                    elif cy >= 12 and 11 <= cx <= 16:
                        tx, ty = 13, 11 
                    else:
                        tx, ty = pac.x // CW, pac.y // CW
                        if i == 1: tx += pac.dx*4; ty += pac.dy*4
                        elif i == 2: tx += choice([-2,2,0]); ty += choice([-2,2,0])
                        elif i == 3:
                            if abs(cx-tx) + abs(cy-ty) < 8: tx, ty = 0, 31
                            
                    best_d, best_dist = dirs[0], 999999
                    for d in dirs:
                        nx, ny = cx + d[0], cy + d[1]
                        dist = (nx - tx)**2 + (ny - ty)**2
                        if dist < best_dist: best_dist, best_d = dist, d
                    g.dx, g.dy = best_d
        
        g.x += g.dx
        g.y += g.dy
        if g.x < 0: g.x = 28*CW - 1
        elif g.x >= 28*CW: g.x = 0
        
    collision = False
    for g in ghosts:
        if g.state == 2: continue
        if abs(pac.x - g.x) < CW-2 and abs(pac.y - g.y) < CW-2:
            if g.state == 1:
                g.set_state(2)
                score += ghost_mult
                ghost_mult *= 2
                draw_ui()
            else:
                lives -= 1
                draw_ui()
                time.sleep(1)
                if lives <= 0: dead = True
                else:
                    reset_entities()
                    ndx, ndy = 0, 0
                    collision = True
    if collision: continue

    cells = []
    for e in entities:
        if e.x != e.old_x or e.y != e.old_y or e.state_changed:
            for px, py in [(e.old_x, e.old_y), (e.x, e.y)]:
                cx, cy = px // CW, py // CW
                pts = [(cx, cy)]
                if px % CW != 0: pts.append(((cx+1)%28, cy))
                if py % CW != 0: pts.append((cx, cy+1))
                if px % CW != 0 and py % CW != 0: pts.append(((cx+1)%28, cy+1))
                for p in pts:
                    if p not in cells: cells.append(p)
            
    for cx, cy in cells:
        draw_cell(cx, cy)
        
    for e in entities:
        if e == pac: draw_pac(e)
        else: draw_ghost(e)
        e.old_x, e.old_y = e.x, e.y
        e.state_changed = False

    time.sleep(FPS_DELAY)

if dots_total <= 0:
    draw_string(" YOU WIN! ", 110, 110, BLACK, YELLOW)
else:
    draw_string(" GAME OVER ", 110, 110, WHITE, color(255,0,0))

while not keydown(KEY_OK): pass
