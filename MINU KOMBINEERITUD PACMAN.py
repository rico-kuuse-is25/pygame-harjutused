# =====================================================================
#  PAC-MAN  -  KOMBINEERITUD MÄNG
# =====================================================================
#  SUUR PILT (kuidas mäng töötab):
#   1) Labürint on kirjas tähtedena (ASCII_MAZE) - iga täht = üks ruut.
#   2) Klass Game on "peaaju": hoiab skoori, elusid, olekut ja juhib kõike.
#   3) Iga kaader (1/60 sekundit) tehakse 3 asja:
#         handle_input()  - loe klahvivajutused
#         update_frame()  - arvuta uus seis (liikumine, söömine, AI)
#         draw_frame()    - joonista pilt ekraanile
#   4) Pac-Man (klass Hero) ja kummitused (klass Ghost) liiguvad
#      RUUDUSTIKUL - pöörata saab ainult siis, kui ollakse täpselt ühe
#      ruudu peal. See annab "päris Pac-Mani" tunnetuse.
#
#  KOMBINEERIMINE (ülesande nõue - 3 mängu kokku):
#   BAAS:        Mäng 1 (janjilecek)      -> klasside struktuur (OOP)
#   KOMBINEERIB: Mäng 2 (DevinLeamy)      -> kummituste AI, heli, rekord,
#                                            puuvili, kombo-skoor, olekud
#                Mäng 3 (mattharootunian) -> vektorgraafika, vilkumine,
#                                            võidu/kaotuse ekraanid
#
#  5 OMAPOOLSET TÄIENDUST (otsitakse koodist märksõna "TÄIENDUS"):
#   1. Failivaba graafika + sünteesitud heli (ei vaja ühtegi pilti/heli)
#   2. Oma A* rajaleidja (ei vaja tcod teeki)
#   3. Tasemesüsteem (kiirus kasvab)
#   4. Hõljuvad skoori-numbrid (popupid)
#   5. Paus + tunnel (ümbermähkimine ekraani servas)
#
#  KÄIVITAMINE:  python pacman_kombineeritud.py
#  JUHTNUPUD:    nooled / WASD = liikumine,  P = paus,
#                TÜHIK = uuesti (kui mäng läbi),  ESC = välju
# =====================================================================

# --- "import" = võõra koodi (teegi) sissetoomine, et saaks seda kasutada ---
import os        # failiteed ja keskkonnamuutujad (rekordifaili asukoht)
import math      # matemaatika: sin/cos (Pac-Mani suu nurk, hõljumine)
import heapq     # "kuhi"-andmestruktuur - A* rajaleidja kasutab seda kiiruseks
import random    # juhuslikkus - hirmunud kummitused valivad suuna juhuslikult
from enum import Enum   # Enum = nimega valikute komplekt (nt suunad, olekud)

import pygame    # PÕHITEEK: aken, joonistamine, klahvid, heli. Vajab installi:
                 # pip install pygame   (selleta mäng ei käivitu)


# ---------------------------------------------------------------------
#  KONSTANDID  (suured tähed = väärtus, mida mängu jooksul ei muudeta)
# ---------------------------------------------------------------------
# TILE = ühe ruudu külje pikkus pikslites. Kogu mäng on ruudustikupõhine:
# labürint koosneb 24x24 piksli suurustest ruutudest.
# SIIN SAAD MUUTA: suurem number (nt 32) = suurem mäng, väiksem (nt 16) =
# väiksem. NB! Kiirus (allpool 2 või 3) peab TILE-i täisarvuga jagama,
# muidu ei satu tegelane enam täpselt ruutude peale ja liikumine "läheb viltu".
TILE = 24
FPS = 60         # frames per second - mitu kaadrit sekundis (mängu kiirus/sujuvus)

# Rekord salvestatakse sellesse faili, SAMASSE kausta, kus see .py fail asub.
# os.path.dirname(...) = "selle faili kaust"; nii leitakse fail alati üles,
# olenemata sellest, kust mäng käivitatakse.
HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "highscore.txt")

# VÄRVID. Iga värv on kolm arvu (Red, Green, Blue), igaüks 0..255.
# Nt (255, 0, 0) = puhas punane. SIIN SAAD MUUTA kõigi asjade värve.
C_BLACK = (0, 0, 0)             # taust
C_WALL = (33, 33, 222)          # seina täidis (sinine)
C_WALL_EDGE = (90, 90, 255)     # seina heledam äär
C_DOOR = (255, 184, 222)        # kummituste maja uks (roosa)
C_PELLET = (255, 200, 170)      # tavaline kook (väike täpp)
C_POWER = (255, 240, 200)       # power-pellet (suur vilkuv täpp)
C_PAC = (255, 224, 0)           # Pac-Man (kollane)
C_TEXT = (255, 255, 255)        # tekst (valge)
C_FRIGHT = (36, 36, 210)        # hirmunud kummitus (sinine)
C_FRIGHT_FLASH = (235, 235, 235)# hirmuaja lõpus vilkuv valge
C_EYE = (255, 255, 255)         # silmavalge
C_PUPIL = (40, 40, 160)         # silmatera
C_FRUIT = (230, 40, 40)         # puuvili (kirss)
C_FRUIT_STEM = (60, 160, 40)    # puuvilja vars

# Nelja kummituse värvid. "Sõnastik" (dict): võti -> väärtus.
# Nt GHOST_COLORS["red"] annab tagasi (222, 0, 0).
GHOST_COLORS = {
    "red": (222, 0, 0),
    "pink": (255, 150, 200),
    "cyan": (0, 220, 222),
    "orange": (255, 170, 40),
}


# ---------------------------------------------------------------------
#  ENUMID  (nimega valikute komplektid - loetavam kui "maagilised arvud")
# ---------------------------------------------------------------------
class Direction(Enum):
    """Liikumissuund. Iga suund hoiab korraga 3 asja:
       (dx, dy) = mitu sammu liikuda x- ja y-teljel,
       angle    = mis nurga all joonistada Pac-Mani suu (kraadides).
       NB! Ekraanil y kasvab ALLA, seega UP on dy = -1 (ülespoole = väiksem y)."""
    UP = (0, -1, 90)
    DOWN = (0, 1, 270)
    LEFT = (-1, 0, 180)
    RIGHT = (1, 0, 0)
    NONE = (0, 0, 0)        # paigalseis (ei liigu kuhugi)

    # @property teeb meetodist "näiliku muutuja": kirjutad dir.dx, mitte dir.dx().
    @property
    def dx(self):
        return self.value[0]    # value on see kolmik ülal; [0] = esimene arv

    @property
    def dy(self):
        return self.value[1]

    @property
    def angle(self):
        return self.value[2]


# Vastassuund. Kummitused EI tohi tavaolekus järsku tagasi pöörata
# (see on päris Pac-Mani reegel). REVERSE[UP] annab DOWN jne.
REVERSE = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
    Direction.NONE: Direction.NONE,
}


