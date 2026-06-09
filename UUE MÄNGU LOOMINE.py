import pygame   # laeme sisse pygame teegi - see on mängu tegemise "mootor", ilma selleta ei tööta mitte midagi

pygame.init()   # käivitame pygame'i - see rida peab ALATI kõige alguses olema, enne kõike muud

import random   # laeme sisse random teegi - seda kasutame juhusliku värvi genereerimiseks


# ── Ekraani seaded ────────────────────────────────────────────────────────────────────────────────────────

screenX = 640   # akna LAIUS pikslites - kui tahad laiemat akent, muuda seda numbrit (nt 800)
screenY = 480   # akna KÕRGUS pikslites - kui tahad kõrgemat akent, muuda seda numbrit (nt 600)

screen = pygame.display.set_mode([screenX, screenY])   # loome akna - screenX ja screenY ütlevad kui suur see on

pygame.display.set_caption("Hiir")   # akna PEALKIRI ülaservas - kirjuta jutumärkide vahele mida iganes tahad

clock = pygame.time.Clock()   # kell, millega hoiame ühtlast kiirust - ilma selleta jookseks mäng liiga kiiresti


# ── Värvid ────────────────────────────────────────────────────────────────────────────────────────────────
# Värvid on RGB kujul: [punane, roheline, sinine], iga number 0-255.
# Näited: [0,0,0]=must, [255,255,255]=valge, [255,0,0]=punane, [0,255,0]=roheline

lBlue = [153, 204, 255]   # hele sinine - see on TAUSTAVÄRV, muuda neid numbreid ja taust muutub


# ── Ringide "mälu" ────────────────────────────────────────────────────────────────────────────────────────

rings = []   # TÜHI NIMEKIRI - iga kord kui klõpsad, lisatakse siia üks ring. Alguses on nimekiri tühi.

MAX_RINGS = 10   # mitu ringi võib KORRAGA ekraanil olla - muuda nt 5-ks ja ekraanil on korraga max 5 ringi

MIN_RADIUS = 10   # VÄIKSEIM ring pikslites - muuda väiksemaks/suuremaks kui tahad väiksemaid/suuremaid ringe
MAX_RADIUS = 30   # SUURIM ring pikslites - pärast seda läheb raadius tagasi MIN_RADIUS-e peale

click_count = 0   # loeb mitu korda oled klõpsanud - seda kasutatakse raadiuse arvutamiseks, ära kustuta


# ── Abifunktsioon: suvalise värvi genereerimine ───────────────────────────────────────────────────────────
# "def" tähendab et teeme oma tööriista. Iga kord kui kirjutad random_color(), saad tagasi juhusliku värvi.

def random_color():
    r = random.randint(0, 200)   # juhuslik punase kogus - max 200 (mitte 255) et värv poleks liiga hele
    g = random.randint(0, 200)   # juhuslik rohelise kogus - tõsta 200 kõrgemale kui tahad eredamaid värve
    b = random.randint(0, 200)   # juhuslik sinise kogus
    return [r, g, b]             # tagastame kolm numbrit koos - see ongi värv


# ── Mängutsükkel ─────────────────────────────────────────────────────────────────────────────────────────
# "while not gameover" tähendab: KORDA LÕPUTULT kuni mäng lõpeb.
# Kõik mis on selle sees, toimub 60 korda sekundis. See on kogu mängu "süda".

gameover = False   # kui see muutub True-ks, siis mäng lõpeb ja tsükkel peatub

while not gameover:
    clock.tick(60)   # oota kuni 1/60 sekundit on möödas - nii jookseb mäng täpselt 60 kaadrit sekundis


    # ── Sündmuste kuulamine ──────────────────────────────────────────────────────────────────────────────
    # Pygame kogub pidevalt "sündmusi" - kas klõpsasid, vajutasid klahvi, sulgesid akna jne.
    # See for-tsükkel vaatab kõik sündmused läbi ja reageerib neile.

    for event in pygame.event.get():

        if event.type == pygame.QUIT:   # kasutaja vajutas akna X nuppu
            gameover = True             # lõpetame mängu - tsükkel peatub


        if event.type == pygame.MOUSEBUTTONDOWN:   # hiire nupp vajutati alla ehk kasutaja KLÕPSAS

            mx, my = pygame.mouse.get_pos()   # saame kätte klõpsu koordinaadid - mx=vasak-parem, my=üles-alla

            click_count += 1   # suurendame klõpsude arvu ühe võrra (+=1 tähendab "lisa 1 juurde")


            # Raadiuse arvutamine - see on tsükliline (nagu kell: pärast 12 tuleb jälle 1)
            # % on "jagamise jääk" - see tagab et raadius ei lähe kunagi üle MAX_RADIUS
            # Tulemus: 10, 11, 12, ... 29, 30, 10, 11, 12, ... 29, 30, 10, ...

            raadius_vahemik = MAX_RADIUS - MIN_RADIUS          # vahemik = 30 - 10 = 20
            new_radius = MIN_RADIUS + (click_count - 1) % (raadius_vahemik + 1)   # tsükliline raadius


            # Loome uue ringi - sõnastik on nagu "pass" kus on kirjas kogu info selle ringi kohta
            # Igal ringil on: asukoht (x,y), suurus (radius) ja värv (color)

            new_ring = {
                'x': mx,                  # ringi keskpunkti x-koordinaat (vasak-parem)
                'y': my,                  # ringi keskpunkti y-koordinaat (üles-alla)
                'radius': new_radius,     # ringi suurus
                'color': random_color()   # ringi värv - kutsume välja oma abifunktsiooni
            }

            rings.append(new_ring)   # lisame uue ringi nimekirja LÕPPU (append = lisa lõppu)


            # Kui ringe on liiga palju, kustutame kõige vanema
            if len(rings) > MAX_RINGS:      # len() ütleb mitu elementi nimekirjas on
                rings.pop(0)                # pop(0) eemaldab nimekirja ESIMESE elemendi (vanim ring)


    # ── Joonistamine ────────────────────────────────────────────────────────────────────────────────────
    # Joonistamine käib ALATI samas järjekorras:
    # 1) kustuta eelmine kaader (fill)
    # 2) joonista kõik asjad
    # 3) näita ekraanil (flip)

    screen.fill(lBlue)   # KUSTUTA eelmine kaader ja täida taust sinisega - ilma selleta jäävad vanad pildid ekraanile


    # Käime kõik ringid nimekirjast läbi ja joonistame igaühe
    for ring in rings:   # "ring" on üks sõnastik nimekirjast - iga kord võtame järgmise

        pygame.draw.circle(
            screen,          # millisele ekraanile joonistame
            ring['color'],   # mis värvi - võtame ringi sõnastikust
            [ring['x'], ring['y']],   # kuhu joonistame - ringi keskpunkt
            ring['radius'],  # kui suur - ringi raadius
            2                # joone PAKSUS pikslites - kui paned 0, on ring täidetud; 2 = ainult piirjoon
        )


    pygame.display.flip()   # NÄITA kõik joonistatu ekraanil - see peab ALATI tsükli lõpus olema


pygame.quit()   # kui kasutaja väljub, sulgeme pygame'i korralikult