"""
SNAKE - Omamoodi Mäng
PAP2022 - Kombineeritud näidismängudest 1, 2 ja 3
"""

# ══════════════════════════════════════════════════════════════════════════════
# TEEKIDE IMPORT
# ══════════════════════════════════════════════════════════════════════════════

import pygame   # mängu "mootor" - aken, joonistamine, klaviatuur, heli
import sys      # sys.exit() jaoks - see on kõige puhtam viis programm sulgeda
import random   # juhuslike arvude ja valikute jaoks (toidu asukoht, muusikavalik jne)
import json     # rekordi salvestamine/laadimine failist (JSON = lihtne tekstiformaat)
import os       # failiteede jaoks (os.path.join teeb õige tee igal operatsioonisüsteemil)
import math     # matemaatilised funktsioonid - sin, cos, pi jne (animatsioonid, silmad)

pygame.init()         # käivita pygame - PEAB olema enne kõike muud
pygame.mixer.init()   # käivita helisüsteem eraldi - ilma selleta ei tööta heli üldse


# ══════════════════════════════════════════════════════════════════════════════
# MÄNGU PÕHIMÕÕTMED
# ══════════════════════════════════════════════════════════════════════════════

# Mänguväljak koosneb ruutudest (cell = ruut).
# Kõik koordinaadid on ruutudes, mitte pikslites - lihtsam arvutada!
# Näiteks uss on ruutudes: [(5,3), (4,3), (3,3)] mitte pikslites.

CELL   = 22      # ühe ruudu suurus pikslites (22x22). Suurem = suurem mäng, aeglasem
COLS   = 28      # mänguväljaku laius RUUTUDES. 28 * 22 = 616 pikslit
ROWS   = 22      # mänguväljaku kõrgus RUUTUDES. 22 * 22 = 484 pikslit
HUD_H  = 54      # HUD (heads-up display) = infopaneel üleval. 54 pikselit kõrge.
                 # HUD näitab skoori, taset, aktiivseid efekte.

WIN_W  = COLS * CELL          # akna laius pikslites = 28 * 22 = 616
WIN_H  = ROWS * CELL + HUD_H  # akna kõrgus pikslites = 22*22 + 54 = 538
                               # HUD on üleval, mänguväljak all

screen = pygame.display.set_mode((WIN_W, WIN_H))   # loob akna arvutatud suuruses
pygame.display.set_caption("SNAKE GAME - Oma Moodi Mäng")
clock  = pygame.time.Clock()   # kell FPS hoidmiseks


# ══════════════════════════════════════════════════════════════════════════════
# VÄRVID (RGB kujul)
# ══════════════════════════════════════════════════════════════════════════════
# Kõik värvid on defineeritud SIIN ülaosas, mitte laiali kogu koodis.
# See on hea tava - kui tahad värvi muuta, muudad ainult siin, mitte kümnes kohas.
# RGB = (punane, roheline, sinine), igaüks 0-255.

# Taustad ja tekst
C_BG       = ( 13,  14,  26)   # väga tume sinakashall - mänguväljaku taust
C_GRID     = ( 22,  24,  42)   # veidi heledam - ruudustiku jooned (peaaegu nähtamatud)
C_HUD_BG   = ( 18,  19,  36)   # HUD-paneeli taustavärv (veidi heledam kui mänguväljak)
C_TEXT     = (220, 220, 235)   # peaaegu valge - tavaline tekst
C_DIM      = ( 90,  92, 115)   # tuhmhall - vähem tähtis tekst (rekord, juhised)
C_WHITE    = (255, 255, 255)   # puhas valge - silmad, liuguri nupp
C_BTN_BG   = ( 30,  32,  58)   # nupu taustavärv (tume sinine)
C_BTN_HOV  = ( 48,  52,  88)   # nupu taustavärv kui hiir peal (heledam = hover-efekt)
C_BTN_BRD  = ( 70,  75, 120)   # nupu äärevärv
C_ACCENT   = ( 90, 235, 150)   # roheline aksent - tähtis info, uss, skoor
C_RED_UI   = (240,  70,  80)   # punane - "mäng läbi" tekst, surmaefekt
C_GOLD_UI  = (255, 210,  40)   # kuldne - taseme nimi, rekord, "WON" tekst
C_WALL     = ( 65,  70,  98)   # seinte värv (tuhmsinakashall)

# Toiduvärvid (iga toiduliigi jaoks oma värv)
C_FOOD_RED  = (240,  75,  85)   # punane toit - kõige tavalisem, +1 punkt
C_FOOD_GRN  = ( 60, 215,  90)   # roheline toit - haruldasem, +3 punkti
C_FOOD_GOLD = (255, 215,  40)   # kuldne toit - kõige haruldasem, +5 punkti

# Power-up värvid (erivõimete värvid)
C_PU_SLOW   = ( 80, 160, 255)   # sinine - aeglustab ussi
C_PU_SCIS   = (210,  80, 210)   # lilla - "käärid" - lõikab ussi pooleks
C_PU_GHOST  = (150, 230, 255)   # heledam sinine - uss läbib seinu
C_PU_DOUBLE = (255, 160,  50)   # oranž - topelt punktid


# ══════════════════════════════════════════════════════════════════════════════
# FONDID
# ══════════════════════════════════════════════════════════════════════════════

def get_font(size, bold=False):
    # Abifunktsioon fondi loomiseks. "Segoe UI" on Windows'i kena font.
    # bold=False on vaikeväärtus - kui bold ei anna kaasa, on tavaline kiri.
    return pygame.font.SysFont("Segoe UI", size, bold=bold)

# Leiame kõik kasutatavad fondid KORRA, sest fontide loomine on aeglane.
# Parem luua üks kord ja hoida muutujas, kui luua uuesti igal kaadril!
F_TITLE = get_font(58, bold=True)   # suur pealkiri - "SNAKE" peamenüüs
F_BIG   = get_font(40, bold=True)   # "MÄNG LÄBI", "PAUS" jne
F_MED   = get_font(24, bold=True)   # nupude tekst, skoori tekst
F_SMALL = get_font(20)              # infotekstid
F_TINY  = get_font(15)              # väike tekst - power-up sildid, juhised


# ══════════════════════════════════════════════════════════════════════════════
# HELID
# ══════════════════════════════════════════════════════════════════════════════
# Helifailid peavad olema kaustas "sounds/" samas kaustas, kus see .py fail.
# Vajalikud failid: eat.mp3, crash.mp3, powerup.mp3, levelup.mp3, click.mp3
# Taustamuusika: music.mp3 VÕI music1.mp3, music2.mp3 jne (mitu lugu)

_BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
# os.path.abspath(__file__) = selle .py faili TÄIELIK tee (nt C:\kasutaja\mang\snake.py)
# os.path.dirname(...)      = eemaldab faili nime lõpust, jätab kausta (C:\kasutaja\mang)
# Nii leiame üles "sounds/" kausta olenemata sellest, kust programmi käivitati.

_SOUNDS_DIR = os.path.join(_BASE_DIR, "sounds")
# os.path.join liidab teeosad kokku.
# Windows'il: C:\kasutaja\mang\sounds
# Linux'il:   /home/kasutaja/mang/sounds
# os.path.join teeb automaatselt õige kaldkriipsu - ei pea ise muretsema!


def _load_sound(filename):
    """
    Laeb helifaili pygame.mixer.Sound objektina.
    Kui faili ei leita, tagastab None - mäng töötab ka ilma helideta.
    """
    path = os.path.join(_SOUNDS_DIR, filename)   # ehitab täieliku tee failini
    try:
        return pygame.mixer.Sound(path)   # proovib faili laadida
    except Exception:
        return None   # kui fail puudub VÕI on vigane, tagasta None (mitte crash!)
                      # "try/except" = "proovi seda, kui läheb valesti, tee hoopis seda"


# Laeme kõik efektihelid üks kord programmi alguses.
# Kui fail puudub, saab muutuja väärtuseks None ja play() ignoreerib seda.
SND_EAT     = _load_sound("eat.mp3")
SND_CRASH   = _load_sound("crash.mp3")
SND_POWERUP = _load_sound("powerup.mp3")
SND_LEVELUP = _load_sound("levelup.mp3")
SND_CLICK   = _load_sound("click.mp3")

VOLUME = 1.0   # globaalne helitugevus 0.0 (vaikus) kuni 1.0 (täistugevus)
               # sätete ekraanil saab kasutaja seda liuguriga muuta


def play(snd):
    """
    Mängib helisignaali ohutult.
    Kontrollib: kas heli on olemas? Kas helitugevus > 0?
    Ilma selle kontrollita jookseks programm kokku kui helifail puudub.
    """
    if snd and VOLUME > 0:
        # "snd" = True kui Sound objekt on olemas, False/None kui laadimine ebaõnnestus
        try:
            snd.set_volume(VOLUME)         # seab helitugevuse enne mängimist
            pygame.mixer.Sound.play(snd)   # mängib heli (kursuse materjali süntaks)
        except Exception:
            pass   # "pass" = "ära tee midagi" - kui ikka läheb valesti, ignoreeri


