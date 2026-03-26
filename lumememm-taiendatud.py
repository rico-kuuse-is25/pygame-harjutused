import pygame
import sys
import math

pygame.init()

# Akna seaded
LAIUS = 300
KORGUS = 300
screen = pygame.display.set_mode((LAIUS, KORGUS))
pygame.display.set_caption("Lumememm - Rico Kuuse")

# Värvid
HELESININE = (173, 216, 230)
VALGE = (255, 255, 255)
MUST = (0, 0, 0)
PUNANE = (255, 0, 0)
PRUUN = (139, 69, 19)
KOLLANE = (255, 255, 0)
HALL = (120, 120, 120)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Taust
    screen.fill(HELESININE)

    # Päike
    pygame.draw.circle(screen, KOLLANE, (250, 50), 20)
    for angle in range(0, 360, 30):
        x1 = 250 + int(math.cos(math.radians(angle)) * 25)
        y1 = 50 + int(math.sin(math.radians(angle)) * 25)
        x2 = 250 + int(math.cos(math.radians(angle)) * 38)
        y2 = 50 + int(math.sin(math.radians(angle)) * 38)
        pygame.draw.line(screen, KOLLANE, (x1, y1), (x2, y2), 2)

    # Pilved
    pygame.draw.circle(screen, VALGE, (45, 45), 15)
    pygame.draw.circle(screen, VALGE, (60, 35), 18)
    pygame.draw.circle(screen, VALGE, (75, 45), 15)

    pygame.draw.circle(screen, VALGE, (120, 60), 14)
    pygame.draw.circle(screen, VALGE, (135, 50), 17)
    pygame.draw.circle(screen, VALGE, (150, 60), 14)

    pygame.draw.circle(screen, VALGE, (190, 95), 13)
    pygame.draw.circle(screen, VALGE, (205, 85), 16)
    pygame.draw.circle(screen, VALGE, (220, 95), 13)

    # Lumememme keha
    pygame.draw.circle(screen, VALGE, (150, 235), 45)  # alumine
    pygame.draw.circle(screen, VALGE, (150, 165), 33)  # keskmine
    pygame.draw.circle(screen, VALGE, (150, 110), 24)  # pea

    # Silmad
    pygame.draw.circle(screen, MUST, (142, 104), 3)
    pygame.draw.circle(screen, MUST, (158, 104), 3)

    # Nina
    pygame.draw.polygon(screen, PUNANE, [(150, 110), (150, 122), (162, 116)])

    # Nööbid
    pygame.draw.circle(screen, MUST, (150, 155), 3)
    pygame.draw.circle(screen, MUST, (150, 168), 3)
    pygame.draw.circle(screen, MUST, (150, 181), 3)

    # Käed
    pygame.draw.line(screen, PRUUN, (123, 160), (90, 145), 3)
    pygame.draw.line(screen, PRUUN, (177, 160), (210, 145), 3)

    # Hari paremas käes
    pygame.draw.line(screen, PRUUN, (210, 145), (235, 120), 3)
    pygame.draw.line(screen, HALL, (235, 120), (245, 110), 2)
    pygame.draw.line(screen, HALL, (235, 120), (248, 120), 2)
    pygame.draw.line(screen, HALL, (235, 120), (245, 130), 2)

    # Kübar
    pygame.draw.rect(screen, MUST, (135, 72, 30, 20))
    pygame.draw.rect(screen, MUST, (128, 88, 44, 5))

    pygame.display.flip()

pygame.quit()
sys.exit()