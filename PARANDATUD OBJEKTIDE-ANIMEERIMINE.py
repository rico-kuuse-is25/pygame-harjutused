import pygame, random   # pygame on mängu "mootor", random annab juhuslikke arve

pygame.init()    # käivitame pygame'i. See rida peab alati kõige alguses olema


# ── Ekraani seaded ──────────────────────────────────────────────────
screenX = 640                                         # mänguakna laius pikslites (ülesandes nõutud 640)
screenY = 480                                         # mänguakna kõrgus pikslites (ülesandes nõutud 480)
screen = pygame.display.set_mode([screenX, screenY])  # loome akna selle suurusega
pygame.display.set_caption("Ülesanne 4")               # akna pealkiri ülaservas
clock = pygame.time.Clock()                           # kell, millega hoiame ühtlast kiirust (FPS)


# ── Värvid ──────────────────────────────────────────────────────────
# Värv on RGB kujul: [punane, roheline, sinine], iga number 0-255.
white = [255, 255, 255]   # valge - skoori teksti värv


# ── Piltide laadimine ───────────────────────────────────────────────
# Pildid bg_rally.jpg, f1_red.png ja f1_blue.png peavad olema selle programmiga samas kaustas.
bg = pygame.image.load("bg_rally.jpg")               # taustapilt (rallirada)
bg = pygame.transform.scale(bg, [screenX, screenY])  # venitame tausta täpselt ekraani suuruseks

redCar = pygame.image.load("f1_red.png")     # punane auto (mängija auto)
blueCar = pygame.image.load("f1_blue.png")   # sinine auto (vastutulev auto)

# Autode suurus
carW = 50   # auto laius
carH = 80   # auto kõrgus
redCar = pygame.transform.scale(redCar, [carW, carH])
blueCar = pygame.transform.scale(blueCar, [carW, carH])

# Sinine auto sõidab ülevalt alla, seega pöörame tema pildi 180 kraadi ringi,
# et auto nina oleks suunaga allapoole (muidu sõidaks auto tagurpidi).
blueCar = pygame.transform.rotate(blueCar, 180)


# ── Rajad ───────────────────────────────────────────────────────────
# Tee on jagatud kolmeks rajaks (valgete joonte vahel). Allpool on radade
# keskkohad ehk x-koordinaadid. Kui autod ei satu täpselt radade keskele,
# muuda neid kolme arvu.
lanes = [202, 319, 437]   # vasak rada, keskmine rada, parem rada


# ── Punane auto ─────────────────────────────────────────────────────
# Punane auto seisab ekraani all keskel.
redX = screenX // 2 - carW // 2   # keskele (võtame arvesse auto laiust)
redY = screenY - carH - 10        # natuke ekraani alläärest üleval


# ── Sinised autod ───────────────────────────────────────────────────
# Iga raja peale paneme ühe sinise auto. Nii ei saa autod kunagi üksteise
# sees olla ega valgete joonte peale sattuda, sest igaüks sõidab oma rajas.
# Iga auto hoiame loendis kujul [x, y, kiirus].
blueCars = []
for lane in lanes:
    x = lane - carW // 2                # paneme auto raja keskele (laius arvestatud)
    y = random.randint(-400, -carH)     # juhuslik algkõrgus üle ekraani ülaserva
    speed = random.randint(2, 4)        # juhuslik kiirus (suurem number = kiirem auto)
    blueCars.append([x, y, speed])


# ── Skoor ───────────────────────────────────────────────────────────
score = 0                                            # mängu alguses on skoor 0
font = pygame.font.SysFont("Arial", 24, bold=True)   # font skoori jaoks (24 = teksti suurus)


# ── Mängutsükkel ────────────────────────────────────────────────────
gameover = False              # kui see muutub True-ks, siis mäng lõpeb
while not gameover:
    clock.tick(60)            # mäng jookseb 60 kaadrit sekundis

    # Vaatame, kas kasutaja sulges akna (vajutas ülanurgas ristile)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameover = True

    # ── Taust ──
    # Joonistame taustapildi iga kaadri alguses uuesti, et liikuvad autod
    # ei jätaks ekraanile jälge.
    screen.blit(bg, (0, 0))

    # ── Siniste autode liigutamine ja joonistamine ──
    for car in blueCars:
        car[1] += car[2]   # liigutame autot allapoole (y suureneb kiiruse võrra)

        # Kui auto jõuab ekraani alla, alustab ta uuesti ülevalt.
        # x ei muutu, seega auto jääb samasse rajasse ega satu joonte peale.
        if car[1] > screenY:
            car[1] = random.randint(-200, -carH)   # paneme auto uuesti üle ülaserva
            car[2] = random.randint(2, 4)          # uus juhuslik kiirus
            score += 1                             # auto jõudis alla -> +1 punkt

        screen.blit(blueCar, (car[0], car[1]))   # joonistame sinise auto

    # ── Punane auto ──
    screen.blit(redCar, (redX, redY))   # joonistame punase auto alla keskele

    # ── Skoor ──
    # str(score) muudab arvu tekstiks, et seda saaks ekraanile kirjutada.
    text = font.render("Skoor: " + str(score), True, white)
    screen.blit(text, (10, 10))

    pygame.display.flip()   # näitame kõik joonistatu ekraanil

pygame.quit()   # kui mäng lõpeb, sulgeme pygame'i