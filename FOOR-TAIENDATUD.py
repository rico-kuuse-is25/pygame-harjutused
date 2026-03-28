import pygame, sys

pygame.init()

screen = pygame.display.set_mode([300, 300])
pygame.display.set_caption("Täiendatud Foor - [Sinu Nimi]")

while True:
    screen.fill((50, 50, 50))  # Tumehall taust, et kõik elemendid eristuks

    # 1. Lisame juurde posti
    # pygame.draw.rect(aken, värv, [x, y, laius, kõrgus])
    pygame.draw.rect(screen, (100, 100, 100), [145, 190, 10, 60])

    # Foori põhikast (nihutatud pisut ülespoole ja tehtud väiksemaks)
    pygame.draw.rect(screen, (200, 200, 200), [115, 20, 70, 170], 2)
    pygame.draw.rect(screen, (0, 0, 0), [117, 22, 66, 166])  # Sisemine täide

    # Foori tuled
    pygame.draw.circle(screen, (255, 0, 0), (150, 55), 22)  # Punane
    pygame.draw.circle(screen, (255, 255, 0), (150, 105), 22)  # Kollane
    pygame.draw.circle(screen, (0, 255, 0), (150, 155), 22)  # Roheline

    # 2. & 3. Postialus (45 kraadi, Eesti lipu värvides)
    # 45 kraadi jaoks: kõrguse muutus(y) ja laiuse muutus(x) peavad olema võrdsed
    # Teeme aluse kõrguseks 40px (y: 250 kuni 290). Triipude kõrgus ~13.3px

    # Et värvid eristuksid, joonistame tervele alusele halli raami ümber
    pygame.draw.polygon(screen, (200, 200, 200), [(130, 250), (170, 250), (210, 290), (90, 290)], 2)

    # Sinine kiht (üleval)
    pygame.draw.polygon(screen, (0, 114, 206), [(130, 250), (170, 250), (183, 263), (117, 263)])

    # Must kiht (keskel)
    pygame.draw.polygon(screen, (0, 0, 0), [(117, 263), (183, 263), (196, 276), (104, 276)])

    # Valge kiht (all)
    pygame.draw.polygon(screen, (255, 255, 255), [(104, 276), (196, 276), (210, 290), (90, 290)])

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()