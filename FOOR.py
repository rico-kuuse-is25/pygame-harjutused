import pygame, sys  # Impordime vajalikud moodulid

pygame.init()  # Käivitame pygame'i

# Loome akna suurusega 300x300
screen = pygame.display.set_mode([300, 300])

# Lisame pealkirjaks ülesande nime ja enda nime
pygame.display.set_caption("Foor - [Sinu Nimi]")

# Peamine tsükkel akna hoidmiseks
while True:
    screen.fill((0, 0, 0))  # Must taustavärv

    # Joonistame foori korpuse (ristkülik, ainult hallide joontega, paksus 2)
    # pygame.draw.rect(aken, värv, [x, y, laius, kõrgus], paksus)
    pygame.draw.rect(screen, (150, 150, 150), [110, 20, 80, 250], 2)

    # Joonistame foorituled (ringid, seest värvitud)
    pygame.draw.circle(screen, (255, 0, 0), (150, 65), 30)    # Punane tuli (üleval)
    pygame.draw.circle(screen, (255, 255, 0), (150, 145), 30) # Kollane tuli (keskel)
    pygame.draw.circle(screen, (0, 255, 0), (150, 225), 30)   # Roheline tuli (all)

    pygame.display.flip()  # Värskendame akna sisu

    # Sündmuste tsükkel, et ristist saaks kinni panna
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()