class ScoreType(Enum):
    """Mitu punkti iga asi annab. SIIN SAAD MUUTA punktiväärtusi."""
    COOKIE = 10        # tavaline kook
    POWERUP = 50       # suur power-pellet
    FRUIT = 100        # puuvili (korrutatakse hiljem tasemega)


class GhostMode(Enum):
    """KÕIGI kummituste ÜHINE režiim (mängu tasandil)."""
    CHASE = 1          # jälitavad Pac-Mani (igaüks oma "isiksuse" järgi)
    SCATTER = 2        # hajuvad oma nurka (annavad mängijale hingetõmbeaja)
    FRIGHTENED = 3     # hirmunud, põgenevad ja on söödavad (power-pelleti järel)


class GhostState(Enum):
    """ÜHE kummituse ENDA olek (iga kummitus on eraldi olekus)."""
    HOUSE = 1          # ootab kummituste majas (hõljub üles-alla)
    LEAVING = 2        # väljub majast (liigub A*-iga ukse poole)
    NORMAL = 3         # on labürindis ja kasutab AI-d
    EATEN = 4          # söödud -> ainult silmad jooksevad majja tagasi


class GameState(Enum):
    """Kogu mängu üldine seis (mis "ekraanil" parasjagu toimub)."""
    READY = 1          # "VALMIS!" - lühike paus enne algust
    PLAYING = 2        # päris mängimine käib
    PAUSED = 3         # paus (P-klahv)
    DYING = 4          # Pac-Man suri, lühike paus
    GAMEOVER = 5       # elud otsas
    WIN = 6            # tase läbi (kõik koogid söödud)


# ---------------------------------------------------------------------
#  MÄNGULAUD  (klassikaline 28x31 ruudu suurune paigutus)
# ---------------------------------------------------------------------
# Labürint on lihtsalt nimekiri tekstiridadest. Iga TÄHT = üks ruut.
# Tähtede tähendused:
#   #  = sein
#   .  = kook (väike punkt, mida süüakse)
#   O  = power-pellet (suur punkt, teeb kummitused söödavaks)
#   P  = Pac-Mani alguskoht
#   ' '= tühi tee (läbitav, aga kooki pole)
#   =  = kummituste maja uks (sealt pääsevad ainult kummitused)
#   g  = kummituste maja sisemus
#   G  = kummituse alguskoht (maja sees)
# SIIN SAAD MUUTA kogu labürinti! Aga ETTEVAATUST: iga rida peab olema
# sama pikk ja kõik koogid peavad olema Pac-Manile kättesaadavad (muidu
# ei saa taset kunagi läbi). Automaattest (run_tests.py) kontrollibki seda.
ASCII_MAZE = [
    "############################",  # 0
    "#............##............#",  # 1
    "#.####.#####.##.#####.####.#",  # 2
    "#O####.#####.##.#####.####O#",  # 3   (O = power-pellet ülanurkades)
    "#.####.#####.##.#####.####.#",  # 4
    "#..........................#",  # 5
    "#.####.##.########.##.####.#",  # 6
    "#.####.##.########.##.####.#",  # 7
    "#......##....##....##......#",  # 8
    "######.#####.##.#####.######",  # 9
    "######.#####.##.#####.######",  # 10
    "######.##..........##.######",  # 11
    "######.##.###==###.##.######",  # 12  (== = maja uks)
    "######.##.#gggggg#.##.######",  # 13  (g = maja sisemus)
    "          #gGGGGg#          ",  # 14  <- TUNNELIRIDA + 4x G (kummituste start)
    "######.##.#gggggg#.##.######",  # 15
    "######.##.########.##.######",  # 16
    "######.##..........##.######",  # 17
    "######.##.########.##.######",  # 18
    "######.##.########.##.######",  # 19
    "#............##............#",  # 20
    "#.####.#####.##.#####.####.#",  # 21
    "#O..##................##..O#",  # 22  (O = power-pellet alanurkades)
    "###.##.##.########.##.##.###",  # 23
    "###.##.##.########.##.##.###",  # 24
    "#......##....##....##......#",  # 25
    "#.##########.##.##########.#",  # 26
    "#.##########.##.##########.#",  # 27
    "#............P#............#",  # 28  (P = Pac-Mani start)
    "#..........................#",  # 29
    "############################",  # 30
]
# Turvalisus: teeme kindlaks, et KÕIK read on sama pikad (täidame puuduva
# seinaga "#"). Kui mõni rida oleks lühem, võiks programm hiljem vea anda.
_MAZE_W = max(len(r) for r in ASCII_MAZE)            # leia pikima rea pikkus
ASCII_MAZE = [r.ljust(_MAZE_W, "#") for r in ASCII_MAZE]  # täida kõik sama pikaks
ROWS = len(ASCII_MAZE)       # ridade arv (31)
COLS = _MAZE_W               # veergude arv (28)
TUNNEL_ROW = 14              # see rida ühendab vasaku ja parema serva (tunnel)

# Kummituste maja võtmekohad (col = veerg, row = rida).
HOUSE_EXIT = (13, 11)        # ruut KOHE ukse kohal (siit saavad kummitused välja)
HOUSE_CENTER = (13, 14)      # ruut maja sees (söödud silmad jooksevad siia)

# "Hulgad" (set): kiire viis küsida "kas see täht kuulub siia komplekti?".
PATH_CHARS = set(".OP ")     # need ruudud on läbitavad Pac-Manile ja tavakummitusele
GHOST_CHARS = set(".OP =gG") # need on läbitavad kummitusele (sh maja ja uks)


