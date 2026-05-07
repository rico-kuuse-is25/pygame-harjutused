import pygame, sys, random   # laeme sisse kolm teeki: pygame (mängumootor), sys (programmi sulgemine), random (juhuslikud arvud)
pygame.init()                 # käivitame pygame'i - see peab alati esimesena olema

# ── Ekraani seaded ──────────────────────────────────────────────────
screenX, screenY = 640, 480                              # ekraani laius on 640 pikslit, kõrgus 480 pikslit
screen = pygame.display.set_mode([screenX, screenY])     # loome akna antud suurusega
pygame.display.set_caption("Ralli Mang")                 # paneme aknale pealkirja
clock = pygame.time.Clock()                              # loome kella, millega hiljem FPS-i piirame

# ── Graafika laadimine ──────────────────────────────────────────────
bg       = pygame.image.load("bg_rally.jpg")             # laeme taustapildi failist "bg_rally.jpg"
bg       = pygame.transform.scale(bg, [screenX, screenY])# skaleerime taustapildi täpselt ekraani suuruseks
blue_img = pygame.image.load("f1_blue.png")              # laeme sinise auto pildi failist
red_img  = pygame.image.load("f1_red.png")               # laeme punase auto pildi failist

CAR_W, CAR_H = 55, 80                                    # kõigi autode laius = 55px, kõrgus = 80px
blue_img = pygame.transform.scale(blue_img, [CAR_W, CAR_H])  # muudame sinise auto pildi õigesse suurusesse
red_img  = pygame.transform.scale(red_img,  [CAR_W, CAR_H])  # muudame punase auto pildi õigesse suurusesse

# ── Tee rajad ──────────────────────────────────────────────────────
ROAD_LEFT  = 155             # tee vasak äär asub x=155 juures (roheline ala on vasakul)
ROAD_RIGHT = 480             # tee parem äär asub x=480 juures (roheline ala on paremal)
LANE_COUNT = 3               # teel on 3 rada kõrvuti
lane_width = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT   # ühe raja laius pikslites (325 / 3 ≈ 108px)
MIN_GAP    = CAR_H + 25      # minimaalne vahe kahe sinise auto vahel samas rajas (80+25=105px)

def lane_x(lane):
    # arvutab raja numbri põhjal auto x-koordinaadi nii, et auto on rajas tsentreeritud
    return ROAD_LEFT + lane * lane_width + (lane_width - CAR_W) // 2

# ── Fondid ─────────────────────────────────────────────────────────
font_small  = pygame.font.SysFont("Arial", 22, bold=True)   # väike font (22px) - skoori jaoks
font_medium = pygame.font.SysFont("Arial", 36, bold=True)   # keskmise suurusega font (36px) - nuppude jaoks
font_big    = pygame.font.SysFont("Arial", 64, bold=True)   # suur font (64px) - pealkirjade jaoks

# ── Vaarvid ────────────────────────────────────────────────────────
WHITE  = (255, 255, 255)   # valge värv - RGB väärtused: punane, roheline, sinine (0-255)
BLACK  = (0,   0,   0)     # must värv
RED    = (220, 30,  30)    # punane värv
YELLOW = (255, 220, 0)     # kollane värv
GREEN  = (40,  160, 60)    # roheline värv (nuppude taust)
LGREEN = (80,  200, 100)   # heledam roheline (nupu hover-efekt)
GRAY   = (180, 180, 180)   # hall värv (juhiste tekst)

# ════════════════════════════════════════════════════════════════════
#  Abifunktsioonid
# ════════════════════════════════════════════════════════════════════
def get_rect(car, pad=8):
    # tagastab auto kokkupõrke ristkülikuliku (Rect) - pad=8 tähendab et äärtest 8px sisse,
    # et kokkupõrge ei toimuks juba siis kui autod on kõrvuti aga ei katu
    return pygame.Rect(car["x"] + pad, car["y"] + pad,
                       CAR_W - 2*pad, CAR_H - 2*pad)

def draw_text_shadow(surface, text, font, color, x, y, offset=2):
    # joonistab teksti varjuga: kõigepealt must tekst veidi nihkes (vari), siis päris tekst peale
    surface.blit(font.render(text, True, BLACK), (x + offset, y + offset))  # must vari
    surface.blit(font.render(text, True, color), (x, y))                    # päris tekst

