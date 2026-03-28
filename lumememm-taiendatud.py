import pygame, sys

pygame.init()

screen = pygame.display.set_mode([300, 300])
pygame.display.set_caption("Täiendatud Lumemees - [Sinu Nimi]")

while True:
    # 4. Taustaks helesinine
    screen.fill((173, 216, 230))

    # 6. Päike koos kiirtega (vasakul üleval)
    pygame.draw.circle(screen, (255, 255, 0), (40, 40), 20) # Päikese keha
    pygame.draw.line(screen, (255, 255, 0), (40, 10), (40, 70), 2) # Vertikaalne kiir
    pygame.draw.line(screen, (255, 255, 0), (10, 40), (70, 40), 2) # Horisontaalne kiir
    pygame.draw.line(screen, (255, 255, 0), (20, 20), (60, 60), 2) # Diagonaal
    pygame.draw.line(screen, (255, 255, 0), (60, 20), (20, 60), 2) # Diagonaal

    # 7. 3 Pilve (teeme need valgetest kattuvatest ringidest)
    # Esimene pilv
    pygame.draw.circle(screen, (255, 255, 255), (220, 40), 15)
    pygame.draw.circle(screen, (255, 255, 255), (240, 35), 20)
    pygame.draw.circle(screen, (255, 255, 255), (260, 40), 15)
    # Teine pilv
    pygame.draw.circle(screen, (255, 255, 255), (100, 60), 12)
    pygame.draw.circle(screen, (255, 255, 255), (115, 55), 15)
    pygame.draw.circle(screen, (255, 255, 255), (130, 60), 12)
    # Kolmas pilv
    pygame.draw.circle(screen, (255, 255, 255), (250, 90), 10)
    pygame.draw.circle(screen, (255, 255, 255), (265, 85), 15)
    pygame.draw.circle(screen, (255, 255, 255), (280, 90), 10)

    # Lumememme keha (nihutatud natuke alla, et asjad mahuks)
    pygame.draw.circle(screen, (255, 255, 255), (150, 250), 50) # Alumine
    pygame.draw.circle(screen, (255, 255, 255), (150, 170), 40) # Keskmine
    pygame.draw.circle(screen, (255, 255, 255), (150, 110), 30) # Pea

    # 1. Käed (pruunid jooned keskelt välja)
    pygame.draw.line(screen, (139, 69, 19), (115, 170), (70, 150), 4) # Vasak käsi
    pygame.draw.line(screen, (139, 69, 19), (185, 170), (230, 150), 4) # Parem käsi

    # 5. Kätte hari (joonistame vasakusse kätte)
    pygame.draw.line(screen, (139, 69, 19), (70, 100), (70, 200), 3) # Harja vars
    pygame.draw.polygon(screen, (210, 180, 140), [(65, 200), (75, 200), (85, 230), (55, 230)]) # Harjased

    # 2. Nööbid (3 tk keskmisele pallile)
    pygame.draw.circle(screen, (0, 0, 0), (150, 150), 4)
    pygame.draw.circle(screen, (0, 0, 0), (150, 170), 4)
    pygame.draw.circle(screen, (0, 0, 0), (150, 190), 4)

    # Silmad ja nina
    pygame.draw.circle(screen, (0, 0, 0), (140, 105), 4)
    pygame.draw.circle(screen, (0, 0, 0), (160, 105), 4)
    pygame.draw.polygon(screen, (255, 0, 0), [(145, 115), (155, 115), (150, 125)])

    # 3. Kübar/müts (kaks musta ristkülikut)
    pygame.draw.rect(screen, (30, 30, 30), [125, 75, 50, 10]) # Mütsi äär
    pygame.draw.rect(screen, (30, 30, 30), [135, 45, 30, 30]) # Mütsi ülemine osa

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()