# ---------------------------------------------------------------------
#  TÄIENDUS 2:  OMA A* RAJALEIDJA
# ---------------------------------------------------------------------
class Pathfinder:
    """A* on algoritm, mis leiab LÜHIMA tee ühest ruudust teise, vältides
       seinu. Kasutame seda ainult kummituste maja jaoks: majast välja ja
       (söödud silmade) majja tagasi. Tavaline labürindi-jälitamine ei kasuta
       A*-i, vaid lihtsamat "ahnet" valikut (vt Ghost._greedy_dir).

       grid[row][col] == True tähendab: see ruut on läbitav."""

    def __init__(self, grid):
        # __init__ on "ehitaja" - käivitub, kui luuakse uus Pathfinder.
        # self = "see konkreetne objekt". self.grid jätab ruudustiku meelde.
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

    def _walkable(self, r, c):
        # Kas ruut (r, c) on olemas ja läbitav? Allkriips _ ees tähendab
        # "abimeetod, mõeldud ainult klassi sees kasutamiseks".
        return 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c]

    def get_path(self, start, goal):
        """Tagastab tee nimekirjana [(row,col), (row,col), ...] algusest sihini.
           Kui teed pole, tagastab ainult alguse."""
        if start == goal:
            return [start]

        # h() = "heuristika": hinnang, kui kaugel on kaks ruutu (Manhattani
        # kaugus = sammud x-teljel + sammud y-teljel). A* kasutab seda, et
        # eelistada ruute, mis tunduvad sihile lähemal.
        def h(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        # open_heap = "kuhi", kust tõmbame alati kõige lootustandvama ruudu.
        open_heap = [(h(start, goal), 0, start)]
        came = {}                      # came[ruut] = kust me sinna tulime
        gscore = {start: 0}            # gscore[ruut] = mitu sammu alguseni
        while open_heap:
            _, gc, cur = heapq.heappop(open_heap)   # võta parima hinnanguga ruut
            if cur == goal:
                # Jõudsime sihini -> kerime "came" abil tee tagasi kokku.
                path = [cur]
                while cur in came:
                    cur = came[cur]
                    path.append(cur)
                path.reverse()         # tee oli tagurpidi -> pööra õigetpidi
                return path
            r, c = cur
            # vaata 4 naabrit: üles, vasak, alla, parem
            for dr, dc in ((-1, 0), (0, -1), (1, 0), (0, 1)):
                nr, nc = r + dr, c + dc
                if not self._walkable(nr, nc):
                    continue           # sein või väljas -> jäta vahele
                ng = gc + 1            # naabrini on 1 samm rohkem
                # kui leidsime naabrini lühema tee, jäta see meelde
                if ng < gscore.get((nr, nc), 10 ** 9):
                    gscore[(nr, nc)] = ng
                    came[(nr, nc)] = cur
                    heapq.heappush(open_heap,
                                   (ng + h((nr, nc), goal), ng, (nr, nc)))
        return [start]                 # teed ei leitud


def dir_from_delta(dc, dr):
    """Abifunktsioon: ruutude vahe (dc, dr) -> Direction.
       Nt kui järgmine ruut on paremal (dc=1), tagasta Direction.RIGHT."""
    if dc > 0:
        return Direction.RIGHT
    if dc < 0:
        return Direction.LEFT
    if dr > 0:
        return Direction.DOWN
    if dr < 0:
        return Direction.UP
    return Direction.NONE


# ---------------------------------------------------------------------
#  MÄNGUOBJEKTID  (Mäng 1 OOP-hierarhia: ühised asjad ühte kohta)
# ---------------------------------------------------------------------
# OOP idee: paneme ühised omadused "vanemklassi" ja erilised asjad
# "lapsklassidesse". GameObject on kõige üldisem (kõigil on asukoht ja suurus).
class GameObject:
    def __init__(self, game, x, y, size):
        self.game = game     # viide peamängule (et pääseda ligi seintele jne)
        self.x = x           # asukoht pikslites (vasak ülanurk), x = vasak-parem
        self.y = y           # y = üles-alla
        self.size = size     # objekti külje pikkus pikslites

    def get_shape(self):
        # Tagastab ristküliku (Rect) kokkupõrgete kontrollimiseks.
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def get_position(self):
        return (self.x, self.y)

    def tile(self):
        """Mis ruudu peal objekt PARASJAGU on (col, row).
           round() ümardab lähima ruudu keskmeni."""
        return (int(round(self.x / TILE)), int(round(self.y / TILE)))

    def aligned(self):
        """Kas objekt on TÄPSELT mõne ruudu peal? Ainult siis tohib pöörata.
           % on jäägitehe: x % TILE == 0 tähendab "x jagub TILE-iga täpselt"."""
        return self.x % TILE == 0 and self.y % TILE == 0

    def tick(self):
        # "tick" = üks samm/kaader. Vanemklassis tühi; lapsklassid täidavad.
        pass

    def draw(self, screen):
        pass


class MovableObject(GameObject):
    """Liikuv objekt = GameObject + kiirus + suund. Pac-Man ja kummitused
       pärivad sellest. Sulgudes (GameObject) tähendab "pärib GameObjectist"."""

    def __init__(self, game, x, y, size, speed):
        super().__init__(game, x, y, size)    # käivita ka vanema __init__
        self.speed = speed                    # mitu pikslit kaadris liigub
        self.current_direction = Direction.NONE

    def _wrap(self):
        """TÄIENDUS 5: tunnel. Kui objekt läheb vasakust servast välja,
           ilmub paremale (ja vastupidi). Klassikaline Pac-Mani trikk."""
        if self.x <= -TILE:
            self.x = (COLS - 1) * TILE
        elif self.x >= COLS * TILE:
            self.x = 0


class Hero(MovableObject):
    """Pac-Man. KÕIGE TÄHTSAM uuendus: liikumine on RUUDUSTIKULE LUKUS.
       See tähendab, et pöörde- ja söömisotsuseid teeme AINULT siis, kui
       Pac on täpselt ühe ruudu peal (aligned). Ruutude vahel liigub ta
       ainult ühel teljel. Nii ei saa "vabalt libiseda" - tunnetus on
       nagu päris Pac-Mani mängus."""

    def __init__(self, game, col, row, speed):
        # col*TILE teisendab ruudu-koordinaadi piksliteks.
        super().__init__(game, col * TILE, row * TILE, TILE, speed)
        self.spawn = (col * TILE, row * TILE)   # alguskoht (surma järel naaseb siia)
        self.want = Direction.NONE              # suund, mida mängija SOOVIB minna
        self.mouth = 0.0                        # suu avanemise/sulgumise faas (0..1)

    def reset(self):
        # Pane Pac algusesse tagasi (kasutatakse pärast surma).
        self.x, self.y = self.spawn
        self.current_direction = Direction.NONE
        self.want = Direction.NONE

    def tick(self):
        # Kõik OTSUSED tehakse ainult ruudustiku peal (see ongi grid-lukk).
        if self.aligned():
            col, row = self.tile()
            # 1) Kui mängija soovsuund on vaba (pole sein), pööra sinna.
            #    "want" puhver tähendab: võid klahvi vajutada veidi varem ja
            #    pööre toimub kohe, kui ristmik tuleb.
            if self.want != Direction.NONE and \
                    self.game.pac_can(col + self.want.dx, row + self.want.dy):
                self.current_direction = self.want
            # 2) Kui PRAEGUSE suuna ees on sein, jää seisma (ära jookse seina).
            if self.current_direction != Direction.NONE and \
                    not self.game.pac_can(col + self.current_direction.dx,
                                          row + self.current_direction.dy):
                self.current_direction = Direction.NONE
            # 3) Söö see, mis sellel ruudul on (kook / power / puuvili).
            self.game.handle_eating(col, row)

        # Liigu valitud suunas: x ja y muutuvad suuna * kiiruse võrra.
        self.x += self.current_direction.dx * self.speed
        self.y += self.current_direction.dy * self.speed
        self._wrap()                            # tunneli kontroll

        # Suu animatsioon: mouth käib 0 -> 1 -> 0 ringi, ainult liikudes.
        if self.current_direction != Direction.NONE:
            self.mouth = (self.mouth + 0.18) % 1.0

    def draw(self, screen):
        # Joonista Pac-Man: kollane ring + must "suu" lõik liikumissuunas.
        cx = int(self.x + self.size / 2)        # ringi keskpunkt x
        cy = int(self.y + self.size / 2)        # ringi keskpunkt y
        r = self.size // 2 - 1                  # raadius
        ang = self.current_direction.angle \
            if self.current_direction != Direction.NONE else 0
        # half = suu poolnurk (0..40 kraadi). sin teeb selle pidevalt
        # avanevaks-sulguvaks -> "näts-näts" efekt.
        half = abs(math.sin(self.mouth * math.pi)) * 40
        pygame.draw.circle(screen, C_PAC, (cx, cy), r)   # kollane ring
        if half > 2:
            # PARANDUS (kasutaja tagasiside "kollane laik"): varem joonistati
            # suu KOLMNURGana, mille tõttu ringi kumer serv jäi kolmnurgast
            # välja ja tekkisid kollased laigud. Nüüd joonistame suu korraliku
            # "pirukalõiguna" - hulknurk, mille servapunktid järgivad ringi
            # kaart (12 väikest sammu). Nii katab must ala kogu suuava.
            pts = [(cx, cy)]                    # alusta keskpunktist
            steps = 12
            a_start = ang - half
            a_end = ang + half
            for i in range(steps + 1):
                a = math.radians(a_start + (a_end - a_start) * i / steps)
                # NB! cy - sin, sest ekraanil y kasvab alla.
                pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
            pygame.draw.polygon(screen, C_BLACK, pts)   # must suu


class Ghost(MovableObject):
    """Kummitus. Kasutab AUTENTSET Pac-Mani AI-d (nagu Mäng 2 / originaal).
       Iga kummitus on alati ühes neljast olekust (GhostState):
         HOUSE   - ootab majas
         LEAVING - väljub majast (A*-iga)
         NORMAL  - on labürindis ja jälitab oma "isiksuse" järgi
         EATEN   - söödud, ainult silmad jooksevad majja tagasi (A*-iga)."""

    def __init__(self, game, col, row, speed, kind, corner, release_frame):
        super().__init__(game, col * TILE, row * TILE, TILE, speed)
        self.spawn = (col * TILE, row * TILE)
        self.kind = kind                  # "red"/"pink"/"cyan"/"orange"
        self.color = GHOST_COLORS[kind]   # selle kummituse värv
        self.corner = corner              # SCATTER-režiimi sihtnurk
        self.release_frame = release_frame  # mitu kaadrit ootab, enne kui väljub
        self.reset(full=True)

    def reset(self, full=False):
        # Pane kummitus algusesse. Punane väljub kohe, ülejäänud ootavad majas.
        self.x, self.y = self.spawn
        self.current_direction = Direction.UP
        self.state = GhostState.LEAVING if self.kind == "red" else GhostState.HOUSE
        self.house_t = 0                  # loendur, kui kaua majas oodatud

    # ---- SIHTRUUT isiksuse järgi (see ongi "AI süda") -------------------
    def target_tile(self):
        """Iga kummitus tahab jõuda oma SIHTRUUDU poole. Sihtruut sõltub
           režiimist ja kummituse "isiksusest". Need on PÄRIS Pac-Mani reeglid."""
        mode = self.game.ghost_mode
        if mode == GhostMode.SCATTER:
            return self.corner            # SCATTER: mine oma nurka
        # CHASE: jälita, aga igaüks erinevalt:
        pac = self.game.hero
        pt = pac.tile()                   # Pac-Mani praegune ruut
        pdx, pdy = pac.current_direction.dx, pac.current_direction.dy
        if self.kind == "red":            # Blinky: otse Pac-Mani peale (agressiivne)
            return pt
        if self.kind == "pink":           # Pinky: 4 ruutu Pac-Mani ETTE (varitseb)
            return (pt[0] + pdx * 4, pt[1] + pdy * 4)
        if self.kind == "cyan":           # Inky: keeruline - peegeldab punase kaudu
            ahead = (pt[0] + pdx * 2, pt[1] + pdy * 2)
            red = self.game.blinky_tile()
            return (2 * ahead[0] - red[0], 2 * ahead[1] - red[1])
        if self.kind == "orange":         # Clyde: kaugel -> jälitab; lähedal -> põgeneb
            mt = self.tile()
            d = abs(mt[0] - pt[0]) + abs(mt[1] - pt[1])
            return pt if d > 8 else self.corner
        return pt

    # ---- AHNE suunavalik ristmikul (NORMAL-olekus) ----------------------
    def _greedy_dir(self, col, row, target, frightened):
        """Ristmikul valib kummitus selle suuna, mis viib SIHTRUUDULE kõige
           lähemale - aga EI tohi tagasi pöörata. See lihtne reegel annab just
           selle klassikalise kummituste käitumise. Hirmununa valib juhuslikult."""
        rev = REVERSE[self.current_direction]   # keelatud (tagasi) suund
        cand = []
        # Proovi suundi kindlas järjekorras (viigi korral: üles, vasak, alla, parem).
        for d in (Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT):
            if d == rev:
                continue                  # ära pööra tagasi
            if self.game.ghost_can(col + d.dx, row + d.dy):
                cand.append((d, col + d.dx, row + d.dy))   # see suund on vaba
        if not cand:                      # ummiktee -> ainsana luba tagasipööre
            return rev
        if frightened:                    # hirmununa: juhuslik vaba suund
            return random.choice(cand)[0]
        # Muidu: vali suund, mille järgmine ruut on sihile lähim.
        # Kaugust mõõdame ruudu vahega ruudus (võrdluseks pole vaja juurt võtta).
        best, best_val = cand[0][0], None
        for d, nc, nr in cand:
            val = (nc - target[0]) ** 2 + (nr - target[1]) ** 2
            if best_val is None or val < best_val:
                best_val = val
                best = d
        return best

    # ---- A* samm (kasutame maja sisse/välja, kus tee on kitsas) ---------
    def _astar_dir(self, start, goal):
        """Küsi A*-lt tee ja võta ESIMENE samm selle suunas."""
        path = self.game.pathfinder.get_path((start[1], start[0]),
                                             (goal[1], goal[0]))
        if len(path) >= 2:
            nr, nc = path[1]              # path[0] on praegune ruut, [1] järgmine
            return dir_from_delta(nc - start[0], nr - start[1])
        return self.current_direction

    def _bob(self):
        """HOUSE-olek: kummitus hõljub majas üles-alla, kuni vabastusaeg käes."""
        self.house_t += 1
        # sin annab pehme üles-alla õõtsumise (+/- 4 pikslit).
        self.y = self.spawn[1] + int(4 * math.sin(self.house_t * 0.12))
        # Kui mäng käib JA piisavalt kaua oodatud -> hakka väljuma.
        if self.game.state == GameState.PLAYING and self.house_t >= self.release_frame:
            self.x, self.y = self.spawn          # joonda täpselt ruudule tagasi
            self.state = GhostState.LEAVING
            self.current_direction = Direction.UP

    def tick(self):
        # Käitumine sõltub olekust. Iga "if state == ..." on üks olek.
        if self.state == GhostState.HOUSE:
            self._bob()
            return

        if self.state == GhostState.LEAVING:
            # Liigu A*-iga ukse kohale; kui jõudsid, mine NORMAL-olekusse.
            if self.aligned():
                t = self.tile()
                if t == HOUSE_EXIT:
                    self.state = GhostState.NORMAL
                    self.current_direction = Direction.LEFT
                else:
                    self.current_direction = self._astar_dir(t, HOUSE_EXIT)
            self.x += self.current_direction.dx * self.speed
            self.y += self.current_direction.dy * self.speed
            return

        if self.state == GhostState.EATEN:
            # Silmad jooksevad A*-iga maja keskele; siis hakkavad uuesti väljuma.
            if self.aligned():
                t = self.tile()
                if t == HOUSE_CENTER:
                    self.state = GhostState.LEAVING
                    self.current_direction = Direction.UP
                else:
                    self.current_direction = self._astar_dir(t, HOUSE_CENTER)
            self.x += self.current_direction.dx * self.speed
            self.y += self.current_direction.dy * self.speed
            return

        # NORMAL: päris labürindis. Suunaotsus AINULT ruudustiku peal (grid-lukk).
        if self.aligned():
            col, row = self.tile()
            fr = (self.game.ghost_mode == GhostMode.FRIGHTENED)
            self.current_direction = self._greedy_dir(col, row,
                                                      self.target_tile(), fr)
        self.x += self.current_direction.dx * self.speed
        self.y += self.current_direction.dy * self.speed
        self._wrap()                     # NORMAL-kummitus saab samuti tunnelit kasutada

    def draw(self, screen):
        cx = int(self.x + self.size / 2)
        cy = int(self.y + self.size / 2)
        r = self.size // 2 - 1
        # kas see kummitus on PARASJAGU hirmunud (söödav)?
        fright = (self.game.ghost_mode == GhostMode.FRIGHTENED
                  and self.state == GhostState.NORMAL)

        if self.state != GhostState.EATEN:
            # EATEN-olekus joonistame AINULT silmad (keha pole - on "söödud").
            if fright:
                # Hirmuaja lõpus vilgub valgeks - hoiatab, et aeg saab otsa.
                flash = (self.game.fright_timer < 120
                         and (self.game.fright_timer // 15) % 2 == 0)
                body = C_FRIGHT_FLASH if flash else C_FRIGHT
            else:
                body = self.color
            # Keha = kuppel (ring) + ristkülik all + sakiline allserv.
            pygame.draw.circle(screen, body, (cx, cy), r)
            pygame.draw.rect(screen, body, (cx - r, cy, 2 * r, r))
            step = (2 * r) / 3.0
            pts = [(cx - r, cy + r)]
            for i in range(4):           # tee 3 "saki" alumisse serva
                px = cx - r + i * step
                py = cy + r if i % 2 == 0 else cy + r - 6
                pts.append((px, py))
            pts.append((cx + r, cy + r))
            pygame.draw.polygon(screen, body, pts)

        # Silmad. Hirmunud kummitusel jätame silmad joonistamata (lihtne nägu).
        if fright and self.state != GhostState.EATEN:
            return
        ex = self.current_direction.dx   # silmatera nihkub liikumissuunas
        ey = self.current_direction.dy
        for sx in (-r // 3, r // 3):     # vasak ja parem silm
            pygame.draw.circle(screen, C_EYE, (cx + sx, cy - r // 3), max(2, r // 4))
            pygame.draw.circle(screen, C_PUPIL,
                               (int(cx + sx + ex * 2), int(cy - r // 3 + ey * 2)),
                               max(1, r // 8))


class Fruit(GameObject):
    """Boonuspuuvili (Mäng 2/3). Joonistatakse kahe kirsina (vektorgraafika)."""

    def __init__(self, game, col, row):
        super().__init__(game, col * TILE, row * TILE, TILE)
        self.tile_pos = (col, row)       # mis ruudul puuvili on (söömise kontroll)

    def draw(self, screen):
        cx = int(self.x + self.size / 2)
        cy = int(self.y + self.size / 2)
        pygame.draw.circle(screen, C_FRUIT, (cx - 4, cy + 4), 5)    # vasak kirss
        pygame.draw.circle(screen, C_FRUIT, (cx + 4, cy + 4), 5)    # parem kirss
        pygame.draw.line(screen, C_FRUIT_STEM, (cx - 4, cy + 1), (cx + 2, cy - 6), 2)
        pygame.draw.line(screen, C_FRUIT_STEM, (cx + 4, cy + 1), (cx + 2, cy - 6), 2)


class Wall(GameObject):
    """Sein. TÄIENDUS 1: joonistatakse pygame primitiividega (ristkülik),
       MITTE pildifailist. Nii ei vaja mäng ühtegi välist faili."""

    def __init__(self, game, col, row):
        super().__init__(game, col * TILE, row * TILE, TILE)

    def draw(self, screen):
        rect = pygame.Rect(self.x + 2, self.y + 2, TILE - 4, TILE - 4)
        pygame.draw.rect(screen, C_WALL, rect, border_radius=6)        # täidis
        pygame.draw.rect(screen, C_WALL_EDGE, rect, width=2, border_radius=6)  # äär


# ---------------------------------------------------------------------
#  PÕHIKONTROLLER  -  klass Game on kogu mängu "peaaju"
# ---------------------------------------------------------------------
class Game:
    # MODE_PHASES = ajakava, millal kummitused vahetavad SCATTER <-> CHASE.
    # Iga paar on (režiim, mitu kaadrit). Nt (SCATTER, 7*FPS) = 7 sekundit
    # hajumist. Viimane CHASE kestab "lõputult" (10**9 = väga suur arv).
    # SIIN SAAD MUUTA mängu raskust/rütmi.
    MODE_PHASES = [(GhostMode.SCATTER, 7 * FPS),
                   (GhostMode.CHASE, 20 * FPS),
                   (GhostMode.SCATTER, 7 * FPS),
                   (GhostMode.CHASE, 20 * FPS),
                   (GhostMode.SCATTER, 5 * FPS),
                   (GhostMode.CHASE, 10 ** 9)]

    def __init__(self, headless=False):
        # headless=True tähendab "ilma ekraani/helita" - seda kasutavad
        # automaattestid (run_tests.py), et mängu loogikat kontrollida.
        # Tavaline mängija jätab selle vahele -> headless=False.
        self.headless = headless
        if headless:
            # ütle SDL-ile (pygame'i mootor), et ekraani/heli pole vaja
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        pygame.init()                    # käivita pygame
        pygame.font.init()               # käivita fondisüsteem (teksti jaoks)

        self.width = COLS * TILE         # akna laius pikslites
        self.height = ROWS * TILE + TILE # akna kõrgus (+1 rida skoori jaoks all)
        self.screen = pygame.display.set_mode((self.width, self.height))  # loo aken
        pygame.display.set_caption("Pac-Man - Kombineeritud")             # akna pealkiri
        self.clock = pygame.time.Clock() # kell, mis hoiab FPS-i ühtlasena
        self.font = pygame.font.SysFont("Arial", 20, bold=True)           # tavafont
        self.big_font = pygame.font.SysFont("Arial", 56, bold=True)       # suur font

        # Kaks läbitavus-ruudustikku (True = saab minna):
        #  open_grid - tavaline labürint (Pac ja NORMAL-kummitused)
        #  full_grid - sama + maja sisemus ja uks (A* navigatsioon)
        self.open_grid = [[ASCII_MAZE[r][c] in PATH_CHARS for c in range(COLS)]
                          for r in range(ROWS)]
        self.full_grid = [[ASCII_MAZE[r][c] in GHOST_CHARS for c in range(COLS)]
                          for r in range(ROWS)]
        self.pathfinder = Pathfinder(self.full_grid)   # A* töötab full_grid peal

        # Tühjad "nõud", mille _parse_maze() kohe täidab:
        self.walls = []                  # seinaobjektide nimekiri
        self.doors = []                  # ukseruudud (joonistamiseks)
        self.cookies = {}                # (col,row) -> True  (söömata koogid)
        self.powerups = {}               # (col,row) -> True  (söömata power-pelletid)
        self.ghost_spawns = []           # kummituste algusruudud
        self.pac_spawn = (13, 28)        # Pac-Mani algusruut (vaikimisi)
        self._parse_maze()               # loe labürint tähtedest objektideks

        # Üldine mänguseis:
        self.high_score = self._load_highscore()  # loe rekord failist
        self.score = 0
        self.lives = 3                   # SIIN SAAD MUUTA algusElude arvu
        self.level = 1
        self.popups = []                 # hõljuvad skoorinumbrid (TÄIENDUS 4)

        # Kummituste režiim ja loendurid:
        self.ghost_mode = GhostMode.SCATTER
        self.mode_timer = 0              # kui kaua praegune faas kestnud
        self.mode_index = 0              # mitmes faas MODE_PHASES nimekirjas
        self.fright_timer = 0            # hirmuaja loendur
        self.ghost_combo = 0             # mitu kummitust järjest söödud (200/400/...)

        # Puuvili:
        self.fruit = None                # None = puuvilja pole hetkel
        self.fruit_timer = 0
        self.cookies_eaten = 0           # mitu kooki söödud (puuvilja ilmumiseks)

        # Mängu olek:
        self.state = GameState.READY
        self.state_timer = 90            # "VALMIS!" kestab 90 kaadrit (~1.5 s)
        self.done = False                # True = sulge mäng
        self.chomp_toggle = 0            # vahetab waka-heli kahe tooni vahel

        # HELI (TÄIENDUS 1) - sünteesitakse jooksu ajal, faili pole vaja.
        self.audio = False
        self.sounds = {}
        if not headless:                 # testides heli vahele
            self._init_audio()

        self._spawn_entities()           # loo Pac-Man ja kummitused

    # ---- HELI SÜNTEES (numpy + pygame.sndarray) -----------------------
    def _init_audio(self):
        """Proovi heli sisse lülitada. Kogu asi on try/except sees: kui numpy
           puudub või helikaarti pole (nt õpetaja masin), siis lihtsalt
           self.audio = False ja mäng töötab VAIKSELT (ei kuku kokku)."""
        try:
            import numpy as np           # numpy aitab arvutada helilaineid
            pygame.mixer.init(22050, -16, 1, 256)   # ava helisüsteem
            self.np = np
            # Tekita 6 lühikest heli. _tone() arvutab laine ise (vt allpool).
            self.sounds = {
                "chomp1": self._tone(440, 45, 0.25, "square"),
                "chomp2": self._tone(330, 45, 0.25, "square"),
                "power": self._tone(660, 300, 0.3, "square", slide=-300),
                "eat_ghost": self._tone(300, 250, 0.3, "square", slide=500),
                "fruit": self._tone(880, 200, 0.3, "sine"),
                "death": self._tone(500, 700, 0.35, "sine", slide=-420),
            }
            self.audio = True
        except Exception:
            self.audio = False           # midagi ei õnnestunud -> vaikne mäng

    def _tone(self, freq, ms, vol=0.3, wave="square", slide=0):
        """Tekita üks heli matemaatiliselt.
           freq = kõrgus (Hz), ms = kestus (millisekundid), vol = valjus,
           wave = "square" (teravam) või "sine" (pehmem), slide = sageduse
           muutus (nt -300 = toon langeb). Tagastab pygame heli-objekti."""
        np = self.np
        sr = 22050                       # diskreetimissagedus (proovide arv sekundis)
        n = int(sr * ms / 1000)          # mitu proovi kokku
        t = np.linspace(0, ms / 1000.0, n, False)   # ajatelg
        f = freq + slide * (t / (ms / 1000.0))      # sagedus ajas (liug)
        phase = 2 * np.pi * np.cumsum(f) / sr        # laine faas
        w = np.sign(np.sin(phase)) if wave == "square" else np.sin(phase)
        # env = "ümbrik": heli tõuseb pehmelt ja vaibub (ei prõksu/klõpsa).
        env = np.minimum(1.0, np.minimum(t * 60, (ms / 1000.0 - t) * 60))
        arr = (w * env * vol * 32767).astype(np.int16)   # teisenda heliproovideks
        return pygame.sndarray.make_sound(np.ascontiguousarray(arr))

    def _play(self, name):
        # Mängi heli, KUI heli on sisse lülitatud. Muidu ära tee midagi.
        if self.audio and name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception:
                pass                     # heli ebaõnnestus -> ignoreeri vaikselt

    # ---- LABÜRINDI LUGEMINE -------------------------------------------
    def _parse_maze(self):
        """Käi labürint täht-haaval läbi ja tee tähtedest päris objektid/andmed."""
        for r in range(ROWS):
            for c in range(COLS):
                ch = ASCII_MAZE[r][c]
                if ch == "#":
                    self.walls.append(Wall(self, c, r))
                elif ch == "=":
                    self.doors.append((c, r))
                elif ch == "P":
                    self.pac_spawn = (c, r)
                elif ch == "G":
                    self.ghost_spawns.append((c, r))
                elif ch == "O":
                    self.powerups[(c, r)] = True
                elif ch == ".":
                    self.cookies[(c, r)] = True
        # mitu söödavat kokku (võib kasutada statistikaks)
        self.total_pellets = len(self.cookies) + len(self.powerups)

    def _spawn_entities(self):
        """Loo Pac-Man ja 4 kummitust. Kutsutakse mängu alguses ja iga taseme algul."""
        # TÄIENDUS 3: kiirus kasvab tasemega. NB! 2 ja 3 jagavad mõlemad
        # TILE=24 täpselt, seega grid-lukk püsib.
        self.speed = 2 if self.level < 3 else 3
        self.hero = Hero(self, self.pac_spawn[0], self.pac_spawn[1], self.speed)
        kinds = ["red", "pink", "cyan", "orange"]
        # SCATTER-nurgad (igale kummitusele oma): paremüla, vasaküla, jne.
        corners = [(COLS - 2, 1), (1, 1), (COLS - 2, ROWS - 2), (1, ROWS - 2)]
        # Vabastusaeg: punane kohe (0), siis 3s, 6s, 9s -> väljuvad JÄRJEST,
        # mitte korraga (nii ei lenda nad alguses kõik seina).
        releases = [0, 3 * FPS, 6 * FPS, 9 * FPS]
        slots = self.ghost_spawns[:4] if len(self.ghost_spawns) >= 4 else \
            [(12, 14), (13, 14), (14, 14), (15, 14)]
        self.ghosts = []
        for i in range(4):
            c, r = slots[i]
            self.ghosts.append(Ghost(self, c, r, self.speed,
                                     kinds[i], corners[i], releases[i]))

    def blinky_tile(self):
        # Leia punase (Blinky) kummituse ruut - Inky vajab seda oma sihi jaoks.
        for g in self.ghosts:
            if g.kind == "red":
                return g.tile()
        return self.hero.tile()

    # ---- LÄBITAVUS (kas ruudule tohib minna) - arvestab tunnelit -------
    def pac_can(self, col, row):
        # Tunnelireal lubame minna ekraanist välja (sealt mähitakse ümber).
        if row == TUNNEL_ROW and (col < 0 or col >= COLS):
            return True
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.open_grid[row][col]
        return False

    def ghost_can(self, col, row):
        # NORMAL-kummitus kasutab open_grid'i -> ei lähe tavaliikumisel majja
        # tagasi (maja pole open_grid'is). Majja saab ainult EATEN-olekus (A*).
        if row == TUNNEL_ROW and (col < 0 or col >= COLS):
            return True
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.open_grid[row][col]
        return False

    # ---- REKORD (salvesta/loe failist) --------------------------------
    def _load_highscore(self):
        # Proovi lugeda rekord failist. Kui faili pole/on vigane -> 0.
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip() or 0)
        except (OSError, ValueError):
            return 0

    def _save_highscore(self):
        try:
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(self.high_score))
        except OSError:
            pass                         # kui kirjutamine ebaõnnestub, ignoreeri

    # ---- SKOOR + POPUPID ----------------------------------------------
    def add_score(self, amount):
        self.score += amount
        if self.score > self.high_score: # uus rekord?
            self.high_score = self.score

    def add_popup(self, x, y, text):
        # TÄIENDUS 4: lisa hõljuv number. Nimekiri: [x, y, tekst, eluiga].
        self.popups.append([x, y, str(text), 45])

    # ---- SÖÖMINE (kutsutakse Pac-Mani tick()-ist) ---------------------
    def handle_eating(self, col, row):
        tile = (col, row)
        if tile in self.cookies:               # kook?
            del self.cookies[tile]             # eemalda söödud kook
            self.add_score(ScoreType.COOKIE.value)
            self.cookies_eaten += 1
            self.chomp_toggle ^= 1             # vaheta waka-tooni (0<->1)
            self._play("chomp1" if self.chomp_toggle else "chomp2")
            self._maybe_spawn_fruit()
        elif tile in self.powerups:            # power-pellet?
            del self.powerups[tile]
            self.add_score(ScoreType.POWERUP.value)
            self._activate_fright()            # tee kummitused hirmunuks
            self._play("power")
        if self.fruit and tile == self.fruit.tile_pos:   # puuvili?
            pts = ScoreType.FRUIT.value * self.level      # rohkem punkte kõrgemal tasemel
            self.add_score(pts)
            self.add_popup(self.fruit.x, self.fruit.y, pts)
            self.fruit = None
            self._play("fruit")
        if not self.cookies and not self.powerups:        # kõik söödud?
            self._win_level()                  # -> tase läbi

    def _maybe_spawn_fruit(self):
        # Puuvili ilmub, kui söödud on täpselt 60 või 140 kooki.
        # SIIN SAAD MUUTA, millal puuvili ilmub.
        if self.fruit is None and self.cookies_eaten in (60, 140):
            for cand in [(13, 17), (14, 17), (13, 11), (6, 14)]:   # proovi neid kohti
                c, r = cand
                if self.open_grid[r][c]:        # ainult läbitavale ruudule
                    self.fruit = Fruit(self, c, r)
                    self.fruit_timer = 9 * FPS  # puuvili püsib ~9 sekundit
                    break

    def _activate_fright(self):
        # Lülita hirmurežiim sisse.
        self.ghost_mode = GhostMode.FRIGHTENED
        # TÄIENDUS 3: kõrgemal tasemel kestab hirm lühemalt (raskem).
        self.fright_timer = max(150, 420 - (self.level - 1) * 40)
        self.ghost_combo = 0
        # Klassikaline reegel: hirmu alguses kummitused pööravad ümber.
        for g in self.ghosts:
            if g.state == GhostState.NORMAL:
                g.current_direction = REVERSE[g.current_direction]

    # ---- REŽIIMI VAHETUS (SCATTER <-> CHASE ajakava järgi) ------------
    def _update_mode(self):
        if self.ghost_mode == GhostMode.FRIGHTENED:
            self.fright_timer -= 1                  # loe hirmuaeg maha
            if self.fright_timer <= 0:
                # hirm läbi -> naase sellesse faasi, kus pooleli jäi
                self.ghost_mode = self.MODE_PHASES[self.mode_index][0]
            return
        self.mode_timer += 1
        if self.mode_timer >= self.MODE_PHASES[self.mode_index][1]:  # faas läbi?
            self.mode_timer = 0
            self.mode_index = min(self.mode_index + 1, len(self.MODE_PHASES) - 1)
            self.ghost_mode = self.MODE_PHASES[self.mode_index][0]

    # ---- KOKKUPÕRKED kummitustega -------------------------------------
    def _check_ghost_collisions(self):
        hero_rect = self.hero.get_shape()
        for g in self.ghosts:
            # majas/söödud kummitus ei tee midagi
            if g.state in (GhostState.HOUSE, GhostState.EATEN):
                continue
            if not hero_rect.colliderect(g.get_shape()):   # kas puutuvad kokku?
                continue
            if self.ghost_mode == GhostMode.FRIGHTENED and g.state == GhostState.NORMAL:
                # Pac sõi kummituse -> kombo-punktid (200, 400, 800, 1600...)
                self.ghost_combo += 1
                pts = 200 * (2 ** (self.ghost_combo - 1))
                self.add_score(pts)
                self.add_popup(g.x, g.y, pts)
                g.state = GhostState.EATEN          # kummitus muutub silmadeks
                self._play("eat_ghost")
            else:
                self._lose_life()                   # kummitus sõi Pac-Mani
                return

    # ---- ELU KAOTUS / VÕIT / TASEMED ----------------------------------
    def _lose_life(self):
        self.lives -= 1
        self.state = GameState.DYING
        self.state_timer = 75
        self._play("death")

    def _respawn_after_death(self):
        if self.lives <= 0:
            # elud otsas -> mäng läbi
            self.state = GameState.GAMEOVER
            self.state_timer = 1
            self._save_highscore()
        else:
            # veel elusid -> pane kõik algusesse tagasi
            self.hero.reset()
            for g in self.ghosts:
                g.reset()
            self.ghost_mode = GhostMode.SCATTER
            self.mode_index = 0
            self.mode_timer = 0
            self.fright_timer = 0
            self.fruit = None
            self.state = GameState.READY
            self.state_timer = 60

    def _win_level(self):
        self.state = GameState.WIN
        self.state_timer = 100
        self._save_highscore()

    def _reset_board(self):
        # Ehita laud uuesti üles (uus tase või restart). Abimeetod.
        self.cookies = {}
        self.powerups = {}
        self.walls = []
        self.doors = []
        self.cookies_eaten = 0
        self.fruit = None
        self._parse_maze()
        self.ghost_mode = GhostMode.SCATTER
        self.mode_index = 0
        self.mode_timer = 0
        self.fright_timer = 0
        self._spawn_entities()

    def _next_level(self):
        self.level += 1                  # tase kasvab (kiirus tõuseb _spawn_entities-is)
        self._reset_board()
        self.state = GameState.READY
        self.state_timer = 60

    def restart(self):
        # Alusta täiesti otsast (game over -> TÜHIK).
        self.score = 0
        self.lives = 3
        self.level = 1
        self._reset_board()
        self.state = GameState.READY
        self.state_timer = 90

    # ---- ÜHE KAADRI LOOGIKA  (ekraanivaba - seda saab automaatselt testida) ---
    def update_frame(self):
        # Loogika hargneb mängu oleku järgi. READY/PAUSED/DYING/WIN/GAMEOVER
        # ei mängi - ainult loendavad aega või ootavad. PLAYING teeb päris töö.
        if self.state == GameState.READY:
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.state = GameState.PLAYING
            return
        if self.state == GameState.PAUSED:
            return                       # pausis ei tehta midagi
        if self.state == GameState.DYING:
            self.state_timer -= 1
            if self.state_timer <= 0:
                self._respawn_after_death()
            return
        if self.state == GameState.WIN:
            self.state_timer -= 1
            if self.state_timer <= 0:
                self._next_level()
            return
        if self.state == GameState.GAMEOVER:
            return

        # --- PLAYING: päris mängusamm ---
        self._update_mode()              # uuenda SCATTER/CHASE/hirm
        self.hero.tick()                 # liiguta Pac-Mani
        for g in self.ghosts:            # liiguta kummitusi
            g.tick()
        self._check_ghost_collisions()   # kontrolli kokkupõrkeid

        # puuvili aegub
        if self.fruit:
            self.fruit_timer -= 1
            if self.fruit_timer <= 0:
                self.fruit = None

        # popupid hõljuvad ülespoole ja kaovad (eluiga p[3] kahaneb)
        for p in self.popups:
            p[1] -= 0.5                  # liiguta numbrit üles
            p[3] -= 1                    # vähenda eluiga
        self.popups = [p for p in self.popups if p[3] > 0]   # eemalda surnud

    # ---- SISEND (klahvivajutused) -------------------------------------
    def handle_input(self):
        for event in pygame.event.get():            # käi kõik sündmused läbi
            if event.type == pygame.QUIT:           # akna sulgemise rist
                self.done = True
            elif event.type == pygame.KEYDOWN:      # klahvi alla vajutamine
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.hero.want = Direction.UP   # ainult MÄRGIME soovi;
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.hero.want = Direction.DOWN # päris pööre toimub ruudul
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.hero.want = Direction.LEFT
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.hero.want = Direction.RIGHT
                elif event.key == pygame.K_p:       # TÄIENDUS 5: paus sisse/välja
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                elif event.key == pygame.K_SPACE:   # uuesti, kui mäng läbi
                    if self.state == GameState.GAMEOVER:
                        self.restart()
                elif event.key == pygame.K_ESCAPE:  # välju
                    self.done = True

    # ---- JOONISTAMINE (joonistab praeguse seisu ekraanile) ------------
    def draw_frame(self):
        self.screen.fill(C_BLACK)               # kustuta ekraan mustaks
        for wall in self.walls:                 # joonista seinad
            wall.draw(self.screen)
        for (c, r) in self.doors:               # joonista maja uks (roosa riba)
            pygame.draw.rect(self.screen, C_DOOR,
                             (c * TILE + 3, r * TILE + TILE // 2 - 2, TILE - 6, 4))
        for (c, r) in self.cookies:             # joonista koogid (väikesed täpid)
            pygame.draw.circle(self.screen, C_PELLET,
                               (c * TILE + TILE // 2, r * TILE + TILE // 2), 3)
        # power-pelletid VILGUVAD (Mäng 3): joonistame ainult pooltel kaadritel
        if (pygame.time.get_ticks() // 250) % 2 == 0:
            for (c, r) in self.powerups:
                pygame.draw.circle(self.screen, C_POWER,
                                   (c * TILE + TILE // 2, r * TILE + TILE // 2), 7)
        if self.fruit:
            self.fruit.draw(self.screen)
        for g in self.ghosts:                   # kummitused
            g.draw(self.screen)
        self.hero.draw(self.screen)             # Pac-Man (kõige peal)

        for p in self.popups:                   # hõljuvad numbrid
            surf = self.font.render(p[2], True, C_TEXT)
            self.screen.blit(surf, (p[0], int(p[1])))

        self._draw_hud()                        # skoor/elud/tase all
        self._draw_overlays()                   # "VALMIS!"/"PAUS"/"MÄNG LÄBI" jms
        pygame.display.flip()                   # näita valmis pilt ekraanil

    def _draw_hud(self):
        # HUD = ekraani info (skoor, rekord, elud, tase) alumisel ribal.
        info = self.font.render(
            f"Skoor: {self.score}   Rekord: {self.high_score}   "
            f"Elud: {self.lives}   Tase: {self.level}",
            True, C_TEXT)
        self.screen.blit(info, (8, self.height - TILE + 2))

    def _draw_overlays(self):
        # Suured tekstid keset ekraani sõltuvalt olekust.
        msg = None
        if self.state == GameState.READY:
            msg = ("VALMIS!", C_PAC)
        elif self.state == GameState.PAUSED:
            msg = ("PAUS", C_TEXT)
        elif self.state == GameState.GAMEOVER:
            msg = ("MÄNG LÄBI", (255, 60, 60))
        elif self.state == GameState.WIN:
            msg = ("TASE LÄBI!", (60, 255, 120))
        if msg:
            surf = self.big_font.render(msg[0], True, msg[1])
            rect = surf.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(surf, rect)
            if self.state == GameState.GAMEOVER:
                hint = self.font.render("Vajuta TÜHIK uuesti alustamiseks",
                                        True, C_TEXT)
                hrect = hint.get_rect(center=(self.width // 2, self.height // 2 + 46))
                self.screen.blit(hint, hrect)

    # ---- PEAMINE TSÜKKEL (mängu "süda") -------------------------------
    def run(self):
        # See silmus käib seni, kuni done == True. Iga ring = üks kaader.
        while not self.done:
            self.handle_input()          # 1) loe klahvid
            self.update_frame()          # 2) arvuta uus seis
            self.draw_frame()            # 3) joonista
            self.clock.tick(FPS)         # 4) oota, et hoida ~60 kaadrit/s
        pygame.quit()                    # sulge pygame korralikult


# See plokk käivitub AINULT siis, kui faili otse käivitada
# (python pacman_kombineeritud.py), mitte siis, kui see importida (testid).
if __name__ == "__main__":
    Game().run()