def start_music():
    """
    Käivitab taustamuusika.
    Otsib sounds/ kaustast kõik "music" algusega failid ja valib juhusliku.
    Kui on ainult music.mp3, mängib seda. Kui on music1.mp3, music2.mp3 - valib ühe.
    """
    if not os.path.isdir(_SOUNDS_DIR):
        return   # kui sounds/ kausta pole üldse, lõpeta siia (return ilma väärtuseta)

    # Kogume kõik sobilikud muusikafailid nimekirja.
    # f.startswith("music") = faili nimi algab sõnaga "music"
    # f.endswith((".mp3",".wav",".ogg")) = lõpeb ühe nende laiendustega
    music_files = [
        f for f in os.listdir(_SOUNDS_DIR)
        if f.startswith("music") and f.endswith((".mp3", ".wav", ".ogg"))
    ]
    # See on "list comprehension" - lühike viis nimekirja filtreerimiseks.
    # Pikemalt kirjutatuna:
    #   music_files = []
    #   for f in os.listdir(_SOUNDS_DIR):
    #       if f.startswith("music") and f.endswith((".mp3",".wav",".ogg")):
    #           music_files.append(f)

    if not music_files:
        return   # ühtegi muusikafaili ei leitud - lõpeta

    chosen = random.choice(music_files)   # vali juhuslik laul nimekirjast
    path   = os.path.join(_SOUNDS_DIR, chosen)
    try:
        pygame.mixer.music.load(path)       # laeb valitud laulu
        pygame.mixer.music.set_volume(0.3)  # taustamuusika on vaiksem kui efektid
        pygame.mixer.music.play(-1)         # -1 = korda igavesti (loop)
    except Exception:
        pass


def stop_music():
    """Peatab taustamuusika. Kutsutakse välja mängu sulgemisel."""
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass


def set_music_volume(vol):
    """
    Uuendab taustamuusika helitugevust.
    Taustamuusika on alati 30% efektide tugevusest (et efektid oleksid kuuldavamad).
    Kui kasutaja seab helitugevuse 100%, mängib muusika 30% tugevusel.
    """
    try:
        pygame.mixer.music.set_volume(vol * 0.3)
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# REKORDI SALVESTAMINE
# ══════════════════════════════════════════════════════════════════════════════
# Rekord salvestatakse JSON faili, et see säiliks ka pärast mängu sulgemist.
# JSON on lihtne tekstiformaat: {"hs": 42}

HS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.json")
# highscore.json luuakse automaatselt samasse kausta kus snake.py


def load_highscore():
    """
    Loeb rekordi failist. Kui faili pole (esimene kord mängida), tagastab 0.
    json.load(f) muudab JSON teksti Pythoni sõnastikuks: {"hs": 42} -> {"hs": 42}
    .get("hs", 0) = võta "hs" väärtus; kui seda pole, tagasta 0
    """
    try:
        with open(HS_FILE) as f:
            return json.load(f).get("hs", 0)
    except Exception:
        return 0   # fail puudub või on vigane - alusta nullist


def save_highscore(hs):
    """
    Salvestab uue rekordi faili.
    json.dump({"hs": hs}, f) kirjutab sõnastiku JSON-tekstina faili.
    Näiteks kui hs=77, kirjutab faili: {"hs": 77}
    """
    try:
        with open(HS_FILE, "w") as f:
            json.dump({"hs": hs}, f)
    except Exception:
        pass   # kui salvestamine ebaõnnestub (nt kirjutusõigus puudub), eira


# ══════════════════════════════════════════════════════════════════════════════
# TASEMETE DEFINITSIOONID
# ══════════════════════════════════════════════════════════════════════════════
# LEVELS on nimekiri sõnastikest. Iga sõnastik kirjeldab ühte taset.
# dict(...) = sõnastik (dictionary) - hoiab võti:väärtus paare.
# name  = taseme nimi (kuvatakse HUD-is)
# fps   = mängu kiirus (mitu korda sekundis uss liigub - suurem = kiirem)
# walls = seinte arv (suurem = raskem)
# next  = mitu toitu tuleb süüa järgmisele tasemele jõudmiseks

LEVELS = [
    dict(name="Algaja",   fps=7,  walls=0,  next=5),
    dict(name="Harjuja",  fps=10, walls=4,  next=8),
    dict(name="Oskaja",   fps=14, walls=7,  next=12),
    dict(name="Ekspert",  fps=18, walls=10, next=17),
    dict(name="LEGEND",   fps=23, walls=14, next=9999),
    # LEGEND tase ei lõpe kunagi (next=9999 - peaaegu võimatu saavutada)
    # Tahad lisada taseme? Kopeeri üks rida, muuda väärtusi ja lisa siia.
]

# Ussi värvide valikud sätete ekraanil.
# Iga element on: ("nimi", pea-värv, keha-värv)
# Kasutaja näeb sätteid ekraanil värvilisi ringe ja valib oma lemmiku.
SNAKE_COLORS = [
    ("Roheline",   ( 80, 230, 140), ( 40, 160,  80)),
    ("Tsüaan",     ( 60, 215, 215), ( 30, 150, 150)),
    ("Oranž",      (255, 155,  50), (200, 110,  30)),
    ("Roosa",      (255, 120, 170), (200,  75, 120)),
    ("Lilla",      (180, 105, 255), (120,  60, 200)),
    ("Valge",      (225, 225, 230), (160, 160, 170)),
    # Tahad uut värvi lisada? Kopeeri rida ja muuda RGB väärtusi!
]


# ══════════════════════════════════════════════════════════════════════════════
# ABIFUNKTSIOONID
# ══════════════════════════════════════════════════════════════════════════════

def cell_rect(col, row):
    """
    Muudab ruudu koordinaadid (col, row) pikslite Rect-iks.
    col=2, row=3 tähendab 3. veerg, 4. rida (0-st alates).
    HUD_H liitmine lükkab kõik alla, sest HUD on ekraani ülaosas.
    Tagastab pygame.Rect, mida saab joonistamiseks kasutada.
    """
    return pygame.Rect(col * CELL, HUD_H + row * CELL, CELL, CELL)


def rand_cell(exclude):
    """
    Leiab juhusliku VABA ruudu mänguväljakul.
    exclude = hulk (set) asustatud ruutudest (uss, seinad, olemasolev toit).
    Proovib ikka ja jälle kuni leiab tühja ruudu.
    """
    while True:
        c = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
        if c not in exclude:   # "not in" = kas see ruut EI OLE keelatud ruutude hulgas?
            return c


def lerp_color(c1, c2, t):
    """
    Interpoleerib (segab) kaht värvi.
    t=0.0 → tagastab täielikult c1
    t=1.0 → tagastab täielikult c2
    t=0.5 → tagastab c1 ja c2 poolel teel (segu)
    Kasutatakse ussi gradientvärvimiseks (pea heledamast sabast tumedamaks).
    max(0.0, min(1.0, t)) tagab et t jääb alati 0 ja 1 vahele.
    """
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    # tuple(...) = muudab loendi kolmikuks
    # for i in range(3) = käib läbi R, G, B (0, 1, 2)
    # c1[i] + (c2[i] - c1[i]) * t = matemaatiline interpolatsioon iga kanali jaoks


def draw_pill(surf, color, rect, radius=None, border=0, border_color=None):
    """
    Joonistab ümmardatud ristkülikut ("tableti" kuju).
    radius = nurkade ümardumine. None = automaatne (pool kõrgusest = täiuslik oval).
    border = äärte paksus. 0 = ei joonista äärt.
    Kasutatakse nuppude, ussi, toidu jne joonistamiseks.
    """
    r = radius if radius is not None else min(rect.width, rect.height) // 2
    pygame.draw.rect(surf, color, rect, border_radius=r)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=r)
        # teine pygame.draw.rect kus border > 0 joonistab ainult ÄÄRT (täitmata)


