import pygame
import sys

pygame.init()

# Aken
LAIUS = 640
KORGUS = 480
ekraan = pygame.display.set_mode((LAIUS, KORGUS))
pygame.display.set_caption("Harjutamine")

# Pildid
taust = pygame.image.load("bg_shop.jpg").convert()
myyja = pygame.image.load("seller.png").convert_alpha()
jutt = pygame.image.load("chat.png").convert_alpha()

# Skaleeri taust täpselt akna suuruseks
taust = pygame.transform.scale(taust, (LAIUS, KORGUS))

# Müüja
myyja = pygame.transform.scale(myyja, (260, 307))
myyja_x = 103
myyja_y = 158

# Jutumull
jutt = pygame.transform.scale(jutt, (257, 204))
jutt_x = 246
jutt_y = 65

# Tekst
font = pygame.font.SysFont("arial", 19)
tekst = font.render("Tere, olen Rico Kuuse", True, (245, 245, 245))
teksti_x = 290
teksti_y = 139

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    ekraan.blit(taust, (0, 0))
    ekraan.blit(myyja, (myyja_x, myyja_y))
    ekraan.blit(jutt, (jutt_x, jutt_y))
    ekraan.blit(tekst, (teksti_x, teksti_y))

    pygame.display.flip()