import pygame
import sys

pygame.init()

# Akna seaded
WIDTH = 640
HEIGHT = 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ülesanne 3 - Ruudustik")
clock = pygame.time.Clock()

# Fondid
TITLE_FONT = pygame.font.SysFont("arial", 22, bold=True)
LABEL_FONT = pygame.font.SysFont("arial", 16)
SMALL_FONT = pygame.font.SysFont("arial", 13)

# Värvid
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK = (35, 35, 35)
PANEL_BG = (250, 250, 250)
PANEL_BORDER = (180, 180, 180)
BUTTON_COLOR = (245, 245, 245)
BUTTON_HOVER = (220, 220, 220)

COLOR_OPTIONS = [
    ("Punane", (255, 0, 0)),
    ("Roheline", (120, 255, 120)),
    ("Sinine", (80, 140, 255)),
    ("Kollane", (255, 235, 80)),
    ("Oranž", (255, 165, 60)),
    ("Lilla", (180, 100, 255)),
    ("Must", (0, 0, 0)),
    ("Valge", (255, 255, 255)),
]

DEFAULTS = {
    "square_size": 20,
    "rows": 24,
    "cols": 32,
    "line_width": 2,
    "background_color": (120, 255, 120),
    "line_color": (255, 0, 0),
}

square_size = DEFAULTS["square_size"]
rows = DEFAULTS["rows"]
cols = DEFAULTS["cols"]
line_width = DEFAULTS["line_width"]
background_color = DEFAULTS["background_color"]
line_color = DEFAULTS["line_color"]

show_menu = True

PANEL_WIDTH = 230
MENU_CONTENT_HEIGHT = 660
scroll_y = 0


def reset_defaults():
    global square_size, rows, cols, line_width, background_color, line_color

    square_size = DEFAULTS["square_size"]
    rows = DEFAULTS["rows"]
    cols = DEFAULTS["cols"]
    line_width = DEFAULTS["line_width"]
    background_color = DEFAULTS["background_color"]
    line_color = DEFAULTS["line_color"]


def keep_values_valid():
    global square_size, rows, cols, line_width

    square_size = max(5, min(square_size, 60))
    rows = max(1, min(rows, 100))
    cols = max(1, min(cols, 100))
    line_width = max(1, min(line_width, 8))


def keep_scroll_valid():
    global scroll_y

    max_scroll = MENU_CONTENT_HEIGHT - HEIGHT

    if max_scroll < 0:
        max_scroll = 0

    scroll_y = max(0, min(scroll_y, max_scroll))


def fit_grid_to_screen():
    global rows, cols

    cols = WIDTH // square_size
    rows = HEIGHT // square_size


def get_color_name(selected_color):
    for name, color in COLOR_OPTIONS:
        if color == selected_color:
            return name

    return "Tundmatu"


def draw_text(surface, text, x, y, font, color=BLACK):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))


def draw_button(surface, rect, text, mouse_pos_on_menu):
    if rect.collidepoint(mouse_pos_on_menu):
        color = BUTTON_HOVER
    else:
        color = BUTTON_COLOR

    pygame.draw.rect(surface, color, rect, border_radius=6)
    pygame.draw.rect(surface, BLACK, rect, 2, border_radius=6)

    text_surface = SMALL_FONT.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


def draw_stepper(surface, label, value, x, y, mouse_pos_on_menu):
    draw_text(surface, f"{label}: {value}", x, y, LABEL_FONT, DARK)

    minus_rect = pygame.Rect(x, y + 24, 42, 28)
    plus_rect = pygame.Rect(x + 52, y + 24, 42, 28)

    draw_button(surface, minus_rect, "-", mouse_pos_on_menu)
    draw_button(surface, plus_rect, "+", mouse_pos_on_menu)

    return minus_rect, plus_rect


def draw_color_button(surface, rect, color, selected_color):
    pygame.draw.rect(surface, color, rect, border_radius=5)

    if color == selected_color:
        pygame.draw.rect(surface, BLACK, rect, 4, border_radius=5)
    else:
        pygame.draw.rect(surface, (80, 80, 80), rect, 1, border_radius=5)


def draw_color_palette(surface, title, selected_color, x, y):
    draw_text(surface, title, x, y, LABEL_FONT, DARK)

    draw_text(
        surface,
        "Valitud: " + get_color_name(selected_color),
        x,
        y + 22,
        SMALL_FONT,
        DARK
    )

    buttons = []

    swatch_size = 24
    gap = 10
    start_y = y + 48

    for index, color_data in enumerate(COLOR_OPTIONS):
        name = color_data[0]
        color = color_data[1]

        row = index // 4
        col = index % 4

        rect_x = x + col * (swatch_size + gap)
        rect_y = start_y + row * (swatch_size + gap)

        rect = pygame.Rect(rect_x, rect_y, swatch_size, swatch_size)
        draw_color_button(surface, rect, color, selected_color)

        buttons.append((rect, color, name))

    return buttons


def draw_grid(square_size, rows, cols, background_color, line_color, line_width):
    screen.fill(background_color)

    grid_width = cols * square_size
    grid_height = rows * square_size

    start_x = (WIDTH - grid_width) // 2
    start_y = (HEIGHT - grid_height) // 2

    for col in range(cols + 1):
        x = start_x + col * square_size

        pygame.draw.line(
            screen,
            line_color,
            (x, start_y),
            (x, start_y + grid_height),
            line_width
        )

    for row in range(rows + 1):
        y = start_y + row * square_size

        pygame.draw.line(
            screen,
            line_color,
            (start_x, y),
            (start_x + grid_width, y),
            line_width
        )


