"""
SNAKE - Omamoodi Mäng
PAP2022 - Kombineeritud näidismängudest 1, 2 ja 3
"""

import pygame
import sys
import random
import json
import os
import math

pygame.init()
pygame.mixer.init()

CELL   = 22
COLS   = 28
ROWS   = 22
HUD_H  = 54
WIN_W  = COLS * CELL
WIN_H  = ROWS * CELL + HUD_H

screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("SNAKE GAME - Oma Moodi Mäng")
clock  = pygame.time.Clock()

C_BG       = ( 13,  14,  26)
C_GRID     = ( 22,  24,  42)
C_HUD_BG   = ( 18,  19,  36)
C_TEXT     = (220, 220, 235)
C_DIM      = ( 90,  92, 115)
C_WHITE    = (255, 255, 255)
C_BTN_BG   = ( 30,  32,  58)
C_BTN_HOV  = ( 48,  52,  88)
C_BTN_BRD  = ( 70,  75, 120)
C_ACCENT   = ( 90, 235, 150)
C_RED_UI   = (240,  70,  80)
C_GOLD_UI  = (255, 210,  40)
C_WALL     = ( 65,  70,  98)
C_FOOD_RED  = (240,  75,  85)
C_FOOD_GRN  = ( 60, 215,  90)
C_FOOD_GOLD = (255, 215,  40)
C_PU_SLOW   = ( 80, 160, 255)
C_PU_SCIS   = (210,  80, 210)
C_PU_GHOST  = (150, 230, 255)
C_PU_DOUBLE = (255, 160,  50)

def get_font(size, bold=False):
    return pygame.font.SysFont("Segoe UI", size, bold=bold)

F_TITLE = get_font(58, bold=True)
F_BIG   = get_font(40, bold=True)
F_MED   = get_font(24, bold=True)
F_SMALL = get_font(20)
F_TINY  = get_font(15)

# ─────────────────────────────────────────────────────────────────────────
# HELID
#
# Kasutatakse pygame.mixer.Sound objekti (kursuse materjali järgi).
# Helifailid peavad asuma kaustas "sounds/" samas kaustas, kus see skript.
#
# Vajalikud failid:
#   sounds/eat.wav       - söömise heli
#   sounds/crash.wav     - kokkupõrke/surma heli
#   sounds/powerup.wav   - power-upi korjamise heli
#   sounds/levelup.wav   - taseme tõusu heli
#   sounds/click.wav     - nupuklõpsu heli
#
# Taustamuusika (valikuline):
#   sounds/music.mp3           - üks lugu (mängitakse lõpmatult)
#   sounds/music1.mp3, music2.mp3 jne - mitu lugu (valitakse juhuslikult)
#
# ─────────────────────────────────────────────────────────────────────────

_BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
_SOUNDS_DIR = os.path.join(_BASE_DIR, "sounds")


def _load_sound(filename):
    """
    Laeb helifaili pygame.mixer.Sound objektina.
    Kui faili ei leita, tagastab None - mäng töötab ka ilma helideta.
    """
    path = os.path.join(_SOUNDS_DIR, filename)
    try:
        return pygame.mixer.Sound(path)   # loob Sound objekti antud failist
    except Exception:
        return None                        # fail puudub - tagastame None


# Laeme kõik efektihelid
SND_EAT     = _load_sound("eat.mp3")      # söömise heli
SND_CRASH   = _load_sound("crash.mp3")    # kokkupõrke/surma heli
SND_POWERUP = _load_sound("powerup.mp3")  # power-upi korjamise heli
SND_LEVELUP = _load_sound("levelup.mp3")  # taseme tõusu heli
SND_CLICK   = _load_sound("click.mp3")    # nupuklõpsu heli

VOLUME = 1.0  # helitugevus 0.0 - 1.0


def play(snd):
    """
    Mängib Sound objekti, kui see on olemas ja helitugevus pole 0.
    Kursuse materjali süntaks: pygame.mixer.Sound.play(snd)
    """
    if snd and VOLUME > 0:
        try:
            snd.set_volume(VOLUME)
            pygame.mixer.Sound.play(snd)
        except Exception:
            pass


def start_music():
    """
    Käivitab taustamuusika pygame.mixer.music abil.
    Kui sounds/ kaustas on mitu lugu (music1.mp3, music2.mp3 ...),
    valitakse random.choice abil juhuslikult üks (kursuse materjali näide).
    Mängitakse lõpmatult (play(-1)).
    """
    if not os.path.isdir(_SOUNDS_DIR):
        return  # sounds/ kausta pole - ei tee midagi

    # Kogume kõik muusikafailid nimekirja (kursuse esitusloendi näide)
    music_files = [
        f for f in os.listdir(_SOUNDS_DIR)
        if f.startswith("music") and f.endswith((".mp3", ".wav", ".ogg"))
    ]

    if not music_files:
        return  # muusikafaile ei leitud

    # Valime juhuslikult ühe loo esitusloendist
    chosen = random.choice(music_files)
    path   = os.path.join(_SOUNDS_DIR, chosen)
    try:
        pygame.mixer.music.load(path)         # laeme valitud loo
        pygame.mixer.music.set_volume(0.3)    # taustamuusika vaiksemaks kui efektid
        pygame.mixer.music.play(-1)            # -1 = mängi lõpmatult
    except Exception:
        pass


def stop_music():
    """Peatab taustamuusika."""
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass


