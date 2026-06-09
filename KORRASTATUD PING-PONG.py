import pygame   # laeme sisse pygame teegi, mis on mängu tegemise "mootor"

pygame.init()    # käivitame pygame'i - see rida peab alati kõige alguses olema

import random   # laeme sisse random teegi, millega saame suvalisi arve genereerida


# ── Heli ─────────────────────────────────────────────────────────────────────────────────────────────────
sounds = ['do_it.mp3', 'lemonade.mp3', 'loud.mp3', 'stylish.mp3']   # nimekiri muusikafailidest
pygame.mixer.music.load(random.choice(sounds))   # laeme juhusliku muusikafaili
pygame.mixer.music.play()                        # mängime muusikat
pygame.mixer.music.set_volume(0.2)               # helitugevus 20%


# ── Ekraani seaded ────────────────────────────────────────────────────────────────────────────────────────
screenX = 640                                         # mänguakna laius pikslites (ülesandes nõutud 640)
screenY = 480                                         # mänguakna kõrgus pikslites (ülesandes nõutud 480)
screen = pygame.display.set_mode([screenX, screenY])  # loome akna selle suurusega
pygame.display.set_caption("Ülesanne 6")              # akna pealkiri ülaservas
clock = pygame.time.Clock()                           # kell, millega hoiame ühtlast kiirust (FPS)


# ── Värvid ────────────────────────────────────────────────────────────────────────────────────────────────
# Värvid on RGB kujul: [punane, roheline, sinine], iga number 0-255.
lBlue = [153, 204, 255]   # hele sinine - mängu taustavärv (SIIT saad tausta värvi muuta)
black = [0, 0, 0]         # must - skoori teksti värv
white = [255, 255, 255]   # valge - mängu lõpu teksti värv


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
ball.x = random.randint(0, 620)   # pall alustab suvalisest kohast x-teljel
ball.y = 0   # pall alustab ekraani ülaservast

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
        hit_sound = pygame.mixer.Sound('hit.mp3')
        pygame.mixer.Sound.play(hit_sound)
        ballSpeedX = -ballSpeedX   # vahetame külgsuuna vastupidiseks

    # Pall põrkab ülemisest seinast tagasi
    if ball.top < 0:
        hit_sound = pygame.mixer.Sound('hit.mp3')
        pygame.mixer.Sound.play(hit_sound)
        ballSpeedY = -ballSpeedY

    # Kui pall puudutab alumist äärt, siis mäng lõppeb.
    if ball.bottom > screenY:
        gameover = True

    # ── Aluse liigutamine ───────────────────────────────────────────────────────────────────────────────
    # Alust juhitakse klaviatuuri vasak/parem nooltega.
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        if pad.left > 0:               # ei lase alusel vasakust servast välja minna
            pad.x -= padSpeed
    if keys[pygame.K_RIGHT]:
        if pad.right < screenX:        # ei lase alusel paremast servast välja minna
            pad.x += padSpeed

    # ── Kokkupõrge palli ja aluse vahel ─────────────────────────────────────────────────────────────────
    # ballSpeedY > 0 tähendab, et pall liigub allapoole.
    # See kontroll hoiab ära olukorra, kus pall jääb aluse külge kinni "värisema".
    if ball.colliderect(pad) and ballSpeedY > 0:
        hit_sound = pygame.mixer.Sound('hit.mp3')
        pygame.mixer.Sound.play(hit_sound)
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


# ── Mängu lõpu ekraan ─────────────────────────────────────────────────────────────────────────────────────
# Kui jõuame siia, siis mäng on läbi. Näitame kasutajasõbralikku lõpuekraani.
bigFont = pygame.font.SysFont("Arial", 48, bold=True)   # suurem font pealkirja jaoks

# Poolläbipaistev tume kiht, et tekst oleks mängupildi peal selgelt loetav.
overlay = pygame.Surface([screenX, screenY])
overlay.set_alpha(180)        # läbipaistvus: 0 = nähtamatu, 255 = täiesti tume
overlay.fill(black)

showGameover = True
while showGameover:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:        # akna sulgemine ristist
            showGameover = False
        if event.type == pygame.KEYDOWN:     # suvalise klahvi vajutamine
            showGameover = False

    screen.blit(overlay, [0, 0])             # joonistame tumeda kihi mängupildi peale

    # "Mäng läbi!" tekst keskele
    overText = bigFont.render("Mäng läbi!", True, white)
    screen.blit(overText, [screenX // 2 - overText.get_width() // 2, 150])

    # Lõppskoor
    scoreText = font.render("Sinu skoor: " + str(score), True, white)
    screen.blit(scoreText, [screenX // 2 - scoreText.get_width() // 2, 230])

    # Juhend väljumiseks
    infoText = font.render("Vajuta suvalist klahvi, et väljuda", True, white)
    screen.blit(infoText, [screenX // 2 - infoText.get_width() // 2, 290])

    pygame.display.flip()

pygame.quit()   # kui kasutaja väljub, sulgeme pygame'i