def draw_centered(surface, text, font, color, cy, offset=2):
    # joonistab teksti horisontaalselt tsentreeritud - arvutab laiuse ja jagab pooleks
    w = font.size(text)[0]                                          # mõõdab teksti laiuse pikslites
    draw_text_shadow(surface, text, font, color, screenX//2 - w//2, cy, offset)  # joonistab tsentreeritud

def draw_overlay(alpha=160):
    # joonistab pool-läbipaistva musta kihi kogu ekraanile (kasutatakse menüüdes)
    ov = pygame.Surface((screenX, screenY), pygame.SRCALPHA)  # loob läbipaistvust toetava pinna
    ov.fill((0, 0, 0, alpha))                                  # täidab musta värviga, alpha=läbipaistvus (0-255)
    screen.blit(ov, (0, 0))                                    # kleebib ekraanile vasakusse ülanurka

# ════════════════════════════════════════════════════════════════════
#  Siniste autode overlap-prevention
#  Liigutame iga kaadri tagant: sordi raja autod y jargi (yla->alla),
#  ja tagage minimaalne vahe paari kaupa.
# ════════════════════════════════════════════════════════════════════
def enforce_gaps(blue_cars):
    # käib läbi kõik 3 rada ja tagab et sama raja autode vahel on piisav ruum
    for lane in range(LANE_COUNT):                       # kordab iga raja jaoks (0, 1, 2)
        in_lane = sorted(
            [c for c in blue_cars if c["lane"] == lane], # filtreerib ainult selle raja autod
            key=lambda c: c["y"]                         # sorteerib y-koordinaadi järgi (ülemine esimesena)
        )
        for i in range(1, len(in_lane)):                 # käib läbi autode paarid
            above = in_lane[i-1]                         # ülemine auto paarist
            below = in_lane[i]                           # alumine auto paarist
            gap = below["y"] - above["y"]                # arvutab vahe kahe auto vahel
            if gap < MIN_GAP:                            # kui vahe on liiga väike...
                above["y"] = below["y"] - MIN_GAP       # lükkab ülemist autot kaugemale üles

# ════════════════════════════════════════════════════════════════════
#  Mängu lähtestamine
# ════════════════════════════════════════════════════════════════════
def reset_game():
    # loob uue mängu algseisu: paneb punase auto alla ja 5 sinist autot üles
    red = {"x": lane_x(1), "y": screenY - CAR_H - 10, "speed": 5}
    # punane auto: keskmises rajas (lane 1), alumises servas, kiirus 5px/kaader

    # blueprint = plaan kus iga sinine auto algab: (rada, y-koordinaat)
    blueprint = [
        (0, -1 * (CAR_H + 40)),                       # rada 0, veidi üle ekraani ülaserva
        (0, -1 * (CAR_H + 40 + MIN_GAP + 60)),        # rada 0, veel kaugemal ülaservast
        (1, -1 * (CAR_H + 40)),                        # rada 1, veidi üle ekraani ülaserva
        (1, -1 * (CAR_H + 40 + MIN_GAP + 60)),        # rada 1, veel kaugemal ülaservast
        (2, -1 * (CAR_H + 40 + MIN_GAP//2)),          # rada 2, keskmiselt kaugel
    ]
    blues = []                                          # tühi loend siniste autode jaoks
    for lane, y in blueprint:                           # käib iga plaani rea läbi
        blues.append({                                  # lisab uue auto loendisse
            "x":     lane_x(lane),                     # x-koordinaat raja põhjal
            "y":     y,                                 # y-koordinaat plaanist
            "speed": random.randint(2, 4),              # juhuslik kiirus 2-4 px/kaader
            "lane":  lane,                              # raja number (meeles pidamiseks)
        })
    return red, blues, 0   # tagastab punase auto, siniste autode loendi ja skoori (0)

# ── Olekud ─────────────────────────────────────────────────────────
STATE_START    = "start"     # mängu olek: algusmenüü
STATE_PLAY     = "play"      # mängu olek: mäng käib
STATE_GAMEOVER = "gameover"  # mängu olek: mäng läbi

red_car, blue_cars, score = reset_game()   # käivitame mängu lähtestamisfunktsiooni
state       = STATE_START                  # mäng algab algusmenüüst
flash_timer = 0                            # vilkumise loendur (punase auto vilkumiseks põrkel)

# ── Nupu klass (ilma erisumbolita) ─────────────────────────────────
class Button:
    # klass mis esindab üht nuppu - hoiab koos nupu teksti, asukoha ja hover-seisu
    def __init__(self, text, cx, cy, w=190, h=54):
        # konstruktor: text=nupu tekst, cx/cy=nupu keskpunkt, w/h=laius/kõrgus
        self.text = text                                             # salvestab teksti
        self.rect = pygame.Rect(cx - w//2, cy - h//2, w, h)        # loob ristkülikuliku nupu jaoks
        self.hovered = False                                         # kas hiir on nupu peal? (algul ei ole)

    def draw(self, surface):
        # joonistab nupu ekraanile
        col    = LGREEN if self.hovered else GREEN       # kui hiir peal = heledam roheline, muidu tavaline
        shadow = pygame.Rect(self.rect.x+3, self.rect.y+4,
                             self.rect.w, self.rect.h)              # vari on 3px paremale ja 4px alla nihutatud
        pygame.draw.rect(surface, (20, 80, 30), shadow, border_radius=12)  # joonistab varju (tume roheline)
        pygame.draw.rect(surface, col,          self.rect, border_radius=12)  # joonistab nupu põhja
        pygame.draw.rect(surface, WHITE,        self.rect, 2, border_radius=12)  # joonistab valge ääre (2px)
        lbl = font_medium.render(self.text, True, WHITE)             # loob tekstipildi
        surface.blit(lbl, (self.rect.centerx - lbl.get_width()//2,  # kleebib teksti nupu keskele
                           self.rect.centery - lbl.get_height()//2))

    def update(self, pos):
        # uuendab hover-seisu - kontrollib kas hiirekursor on nupu peal
        self.hovered = self.rect.collidepoint(pos)

    def clicked(self, ev):
        # tagastab True kui nupul klikiti (vasak hiirenupp + kursor nupu peal)
        return (ev.type == pygame.MOUSEBUTTONDOWN and   # kas hiirenupp vajutati alla?
                ev.button == 1 and                      # kas see oli vasak nupp (1)?
                self.rect.collidepoint(ev.pos))         # kas kursor oli nupu peal?

play_btn    = Button("Mangi",   screenX//2, 285)         # "Mängi" nupp algusmenüüsse, y=285
restart_btn = Button("Uuesti",  screenX//2, 320)         # "Uuesti" nupp game over ekraanile
quit_btn    = Button("Valju",   screenX//2, 385, w=190, h=50)  # "Välju" nupp game over ekraanile

# ════════════════════════════════════════════════════════════════════
#  Peatsukkel
# ════════════════════════════════════════════════════════════════════
while True:              # lõputu tsükkel - mäng jookseb kuni programm suletakse
    clock.tick(60)       # piirab tsükli kiirust 60 kaadriga sekundis (60 FPS)
    mouse = pygame.mouse.get_pos()   # küsib hiirekursori hetke koordinaadid (x, y)

    for event in pygame.event.get():              # käib läbi kõik sündmused mis on toimunud
        if event.type == pygame.QUIT:             # kui kasutaja vajutas akna sulgemise nuppu...
            pygame.quit(); sys.exit()             # sulgeme pygame'i ja lõpetame programmi

        if state == STATE_START:                  # kui oleme algusmenüüs...
            if play_btn.clicked(event):           # ja "Mängi" nupule klikiti...
                red_car, blue_cars, score = reset_game()   # lähtestame mängu
                state = STATE_PLAY                # lülitume mängimise olekusse

        elif state == STATE_GAMEOVER:             # kui oleme game over ekraanil...
            if restart_btn.clicked(event):        # ja "Uuesti" nupule klikiti...
                red_car, blue_cars, score = reset_game()   # lähtestame mängu
                state, flash_timer = STATE_PLAY, 0         # lülitume mängimise olekusse, kustutame vilkumise
            if quit_btn.clicked(event):           # ja "Välju" nupule klikiti...
                pygame.quit(); sys.exit()         # sulgeme mängu
            if event.type == pygame.KEYDOWN:      # kui klahvi vajutati...
                if event.key == pygame.K_r:       # ja see klahv oli R...
                    red_car, blue_cars, score = reset_game()
                    state, flash_timer = STATE_PLAY, 0
                if event.key == pygame.K_ESCAPE:  # kui vajutati ESC klahvi...
                    pygame.quit(); sys.exit()     # sulgeme mängu

    play_btn.update(mouse)     # uuendame "Mängi" nupu hover-seisu vastavalt hiirepositsioonile
    restart_btn.update(mouse)  # uuendame "Uuesti" nupu hover-seisu
    quit_btn.update(mouse)     # uuendame "Välju" nupu hover-seisu

    # ════════════════════════════════════════════════════════════
    #  Manguloogika
    # ════════════════════════════════════════════════════════════
    if state == STATE_PLAY:   # see plokk töötab ainult siis kui mäng aktiivselt käib

        # Punane auto
        keys = pygame.key.get_pressed()           # loeb kõik hetkel all hoitavad klahvid
        spd  = red_car["speed"]                   # võtab punase auto kiiruse muutujasse
        if keys[pygame.K_LEFT]:  red_car["x"] -= spd   # vasak nool: liigub vasakule
        if keys[pygame.K_RIGHT]: red_car["x"] += spd   # parem nool: liigub paremale
        if keys[pygame.K_UP]:    red_car["y"] -= spd   # üles nool: liigub üles (y väheneb!)
        if keys[pygame.K_DOWN]:  red_car["y"] += spd   # alla nool: liigub alla
        red_car["x"] = max(ROAD_LEFT,     min(ROAD_RIGHT - CAR_W, red_car["x"]))
        # eelnev rida: piirab punase auto x-koordinaadi tee piiridesse (ei saa tee pealt välja)
        red_car["y"] = max(0,             min(screenY - CAR_H,    red_car["y"]))
        # piirab punase auto y-koordinaadi ekraani piiridesse (ei saa ekraanilt välja)

        # Sinised autod liiguvad alla
        for car in blue_cars:              # käib läbi iga sinise auto
            car["y"] += car["speed"]       # liigutab autot alla vastavalt selle kiirusele
            if car["y"] > screenY:         # kui auto on ekraani alt välja läinud...
                score += 1                 # lisame 1 punkt skoorile
                car["lane"]  = random.randint(0, LANE_COUNT - 1)   # valime uue juhusliku raja
                car["x"]     = lane_x(car["lane"])                  # uuendame x-koordinaati
                car["y"]     = random.randint(-180, -CAR_H - 20)   # paneme auto ekraani ülaservast välja
                car["speed"] = random.randint(2, min(7, 2 + score // 6))
                # eelnev rida: uus juhuslik kiirus - mäng läheb aegamisi raskemaks (max kiirus kasvab)

        enforce_gaps(blue_cars)   # tagame et sinised autod ei kattu üksteisega

        # Kokkupõrge
        rr = get_rect(red_car)              # võtame punase auto kokkupõrke ristkülikuliku
        for car in blue_cars:               # käime läbi kõik sinised autod
            if rr.colliderect(get_rect(car)):  # kui punane auto kattub sinisega...
                state, flash_timer = STATE_GAMEOVER, 36   # mäng läbi! vilkumine 36 kaadrit

    # ════════════════════════════════════════════════════════════
    #  Joonistamine - see osa joonistab kõik ekraanile
    # ════════════════════════════════════════════════════════════
    screen.blit(bg, (0, 0))   # joonistame taustapildi ekraanile (algab vasakust ülanurgast)

    if state in (STATE_PLAY, STATE_GAMEOVER):   # joonistame autod ainult mängu ajal
        for car in blue_cars:                   # käime läbi kõik sinised autod
            screen.blit(blue_img, (car["x"], car["y"]))   # joonistame iga sinise auto oma koordinaatidele

        # Punane auto vilgub põrke hetkel (flash_timer loendab alla 36-st 0-ni)
        if not (state == STATE_GAMEOVER and flash_timer > 0 and flash_timer % 6 < 3):
            # flash_timer % 6 < 3 tähendab: iga 6 kaadrist 3 on auto nähtamatu (vilkumine)
            screen.blit(red_img, (red_car["x"], red_car["y"]))   # joonistame punase auto
        if flash_timer > 0:        # kui vilkumisloendur on nullist suurem...
            flash_timer -= 1       # vähendame seda ühe võrra (loendab alla)

        draw_text_shadow(screen, f"Skoor: {score}", font_small, WHITE, 10, 10)
        # joonistame skoori ekraani vasakusse ülanurka (x=10, y=10)

    # ── START ────────────────────────────────────────────────────
    if state == STATE_START:        # kui oleme algusmenüüs...
        draw_overlay(120)           # joonistame pool-läbipaistva musta kihi peale
        draw_centered(screen, "RALLI", font_big, YELLOW, 90,  3)   # "RALLI" kollaselt, y=90
        draw_centered(screen, "MANG",  font_big, WHITE,  160, 3)   # "MÄNG" valgelt, y=160

        for k, h in enumerate([                                      # enumerate annab ka indeksi k (0,1,2)
            "Nooleklahvid - liiguta punast autot",                   # esimene juhis
            "Sinistest autodest mooda soitmine annab punkte",        # teine juhis
            "Kokkuporge = mang labi!",                               # kolmas juhis
        ]):
            draw_centered(screen, h, font_small, GRAY, 368 + k*28, 1)
            # joonistab iga juhise tsentreeritud, 28px allpool eelmist (k*28)

        play_btn.draw(screen)   # joonistame "Mängi" nupu

    # ── GAME OVER ────────────────────────────────────────────────
    if state == STATE_GAMEOVER and flash_timer == 0:   # game over ekraan (ainult pärast vilkumist)
        draw_overlay(170)                              # tumedam läbipaistev kiht kui algusmenüüs
        draw_centered(screen, "MANG LABI!", font_big,    RED,    130, 3)   # suur punane pealkiri
        draw_centered(screen, f"Sinu skoor: {score}",
                               font_medium, YELLOW, 225, 2)                # kollane skoor
        restart_btn.draw(screen)   # joonistame "Uuesti" nupu
        quit_btn.draw(screen)      # joonistame "Välju" nupu

    pygame.display.flip()   # kuvab kõik joonistatu ekraanile (ilma selleta ei näeks midagi)