def set_music_volume(vol):
    """
    Seab taustamuusika helitugevuse (taustamuusika on 30% efektide mahust).
    """
    try:
        pygame.mixer.music.set_volume(vol * 0.3)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────
# REKORDI SALVESTAMINE
# ─────────────────────────────────────────────────────────────────────────
HS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.json")


def load_highscore():
    try:
        with open(HS_FILE) as f:
            return json.load(f).get("hs", 0)
    except Exception:
        return 0


def save_highscore(hs):
    try:
        with open(HS_FILE, "w") as f:
            json.dump({"hs": hs}, f)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────
# TASEMETE MÄÄRATLUSED
# ─────────────────────────────────────────────────────────────────────────
LEVELS = [
    dict(name="Algaja",   fps=7,  walls=0,  next=5),
    dict(name="Harjuja",  fps=10, walls=4,  next=8),
    dict(name="Oskaja",   fps=14, walls=7,  next=12),
    dict(name="Ekspert",  fps=18, walls=10, next=17),
    dict(name="LEGEND",   fps=23, walls=14, next=9999),
]

SNAKE_COLORS = [
    ("Roheline",   ( 80, 230, 140), ( 40, 160,  80)),
    ("Tsüaan",     ( 60, 215, 215), ( 30, 150, 150)),
    ("Oranž",      (255, 155,  50), (200, 110,  30)),
    ("Roosa",      (255, 120, 170), (200,  75, 120)),
    ("Lilla",      (180, 105, 255), (120,  60, 200)),
    ("Valge",      (225, 225, 230), (160, 160, 170)),
]


# ─────────────────────────────────────────────────────────────────────────
# ABIFUNKTSIOONID
# ─────────────────────────────────────────────────────────────────────────
def cell_rect(col, row):
    return pygame.Rect(col * CELL, HUD_H + row * CELL, CELL, CELL)


def rand_cell(exclude):
    while True:
        c = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
        if c not in exclude:
            return c


def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_pill(surf, color, rect, radius=None, border=0, border_color=None):
    r = radius if radius is not None else min(rect.width, rect.height) // 2
    pygame.draw.rect(surf, color, rect, border_radius=r)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=r)


