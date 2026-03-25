# Rico Kuuse

import pygame
import sys

pygame.init()

# Akna seaded
laius = 300
korgus = 300
screen = pygame.display.set_mode((laius, korgus))
pygame.display.set_caption("Lumememm - Rico Kuuse")

# Värvid
MUST = (0, 0, 0)
VALGE = (255, 255, 255)
PUNANE = (255, 0, 0)

# Peamine programmitsükkel
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Taust
    screen.fill(MUST)

    # Lumememme keha
    pygame.draw.circle(screen, VALGE, (150, 230), 55)  # alumine
    pygame.draw.circle(screen, VALGE, (150, 150), 40)  # keskmine
    pygame.draw.circle(screen, VALGE, (150, 85), 28)   # pea

    # Silmad
    pygame.draw.circle(screen, MUST, (140, 78), 4)
    pygame.draw.circle(screen, MUST, (160, 78), 4)

    # Nina
    pygame.draw.polygon(screen, PUNANE, [(150, 88), (145, 102), (155, 102)])

    pygame.display.flip()

pygame.quit()
sys.exit()