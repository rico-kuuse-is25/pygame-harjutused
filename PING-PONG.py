import pygame
import os

pygame.init()

# -----------------------------
# Ekraani seaded
# -----------------------------
screenX = 640
screenY = 480
screen = pygame.display.set_mode((screenX, screenY))
pygame.display.set_caption("Ping-pong")

clock = pygame.time.Clock()

# -----------------------------
# Värvid
# -----------------------------
TAUST_YLEMINE = (186, 225, 250)
TAUST_ALUMINE = (235, 248, 255)

TUME = (35, 45, 60)
HELE = (255, 255, 255)
SININE = (95, 160, 215)
ORANZ = (255, 155, 35)
VARI = (120, 140, 160)

# -----------------------------
# Piltide laadimine
# -----------------------------
kaust = os.path.dirname(__file__)

ballImage = pygame.image.load(os.path.join(kaust, "ball.png")).convert_alpha()
padImage = pygame.image.load(os.path.join(kaust, "pad.png")).convert_alpha()

# Ülesande nõutud suurused
ballImage = pygame.transform.scale(ballImage, (20, 20))
padImage = pygame.transform.scale(padImage, (120, 20))

# -----------------------------
# Fontid
# -----------------------------
titleFont = pygame.font.SysFont("comicsansms", 62, True)
bigFont = pygame.font.SysFont("comicsansms", 34, True)
font = pygame.font.SysFont("comicsansms", 26, True)
smallFont = pygame.font.SysFont("comicsansms", 18, True)

# -----------------------------
# Mängu seaded
# -----------------------------
BALL_SPEED = 5
PAD_SPEED = 7


def reset_game():
    ball = ballImage.get_rect()
    ball.centerx = screenX // 2
    ball.y = 80

    pad = padImage.get_rect()
    pad.centerx = screenX // 2
    pad.y = int(screenY / 1.5)

    score = 0
    ballSpeedX = BALL_SPEED
    ballSpeedY = BALL_SPEED
    ballTrail = []

    return ball, pad, score, ballSpeedX, ballSpeedY, ballTrail


ball, pad, score, ballSpeedX, ballSpeedY, ballTrail = reset_game()

# Mängu olekud:
# title = algusekraan
# playing = mäng käib
# paused = paus
gameState = "title"


# -----------------------------
# Taust
# -----------------------------
def draw_background():
    # Pehme hele gradient-taust
    for y in range(screenY):
        ratio = y / screenY

        r = int(TAUST_YLEMINE[0] * (1 - ratio) + TAUST_ALUMINE[0] * ratio)
        g = int(TAUST_YLEMINE[1] * (1 - ratio) + TAUST_ALUMINE[1] * ratio)
        b = int(TAUST_YLEMINE[2] * (1 - ratio) + TAUST_ALUMINE[2] * ratio)

        pygame.draw.line(screen, (r, g, b), (0, y), (screenX, y))

    # Pehmed dekoratiivsed taustamullid
    pygame.draw.circle(screen, (210, 235, 250), (90, 110), 42)
    pygame.draw.circle(screen, (220, 242, 255), (555, 150), 55)
    pygame.draw.circle(screen, (215, 238, 252), (500, 390), 70)
    pygame.draw.circle(screen, (225, 245, 255), (135, 390), 58)


# -----------------------------
# Joonistamise abifunktsioonid
# -----------------------------
def draw_panel(x, y, width, height, color, alpha):
    panel = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*color, alpha), (0, 0, width, height), border_radius=22)
    screen.blit(panel, (x, y))


def draw_text(text, usedFont, color, x, y, center=False):
    textImage = usedFont.render(text, True, color)

    if center:
        rect = textImage.get_rect(center=(x, y))
    else:
        rect = textImage.get_rect(topleft=(x, y))

    # Väga pehme vari
    softShadow = usedFont.render(text, True, VARI)
    screen.blit(softShadow, (rect.x + 1, rect.y + 1))
    screen.blit(textImage, rect)


def draw_score():
    # Läbipaistev valge kast, mis jääb palli peale
    draw_panel(15, 13, 175, 45, HELE, 215)
    draw_text("Punktid: " + str(score), font, TUME, 30, 18)