def draw_text_centered(surf, text, font, color, cx, cy):
    s = font.render(text, True, color)
    surf.blit(s, (cx - s.get_width()//2, cy - s.get_height()//2))
    return s


# ─────────────────────────────────────────────────────────────────────────
# NUPU KLASS
# ─────────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, cx, cy, w, h, text, color=None, text_color=None):
        self.rect       = pygame.Rect(cx - w//2, cy - h//2, w, h)
        self.text       = text
        self.color      = color or C_BTN_BG
        self.hov_color  = C_BTN_HOV
        self.text_color = text_color or C_TEXT
        self.hovered    = False
        self.radius     = h // 2

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surf, font=None):
        f   = font or F_MED
        col = self.hov_color if self.hovered else self.color
        shadow = self.rect.move(0, 3)
        draw_pill(surf, (0, 0, 0, 60), shadow, self.radius)
        draw_pill(surf, col, self.rect, self.radius)
        border_col = lerp_color(C_BTN_BRD, C_ACCENT, 0.6) if self.hovered else C_BTN_BRD
        draw_pill(surf, border_col, self.rect, self.radius, border=2)
        draw_text_centered(surf, self.text, f, self.text_color,
                           self.rect.centerx, self.rect.centery)

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ─────────────────────────────────────────────────────────────────────────
# LIUGURI KLASS
# ─────────────────────────────────────────────────────────────────────────
class Slider:
    def __init__(self, cx, cy, width, value=1.0):
        self.rect     = pygame.Rect(cx - width//2, cy - 4, width, 8)
        self.value    = value
        self.dragging = False

    def handle_pos_x_to_value(self, x):
        rel = (x - self.rect.left) / self.rect.width
        return max(0.0, min(1.0, rel))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            grab_area = self.rect.inflate(0, 20)
            if grab_area.collidepoint(event.pos):
                self.dragging = True
                self.value = self.handle_pos_x_to_value(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.value = self.handle_pos_x_to_value(event.pos[0])

    def draw(self, surf):
        draw_pill(surf, C_BTN_BG, self.rect, radius=4)
        fill_w = int(self.rect.width * self.value)
        if fill_w > 0:
            fill_rect = pygame.Rect(self.rect.left, self.rect.top, fill_w, self.rect.height)
            draw_pill(surf, C_ACCENT, fill_rect, radius=4)
        knob_x = self.rect.left + fill_w
        knob_y = self.rect.centery
        pygame.draw.circle(surf, C_WHITE, (knob_x, knob_y), 10)
        pygame.draw.circle(surf, C_ACCENT, (knob_x, knob_y), 10, 2)


# ─────────────────────────────────────────────────────────────────────────
# OSAKESTE SÜSTEEM
# ─────────────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        angle  = random.uniform(0, math.tau)
        speed  = random.uniform(1.5, 4.5)
        self.vx       = math.cos(angle) * speed
        self.vy       = math.sin(angle) * speed
        self.color    = color
        self.life     = random.randint(18, 38)
        self.max_life = self.life
        self.size     = random.randint(2, 5)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.12
        self.life -= 1

    def draw(self, surf):
        if self.life <= 0:
            return
        alpha = self.life / self.max_life
        col = lerp_color(C_BG, self.color, alpha)
        pygame.draw.circle(surf, col, (int(self.x), int(self.y)), self.size)


# ─────────────────────────────────────────────────────────────────────────
# MÄNGU KLASS
# ─────────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, level_idx=0, score=0, color_idx=0):
        self.level_idx = level_idx
        self.lv        = LEVELS[level_idx]
        self.score     = score
        self.food_eaten= 0
        self.color_idx = color_idx
        self.head_col  = SNAKE_COLORS[color_idx][1]
        self.body_col  = SNAKE_COLORS[color_idx][2]

        cx, cy       = COLS//2, ROWS//2
        self.snake   = [(cx, cy), (cx-1, cy), (cx-2, cy)]
        self.dir     = (1, 0)
        self.next_d  = (1, 0)
        self.alive   = True
        self.won     = False
        self.tick    = 0

        self.walls = self._place_walls(self.lv["walls"])
        self.food_items = []
        self.powerups = []
        self._spawn_food()

        self.active_fx  = {}
        self.double_pts = False

        self.particles   = []
        self.flash_col   = None
        self.flash_timer = 0
        self.wiggle      = 0.0

    def _place_walls(self, n):
        excl = set(self.snake)

        head = self.snake[0]

        excl |= {
            head,
            (head[0] + 1, head[1]),
            (head[0] + 2, head[1]),
            (head[0] + 3, head[1]),
            (head[0] - 1, head[1]),
            (head[0], head[1] + 1),
            (head[0], head[1] - 1),
        }

        walls = []
        tries = 0
        while len(walls) < n and tries < 2000:
            w = (random.randint(2, COLS-3), random.randint(2, ROWS-3))
            if w not in excl and w not in walls:
                walls.append(w)
                excl.add(w)
            tries += 1
        return walls

    def _spawn_food(self):
        occ = set(self.snake) | set(self.walls)
        occ |= {f["pos"] for f in self.food_items}
        occ |= {p["pos"] for p in self.powerups}

        if not any(f["type"] == "red" for f in self.food_items):
            pos = rand_cell(occ); occ.add(pos)
            self.food_items.append({"pos": pos, "type": "red",   "pts": 1})

        if not any(f["type"] == "green" for f in self.food_items):
            if random.random() < 0.30:
                pos = rand_cell(occ); occ.add(pos)
                self.food_items.append({"pos": pos, "type": "green", "pts": 3})

        if not any(f["type"] == "gold" for f in self.food_items):
            if random.random() < 0.15:
                pos = rand_cell(occ); occ.add(pos)
                self.food_items.append({"pos": pos, "type": "gold",  "pts": 5})

    def _maybe_spawn_powerup(self):
        if len(self.powerups) >= 2:
            return
        if random.random() < 0.015:
            occ = set(self.snake) | set(self.walls)
            occ |= {f["pos"] for f in self.food_items}
            occ |= {p["pos"] for p in self.powerups}
            pu_type = random.choice(["slow", "scissors", "ghost", "double"])
            pos = rand_cell(occ)
            self.powerups.append({
                "pos":    pos,
                "type":   pu_type,
                "expiry": self.tick + self.lv["fps"] * 7,
            })

    def handle_key(self, key):
        dirs = {
            pygame.K_UP:    (0, -1), pygame.K_w: (0, -1),
            pygame.K_DOWN:  (0,  1), pygame.K_s: (0,  1),
            pygame.K_LEFT:  (-1, 0), pygame.K_a: (-1, 0),
            pygame.K_RIGHT: (1,  0), pygame.K_d: (1,  0),
        }
        if key in dirs:
            nd = dirs[key]
            if (nd[0] != -self.dir[0]) or (nd[1] != -self.dir[1]):
                self.next_d = nd

    def step(self):
        if not self.alive:
            return None

        self.tick    += 1
        self.dir      = self.next_d
        self.wiggle  += 0.4

        nx = self.snake[0][0] + self.dir[0]
        ny = self.snake[0][1] + self.dir[1]

        if "ghost" in self.active_fx and self.active_fx["ghost"] > self.tick:
            nx %= COLS
            ny %= ROWS
        else:
            if not (0 <= nx < COLS and 0 <= ny < ROWS):
                return self._die()
            if (nx, ny) in self.walls:
                return self._die()

        new_head = (nx, ny)

        if new_head in self.snake[:-1]:
            return self._die()

        self.snake.insert(0, new_head)
        grew = False

        for food in list(self.food_items):
            if new_head == food["pos"]:
                pts = food["pts"] * (2 if self.double_pts else 1)
                self.score      += pts
                self.food_eaten += pts
                grew = True
                col_map = {"red": C_FOOD_RED, "green": C_FOOD_GRN, "gold": C_FOOD_GOLD}
                self._burst(new_head, col_map.get(food["type"], C_ACCENT))
                self.flash_col, self.flash_timer = C_ACCENT, 4
                self.food_items.remove(food)
                play(SND_EAT)          # söömise heli (pygame.mixer.Sound)
                self._spawn_food()
                break

        for pu in list(self.powerups):
            if new_head == pu["pos"]:
                self._apply_pu(pu["type"])
                self.powerups.remove(pu)
                play(SND_POWERUP)      # power-upi heli (pygame.mixer.Sound)
                break

        self.powerups = [p for p in self.powerups if p["expiry"] > self.tick]

        self.double_pts = ("double" in self.active_fx and
                           self.active_fx["double"] > self.tick)

        if not grew:
            self.snake.pop()

        self._maybe_spawn_powerup()

        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

        if self.flash_timer > 0:
            self.flash_timer -= 1

        if self.food_eaten >= self.lv["next"]:
            if self.level_idx < len(LEVELS) - 1:
                return "LEVELUP"
            else:
                self.won = True
                return "WON"

        return None

    def _apply_pu(self, pu_type):
        dur = self.lv["fps"] * 6

        if pu_type == "slow":
            self.active_fx["slow"]   = self.tick + dur
        elif pu_type == "scissors":
            half = max(3, len(self.snake)//2)
            self.snake = self.snake[:half]
            self._burst(self.snake[0], C_PU_SCIS, count=24)
        elif pu_type == "ghost":
            self.active_fx["ghost"]  = self.tick + dur
        elif pu_type == "double":
            self.active_fx["double"] = self.tick + dur

        col_map = {"slow": C_PU_SLOW, "scissors": C_PU_SCIS,
                   "ghost": C_PU_GHOST, "double": C_PU_DOUBLE}
        self.flash_col   = col_map.get(pu_type, C_ACCENT)
        self.flash_timer = 9

    def _die(self):
        self.alive = False
        play(SND_CRASH)                # kokkupõrke heli (pygame.mixer.Sound)
        for seg in self.snake[:10]:
            self._burst(seg, C_RED_UI, count=7)
        return "DEAD"

    def _burst(self, cell, color, count=14):
        cx = cell[0] * CELL + CELL//2
        cy = HUD_H + cell[1] * CELL + CELL//2
        for _ in range(count):
            self.particles.append(Particle(cx, cy, color))

    def get_fps(self):
        if "slow" in self.active_fx and self.active_fx["slow"] > self.tick:
            return max(3, self.lv["fps"]//2)
        return self.lv["fps"]

    def draw(self, surf, paused, highscore):
        surf.fill(C_BG)

        for c in range(COLS+1):
            pygame.draw.line(surf, C_GRID, (c*CELL, HUD_H), (c*CELL, HUD_H+ROWS*CELL))
        for r in range(ROWS+1):
            pygame.draw.line(surf, C_GRID, (0, HUD_H+r*CELL), (WIN_W, HUD_H+r*CELL))

        if "ghost" in self.active_fx and self.active_fx["ghost"] > self.tick:
            gsurf = pygame.Surface((WIN_W, ROWS*CELL), pygame.SRCALPHA)
            gsurf.fill((80, 160, 255, 12))
            surf.blit(gsurf, (0, HUD_H))

        for wx, wy in self.walls:
            r = cell_rect(wx, wy).inflate(-2, -2)
            draw_pill(surf, C_WALL, r, radius=4)
            pygame.draw.rect(surf, (85, 90, 120), r.move(0, -1), 1, border_radius=4)

        for food in self.food_items:
            fx, fy = food["pos"]
            rect = cell_rect(fx, fy)
            cx, cy = rect.centerx, rect.centery
            r = CELL//2 - 3
            col = {"red": C_FOOD_RED, "green": C_FOOD_GRN, "gold": C_FOOD_GOLD}[food["type"]]
            pygame.draw.circle(surf, lerp_color(C_BG, col, 0.3), (cx, cy+2), r)
            pygame.draw.circle(surf, col, (cx, cy), r)
            pygame.draw.circle(surf, (255,255,255), (cx - r//3, cy - r//3), max(2, r//4))

        PU_COLORS = {"slow": C_PU_SLOW, "scissors": C_PU_SCIS,
                     "ghost": C_PU_GHOST, "double": C_PU_DOUBLE}
        PU_LABELS = {"slow": "AEGLANE", "scissors": "LÕIKA",
                     "ghost": "GHOST", "double": "x2"}

        for pu in self.powerups:
            px, py = pu["pos"]
            rect = cell_rect(px, py)
            col  = PU_COLORS[pu["type"]]
            lbl  = PU_LABELS[pu["type"]]

            glow_surf = pygame.Surface((CELL+8, CELL+8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*col, 40), (0, 0, CELL+8, CELL+8), border_radius=8)
            surf.blit(glow_surf, (rect.left-4, rect.top-4))

            draw_pill(surf, lerp_color(C_BG, col, 0.25), rect.inflate(-1,-1), radius=6)
            draw_pill(surf, col, rect.inflate(-5,-5), radius=5)

            sym = F_TINY.render(lbl, True, C_BG)
            surf.blit(sym, sym.get_rect(center=rect.center))

            total = self.lv["fps"] * 7
            pct   = max(0, (pu["expiry"] - self.tick) / total)
            bar   = pygame.Rect(rect.left, rect.bottom + 3, CELL, 4)
            pygame.draw.rect(surf, (40, 42, 65), bar, border_radius=2)
            fill_w = int(CELL * pct)
            if fill_w > 0:
                pygame.draw.rect(surf, col, pygame.Rect(bar.left, bar.top, fill_w, 4), border_radius=2)

        self._draw_snake(surf)

        for p in self.particles:
            p.draw(surf)

        if self.flash_timer > 0 and self.flash_col:
            a = int(70 * self.flash_timer / 9)
            fsurf = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
            fsurf.fill((*self.flash_col, a))
            surf.blit(fsurf, (0, 0))

        self._draw_hud(surf, paused, highscore)

    def _draw_snake(self, surf):
        n = len(self.snake)
        for i in range(n-1, -1, -1):
            sc, sr = self.snake[i]
            rect   = cell_rect(sc, sr)
            cx, cy = rect.centerx, rect.centery

            scale = 1.0 if i == 0 else max(0.55, 1.0 - i * 0.012)
            r = int(CELL * 0.48 * scale)

            t_grad = i / max(n - 1, 1)
            col = lerp_color(self.head_col, self.body_col, min(t_grad * 1.4, 1.0))

            if i == 0:
                head_r = int(CELL * 0.52)
                pygame.draw.circle(surf, lerp_color(C_BG, col, 0.35), (cx, cy+2), head_r)
                pygame.draw.circle(surf, col, (cx, cy), head_r)

                dx, dy = self.dir
                eye_offset_x = dx * 4
                eye_offset_y = dy * 4
                perp_x =  dy * 5
                perp_y = -dx * 5

                for sign in (+1, -1):
                    ex = cx + eye_offset_x + sign * perp_x
                    ey = cy + eye_offset_y + sign * perp_y
                    pygame.draw.circle(surf, C_WHITE, (ex, ey), 4)
                    px2 = ex + dx
                    py2 = ey + dy
                    pygame.draw.circle(surf, (30, 30, 50), (px2, py2), 2)
                    pygame.draw.circle(surf, C_WHITE, (px2-1, py2-1), 1)

                mouth_cx = cx + dx * 5
                mouth_cy = cy + dy * 5
                mouth_col = lerp_color(col, (0,0,0), 0.4)
                for angle_off in (-20, 0, 20):
                    angle_rad = math.radians(
                        math.degrees(math.atan2(dy, dx)) + 90 + angle_off
                    )
                    mx2 = int(mouth_cx + math.cos(angle_rad) * 3)
                    my2 = int(mouth_cy + math.sin(angle_rad) * 3)
                    pygame.draw.circle(surf, mouth_col, (mx2, my2), 1)

            else:
                wiggle_off = int(math.sin(self.wiggle + i * 0.7) * 1.2)
                pygame.draw.circle(surf, lerp_color(C_BG, col, 0.3), (cx, cy + 2), r)
                pygame.draw.circle(surf, col, (cx + wiggle_off, cy), r)
                if r > 5:
                    pygame.draw.circle(surf,
                                       lerp_color(col, C_WHITE, 0.35),
                                       (cx + wiggle_off - r//4, cy - r//4), max(2, r//4))

    def _draw_hud(self, surf, paused, highscore):
        pygame.draw.rect(surf, C_HUD_BG, (0, 0, WIN_W, HUD_H))
        pygame.draw.line(surf, (32, 34, 58), (0, HUD_H-1), (WIN_W, HUD_H-1), 1)

        sc_s = F_MED.render(f"Skoor  {self.score:04d}", True, C_ACCENT)
        surf.blit(sc_s, (12, 8))
        hs_s = F_TINY.render(f"Rekord {highscore:04d}", True, C_DIM)
        surf.blit(hs_s, (12, 34))

        lv_s = F_SMALL.render(self.lv["name"], True, C_GOLD_UI)
        surf.blit(lv_s, (WIN_W//2 - lv_s.get_width()//2, 17))

        PU_COLS = {"slow": C_PU_SLOW, "ghost": C_PU_GHOST, "double": C_PU_DOUBLE}
        PU_LBLS = {"slow": "Aeglane", "ghost": "Ghost", "double": "x2"}
        x = WIN_W - 10
        for eff, expiry in self.active_fx.items():
            if expiry > self.tick and eff in PU_LBLS:
                col   = PU_COLS[eff]
                total = self.lv["fps"] * 6
                pct   = max(0, (expiry - self.tick) / total)
                lbl   = F_TINY.render(PU_LBLS[eff], True, col)
                x    -= lbl.get_width() + 4
                surf.blit(lbl, (x, 10))
                bw = lbl.get_width()
                pygame.draw.rect(surf, (40, 42, 65), (x, 26, bw, 4), border_radius=2)
                pygame.draw.rect(surf, col, (x, 26, int(bw * pct), 4), border_radius=2)
                x -= 10

        if paused:
            p_s = F_MED.render("PAUS", True, C_GOLD_UI)
            surf.blit(p_s, (WIN_W - p_s.get_width() - 10, 17))


# ─────────────────────────────────────────────────────────────────────────
# MENÜÜ ABIFUNKTSIOONID
# ─────────────────────────────────────────────────────────────────────────
def draw_menu_bg(surf, tick):
    surf.fill(C_BG)
    for i in range(6):
        phase = tick * 0.015 + i * 1.05
        cx = int(WIN_W * (0.15 + 0.14 * i) + math.sin(phase) * 40)
        cy = int(WIN_H * 0.5 + math.cos(phase * 0.7 + i) * 80)
        r  = 60 + int(math.sin(phase * 0.5) * 20)
        col = lerp_color(C_BG, C_ACCENT, 0.04 + 0.02 * math.sin(phase))
        pygame.draw.circle(surf, col, (cx, cy), r)


def draw_snake_logo(surf, cx, cy):
    head_col = SNAKE_COLORS[0][1]
    body_col = SNAKE_COLORS[0][2]
    segments = [(-46, 14, 9), (-34, 8, 10), (-22, 4, 11), (-10, 2, 12), (0, 0, 13)]
    for i, (ox, oy, r) in enumerate(segments[:-1]):
        sx, sy = cx + ox, cy + oy
        t = i / (len(segments) - 1)
        col = lerp_color(head_col, body_col, t)
        pygame.draw.circle(surf, lerp_color(C_BG, col, 0.3), (sx, sy + 2), r)
        pygame.draw.circle(surf, col, (sx, sy), r)
    hx, hy, hr = segments[-1]
    hx, hy = cx + hx, cy + hy
    pygame.draw.circle(surf, lerp_color(C_BG, head_col, 0.3), (hx, hy + 2), hr)
    pygame.draw.circle(surf, head_col, (hx, hy), hr)
    for sign in (+1, -1):
        ex = hx + 5
        ey = hy - 5 + sign * 7
        pygame.draw.circle(surf, C_WHITE, (ex, ey), 4)
        pygame.draw.circle(surf, (30, 30, 50), (ex + 1, ey), 2)


def draw_overlay(surf, lines, alpha=165):
    ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    ov.fill((5, 6, 18, alpha))
    surf.blit(ov, (0, 0))
    fonts  = [F_BIG, F_MED, F_SMALL]
    line_h = 14
    total_h = sum(fonts[min(fi,2)].get_height() + line_h for _, fi, _ in lines)
    y = WIN_H//2 - total_h//2
    for text, fi, color in lines:
        f = fonts[min(fi, 2)]
        s = f.render(text, True, color)
        surf.blit(s, (WIN_W//2 - s.get_width()//2, y))
        y += s.get_height() + line_h


# ─────────────────────────────────────────────────────────────────────────
# MENÜÜD JA EKRAANID
# ─────────────────────────────────────────────────────────────────────────
def main_menu(highscore, color_idx):
    btn_start = Button(WIN_W//2, WIN_H//2 - 10, 220, 52, "Alusta mäng",
                       color=lerp_color(C_BTN_BG, C_ACCENT, 0.15), text_color=C_ACCENT)
    btn_info  = Button(WIN_W//2, WIN_H//2 + 60, 220, 44, "Kuidas mängida", text_color=C_TEXT)
    btn_set   = Button(WIN_W//2, WIN_H//2 + 118, 220, 44, "Sätted", text_color=C_TEXT)
    tick = 0
    while True:
        tick += 1
        mouse = pygame.mouse.get_pos()
        btn_start.update(mouse); btn_info.update(mouse); btn_set.update(mouse)
        draw_menu_bg(screen, tick)
        title = F_TITLE.render("SNAKE", True, C_ACCENT)
        screen.blit(title, (WIN_W//2 - title.get_width()//2, 38))
        draw_snake_logo(screen, WIN_W//2 - title.get_width()//2 - 35, 68)
        if highscore > 0:
            hs = F_SMALL.render(f"Rekord:  {highscore}", True, C_GOLD_UI)
            screen.blit(hs, (WIN_W//2 - hs.get_width()//2, 110))
        btn_start.draw(screen, F_MED)
        btn_info.draw(screen, F_SMALL)
        btn_set.draw(screen, F_SMALL)
        ctrl = F_TINY.render("Nooled / WASD  |  P = Paus  |  ESC = Välja", True, C_DIM)
        screen.blit(ctrl, (WIN_W//2 - ctrl.get_width()//2, WIN_H - 18))
        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", color_idx
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit", color_idx
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    play(SND_CLICK); return "start", color_idx
            if btn_start.clicked(event):
                play(SND_CLICK); return "start", color_idx
            if btn_info.clicked(event):
                play(SND_CLICK); info_screen()
            if btn_set.clicked(event):
                play(SND_CLICK); color_idx = settings_screen(color_idx)


def info_screen():
    btn_back = Button(WIN_W//2, WIN_H - 38, 160, 42, "Tagasi")
    tick = 0
    while True:
        tick += 1
        mouse = pygame.mouse.get_pos()
        btn_back.update(mouse)
        draw_menu_bg(screen, tick)
        title = F_BIG.render("Kuidas mängida", True, C_ACCENT)
        screen.blit(title, (WIN_W//2 - title.get_width()//2, 18))
        col1_x = 36; y = 78
        head1 = F_MED.render("TOIDUD", True, C_GOLD_UI)
        screen.blit(head1, (col1_x, y)); y += head1.get_height() + 14
        for col, txt in [(C_FOOD_RED, "Punane    +1 punkt"),
                         (C_FOOD_GRN, "Roheline  +3 punkti"),
                         (C_FOOD_GOLD,"Kuldne    +5 punkti")]:
            pygame.draw.circle(screen, col, (col1_x + 11, y + 11), 10)
            pygame.draw.circle(screen, C_WHITE, (col1_x + 7, y + 7), 3)
            s = F_SMALL.render(txt, True, C_TEXT)
            screen.blit(s, (col1_x + 30, y + 1)); y += s.get_height() + 14
        col2_x = WIN_W//2 + 16; y2 = 78
        head2 = F_MED.render("POWER-UPID", True, C_GOLD_UI)
        screen.blit(head2, (col2_x, y2)); y2 += head2.get_height() + 14
        for col, lbl, desc in [(C_PU_SLOW,  "AEGLANE","Uss liigub aeglasemalt 6 sek"),
                                (C_PU_SCIS,  "LÕIKA",  "Uss lõigatakse pooleks"),
                                (C_PU_GHOST, "GHOST",  "Läbi seinte 6 sekundit"),
                                (C_PU_DOUBLE,"x2",     "Topelt punktid 6 sek")]:
            badge = pygame.Rect(col2_x, y2, 78, 28)
            draw_pill(screen, lerp_color(C_BG, col, 0.3), badge, radius=6)
            draw_pill(screen, col, badge, radius=6, border=1, border_color=col)
            ls = F_TINY.render(lbl, True, C_BG)
            screen.blit(ls, ls.get_rect(center=badge.center))
            ds = F_SMALL.render(desc, True, C_TEXT)
            screen.blit(ds, (col2_x + 88, y2 + 4))
            y2 += max(ds.get_height(), badge.height) + 12
        y3 = max(y, y2) + 24
        head3 = F_MED.render("TASEMED", True, C_GOLD_UI)
        screen.blit(head3, (36, y3)); y3 += head3.get_height() + 10
        for lv in LEVELS:
            ls = F_SMALL.render(f"{lv['name']:10s}  {lv['fps']} FPS  |  {lv['walls']} seina", True, C_DIM)
            screen.blit(ls, (36, y3)); y3 += ls.get_height() + 6
        btn_back.draw(screen, F_MED)
        pygame.display.flip(); clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                return
            if btn_back.clicked(event):
                play(SND_CLICK); return


def settings_screen(color_idx):
    global VOLUME
    btn_back = Button(WIN_W//2, WIN_H - 38, 160, 42, "Tagasi")
    swatch_w = 52
    n_col    = len(SNAKE_COLORS)
    total_sw = n_col * (swatch_w + 12)
    sw_x0    = WIN_W//2 - total_sw//2
    slider   = Slider(WIN_W//2, WIN_H - 38 - 70, 260, value=VOLUME)
    tick = 0
    while True:
        tick += 1
        mouse = pygame.mouse.get_pos()
        btn_back.update(mouse)
        draw_menu_bg(screen, tick)
        title = F_BIG.render("Sätted", True, C_ACCENT)
        screen.blit(title, (WIN_W//2 - title.get_width()//2, 24))
        lbl = F_MED.render("Vali ussi värv:", True, C_TEXT)
        screen.blit(lbl, (WIN_W//2 - lbl.get_width()//2, 100))
        sw_y = 145
        for i, (name, hcol, bcol) in enumerate(SNAKE_COLORS):
            sx   = sw_x0 + i * (swatch_w + 12)
            rect = pygame.Rect(sx, sw_y, swatch_w, swatch_w)
            pygame.draw.rect(screen, lerp_color(C_BG, hcol, 0.15), rect.inflate(4,4), border_radius=14)
            pygame.draw.circle(screen, hcol, rect.center, swatch_w//2 - 4)
            pygame.draw.circle(screen, bcol, (rect.centerx, rect.centery + 7), swatch_w//4)
            pygame.draw.circle(screen, C_WHITE, (rect.centerx - 6, rect.centery - 6), 5)
            pygame.draw.circle(screen, C_WHITE, (rect.centerx + 6, rect.centery - 6), 5)
            pygame.draw.circle(screen, (30,30,50), (rect.centerx - 5, rect.centery - 6), 2)
            pygame.draw.circle(screen, (30,30,50), (rect.centerx + 7, rect.centery - 6), 2)
            if i == color_idx:
                pygame.draw.rect(screen, C_WHITE, rect, 3, border_radius=12)
            ns = F_TINY.render(name, True, C_DIM if i != color_idx else C_TEXT)
            screen.blit(ns, (rect.centerx - ns.get_width()//2, sw_y + swatch_w + 6))
            if rect.collidepoint(mouse):
                pygame.draw.rect(screen, C_ACCENT, rect, 2, border_radius=12)
        vol_lbl = F_MED.render(f"Heli tugevus: {int(slider.value * 100)}%", True, C_TEXT)
        screen.blit(vol_lbl, (WIN_W//2 - vol_lbl.get_width()//2, slider.rect.top - 38))
        slider.draw(screen)
        btn_back.draw(screen, F_MED)
        pygame.display.flip(); clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return color_idx
            if btn_back.clicked(event):
                play(SND_CLICK); return color_idx
            slider.handle_event(event)
            VOLUME = slider.value
            set_music_volume(VOLUME)    # uuendame taustamuusika helitugevust
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i in range(n_col):
                    sx   = sw_x0 + i * (swatch_w + 12)
                    rect = pygame.Rect(sx, sw_y, swatch_w, swatch_w)
                    if rect.collidepoint(event.pos):
                        color_idx = i; play(SND_CLICK)


def game_over_screen(surf, game, highscore, new_record):
    for a in (160, 100, 50, 15):
        game.draw(surf, False, highscore)
        ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        ov.fill((200, 0, 0, a))
        surf.blit(ov, (0, 0))
        pygame.display.flip(); pygame.time.wait(65)
    game.draw(surf, False, highscore)
    lines = [("MÄNG LÄBI", 0, C_RED_UI), (f"Skoor:  {game.score}", 1, C_TEXT)]
    if new_record:
        lines.append(("** UUS REKORD! **", 1, C_GOLD_UI))
    else:
        lines.append((f"Rekord: {highscore}", 1, C_GOLD_UI))
    lines += [("", 2, C_DIM), ("[R]  Proovi uuesti", 2, C_ACCENT), ("[M]  Peamenüü", 2, C_DIM)]
    draw_overlay(surf, lines)
    btn_r = Button(WIN_W//2 - 85, WIN_H - 55, 155, 42, "Proovi uuesti",
                   text_color=C_ACCENT, color=lerp_color(C_BTN_BG, C_ACCENT, 0.1))
    btn_m = Button(WIN_W//2 + 85, WIN_H - 55, 140, 42, "Peamenüü")
    while True:
        mouse = pygame.mouse.get_pos()
        btn_r.update(mouse); btn_m.update(mouse)
        game.draw(surf, False, highscore)
        draw_overlay(surf, lines)
        btn_r.draw(surf, F_SMALL); btn_m.draw(surf, F_SMALL)
        pygame.display.flip(); clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    play(SND_CLICK); return "RESTART"
                if event.key == pygame.K_m:
                    play(SND_CLICK); return "MENU"
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
            if btn_r.clicked(event):
                play(SND_CLICK); return "RESTART"
            if btn_m.clicked(event):
                play(SND_CLICK); return "MENU"


def pause_screen(surf, game, highscore):
    btn_resume = Button(WIN_W//2, WIN_H//2 + 10, 180, 48, "Jätka",
                        color=lerp_color(C_BTN_BG, C_ACCENT, 0.15), text_color=C_ACCENT)
    btn_menu   = Button(WIN_W//2, WIN_H//2 + 72, 180, 42, "Peamenüü")
    while True:
        mouse = pygame.mouse.get_pos()
        btn_resume.update(mouse); btn_menu.update(mouse)
        game.draw(surf, True, highscore)
        ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        ov.fill((5, 6, 18, 145)); surf.blit(ov, (0, 0))
        title = F_BIG.render("PAUS", True, C_GOLD_UI)
        surf.blit(title, (WIN_W//2 - title.get_width()//2, WIN_H//2 - 80))
        btn_resume.draw(surf, F_MED); btn_menu.draw(surf, F_SMALL)
        pygame.display.flip(); clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    return "RESUME"
                if event.key == pygame.K_m:
                    play(SND_CLICK); return "MENU"
            if btn_resume.clicked(event):
                play(SND_CLICK); return "RESUME"
            if btn_menu.clicked(event):
                play(SND_CLICK); return "MENU"


def levelup_screen(surf, game, highscore, next_lv):
    game.draw(surf, False, highscore)
    lines = [
        ("TASE ÜLES!", 0, C_GOLD_UI),
        (f"Järgmine: {next_lv['name']}", 1, C_ACCENT),
        ("Kiirus tõuseb", 2, C_TEXT),
    ]
    draw_overlay(surf, lines, alpha=150)
    play(SND_LEVELUP)      # taseme tõusu heli (pygame.mixer.Sound)
    pygame.display.flip()
    pygame.time.wait(2200)


# ─────────────────────────────────────────────────────────────────────────
# PEAMINE MÄNGUTSÜKKEL
# ─────────────────────────────────────────────────────────────────────────
def main():
    highscore = load_highscore()
    color_idx = 0

    start_music()    # käivitame taustamuusika (pygame.mixer.music)

    while True:
        action, color_idx = main_menu(highscore, color_idx)
        if action == "quit":
            stop_music()
            pygame.quit(); sys.exit()

        level_idx = 0
        game      = Game(level_idx, score=0, color_idx=color_idx)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if game.score > highscore:
                        save_highscore(game.score)
                    stop_music()
                    pygame.quit(); sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if game.score > highscore:
                            save_highscore(game.score)
                        stop_music()
                        pygame.quit(); sys.exit()

                    if event.key == pygame.K_p:
                        res = pause_screen(screen, game, highscore)
                        if res == "MENU":
                            running = False; break
                    else:
                        game.handle_key(event.key)

            else:
                result = game.step()

                if result == "DEAD":
                    new_rec = game.score > highscore
                    if new_rec:
                        highscore = game.score
                        save_highscore(highscore)
                    action = game_over_screen(screen, game, highscore, new_rec)
                    if action == "RESTART":
                        game = Game(0, score=0, color_idx=color_idx); level_idx = 0
                    else:
                        running = False

                elif result == "LEVELUP":
                    next_lv = LEVELS[game.level_idx + 1]
                    levelup_screen(screen, game, highscore, next_lv)
                    level_idx += 1
                    old_score = game.score
                    game = Game(level_idx, score=old_score, color_idx=color_idx)

                elif result == "WON":
                    new_rec = game.score > highscore
                    if new_rec:
                        highscore = game.score
                        save_highscore(highscore)
                    game.draw(screen, False, highscore)
                    lines = [
                        ("SA OLED LEGEND!", 0, C_GOLD_UI),
                        (f"Lõplikud punktid: {game.score}", 1, C_ACCENT),
                        ("Kõik tasemed läbitud!", 1, C_GOLD_UI),
                        ("[R] Uuesti   [M] Menüü", 2, C_DIM),
                    ]
                    draw_overlay(screen, lines)
                    play(SND_LEVELUP)
                    pygame.display.flip()
                    waiting = True
                    while waiting:
                        for ev in pygame.event.get():
                            if ev.type == pygame.QUIT:
                                stop_music(); pygame.quit(); sys.exit()
                            if ev.type == pygame.KEYDOWN:
                                if ev.key == pygame.K_r:
                                    game = Game(0, 0, color_idx); level_idx = 0; waiting = False
                                elif ev.key == pygame.K_m:
                                    running = False; waiting = False
                        clock.tick(30)

                if running:
                    game.draw(screen, False, highscore)
                    pygame.display.flip()
                    clock.tick(game.get_fps())
                continue
            break


if __name__ == "__main__":
    main()