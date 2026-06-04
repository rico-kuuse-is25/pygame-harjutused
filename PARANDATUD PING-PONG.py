import pygame   # laeme sisse pygame teegi, mis on mängu tegemise "mootor"

pygame.init()    # käivitame pygame'i - see rida peab alati kõige alguses olema


# ── Ekraani seaded ────────────────────────────────────────────────────────────────────────────────────────
screenX = 640                                         # mänguakna laius pikslites (ülesandes nõutud 640)
screenY = 480                                         # mänguakna kõrgus pikslites (ülesandes nõutud 480)
screen = pygame.display.set_mode([screenX, screenY])  # loome akna selle suurusega
pygame.display.set_caption("PingPong")                # akna pealkiri ülaservas
clock = pygame.time.Clock()                           # kell, millega hoiame ühtlast kiirust (FPS)


# ── Värvid ────────────────────────────────────────────────────────────────────────────────────────────────
# Värvid on RGB kujul: [punane, roheline, sinine], iga number 0-255.
lBlue = [153, 204, 255]   # hele sinine - mängu taustavärv (SIIT saad tausta värvi muuta)
black = [0, 0, 0]         # must - skoori teksti värv


# ── Piltide laadimine ─────────────────────────────────────────────────────────────────────────────────────
# Pildifailid ball.png ja pad.png peavad olema selle programmiga samas kaustas.
ballImage = pygame.image.load("ball.png")   # laeme palli pildi
padImage = pygame.image.load("pad.png")     # laeme aluse pildi

# Muudame pildid ülesandes nõutud suurusesse.
ballImage = pygame.transform.scale(ballImage, [20, 20])    # palli suurus 20x20
padImage = pygame.transform.scale(padImage, [120, 20])     # aluse suurus 120x20


# ── Pall ─────────────────────────────────────────────────────────────────────────────────────────────────
# Paneme palli Rect-i (ristküliku) sisse, sest siis on lihtne kokkupõrget tuvastada.
ball = pygame.Rect(0, 0, 20, 20)   # Rect tehakse kujul (x, y, laius, kõrgus)
ball.centerx = screenX // 2        # pall alustab ekraani keskelt (vasakult-paremalt)
ball.y = 50                        # pall alustab ülevalt

ballSpeedX = 4   # palli kiirus külgsuunas (suurem number = kiirem pall)
ballSpeedY = 4   # palli kiirus üles-alla suunas (suurem number = kiirem pall)


# ── Alus ─────────────────────────────────────────────────────────────────────────────────────────────────
pad = pygame.Rect(0, 0, 120, 20)   # aluse Rect, suurus 120x20
pad.centerx = screenX // 2         # alus alustab keskelt
pad.y = int(screenY / 1.5)         # aluse y-koordinaat on keskkohast allpool (screenY / 1.5)

padSpeed = 3   # aluse liikumiskiirus (võid muuta, et alus liiguks kiiremini/aeglasemalt)


# ── Skoor ────────────────────────────────────────────────────────────────────────────────────────────────
score = 0                                      # mängu alguses on skoor 0
font = pygame.font.SysFont("Arial", 24, bold=True)   # font skoori jaoks (24 = teksti suurus)


# ── Mängutsükkel ─────────────────────────────────────────────────────────────────────────────────────────
gameover = False              # kui see muutub True-ks, siis mäng lõpeb
while not gameover:
    clock.tick(60)            # mäng jookseb 60 kaadrit sekundis (suurem = kiirem mäng)

    # Vaatame, kas kasutaja sulges akna (vajutas ülanurgas ristile)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameover = True

    # ── Palli liigutamine ────────────────────────────────────────────────────────────────────────────────
    ball.x += ballSpeedX      # liigutame palli külgsuunas
    ball.y += ballSpeedY      # liigutame palli üles-alla

    # Pall põrkab vasakust ja paremast seinast tagasi
    if ball.left < 0 or ball.right > screenX:
        ballSpeedX = -ballSpeedX   # vahetame külgsuuna vastupidiseks

    # Pall põrkab ülemisest seinast tagasi
    if ball.top < 0:
        ballSpeedY = -ballSpeedY

    # Kui pall puudutab alumist äärt, põrkab ta tagasi ja mängija kaotab ühe punkti
    if ball.bottom > screenY:
        ballSpeedY = -ballSpeedY
        score -= 1            # miinuspunkt

    # ── Aluse liigutamine ───────────────────────────────────────────────────────────────────────────────
    # Alus liigub ise vasakule-paremale ja vahetab seina juures suunda.
    pad.x += padSpeed
    if pad.left < 0 or pad.right > screenX:
        padSpeed = -padSpeed   # seina juures vahetab alus suunda

    # ── Kokkupõrge palli ja aluse vahel ─────────────────────────────────────────────────────────────────
    # ballSpeedY > 0 tähendab, et pall liigub allapoole.
    # See kontroll hoiab ära olukorra, kus pall jääb aluse külge kinni "värisema".
    if ball.colliderect(pad) and ballSpeedY > 0:
        ballSpeedY = -ballSpeedY   # pall põrkab aluselt üles tagasi
        score += 1                 # plusspunkt

    # ── Joonistamine ────────────────────────────────────────────────────────────────────────────────────
    screen.fill(lBlue)             # täidame tausta heleda sinisega (kustutab eelmise kaadri)
    screen.blit(ballImage, ball)   # joonistame palli tema Rect-i kohale
    screen.blit(padImage, pad)     # joonistame aluse

    # Kirjutame skoori ekraani ülemisse vasakusse nurka.
    # str(score) muudab arvu tekstiks, et seda saaks ekraanile kirjutada.
    text = font.render("Skoor: " + str(score), True, black)
    screen.blit(text, (10, 10))

    pygame.display.flip()          # näitame kõik joonistatu ekraanil

pygame.quit()   # kui mäng lõpeb, sulgeme pygame'i