def draw_title_screen():
    draw_background()

    # Dekoratiivne pall ja alus
    pygame.draw.circle(screen, ORANZ, (screenX // 2, 128), 18)
    screen.blit(padImage, (screenX // 2 - 60, 315))

    draw_text("PING-PONG", titleFont, ORANZ, screenX // 2, 190, center=True)

    draw_panel(132, 235, 376, 130, HELE, 180)

    draw_text("Vajuta SPACE", bigFont, SININE, screenX // 2, 275, center=True)
    draw_text("et mängida", font, TUME, screenX // 2, 317, center=True)

    instruction = smallFont.render("Liiguta alust A/D või nooleklahvidega", True, TUME)
    screen.blit(instruction, (screenX // 2 - instruction.get_width() // 2, 370))

    pauseText = smallFont.render("Mängu ajal vajuta ESC, et pausida", True, TUME)
    screen.blit(pauseText, (screenX // 2 - pauseText.get_width() // 2, 398))


def draw_pause_screen():
    overlay = pygame.Surface((screenX, screenY), pygame.SRCALPHA)
    overlay.fill((30, 45, 60, 110))
    screen.blit(overlay, (0, 0))

    draw_panel(145, 155, 350, 150, HELE, 220)

    draw_text("PAUS", titleFont, ORANZ, screenX // 2, 215, center=True)
    draw_text("SPACE = jätka", font, TUME, screenX // 2, 275, center=True)


# -----------------------------
# Mängutsükkel
# -----------------------------
gameover = False

while not gameover:
    clock.tick(60)

    # -----------------------------
    # Sündmused
    # -----------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameover = True

        if event.type == pygame.KEYDOWN:
            # Title screenilt mängu
            if gameState == "title":
                if event.key == pygame.K_SPACE:
                    ball, pad, score, ballSpeedX, ballSpeedY, ballTrail = reset_game()
                    gameState = "playing"

            # Mängu pausile
            elif gameState == "playing":
                if event.key == pygame.K_ESCAPE:
                    gameState = "paused"

            # Pausilt tagasi mängu
            elif gameState == "paused":
                if event.key == pygame.K_SPACE:
                    gameState = "playing"

    # -----------------------------
    # Title screen
    # -----------------------------
    if gameState == "title":
        draw_title_screen()
        pygame.display.flip()
        continue

    # -----------------------------
    # Mängu loogika
    # -----------------------------
    if gameState == "playing":
        keys = pygame.key.get_pressed()

        # Aluse liigutamine klaviatuuriga
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            pad.x -= PAD_SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            pad.x += PAD_SPEED

        # Alus ei lähe ekraanist välja
        if pad.left < 0:
            pad.left = 0

        if pad.right > screenX:
            pad.right = screenX

        # Palli liikumine
        ball.x += ballSpeedX
        ball.y += ballSpeedY

        # Pall põrkab vasakust seinast
        if ball.left <= 0:
            ball.left = 0
            ballSpeedX = -ballSpeedX

        # Pall põrkab paremast seinast
        if ball.right >= screenX:
            ball.right = screenX
            ballSpeedX = -ballSpeedX

        # Pall põrkab päris ülemisest seinast, mitte skoorikastist
        if ball.top <= 0:
            ball.top = 0
            ballSpeedY = -ballSpeedY

        # Kui pall puudutab alumist äärt, saab mängija miinuspunkti
        if ball.bottom >= screenY:
            ball.bottom = screenY
            ballSpeedY = -ballSpeedY
            score -= 1

        # Kokkupõrge palli ja aluse vahel
        if ball.colliderect(pad) and ballSpeedY > 0:
            ball.bottom = pad.top
            ballSpeedY = -ballSpeedY
            score += 1

            # Põrke nurk oleneb sellest, kuhu pall alust puudutab
            kaugus_keskelt = ball.centerx - pad.centerx
            ballSpeedX = int(kaugus_keskelt / 14)

            if ballSpeedX == 0:
                ballSpeedX = 2

            if ballSpeedX > 6:
                ballSpeedX = 6

            if ballSpeedX < -6:
                ballSpeedX = -6

        # Väike palli trail efekt
        ballTrail.append(ball.center)

        if len(ballTrail) > 5:
            ballTrail.pop(0)

    # -----------------------------
    # Joonistamine
    # -----------------------------
    draw_background()

    # Õrn palli trail ghost efekt
    trailSurface = pygame.Surface((screenX, screenY), pygame.SRCALPHA)

    for i, pos in enumerate(ballTrail):
        suurus = int(2 + i * 0.5)
        alpha = 20 + i * 10
        pygame.draw.circle(trailSurface, (255, 170, 40, alpha), pos, suurus)

    screen.blit(trailSurface, (0, 0))

    # Pall ja alus
    screen.blit(ballImage, ball)
    screen.blit(padImage, pad)

    # Punktid joonistame kõige lõpus,
    # et pall lendaks skoori taga, mitte selle vastu
    draw_score()

    # Pausi ekraan
    if gameState == "paused":
        draw_pause_screen()

    pygame.display.flip()

pygame.quit()