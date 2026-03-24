import pygame

pygame.init()

laius = 800
korgus = 600
ekraan = pygame.display.set_mode((laius, korgus))
pygame.display.set_caption("Liikuv ruut")

valge = (255, 255, 255)
sinine = (0, 100, 255)

ruudu_suurus = 50
kiirus = 5

# Ruut algab akna keskel
x = laius // 2 - ruudu_suurus // 2
y = korgus // 2 - ruudu_suurus // 2

too_kaib = True
kell = pygame.time.Clock()

while too_kaib:
    for sundmus in pygame.event.get():
        if sundmus.type == pygame.QUIT:
            too_kaib = False

    klahvid = pygame.key.get_pressed()

    if klahvid[pygame.K_LEFT]:
        x -= kiirus
    if klahvid[pygame.K_RIGHT]:
        x += kiirus
    if klahvid[pygame.K_UP]:
        y -= kiirus
    if klahvid[pygame.K_DOWN]:
        y += kiirus

    ekraan.fill(valge)
    pygame.draw.rect(ekraan, sinine, (x, y, ruudu_suurus, ruudu_suurus))
    pygame.display.flip()

    kell.tick(60)

pygame.quit()