def draw_text_centered(surf, text, font, color, cx, cy):
    """
    Joonistab teksti nii et selle KESKKOHTA on (cx, cy).
    Tavaliselt blit() kasutab vasakut ülanurka, aga see funktsioon arvutab
    automaatselt õige offseti et tekst oleks täpselt tsentreeritud.
    Tagastab ka teksti Surface'i, juhuks kui seda vaja läheb.
    """
    s = font.render(text, True, color)
    surf.blit(s, (cx - s.get_width()//2, cy - s.get_height()//2))
    return s


# ══════════════════════════════════════════════════════════════════════════════
# NUPU KLASS
# ══════════════════════════════════════════════════════════════════════════════
# Klass = "mall" objektide loomiseks. Kõik nupud töötavad ühtemoodi,
# aga igal on oma asukoht, tekst ja värv.
# "self" viitab konkreetsele nupu EKSEMPLARILE (ühele kindlale nupule).

class Button:
    def __init__(self, cx, cy, w, h, text, color=None, text_color=None):
        """
        cx, cy = nupu KESKKOHTA koordinaadid (mitte vasakut ülanurka!)
        w, h   = laius ja kõrgus
        text   = nupul kuvatav tekst
        color  = nupu taustavärv (None = kasuta vaikimisi C_BTN_BG)
        text_color = teksti värv (None = kasuta vaikimisi C_TEXT)
        """
        self.rect       = pygame.Rect(cx - w//2, cy - h//2, w, h)
        # cx - w//2 = vasak serv (keskkohast lahuta pool laiust)
        # cy - h//2 = ülemine serv (keskkohast lahuta pool kõrgust)

        self.text       = text
        self.color      = color or C_BTN_BG      # "or" = kui color on None, kasuta C_BTN_BG
        self.hov_color  = C_BTN_HOV              # hover-värv on alati sama
        self.text_color = text_color or C_TEXT
        self.hovered    = False   # kas hiir on nupul? Alguses ei ole.
        self.radius     = h // 2  # ümardumine = pool kõrgust (täiuslik "pilli" kuju)

    def update(self, mouse_pos):
        """
        Uuendab hover-olekut.
        collidepoint = kas antud punkt on selle Rect-i SEES?
        Kutsutakse IGAL kaadril, et nupp teaks kas hiir on peal.
        """
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surf, font=None):
        """Joonistab nupu koos varju, täitmise, ääre ja tekstiga."""
        f   = font or F_MED   # kui fonti ei anta, kasuta vaikimisi F_MED
        col = self.hov_color if self.hovered else self.color
        # Joonistame kerge varju nupust 3 pikslit allpool
        shadow = self.rect.move(0, 3)   # move(x, y) nihutab Rect-i
        draw_pill(surf, (0, 0, 0, 60), shadow, self.radius)
        # (0,0,0,60) = must 60/255 läbipaistvusega - SRCALPHA peaks olema, aga visuaalselt näeb hea välja
        draw_pill(surf, col, self.rect, self.radius)
        # Ääre värv muutub rohekaks kui hiir peal
        border_col = lerp_color(C_BTN_BRD, C_ACCENT, 0.6) if self.hovered else C_BTN_BRD
        draw_pill(surf, border_col, self.rect, self.radius, border=2)
        draw_text_centered(surf, self.text, f, self.text_color,
                           self.rect.centerx, self.rect.centery)

    def clicked(self, event):
        """
        Tagastab True kui selle sündmusega KLÕPSATI sellel nupul.
        Kontrollib:
          1. Kas see on hiireklõpsu sündmus? (MOUSEBUTTONDOWN)
          2. Kas klõpsati VASAKU nupuga? (button == 1)
          3. Kas klõps oli nupu SEES? (collidepoint)
        Kõik kolm peavad olema True.
        """
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ══════════════════════════════════════════════════════════════════════════════
# LIUGURI KLASS
# ══════════════════════════════════════════════════════════════════════════════
# Liugur (slider) helitugevuse seadmiseks sätete ekraanil.
# Kasutaja saab hiirega lohistada.

class Slider:
    def __init__(self, cx, cy, width, value=1.0):
        """
        cx, cy = liuguri KESKKOHTA koordinaadid
        width  = liuguri pikkus pikslites
        value  = algväärtus 0.0-1.0 (1.0 = täistugevus)
        """
        self.rect     = pygame.Rect(cx - width//2, cy - 4, width, 8)
        # 4 = pool kõrgusest (8//2), et liuguri keskkohta oleks (cx, cy)
        self.value    = value
        self.dragging = False   # kas kasutaja hetkel lohistab? Alguses ei lohista.

    def handle_pos_x_to_value(self, x):
        """
        Muudab hiire x-koordinaadi 0.0-1.0 väärtuseks.
        rel = suhteline asukoht liuguril (0 = vasakus servas, 1 = paremas servas)
        max/min tagab et väärtus jääb alati 0.0 ja 1.0 vahele.
        """
        rel = (x - self.rect.left) / self.rect.width
        return max(0.0, min(1.0, rel))

    def handle_event(self, event):
        """
        Töötleb hiire sündmusi.
        MOUSEBUTTONDOWN = nupu vajutamine  → alusta lohistamist
        MOUSEBUTTONUP   = nupu vabastamine → lõpeta lohistamine
        MOUSEMOTION     = hiire liikumine  → uuenda väärtust (ainult lohistamisel)
        inflate(0, 20) teeb klikitava ala 20 pikslit kõrgemaks (lihtsam klõpsata)
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            grab_area = self.rect.inflate(0, 20)
            if grab_area.collidepoint(event.pos):
                self.dragging = True
                self.value = self.handle_pos_x_to_value(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.value = self.handle_pos_x_to_value(event.pos[0])

    def draw(self, surf):
        """Joonistab liuguri: taustariba, täidetud osa ja ümmargune käepide."""
        draw_pill(surf, C_BTN_BG, self.rect, radius=4)   # hall taustariba
        fill_w = int(self.rect.width * self.value)        # täidetud osa laius
        if fill_w > 0:
            fill_rect = pygame.Rect(self.rect.left, self.rect.top, fill_w, self.rect.height)
            draw_pill(surf, C_ACCENT, fill_rect, radius=4)   # roheline täidetud osa
        knob_x = self.rect.left + fill_w   # käepideme x-koordinaat (täidetud osa lõpus)
        knob_y = self.rect.centery
        pygame.draw.circle(surf, C_WHITE, (knob_x, knob_y), 10)    # valge ring
        pygame.draw.circle(surf, C_ACCENT, (knob_x, knob_y), 10, 2)  # roheline ääre


# ══════════════════════════════════════════════════════════════════════════════
# OSAKESTE SÜSTEEM
# ══════════════════════════════════════════════════════════════════════════════
# Osakesed (particles) = väikesed värvipunktid mis lendavad laiali toidu söömisel.
# Iga osakene on eraldi objekt oma asukoha, kiiruse ja elueaga.

class Particle:
    def __init__(self, x, y, color):
        """
        x, y  = lendamise alguspunkt (tavaliselt toidu asukoht)
        color = osakese värv (sama mis toidul/power-upil)
        """
        self.x = float(x)
        self.y = float(y)
        # Juhuslik suund ja kiirus - igal osasel erinev trajektoor
        angle  = random.uniform(0, math.tau)   # math.tau = 2*pi = täisring radiaanides
        speed  = random.uniform(1.5, 4.5)      # juhuslik kiirus 1.5 ja 4.5 pikslit/kaader
        # Kiirus jaotame x ja y komponentideks trigonomeetriaga:
        self.vx       = math.cos(angle) * speed   # x-kiirus (cos(nurk) * kiirus)
        self.vy       = math.sin(angle) * speed   # y-kiirus (sin(nurk) * kiirus)
        self.color    = color
        self.life     = random.randint(18, 38)    # eluiga kaadrites (18-38 kaadrit ≈ 0.3-0.6 sek)
        self.max_life = self.life                 # meename algse eluea et arvutada läbipaistvust
        self.size     = random.randint(2, 5)      # suurus pikslites

    def update(self):
        """
        Uuendab osakese asukohta ja eluiga.
        Kutsutakse igal kaadril.
        """
        self.x  += self.vx    # liiguta x-suunas kiiruse võrra
        self.y  += self.vy    # liiguta y-suunas
        self.vy += 0.12       # gravitatsioon - vy suureneb pidevalt allapoole
                              # 0.12 on väike gravitatsioonikonstant, katsetusega valitud
        self.life -= 1        # üks kaader möödas = üks elu vähem

    def draw(self, surf):
        """
        Joonistab osakese. Mida väiksem life, seda tuhmim (hääbub ära).
        alpha = eluosa 0.0-1.0 kujul (1.0 = täisvärviline, 0.0 = sama kui taust)
        lerp_color segab taustaga - see simuleerib läbipaistvust ilma SRCALPHA-ta.
        """
        if self.life <= 0:
            return   # elu otsas - ära joonista
        alpha = self.life / self.max_life          # 0.0 ... 1.0
        col = lerp_color(C_BG, self.color, alpha)  # segab taustaga: hääbub tausta
        pygame.draw.circle(surf, col, (int(self.x), int(self.y)), self.size)


# ══════════════════════════════════════════════════════════════════════════════
# MÄNGU PÕHIKLASS
# ══════════════════════════════════════════════════════════════════════════════
# Game klass hoiab KOGU mängu oleku:
# uss, toit, seinad, skoor, power-upid, osakesed, animatsioonid...

class Game:
    def __init__(self, level_idx=0, score=0, color_idx=0):
        """
        Loob uue mängu.
        level_idx = millise tasemega alustada (0 = Algaja, 4 = LEGEND)
        score     = algne skoor (taseme tõusmisel kantakse skoor üle!)
        color_idx = valitud ussi värv (0-5)
        """
        self.level_idx = level_idx
        self.lv        = LEVELS[level_idx]   # praeguse taseme sõnastik (fps, walls, next...)
        self.score     = score
        self.food_eaten= 0      # söödud toitu SELLEL tasemel (taseme vahetuse arvestus)
        self.color_idx = color_idx
        self.head_col  = SNAKE_COLORS[color_idx][1]   # pea värv (indeks 1 = teine element)
        self.body_col  = SNAKE_COLORS[color_idx][2]   # keha värv (indeks 2 = kolmas element)

        # Uss algab ekraani KESKEL, 3 segmenti pikk, liigub paremale
        cx, cy       = COLS//2, ROWS//2          # keskmised ruudu koordinaadid
        self.snake   = [(cx, cy), (cx-1, cy), (cx-2, cy)]
        # snake on nimekiri ruutude koordinaatidest. snake[0] = pea, snake[-1] = saba.
        # Pea on (cx, cy), esimene kehasegment (cx-1, cy) jne - uss läheb vasakule.

        self.dir     = (1, 0)    # praegune liikumissuund: (1,0) = paremale
        self.next_d  = (1, 0)    # järgmine suund (kasutaja sisend salvestatakse siia)
        # Miks kaks? Et vältida olukorda kus kasutaja vajutab kahe nupu vahel kiiresti
        # ja uss pöörab 180° (mis tapaks ta). next_d rakendub alles järgmisel step()-il.

        self.alive   = True    # kas uss on elus?
        self.won     = False   # kas mängija on võitnud (läbinud kõik tasemed)?
        self.tick    = 0       # kaadri loendur - kasvab iga step()-iga

        # Paigutame seinad ja loome esimese toidu
        self.walls = self._place_walls(self.lv["walls"])
        self.food_items = []    # nimekiri toiduobjektidest [{pos, type, pts}, ...]
        self.powerups = []      # nimekiri aktiivsete power-upide kohta
        self._spawn_food()      # tekitame esimese toidu

        self.active_fx  = {}    # aktiivsed efektid: {"slow": lõpetamiskaader, "ghost": ...}
                                # Kui tick > active_fx["slow"], siis efekt on lõppenud.
        self.double_pts = False # kas topelt punktid on hetkel aktiivsed?

        # Visuaalsed efektid
        self.particles   = []       # kõik hetkel aktiivsed osakesed
        self.flash_col   = None     # välgu värv (toidu söömisel)
        self.flash_timer = 0        # mitu kaadrit välku veel näidata
        self.wiggle      = 0.0      # keha kõikumise faas (animatsioon)

    def _place_walls(self, n):
        """
        Paigutab n seina juhuslikesse kohtadesse.
        Tagab et seinad ei ilmu ussi lähedale (mängija ei sure kohe alguses).
        excl = hulk KEELATUD ruutudest (uss + ümbritsev ala)
        """
        excl = set(self.snake)   # set = hulk, kiire "in" kontroll (hulgas otsing on kiirem kui nimekirjas)

        head = self.snake[0]
        # Lisame ussi pea ümber turvaala - seinad ei teki otse pea ette
        excl |= {
            head,
            (head[0] + 1, head[1]),
            (head[0] + 2, head[1]),
            (head[0] + 3, head[1]),
            (head[0] - 1, head[1]),
            (head[0], head[1] + 1),
            (head[0], head[1] - 1),
        }
        # excl |= {...} = liida hulkade ühend (lisa kõik uued elemendid)

        walls = []
        tries = 0
        while len(walls) < n and tries < 2000:
            # Proovi kuni n seina on paigutatud, aga maksimaalselt 2000 katset
            # (et programm ei jääks lõputusse tsüklisse kui ruumi napib)
            w = (random.randint(2, COLS-3), random.randint(2, ROWS-3))
            # randint(2, COLS-3) = ei pane seinu päris servadesse (äärtes mängida oleks võimatu)
            if w not in excl and w not in walls:
                walls.append(w)
                excl.add(w)
            tries += 1
        return walls

    def _spawn_food(self):
        """
        Tekitab toidu nii et igat tüüpi toitu on täpselt üks korraga.
        Punane toit ilmub ALATI.
        Roheline ilmub 30% tõenäosusega.
        Kuldne ilmub 15% tõenäosusega.
        """
        # Kogume kõik hõivatud ruudud ühte hulka
        occ = set(self.snake) | set(self.walls)
        occ |= {f["pos"] for f in self.food_items}
        occ |= {p["pos"] for p in self.powerups}
        # {f["pos"] for f in self.food_items} = set comprehension
        # = loob hulga kõigi toiduobjektide positsioonidest

        # Punane toit - alati olemas
        if not any(f["type"] == "red" for f in self.food_items):
            # any(...) = True kui VÄHEMALT ÜKS element vastab tingimusele
            # "not any" = ei ole ühtegi punast toitu → tekita üks
            pos = rand_cell(occ); occ.add(pos)
            self.food_items.append({"pos": pos, "type": "red", "pts": 1})

        # Roheline toit - 30% tõenäosus
        if not any(f["type"] == "green" for f in self.food_items):
            if random.random() < 0.30:   # random.random() = juhuslik float 0.0-1.0
                pos = rand_cell(occ); occ.add(pos)
                self.food_items.append({"pos": pos, "type": "green", "pts": 3})

        # Kuldne toit - 15% tõenäosus
        if not any(f["type"] == "gold" for f in self.food_items):
            if random.random() < 0.15:
                pos = rand_cell(occ); occ.add(pos)
                self.food_items.append({"pos": pos, "type": "gold",  "pts": 5})

    def _maybe_spawn_powerup(self):
        """
        Väikese tõenäosusega tekitab power-upi.
        Korraga on maksimaalselt 2 power-upi väljas (len >= 2 = ära tekita).
        1.5% tõenäosus igal kaadril = keskmiselt ilmub power-up iga ~67 kaadri tagant.
        """
        if len(self.powerups) >= 2:
            return
        if random.random() < 0.015:
            occ = set(self.snake) | set(self.walls)
            occ |= {f["pos"] for f in self.food_items}
            occ |= {p["pos"] for p in self.powerups}
            pu_type = random.choice(["slow", "scissors", "ghost", "double"])
            pos = rand_cell(occ)
            self.powerups.append({
                "pos":    pos,
                "type":   pu_type,
                "expiry": self.tick + self.lv["fps"] * 7,
                # expiry = kaader mil power-up KAOB (7 sekundit = fps * 7 kaadrit)
            })

    def handle_key(self, key):
        """
        Töötleb klaviatuuri sisendi.
        Aktsepteerib nii nooleklahve kui WASD-i.
        Ei luba 180° pöördet (ei saa minna otse vastassuunda - see tapaks ussi).
        """
        dirs = {
            pygame.K_UP:    (0, -1), pygame.K_w: (0, -1),   # üles = y väheneb
            pygame.K_DOWN:  (0,  1), pygame.K_s: (0,  1),   # alla  = y suureneb
            pygame.K_LEFT:  (-1, 0), pygame.K_a: (-1, 0),   # vasakule = x väheneb
            pygame.K_RIGHT: (1,  0), pygame.K_d: (1,  0),   # paremale = x suureneb
        }
        if key in dirs:
            nd = dirs[key]
            # Kontrollib et uus suund ei ole otse vastupidine praegusele.
            # Kui uss liigub paremale (1,0), ei saa minna vasakule (-1,0).
            # nd[0] != -self.dir[0] tähendab "x-suund ei ole täpselt vastupidine"
            # OR: piisab et kas x VÕI y ei ole vastupidine (mõlemad peavad olema vastupidised 180° pöörde jaoks)
            if (nd[0] != -self.dir[0]) or (nd[1] != -self.dir[1]):
                self.next_d = nd

    def step(self):
        """
        Üks mängusamma - liigutab ussi ühe ruudu võrra.
        Kutsutakse igal mängukaadril (FPS korda sekundis).
        Tagastab:
          None      = kõik normaalne
          "DEAD"    = uss suri
          "LEVELUP" = tase tõusis
          "WON"     = kõik tasemed läbitud
        """
        if not self.alive:
            return None   # surnud uss ei liigu

        self.tick    += 1
        self.dir      = self.next_d   # rakenda kasutaja valitud suund
        self.wiggle  += 0.4           # keha kõikumise animatsiooni faas edasi

        # Arvuta uus pea koordinaat
        nx = self.snake[0][0] + self.dir[0]   # uus x = vana pea x + suuna x
        ny = self.snake[0][1] + self.dir[1]   # uus y = vana pea y + suuna y

        # Ghost power-up: uss läheb läbi seinte (wrapparound)
        if "ghost" in self.active_fx and self.active_fx["ghost"] > self.tick:
            nx %= COLS   # % = jääk jagamisel. Kui nx=28 ja COLS=28, saab nx=0 (teiselt poolt)
            ny %= ROWS   # Näiteks: -1 % 28 = 27 (vasakult välja = ilmub paremalt)
        else:
            # Tavaliselt: seina tabamine = surm
            if not (0 <= nx < COLS and 0 <= ny < ROWS):
                # 0 <= nx < COLS tähendab "nx on 0 ja COLS-1 vahel"
                # "not (...)" = kui ON väljas, siis sure
                return self._die()
            if (nx, ny) in self.walls:
                return self._die()

        new_head = (nx, ny)

        # Enesesse põrkamine: kui uus pea asub juba ussi sees
        if new_head in self.snake[:-1]:
            # self.snake[:-1] = kõik peale VIIMASE segmendi (saba liigub ära, nii et see on OK)
            return self._die()

        # Lisa uus pea nimekirja ETTE
        self.snake.insert(0, new_head)
        grew = False   # kas uss kasvas selle sammuga?

        # Kontrolli kas sõime mõne toidu
        for food in list(self.food_items):
            # list(...) = koopia, sest eemaldame elemendi tsükli sees
            if new_head == food["pos"]:
                pts = food["pts"] * (2 if self.double_pts else 1)
                # Topelt punktid: food["pts"] * 2 kui double_pts on True, muidu * 1
                self.score      += pts
                self.food_eaten += pts
                grew = True   # uss kasvas - ära võta saba ära
                col_map = {"red": C_FOOD_RED, "green": C_FOOD_GRN, "gold": C_FOOD_GOLD}
                self._burst(new_head, col_map.get(food["type"], C_ACCENT))
                # col_map.get(key, default) = võta väärtus, kui võtit pole kasuta default
                self.flash_col, self.flash_timer = C_ACCENT, 4
                # Pythonis saab mitme muutuja väärtuse korraga omistada!
                self.food_items.remove(food)
                play(SND_EAT)
                self._spawn_food()   # tekita uus toit kohe asemele
                break   # ühe kaadriga saab süüa ainult ühe toidu - lõpeta tsükkel

        # Kontrolli kas astusime power-upi peale
        for pu in list(self.powerups):
            if new_head == pu["pos"]:
                self._apply_pu(pu["type"])
                self.powerups.remove(pu)
                play(SND_POWERUP)
                break

        # Eemalda aegunud power-upid (expiry <= tick tähendab et aeg on läbi)
        self.powerups = [p for p in self.powerups if p["expiry"] > self.tick]
        # List comprehension filtreerimiseks: [element for element in nimekiri if tingimus]

        # Uuenda double_pts lippu
        self.double_pts = ("double" in self.active_fx and
                           self.active_fx["double"] > self.tick)
        # True ainult kui "double" efekt ON aktiivsete efektide hulgas JA ei ole aegunud

        # Kui ei söönud toitu, eemalda saba
        if not grew:
            self.snake.pop()   # .pop() eemaldab nimekirja VIIMASE elemendi (saba)
            # Uss on nüüd sama pikk kui enne - liikus ühe sammu

        self._maybe_spawn_powerup()

        # Puhasta surnud osakesed ja uuenda ülejäänuid
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

        if self.flash_timer > 0:
            self.flash_timer -= 1

        # Kontrolli kas tase on läbitud
        if self.food_eaten >= self.lv["next"]:
            if self.level_idx < len(LEVELS) - 1:
                return "LEVELUP"   # veel tasemeid järel
            else:
                self.won = True
                return "WON"       # viimane tase läbitud - võit!

        return None   # kõik normaalne, mäng jätkub

    def _apply_pu(self, pu_type):
        """
        Rakendab power-up efekti.
        Enamik efekte seab active_fx sõnastikusse lõpetamistiku (tick + kestus).
        "scissors" on erand - see toimib kohe (ei ole ajutine).
        """
        dur = self.lv["fps"] * 6   # efekti kestus = 6 sekundit (fps * 6 kaadrit)

        if pu_type == "slow":
            self.active_fx["slow"]   = self.tick + dur   # aeglustumine kestab dur kaadrit

        elif pu_type == "scissors":
            half = max(3, len(self.snake)//2)   # lõika pooleks, aga vähemalt 3 segment jätame
            self.snake = self.snake[:half]        # kanna alles ainult esimene pool
            # self.snake[:half] = nimekirja esimesed "half" elementi
            self._burst(self.snake[0], C_PU_SCIS, count=24)   # suur osakeste plahvatus

        elif pu_type == "ghost":
            self.active_fx["ghost"]  = self.tick + dur   # läbi seinte kestab dur kaadrit

        elif pu_type == "double":
            self.active_fx["double"] = self.tick + dur   # topelt punktid kestab dur kaadrit

        # Välgu värv ekraanile (visuaalne tagasiside)
        col_map = {"slow": C_PU_SLOW, "scissors": C_PU_SCIS,
                   "ghost": C_PU_GHOST, "double": C_PU_DOUBLE}
        self.flash_col   = col_map.get(pu_type, C_ACCENT)
        self.flash_timer = 9   # välk nähtav 9 kaadrit

    def _die(self):
        """
        Ussi surm.
        Seab alive=False, mängib heli, tekitab plahvatuse osakestest.
        Tagastab "DEAD" et peamine mängutsükkel teaks mis juhtus.
        """
        self.alive = False
        play(SND_CRASH)
        for seg in self.snake[:10]:
            # [:10] = maksimaalselt 10 segmenti - pikema ussi puhul ainult ees
            self._burst(seg, C_RED_UI, count=7)   # iga segmendi kohal punane plahvatus
        return "DEAD"

    def _burst(self, cell, color, count=14):
        """
        Tekitab osakeste plahvatuse antud ruudu kohal.
        Muudab ruudu koordinaadid piksliteks ja loob count osakest.
        """
        cx = cell[0] * CELL + CELL//2    # ruudu keskpunkti x pikslites
        cy = HUD_H + cell[1] * CELL + CELL//2   # + HUD_H et arvestada ülemist paneeli
        for _ in range(count):
            # range(count) = count korda. "_" = muutuja mida ei kasutata (tavaline Pythoni tava)
            self.particles.append(Particle(cx, cy, color))

    def get_fps(self):
        """
        Tagastab praeguse FPS - kas tavalist või aeglustatud.
        "slow" power-up poolitab FPS-i (mäng jookseb poole aeglasemalt).
        max(3, ...) tagab et FPS ei lähe alla 3 (mäng ei jääks täiesti seisma).
        """
        if "slow" in self.active_fx and self.active_fx["slow"] > self.tick:
            return max(3, self.lv["fps"]//2)
        return self.lv["fps"]

    def draw(self, surf, paused, highscore):
        """
        Joonistab kogu mängu: taust, ruudustik, seinad, toit, power-upid,
        uss, osakesed, välk, HUD.
        Kutsutakse igal kaadril.
        paused = kas kuvada "PAUS" tekst HUD-is
        highscore = rekord HUD-is kuvamiseks
        """
        surf.fill(C_BG)   # puhasta ekraan (tumesinine taust)

        # Ruudustik - vertikaalsed ja horisontaalsed jooned
        for c in range(COLS+1):
            pygame.draw.line(surf, C_GRID, (c*CELL, HUD_H), (c*CELL, HUD_H+ROWS*CELL))
            # Joon algab HUD_H kõrguselt (HUD all) ja läheb mänguväljaku lõpuni
        for r in range(ROWS+1):
            pygame.draw.line(surf, C_GRID, (0, HUD_H+r*CELL), (WIN_W, HUD_H+r*CELL))

        # Ghost efekti visuaal - sinakashall kiht kogu väljakul
        if "ghost" in self.active_fx and self.active_fx["ghost"] > self.tick:
            gsurf = pygame.Surface((WIN_W, ROWS*CELL), pygame.SRCALPHA)
            # SRCALPHA = Surface toetab läbipaistvust (alpha kanalit)
            gsurf.fill((80, 160, 255, 12))   # nelik (R,G,B,A) - A=12 on väga läbipaistev
            surf.blit(gsurf, (0, HUD_H))

        # Seinad
        for wx, wy in self.walls:
            # "for wx, wy in self.walls" = lahti pakkimine (tuple unpacking)
            # Iga sein on (wx, wy) koordinaadipaarine, lahti pakituna kaheks muutujaks
            r = cell_rect(wx, wy).inflate(-2, -2)
            # .inflate(-2, -2) teeb Rect-i 2 pikslit igast servast väiksemaks
            # Nii on seinad natuke väiksemad kui ruudud - näevad paremad välja
            draw_pill(surf, C_WALL, r, radius=4)
            pygame.draw.rect(surf, (85, 90, 120), r.move(0, -1), 1, border_radius=4)
            # Üks piksel heledamat joont sein tipus = 3D efekt

        # Toit
        for food in self.food_items:
            fx, fy = food["pos"]
            rect = cell_rect(fx, fy)
            cx, cy = rect.centerx, rect.centery
            r = CELL//2 - 3   # toidu raadius (pisut väiksem kui pool ruudu laiust)
            col = {"red": C_FOOD_RED, "green": C_FOOD_GRN, "gold": C_FOOD_GOLD}[food["type"]]
            # Sõnastik kust kohe indexeerime - lühike viis if/elif asemel
            pygame.draw.circle(surf, lerp_color(C_BG, col, 0.3), (cx, cy+2), r)  # vari allpool
            pygame.draw.circle(surf, col, (cx, cy), r)                             # põhivärv
            pygame.draw.circle(surf, (255,255,255), (cx - r//3, cy - r//3), max(2, r//4))
            # Väike valge punkt ülemises vasakus servas = läike efekt (nagu 3D pall)

        # Power-upid
        PU_COLORS = {"slow": C_PU_SLOW, "scissors": C_PU_SCIS,
                     "ghost": C_PU_GHOST, "double": C_PU_DOUBLE}
        PU_LABELS = {"slow": "AEGLANE", "scissors": "LÕIKA",
                     "ghost": "GHOST", "double": "x2"}

        for pu in self.powerups:
            px, py = pu["pos"]
            rect = cell_rect(px, py)
            col  = PU_COLORS[pu["type"]]
            lbl  = PU_LABELS[pu["type"]]

            # Sära (glow) efekt power-upi ümber
            glow_surf = pygame.Surface((CELL+8, CELL+8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*col, 40), (0, 0, CELL+8, CELL+8), border_radius=8)
            # (*col, 40) = laiali pakkimine (unpacking) + alpha lisamine
            # Kui col=(80,160,255), siis (*col, 40) = (80,160,255,40)
            surf.blit(glow_surf, (rect.left-4, rect.top-4))

            draw_pill(surf, lerp_color(C_BG, col, 0.25), rect.inflate(-1,-1), radius=6)  # taust
            draw_pill(surf, col, rect.inflate(-5,-5), radius=5)   # põhivärv

            sym = F_TINY.render(lbl, True, C_BG)   # silt (nt "x2") tumeda tekstina
            surf.blit(sym, sym.get_rect(center=rect.center))
            # .get_rect(center=...) = Rect millel on antud keskkohta - tsentreeritud positsioon

            # Eluajaribar power-upi all (kahaneb aja jooksul)
            total = self.lv["fps"] * 7    # kogu eluaeg kaadrites
            pct   = max(0, (pu["expiry"] - self.tick) / total)   # 0.0-1.0
            bar   = pygame.Rect(rect.left, rect.bottom + 3, CELL, 4)
            pygame.draw.rect(surf, (40, 42, 65), bar, border_radius=2)   # hall taustariba
            fill_w = int(CELL * pct)
            if fill_w > 0:
                pygame.draw.rect(surf, col, pygame.Rect(bar.left, bar.top, fill_w, 4), border_radius=2)

        # Uss
        self._draw_snake(surf)

        # Osakesed (toiduplahvatused)
        for p in self.particles:
            p.draw(surf)

        # Välk (toidu söömisel ekraan vilgub)
        if self.flash_timer > 0 and self.flash_col:
            a = int(70 * self.flash_timer / 9)   # läbipaistvus kahaneb aja jooksul
            fsurf = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
            fsurf.fill((*self.flash_col, a))
            surf.blit(fsurf, (0, 0))

        # HUD
        self._draw_hud(surf, paused, highscore)

    def _draw_snake(self, surf):
        """
        Joonistab ussi tagant ette (sabast peani).
        Nii on pea alati "peal" (teiste segmentide katab).
        Iga segment on ring, pea on veidi suurem ja silmadega.
        """
        n = len(self.snake)
        for i in range(n-1, -1, -1):
            # range(n-1, -1, -1) = loendab tagurpidi: n-1, n-2, ..., 1, 0
            # i=n-1 = saba (joonistame esimesena), i=0 = pea (joonistame viimasena = peale)
            sc, sr = self.snake[i]
            rect   = cell_rect(sc, sr)
            cx, cy = rect.centerx, rect.centery

            # Segmendid kahanevad pisut peast sabani
            scale = 1.0 if i == 0 else max(0.55, 1.0 - i * 0.012)
            # Pea: scale=1.0 (täissuurus)
            # i=1: scale = max(0.55, 1.0 - 0.012) ≈ 0.988
            # Saba juures: scale ≈ 0.55 (miinimum)

            r = int(CELL * 0.48 * scale)   # segmendi raadius

            # Gradient: pea on head_col, saba poole liikudes muutub body_col-iks
            t_grad = i / max(n - 1, 1)   # 0.0 = pea, 1.0 = saba
            col = lerp_color(self.head_col, self.body_col, min(t_grad * 1.4, 1.0))
            # * 1.4 kiirendab gradienti (sabapoolsed segmendid saavad kiiremini kehavärvit)

            if i == 0:
                # PEA joonistamine - suurem ring + silmad + suu
                head_r = int(CELL * 0.52)
                pygame.draw.circle(surf, lerp_color(C_BG, col, 0.35), (cx, cy+2), head_r)  # vari
                pygame.draw.circle(surf, col, (cx, cy), head_r)

                # Silmad: kaks valget ringi liikumissuunas, küljele nihutatud
                dx, dy = self.dir
                eye_offset_x = dx * 4   # silmad on suunas dx*4 pikslit ees
                eye_offset_y = dy * 4
                perp_x =  dy * 5   # risti liikumissuunaga (perpendikulaar)
                perp_y = -dx * 5   # risti x on -y, risti y on x (matemaatika)

                for sign in (+1, -1):
                    # Kaks silma: üks sign=+1 poole, teine sign=-1 poole
                    ex = cx + eye_offset_x + sign * perp_x
                    ey = cy + eye_offset_y + sign * perp_y
                    pygame.draw.circle(surf, C_WHITE, (ex, ey), 4)        # valge silm
                    px2 = ex + dx
                    py2 = ey + dy
                    pygame.draw.circle(surf, (30, 30, 50), (px2, py2), 2)  # tume pupill
                    pygame.draw.circle(surf, C_WHITE, (px2-1, py2-1), 1)   # läige pupilli sees

                # Suu: 3 väikest stiplit kaare kujul
                mouth_cx = cx + dx * 5
                mouth_cy = cy + dy * 5
                mouth_col = lerp_color(col, (0,0,0), 0.4)
                for angle_off in (-20, 0, 20):
                    angle_rad = math.radians(
                        math.degrees(math.atan2(dy, dx)) + 90 + angle_off
                    )
                    # math.atan2(dy, dx) = suunanurk radiaanides
                    # math.degrees(...) = muudab kraadideks
                    # + 90 + angle_off = nihutab suu servad kaare moodustamiseks
                    # math.radians(...) = tagasi radiaanideks sin/cos jaoks
                    mx2 = int(mouth_cx + math.cos(angle_rad) * 3)
                    my2 = int(mouth_cy + math.sin(angle_rad) * 3)
                    pygame.draw.circle(surf, mouth_col, (mx2, my2), 1)

            else:
                # KEHASESGMENT joonistamine - lihtsam, kõikub kergelt
                wiggle_off = int(math.sin(self.wiggle + i * 0.7) * 1.2)
                # math.sin tagastab -1 kuni 1. * 1.2 = max 1.2 pikslit kõikumist
                # i * 0.7 = iga segment kõigub erineva faasiga (mitte kõik korraga)
                pygame.draw.circle(surf, lerp_color(C_BG, col, 0.3), (cx, cy + 2), r)  # vari
                pygame.draw.circle(surf, col, (cx + wiggle_off, cy), r)
                if r > 5:
                    # Läikeläige: ainult piisavalt suurtel segmentidel
                    pygame.draw.circle(surf,
                                       lerp_color(col, C_WHITE, 0.35),
                                       (cx + wiggle_off - r//4, cy - r//4), max(2, r//4))

    def _draw_hud(self, surf, paused, highscore):
        """
        Joonistab ülemise infopaneeli (HUD).
        Vasakul: skoor ja rekord
        Keskel: taseme nimi
        Paremal: aktiivsed power-up efektid (koos ajastusribaga)
        Paus-tekst kui mäng on peatatud
        """
        pygame.draw.rect(surf, C_HUD_BG, (0, 0, WIN_W, HUD_H))
        pygame.draw.line(surf, (32, 34, 58), (0, HUD_H-1), (WIN_W, HUD_H-1), 1)
        # Õhuke joon HUD-i allservas = visuaalne eraldaja mänguväljast

        # Skoor vasakul
        sc_s = F_MED.render(f"Skoor  {self.score:04d}", True, C_ACCENT)
        # f"..." = f-string (formaaditud tekst)
        # :04d = täisarv, minimaalselt 4 koht, täidetakse nullidega (näiteks 0042)
        surf.blit(sc_s, (12, 8))

        hs_s = F_TINY.render(f"Rekord {highscore:04d}", True, C_DIM)
        surf.blit(hs_s, (12, 34))

        # Taseme nimi keskel
        lv_s = F_SMALL.render(self.lv["name"], True, C_GOLD_UI)
        surf.blit(lv_s, (WIN_W//2 - lv_s.get_width()//2, 17))

        # Aktiivsed efektid paremal (koos ajastusribaga)
        PU_COLS = {"slow": C_PU_SLOW, "ghost": C_PU_GHOST, "double": C_PU_DOUBLE}
        PU_LBLS = {"slow": "Aeglane", "ghost": "Ghost", "double": "x2"}
        x = WIN_W - 10   # algame paremast, liigume vasakule
        for eff, expiry in self.active_fx.items():
            # .items() annab kõik (võti, väärtus) paarid sõnastikust
            if expiry > self.tick and eff in PU_LBLS:
                col   = PU_COLS[eff]
                total = self.lv["fps"] * 6
                pct   = max(0, (expiry - self.tick) / total)
                lbl   = F_TINY.render(PU_LBLS[eff], True, col)
                x    -= lbl.get_width() + 4   # nihuta x vasakule enne joonistamist
                surf.blit(lbl, (x, 10))
                bw = lbl.get_width()
                pygame.draw.rect(surf, (40, 42, 65), (x, 26, bw, 4), border_radius=2)  # hall riba
                pygame.draw.rect(surf, col, (x, 26, int(bw * pct), 4), border_radius=2)  # värvitud osa
                x -= 10   # vahe efektide vahel

        # Paus-tekst
        if paused:
            p_s = F_MED.render("PAUS", True, C_GOLD_UI)
            surf.blit(p_s, (WIN_W - p_s.get_width() - 10, 17))


# ══════════════════════════════════════════════════════════════════════════════
# MENÜÜ ABIFUNKTSIOONID
# ══════════════════════════════════════════════════════════════════════════════

def draw_menu_bg(surf, tick):
    """
    Joonistab menüü animeeritud tausta.
    6 suurt värvilise ringi mis liiguvad aeglaselt sin/cos lainete järgi.
    tick kasvab igal kaadril → animatsioon.
    """
    surf.fill(C_BG)
    for i in range(6):
        phase = tick * 0.015 + i * 1.05
        # tick * 0.015 = aeglane ajupõhine muutus
        # i * 1.05 = iga ring alustab erineva faasiga (mitte kõik samas kohas)
        cx = int(WIN_W * (0.15 + 0.14 * i) + math.sin(phase) * 40)
        # Horisontaalne asukoht: jaotume ühtlaselt + 40 pikslit sin-laine kõikumist
        cy = int(WIN_H * 0.5 + math.cos(phase * 0.7 + i) * 80)
        # Vertikaalne: ekraani keskel + 80 pikslit cos-laine kõikumist
        r  = 60 + int(math.sin(phase * 0.5) * 20)   # raadius kõigub 40-80 vahel
        col = lerp_color(C_BG, C_ACCENT, 0.04 + 0.02 * math.sin(phase))
        # Väga tuhm rohekashall - peaaegu nähtamatu, aga annab sügavust
        pygame.draw.circle(surf, col, (cx, cy), r)


def draw_snake_logo(surf, cx, cy):
    """
    Joonistab väikese dekoratiivse ussi pea menüüpealkirja kõrvale.
    Koosneb 5 segmendist + pea silmadega.
    segments = [(x-offset, y-offset, raadius), ...]
    """
    head_col = SNAKE_COLORS[0][1]
    body_col = SNAKE_COLORS[0][2]
    segments = [(-46, 14, 9), (-34, 8, 10), (-22, 4, 11), (-10, 2, 12), (0, 0, 13)]
    for i, (ox, oy, r) in enumerate(segments[:-1]):
        # segments[:-1] = kõik peale viimase (saba joonistame eraldi)
        # enumerate annab (indeks, väärtus) paare
        sx, sy = cx + ox, cy + oy
        t = i / (len(segments) - 1)
        col = lerp_color(head_col, body_col, t)
        pygame.draw.circle(surf, lerp_color(C_BG, col, 0.3), (sx, sy + 2), r)
        pygame.draw.circle(surf, col, (sx, sy), r)
    hx, hy, hr = segments[-1]   # viimane element = pea
    hx, hy = cx + hx, cy + hy
    pygame.draw.circle(surf, lerp_color(C_BG, head_col, 0.3), (hx, hy + 2), hr)
    pygame.draw.circle(surf, head_col, (hx, hy), hr)
    for sign in (+1, -1):
        ex = hx + 5
        ey = hy - 5 + sign * 7
        pygame.draw.circle(surf, C_WHITE, (ex, ey), 4)
        pygame.draw.circle(surf, (30, 30, 50), (ex + 1, ey), 2)


def draw_overlay(surf, lines, alpha=165):
    """
    Joonistab poolläbipaistva tumeda kihi ekraanile koos tekstiga.
    Kasutatakse "mäng läbi", "võit" jne ekraanidel.
    lines = nimekiri tuubitest: [(tekst, fondi_indeks, värv), ...]
    fondi_indeks: 0=F_BIG, 1=F_MED, 2=F_SMALL
    alpha = kihi läbipaistmatus (165/255 ≈ 65% tume)
    """
    ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    ov.fill((5, 6, 18, alpha))
    surf.blit(ov, (0, 0))
    fonts  = [F_BIG, F_MED, F_SMALL]
    line_h = 14   # vahe ridade vahel
    total_h = sum(fonts[min(fi,2)].get_height() + line_h for _, fi, _ in lines)
    # Arvutame kogu teksti kõrguse et tsentreerida
    y = WIN_H//2 - total_h//2   # algame nii et kogu tekst on vertikaalselt keskel
    for text, fi, color in lines:
        f = fonts[min(fi, 2)]   # min(fi, 2) tagab et indeks ei lähe üle 2 (fondi massiiv on 0-2)
        s = f.render(text, True, color)
        surf.blit(s, (WIN_W//2 - s.get_width()//2, y))
        y += s.get_height() + line_h


# ══════════════════════════════════════════════════════════════════════════════
# MENÜÜD JA EKRAANID
# ══════════════════════════════════════════════════════════════════════════════

def main_menu(highscore, color_idx):
    """
    Peamenüü ekraan.
    Tagastab ("start", color_idx) kui mäng algab, ("quit", color_idx) kui väljutakse.
    Menüü on ise tsükkel - jookseb kuni kasutaja teeb valiku.
    """
    btn_start = Button(WIN_W//2, WIN_H//2 - 10, 220, 52, "Alusta mäng",
                       color=lerp_color(C_BTN_BG, C_ACCENT, 0.15), text_color=C_ACCENT)
    btn_info  = Button(WIN_W//2, WIN_H//2 + 60, 220, 44, "Kuidas mängida", text_color=C_TEXT)
    btn_set   = Button(WIN_W//2, WIN_H//2 + 118, 220, 44, "Sätted", text_color=C_TEXT)
    tick = 0
    while True:
        tick += 1
        mouse = pygame.mouse.get_pos()   # hiire praegused koordinaadid
        btn_start.update(mouse); btn_info.update(mouse); btn_set.update(mouse)
        draw_menu_bg(screen, tick)

        title = F_TITLE.render("SNAKE", True, C_ACCENT)
        screen.blit(title, (WIN_W//2 - title.get_width()//2, 38))
        draw_snake_logo(screen, WIN_W//2 - title.get_width()//2 - 35, 68)

        if highscore > 0:
            hs = F_SMALL.render(f"Rekord:  {highscore}", True, C_GOLD_UI)
            screen.blit(hs, (WIN_W//2 - hs.get_width()//2, 110))

        btn_start.draw(screen, F_MED)
        btn_info.draw(screen, F_SMALL)
        btn_set.draw(screen, F_SMALL)

        ctrl = F_TINY.render("Nooled / WASD  |  P = Paus  |  ESC = Välja", True, C_DIM)
        screen.blit(ctrl, (WIN_W//2 - ctrl.get_width()//2, WIN_H - 18))
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", color_idx
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit", color_idx
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    play(SND_CLICK); return "start", color_idx
            if btn_start.clicked(event):
                play(SND_CLICK); return "start", color_idx
            if btn_info.clicked(event):
                play(SND_CLICK); info_screen()   # läheme infot vaatama (eraldi tsükkel)
            if btn_set.clicked(event):
                play(SND_CLICK); color_idx = settings_screen(color_idx)
                # settings_screen tagastab (võib-olla muutunud) color_idx


def info_screen():
    """
    "Kuidas mängida" ekraan.
    Näitab toidude ja power-upide selgitusi ning tasemeid.
    Ei tagasta midagi - vajutus Tagasi/ESC/ENTER/SPACE lihtsalt väljub.
    """
    btn_back = Button(WIN_W//2, WIN_H - 38, 160, 42, "Tagasi")
    tick = 0
    while True:
        tick += 1
        mouse = pygame.mouse.get_pos()
        btn_back.update(mouse)
        draw_menu_bg(screen, tick)

        title = F_BIG.render("Kuidas mängida", True, C_ACCENT)
        screen.blit(title, (WIN_W//2 - title.get_width()//2, 18))

        # Vasak veerg: toidud
        col1_x = 36; y = 78
        head1 = F_MED.render("TOIDUD", True, C_GOLD_UI)
        screen.blit(head1, (col1_x, y)); y += head1.get_height() + 14
        for col, txt in [(C_FOOD_RED, "Punane    +1 punkt"),
                         (C_FOOD_GRN, "Roheline  +3 punkti"),
                         (C_FOOD_GOLD,"Kuldne    +5 punkti")]:
            pygame.draw.circle(screen, col, (col1_x + 11, y + 11), 10)
            pygame.draw.circle(screen, C_WHITE, (col1_x + 7, y + 7), 3)
            s = F_SMALL.render(txt, True, C_TEXT)
            screen.blit(s, (col1_x + 30, y + 1)); y += s.get_height() + 14

        # Parem veerg: power-upid
        col2_x = WIN_W//2 + 16; y2 = 78
        head2 = F_MED.render("POWER-UPID", True, C_GOLD_UI)
        screen.blit(head2, (col2_x, y2)); y2 += head2.get_height() + 14
        for col, lbl, desc in [(C_PU_SLOW,  "AEGLANE","Uss liigub aeglasemalt 6 sek"),
                                (C_PU_SCIS,  "LÕIKA",  "Uss lõigatakse pooleks"),
                                (C_PU_GHOST, "GHOST",  "Läbi seinte 6 sekundit"),
                                (C_PU_DOUBLE,"x2",     "Topelt punktid 6 sek")]:
            badge = pygame.Rect(col2_x, y2, 78, 28)
            draw_pill(screen, lerp_color(C_BG, col, 0.3), badge, radius=6)
            draw_pill(screen, col, badge, radius=6, border=1, border_color=col)
            ls = F_TINY.render(lbl, True, C_BG)
            screen.blit(ls, ls.get_rect(center=badge.center))
            ds = F_SMALL.render(desc, True, C_TEXT)
            screen.blit(ds, (col2_x + 88, y2 + 4))
            y2 += max(ds.get_height(), badge.height) + 12

        # Tasemete nimekiri
        y3 = max(y, y2) + 24
        head3 = F_MED.render("TASEMED", True, C_GOLD_UI)
        screen.blit(head3, (36, y3)); y3 += head3.get_height() + 10
        for lv in LEVELS:
            ls = F_SMALL.render(f"{lv['name']:10s}  {lv['fps']} FPS  |  {lv['walls']} seina", True, C_DIM)
            # :10s = tekst minimaalselt 10 tähemärki lai (täidetakse tühikutega) - veergude joondamine
            screen.blit(ls, (36, y3)); y3 += ls.get_height() + 6

        btn_back.draw(screen, F_MED)
        pygame.display.flip(); clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()   # programm täielikult välja
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                return   # tühja return = väljume sellest funktsioonist (tagasi peamenüüsse)
            if btn_back.clicked(event):
                play(SND_CLICK); return


def settings_screen(color_idx):
    """
    Sätete ekraan: ussi värvi valik ja helitugevus.
    Tagastab color_idx (kas muutunud või sama).
    """
    global VOLUME   # "global" = tahame muuta mooduli-taseme muutujat, mitte luua lokaalset
    btn_back = Button(WIN_W//2, WIN_H - 38, 160, 42, "Tagasi")
    swatch_w = 52   # värvivalija ruudu suurus
    n_col    = len(SNAKE_COLORS)
    total_sw = n_col * (swatch_w + 12)   # kõigi ruutude kogulaiust
    sw_x0    = WIN_W//2 - total_sw//2    # kust alustada et kogu rida oleks keskel
    slider   = Slider(WIN_W//2, WIN_H - 38 - 70, 260, value=VOLUME)
    tick = 0
    while True:
        tick += 1
        mouse = pygame.mouse.get_pos()
        btn_back.update(mouse)
        draw_menu_bg(screen, tick)

        title = F_BIG.render("Sätted", True, C_ACCENT)
        screen.blit(title, (WIN_W//2 - title.get_width()//2, 24))

        lbl = F_MED.render("Vali ussi värv:", True, C_TEXT)
        screen.blit(lbl, (WIN_W//2 - lbl.get_width()//2, 100))

        sw_y = 145
        for i, (name, hcol, bcol) in enumerate(SNAKE_COLORS):
            sx   = sw_x0 + i * (swatch_w + 12)
            rect = pygame.Rect(sx, sw_y, swatch_w, swatch_w)
            # Taustakiht valitud värviga
            pygame.draw.rect(screen, lerp_color(C_BG, hcol, 0.15), rect.inflate(4,4), border_radius=14)
            # Väike ussi nägu igas kastis (pea + keha + silmad)
            pygame.draw.circle(screen, hcol, rect.center, swatch_w//2 - 4)
            pygame.draw.circle(screen, bcol, (rect.centerx, rect.centery + 7), swatch_w//4)
            pygame.draw.circle(screen, C_WHITE, (rect.centerx - 6, rect.centery - 6), 5)
            pygame.draw.circle(screen, C_WHITE, (rect.centerx + 6, rect.centery - 6), 5)
            pygame.draw.circle(screen, (30,30,50), (rect.centerx - 5, rect.centery - 6), 2)
            pygame.draw.circle(screen, (30,30,50), (rect.centerx + 7, rect.centery - 6), 2)
            if i == color_idx:
                pygame.draw.rect(screen, C_WHITE, rect, 3, border_radius=12)
                # Valge ääre = hetkel valitud värv
            ns = F_TINY.render(name, True, C_DIM if i != color_idx else C_TEXT)
            screen.blit(ns, (rect.centerx - ns.get_width()//2, sw_y + swatch_w + 6))
            if rect.collidepoint(mouse):
                pygame.draw.rect(screen, C_ACCENT, rect, 2, border_radius=12)
                # Roheline ääre = hover (hiir peal)

        vol_lbl = F_MED.render(f"Heli tugevus: {int(slider.value * 100)}%", True, C_TEXT)
        screen.blit(vol_lbl, (WIN_W//2 - vol_lbl.get_width()//2, slider.rect.top - 38))
        slider.draw(screen)
        btn_back.draw(screen, F_MED)
        pygame.display.flip(); clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return color_idx
            if btn_back.clicked(event):
                play(SND_CLICK); return color_idx
            slider.handle_event(event)
            VOLUME = slider.value   # uuenda globaalset helitugevust liuguri järgi
            set_music_volume(VOLUME)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i in range(n_col):
                    sx   = sw_x0 + i * (swatch_w + 12)
                    rect = pygame.Rect(sx, sw_y, swatch_w, swatch_w)
                    if rect.collidepoint(event.pos):
                        color_idx = i; play(SND_CLICK)


def game_over_screen(surf, game, highscore, new_record):
    """
    "Mäng läbi" ekraan.
    Enne ekraani näitamist vilgub punane kile 4 korda (surma-animatsioon).
    Tagastab "RESTART" või "MENU" vastavalt kasutaja valikule.
    new_record = kas see oli uus rekord?
    """
    # Surmanimatsion: punase kile läbipaistvus kahaneb
    for a in (160, 100, 50, 15):
        game.draw(surf, False, highscore)
        ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        ov.fill((200, 0, 0, a))
        surf.blit(ov, (0, 0))
        pygame.display.flip(); pygame.time.wait(65)   # oota 65ms enne järgmist kaadrit

    game.draw(surf, False, highscore)
    lines = [("MÄNG LÄBI", 0, C_RED_UI), (f"Skoor:  {game.score}", 1, C_TEXT)]
    if new_record:
        lines.append(("** UUS REKORD! **", 1, C_GOLD_UI))
    else:
        lines.append((f"Rekord: {highscore}", 1, C_GOLD_UI))
    lines += [("", 2, C_DIM), ("[R]  Proovi uuesti", 2, C_ACCENT), ("[M]  Peamenüü", 2, C_DIM)]

    btn_r = Button(WIN_W//2 - 85, WIN_H - 55, 155, 42, "Proovi uuesti",
                   text_color=C_ACCENT, color=lerp_color(C_BTN_BG, C_ACCENT, 0.1))
    btn_m = Button(WIN_W//2 + 85, WIN_H - 55, 140, 42, "Peamenüü")
    while True:
        mouse = pygame.mouse.get_pos()
        btn_r.update(mouse); btn_m.update(mouse)
        game.draw(surf, False, highscore)
        draw_overlay(surf, lines)
        btn_r.draw(surf, F_SMALL); btn_m.draw(surf, F_SMALL)
        pygame.display.flip(); clock.tick(30)   # 30 FPS piisab staatilisel ekraanil
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    play(SND_CLICK); return "RESTART"
                if event.key == pygame.K_m:
                    play(SND_CLICK); return "MENU"
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
            if btn_r.clicked(event):
                play(SND_CLICK); return "RESTART"
            if btn_m.clicked(event):
                play(SND_CLICK); return "MENU"


def pause_screen(surf, game, highscore):
    """
    Pausiekraan. Mäng on peatatud kuni kasutaja valib.
    Tagastab "RESUME" (jätka) või "MENU" (peamenüüsse).
    """
    btn_resume = Button(WIN_W//2, WIN_H//2 + 10, 180, 48, "Jätka",
                        color=lerp_color(C_BTN_BG, C_ACCENT, 0.15), text_color=C_ACCENT)
    btn_menu   = Button(WIN_W//2, WIN_H//2 + 72, 180, 42, "Peamenüü")
    while True:
        mouse = pygame.mouse.get_pos()
        btn_resume.update(mouse); btn_menu.update(mouse)
        game.draw(surf, True, highscore)   # True = joonista "PAUS" HUD-i
        ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        ov.fill((5, 6, 18, 145)); surf.blit(ov, (0, 0))
        title = F_BIG.render("PAUS", True, C_GOLD_UI)
        surf.blit(title, (WIN_W//2 - title.get_width()//2, WIN_H//2 - 80))
        btn_resume.draw(surf, F_MED); btn_menu.draw(surf, F_SMALL)
        pygame.display.flip(); clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    return "RESUME"   # P või ESC = jätka mängu
                if event.key == pygame.K_m:
                    play(SND_CLICK); return "MENU"
            if btn_resume.clicked(event):
                play(SND_CLICK); return "RESUME"
            if btn_menu.clicked(event):
                play(SND_CLICK); return "MENU"


def levelup_screen(surf, game, highscore, next_lv):
    """
    Taseme tõusu ekraan.
    Näitab lühikest teatist 2.2 sekundit, siis jätkab automaatselt.
    Ei oota kasutaja sisendit - lihtsalt pygame.time.wait().
    """
    game.draw(surf, False, highscore)
    lines = [
        ("TASE ÜLES!", 0, C_GOLD_UI),
        (f"Järgmine: {next_lv['name']}", 1, C_ACCENT),
        ("Kiirus tõuseb", 2, C_TEXT),
    ]
    draw_overlay(surf, lines, alpha=150)
    play(SND_LEVELUP)
    pygame.display.flip()
    pygame.time.wait(2200)   # 2200 ms = 2.2 sekundit - siis jätkab automaatselt


# ══════════════════════════════════════════════════════════════════════════════
# PEAMINE MÄNGUTSÜKKEL
# ══════════════════════════════════════════════════════════════════════════════
# main() on programmi "juhataja" - korraldab kõik teised ekraanid ja tsüklid.
# Struktuur:
#   main()
#   └── while True (välismine tsükkel: menüü → mäng → menüü → ...)
#       ├── main_menu() → tagastab "start" või "quit"
#       └── while running (mängutsükkel)
#           ├── sündmuste lugemine
#           ├── game.step() → tagastab None/DEAD/LEVELUP/WON
#           └── game.draw() + display.flip()

def main():
    highscore = load_highscore()   # laeme rekordi failist
    color_idx = 0                  # vaikimisi roheline uss

    start_music()   # käivitame taustamuusika (kordab lõputult)

    while True:
        # Välismine tsükkel: peamenüü ja mäng vaheldumisi
        action, color_idx = main_menu(highscore, color_idx)
        if action == "quit":
            stop_music()
            pygame.quit(); sys.exit()

        # Alustame uue mängu esimesest tasemest
        level_idx = 0
        game      = Game(level_idx, score=0, color_idx=color_idx)

        running = True
        while running:
            # Sündmuste lugemine
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if game.score > highscore:
                        save_highscore(game.score)
                    stop_music()
                    pygame.quit(); sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if game.score > highscore:
                            save_highscore(game.score)
                        stop_music()
                        pygame.quit(); sys.exit()

                    if event.key == pygame.K_p:
                        res = pause_screen(screen, game, highscore)
                        if res == "MENU":
                            running = False; break
                        # Kui "RESUME", ei tee midagi - mäng jätkub
                    else:
                        game.handle_key(event.key)
                        # Kõik muu klahv läheb mängu (suunad)

            else:
                # "else" for-tsüklil = käivitatakse kui tsükkel lõppes ILMA break-ita
                # Ehk: kõik sündmused on töödeldud, pole vaja katkestada

                result = game.step()   # liiguta ussi üks samm edasi

                if result == "DEAD":
                    new_rec = game.score > highscore
                    if new_rec:
                        highscore = game.score
                        save_highscore(highscore)
                    action = game_over_screen(screen, game, highscore, new_rec)
                    if action == "RESTART":
                        # Uus mäng algusest
                        game = Game(0, score=0, color_idx=color_idx); level_idx = 0
                    else:
                        running = False   # "MENU" - väljume mängutsüklist

                elif result == "LEVELUP":
                    next_lv = LEVELS[game.level_idx + 1]
                    levelup_screen(screen, game, highscore, next_lv)
                    level_idx += 1
                    old_score = game.score
                    # Loome UUE Game objekti järgmise tasemega, aga kanname skoori üle!
                    game = Game(level_idx, score=old_score, color_idx=color_idx)

                elif result == "WON":
                    # Kõik tasemed läbitud - võit!
                    new_rec = game.score > highscore
                    if new_rec:
                        highscore = game.score
                        save_highscore(highscore)
                    game.draw(screen, False, highscore)
                    lines = [
                        ("SA OLED LEGEND!", 0, C_GOLD_UI),
                        (f"Lõplikud punktid: {game.score}", 1, C_ACCENT),
                        ("Kõik tasemed läbitud!", 1, C_GOLD_UI),
                        ("[R] Uuesti   [M] Menüü", 2, C_DIM),
                    ]
                    draw_overlay(screen, lines)
                    play(SND_LEVELUP)
                    pygame.display.flip()
                    # Ootame kasutaja sisendit (R = uuesti, M = menüü)
                    waiting = True
                    while waiting:
                        for ev in pygame.event.get():
                            if ev.type == pygame.QUIT:
                                stop_music(); pygame.quit(); sys.exit()
                            if ev.type == pygame.KEYDOWN:
                                if ev.key == pygame.K_r:
                                    game = Game(0, 0, color_idx); level_idx = 0; waiting = False
                                elif ev.key == pygame.K_m:
                                    running = False; waiting = False
                        clock.tick(30)

                # Joonistame kaadri (ainult kui mäng veel jookseb)
                if running:
                    game.draw(screen, False, highscore)
                    pygame.display.flip()
                    clock.tick(game.get_fps())
                    # game.get_fps() tagastab aeglustatud FPS-i kui "slow" efekt aktiivne
                continue
            break   # for-tsükli break jõudis siia - väljume ka while running tsüklist


# ══════════════════════════════════════════════════════════════════════════════
# PROGRAMMI KÄIVITAMINE
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # __name__ == "__main__" = True ainult kui see fail on OTSE käivitatud
    # Kui keegi importib selle faili teisest skriptist, main() ei käivitu automaatselt.
    # See on Pythoni hea tava - moodulid ei tohiks ennast automaatselt käivitada.
    main()