import pygame, sys  # Impordime pygame ja sys moodulid

pygame.init()  # Käivitame pygame'i

# Tekitame uue akna suurusega 300x300 pikslit
screen = pygame.display.set_mode([300, 300])

# Lisame aknale pealkirja oma nimega
pygame.display.set_caption("Lumemees - Rico Kuuse")

# Lõpmatu tsükkel, mis hoiab akent lahti
while True:
    screen.fill((0, 0, 0))  # Täidame tausta musta värviga (RGB: 0, 0, 0)

    # Joonistame lumememme keha (kolm valget ringi)
    # pygame.draw.circle(aken, värv, keskpunkt_x_y, raadius)
    pygame.draw.circle(screen, (255, 255, 255), (150, 220), 50)  # Alumine suur pall
    pygame.draw.circle(screen, (255, 255, 255), (150, 140), 40)  # Keskmine pall
    pygame.draw.circle(screen, (255, 255, 255), (150, 80), 30)   # Ülemine pall (pea)

    # Joonistame lumememmele silmad (kaks väikest musta ringi)
    pygame.draw.circle(screen, (0, 0, 0), (140, 75), 4)  # Vasak silm
    pygame.draw.circle(screen, (0, 0, 0), (160, 75), 4)  # Parem silm

    # Joonistame lumememmele nina (punane kolmnurk polygoniga)
    # pygame.draw.polygon(aken, värv, punktide_koordinaadid)
    pygame.draw.polygon(screen, (255, 0, 0), [(145, 85), (155, 85), (150, 95)])

    pygame.display.flip()  # Värskendame ekraani, et joonistused nähtavale ilmuks

    # Kontrollime sündmusi (nt kas kasutaja vajutas sulgemise risti)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()  # Sulgeme pygamei
            sys.exit()     # Väljumine programmist