def draw_scrollbar():
    max_scroll = MENU_CONTENT_HEIGHT - HEIGHT

    if max_scroll <= 0:
        return

    scrollbar_x = PANEL_WIDTH - 8
    scrollbar_width = 6

    scrollbar_height = max(40, int(HEIGHT * HEIGHT / MENU_CONTENT_HEIGHT))
    scrollbar_y = int(scroll_y / max_scroll * (HEIGHT - scrollbar_height))

    pygame.draw.rect(
        screen,
        (220, 220, 220),
        (scrollbar_x, 0, scrollbar_width, HEIGHT)
    )

    pygame.draw.rect(
        screen,
        (120, 120, 120),
        (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height),
        border_radius=3
    )


def draw_menu(mouse_pos):
    menu_surface = pygame.Surface((PANEL_WIDTH, MENU_CONTENT_HEIGHT))
    menu_surface.fill(PANEL_BG)

    mouse_x, mouse_y = mouse_pos
    mouse_pos_on_menu = (mouse_x, mouse_y + scroll_y)

    clickable_rects = {}
    background_buttons = []
    line_buttons = []

    draw_text(menu_surface, "Seaded", 16, 12, TITLE_FONT, DARK)
    draw_text(menu_surface, "Hiireratas = keri menüüd", 16, 40, SMALL_FONT, (90, 90, 90))
    draw_text(menu_surface, "H = peida/näita menüü", 16, 58, SMALL_FONT, (90, 90, 90))

    clickable_rects["square_minus"], clickable_rects["square_plus"] = draw_stepper(
        menu_surface,
        "Ruudu suurus",
        square_size,
        16,
        92,
        mouse_pos_on_menu
    )

    clickable_rects["rows_minus"], clickable_rects["rows_plus"] = draw_stepper(
        menu_surface,
        "Read",
        rows,
        16,
        158,
        mouse_pos_on_menu
    )

    clickable_rects["cols_minus"], clickable_rects["cols_plus"] = draw_stepper(
        menu_surface,
        "Veerud",
        cols,
        16,
        224,
        mouse_pos_on_menu
    )

    clickable_rects["line_minus"], clickable_rects["line_plus"] = draw_stepper(
        menu_surface,
        "Joone paksus",
        line_width,
        16,
        290,
        mouse_pos_on_menu
    )

    clickable_rects["fit"] = pygame.Rect(16, 360, 90, 30)
    clickable_rects["reset"] = pygame.Rect(116, 360, 90, 30)

    draw_button(menu_surface, clickable_rects["fit"], "Täida", mouse_pos_on_menu)
    draw_button(menu_surface, clickable_rects["reset"], "Vaikimisi", mouse_pos_on_menu)

    background_buttons = draw_color_palette(
        menu_surface,
        "Taustavärv",
        background_color,
        16,
        420
    )

    line_buttons = draw_color_palette(
        menu_surface,
        "Joone värv",
        line_color,
        16,
        540
    )

    visible_part = pygame.Rect(0, scroll_y, PANEL_WIDTH, HEIGHT)
    screen.blit(menu_surface, (0, 0), visible_part)

    pygame.draw.line(screen, PANEL_BORDER, (PANEL_WIDTH, 0), (PANEL_WIDTH, HEIGHT), 2)
    draw_scrollbar()

    return clickable_rects, background_buttons, line_buttons


running = True

while running:
    mouse_pos = pygame.mouse.get_pos()

    draw_grid(
        square_size,
        rows,
        cols,
        background_color,
        line_color,
        line_width
    )

    clickable_rects = {}
    background_buttons = []
    line_buttons = []

    if show_menu:
        clickable_rects, background_buttons, line_buttons = draw_menu(mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                show_menu = not show_menu

        elif event.type == pygame.MOUSEWHEEL:
            if show_menu and mouse_pos[0] < PANEL_WIDTH:
                scroll_y -= event.y * 30
                keep_scroll_valid()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if show_menu and mouse_pos[0] < PANEL_WIDTH:
                menu_mouse_pos = (mouse_pos[0], mouse_pos[1] + scroll_y)

                if clickable_rects["square_minus"].collidepoint(menu_mouse_pos):
                    square_size -= 5

                elif clickable_rects["square_plus"].collidepoint(menu_mouse_pos):
                    square_size += 5

                elif clickable_rects["rows_minus"].collidepoint(menu_mouse_pos):
                    rows -= 1

                elif clickable_rects["rows_plus"].collidepoint(menu_mouse_pos):
                    rows += 1

                elif clickable_rects["cols_minus"].collidepoint(menu_mouse_pos):
                    cols -= 1

                elif clickable_rects["cols_plus"].collidepoint(menu_mouse_pos):
                    cols += 1

                elif clickable_rects["line_minus"].collidepoint(menu_mouse_pos):
                    line_width -= 1

                elif clickable_rects["line_plus"].collidepoint(menu_mouse_pos):
                    line_width += 1

                elif clickable_rects["fit"].collidepoint(menu_mouse_pos):
                    fit_grid_to_screen()

                elif clickable_rects["reset"].collidepoint(menu_mouse_pos):
                    reset_defaults()

                for rect, color, name in background_buttons:
                    if rect.collidepoint(menu_mouse_pos):
                        background_color = color

                for rect, color, name in line_buttons:
                    if rect.collidepoint(menu_mouse_pos):
                        line_color = color

                keep_values_valid()
                keep_scroll_valid()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()