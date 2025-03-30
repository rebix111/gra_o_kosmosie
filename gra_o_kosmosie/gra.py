import pygame
import os
import time
import random

pygame.init()

wysokosc_okna, szerokosc_okna = 750, 750
okno = pygame.display.set_mode((szerokosc_okna, wysokosc_okna))

kolor_bialy = (255, 255, 255)
czerwony_statek = pygame.image.load(os.path.join("gra_o_kosmosie","tekstury", "pixel_ship_red_small.png"))
zielony_statek = pygame.image.load(os.path.join("gra_o_kosmosie","tekstury", "pixel_ship_green_small.png"))
niebieski_statek = pygame.image.load(os.path.join("gra_o_kosmosie","tekstury", "pixel_ship_blue_small.png"))
zulty_statek = pygame.image.load(os.path.join("gra_o_kosmosie","tekstury", "pixel_ship_yellow.png"))

czerwony_laser = pygame.image.load(os.path.join("gra_o_kosmosie","tekstury", "pixel_laser_red.png"))
zielony_laser = pygame.image.load(os.path.join("gra_o_kosmosie","tekstury", "pixel_laser_green.png"))
niebieski_laser = pygame.image.load(os.path.join("gra_o_kosmosie","tekstury", "pixel_laser_blue.png"))
zulty_laser = pygame.image.load(os.path.join("gra_o_kosmosie","tekstury", "pixel_laser_yellow.png"))
potka_do_leczenia = pygame.image.load(os.path.join("gra_o_kosmosie","tekstury", "Sprite-0001.png"))
stonks_on_top = pygame.transform.scale(pygame.image.load(os.path.join("gra_o_kosmosie","tekstury", "bink czi li.jpg")), (szerokosc_okna, wysokosc_okna/2))

tlo = pygame.transform.scale(pygame.image.load(os.path.join("gra_o_kosmosie","tekstury", "background-black.png")), (szerokosc_okna, wysokosc_okna))
tlo_do_przegranej = pygame.transform.scale(pygame.image.load(os.path.join("gra_o_kosmosie","tekstury", "tlo_do_przegranej.png")), (szerokosc_okna, wysokosc_okna))
tlo_menu = pygame.transform.scale(pygame.image.load(os.path.join("gra_o_kosmosie","tekstury", "Sprite.jpg")), (szerokosc_okna, wysokosc_okna))

dziwienk_pocisku = pygame.mixer.Sound('gra_o_kosmosie\\dziwieki\\Grenade+1.mp3')
ogien_pocisku = pygame.mixer.Sound('gra_o_kosmosie\\dziwieki\\Gun+Silencer.mp3')
sound_track = pygame.mixer.Sound('gra_o_kosmosie\\dziwieki\\pixel-perfect-112527.mp3')
przejscie_sound = pygame.mixer.Sound('gra_o_kosmosie\\dziwieki\\332003_lloydevans09_whoosh (online-audio-converter.com).mp3')
dziwienk_pocisku.set_volume(0.1)
ogien_pocisku.set_volume(0.1)
sound_track.set_volume(0.4)
przejscie_sound.set_volume(0.2)

class Laser:
    def __init__(self, x, y, zdj):
        self.x = x
        self.y = y
        self.zdj = zdj
        self.mask = pygame.mask.from_surface(zdj)

    def rysowanie(self, okno):
        okno.blit(self.zdj, (self.x, self.y))

    def poruszanie(self, predkosc):
        self.y += predkosc

    def za_ekranem(self):
        return not (self.y <= wysokosc_okna and self.y >= -100)

    def kolizja(self, obj):
        dziwienk_pocisku.play()
        return zderzenie(self, obj)

class Potka:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.obraz = potka_do_leczenia
        self.mask = pygame.mask.from_surface(self.obraz)
        self.czas_zycia = 400
        self.aktywna = True

    def rysuj(self, okno):
        if self.aktywna:
            okno.blit(self.obraz, (self.x, self.y))

    def aktualizuj(self):
        self.czas_zycia -= 1
        if self.czas_zycia <= 0:
            self.aktywna = False

    def kolizja(self, gracz):
        if not self.aktywna:
            return False
        return zderzenie(self, gracz)

class Statek:
    COOL_DOWN = 30

    def __init__(self, x, y, hp=100):
        self.x = x
        self.y = y
        self.hp = hp
        self.obrazek_statku = None
        self.laser_zdj = None
        self.lasery = []
        self.cool_down_licznik = 0

    def draw(self, okno):
        okno.blit(self.obrazek_statku, (self.x, self.y))
        for laser in self.lasery:
            laser.rysowanie(okno)

    def cool_down(self):
        if self.cool_down_licznik >= self.COOL_DOWN:
            self.cool_down_licznik = 0
        elif self.cool_down_licznik > 0:
            self.cool_down_licznik += 1

    def strzelanie(self):
        if self.cool_down_licznik == 0:
            laser = Laser(self.x + self.szerokosc_statku() // 2 - self.laser_zdj.get_width() // 2,
                          self.y, self.laser_zdj)
            self.lasery.append(laser)
            self.cool_down_licznik = 1
            print(self.x)
            ogien_pocisku.play()

    def szerokosc_statku(self):
        return self.obrazek_statku.get_width()

    def wysokosc_statku(self):
        return self.obrazek_statku.get_height()

class Gracz(Statek):
    def __init__(self, x, y, hp=100):
        super().__init__(x, y, hp)
        self.obrazek_statku = zulty_statek
        self.laser_zdj = zulty_laser
        self.mask = pygame.mask.from_surface(self.obrazek_statku)
        self.max_hp = hp
        
        self.dash_cooldown = 0
        self.dash_duration = 15
        self.dash_speed = 15
        self.dash_active = False
        self.dash_direction = 0
        self.dash_cooldown_timer = 0
        self.dash_cooldown_max = 40

    def ruszanie_laserow(self, predkosc, objekty):
        self.cool_down()
        for laser in self.lasery[:]:
            laser.poruszanie(predkosc)
            if laser.za_ekranem():
                self.lasery.remove(laser)
            else:
                for obj in objekty[:]:
                    if laser.kolizja(obj):
                        objekty.remove(obj)
                        if laser in self.lasery:
                            self.lasery.remove(laser)
            


    def dash(self, direction):
        if self.dash_cooldown_timer <= 0 and not self.dash_active:
            self.dash_active = True
            self.dash_direction = direction
            self.dash_cooldown = self.dash_duration
            self.dash_cooldown_timer = self.dash_cooldown_max
            przejscie_sound.play()

    def update_dash(self):
        if self.dash_active:
            new_x = self.x + self.dash_speed * self.dash_direction
            
            if new_x < 0:
                new_x = 0
            elif new_x + self.szerokosc_statku() > szerokosc_okna:
                new_x = szerokosc_okna - self.szerokosc_statku()
            
            self.x = new_x
            
            self.dash_cooldown -= 1
            if self.dash_cooldown <= 0:
                self.dash_active = False
                
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= 1

    def narysuj_tabliczke_zdrowia(self, okno):
        super().draw(okno)
        self.tabliczka_zdrowia(okno)

    def tabliczka_zdrowia(self, okno):
        pygame.draw.rect(okno, (255,0,0), (self.x, self.y + self.obrazek_statku.get_height() + 10, 
                                          self.obrazek_statku.get_width(), 10))
        pygame.draw.rect(okno, (0,255,0), (self.x, self.y + self.obrazek_statku.get_height() + 10, 
                                          self.obrazek_statku.get_width() * (self.hp/self.max_hp), 10))

class Przeciwnicy(Statek):
    kolory_Statkow = {
        "zielony": (zielony_statek, zielony_laser),
        "czerwony": (czerwony_statek, czerwony_laser),
        "niebieski": (niebieski_statek, niebieski_laser)
    }

    def __init__(self, x, y, kolor, hp=100):
        super().__init__(x, y, hp)
        self.obrazek_statku, self.laser_zdj = self.kolory_Statkow[kolor]
        self.mask = pygame.mask.from_surface(self.obrazek_statku)

    def poruszanie(self, predkosc_przeciwnika):
        self.y += predkosc_przeciwnika

    def strzelanie(self):
        if self.cool_down_licznik == 0 and random.randrange(0, 200) == 1:
            laser = Laser(self.x + self.szerokosc_statku() // 2 - self.laser_zdj.get_width() // 2,
                          self.y + self.wysokosc_statku(), self.laser_zdj)
            self.cool_down_licznik = 1
            return laser
        return None

def Przegrana(level):
    zapisz_wynik_levela(level)
    okno.blit(tlo_do_przegranej, (0, 0))
    pixel_font = pygame.font.Font('gra_o_kosmosie\\inne\\PressStart2P-Regular.ttf', 45)
    tekst_przegranej = pixel_font.render('Przegrałeś!', True, kolor_bialy)
    okno.blit(tekst_przegranej, (150, 300))
    pygame.display.update()
    time.sleep(3)

def zderzenie(objekt1, objekt2):
    offset_x = objekt2.x - objekt1.x
    offset_y = objekt2.y - objekt1.y
    return objekt1.mask.overlap(objekt2.mask, (offset_x, offset_y)) is not None


def menu_startowe():
    przycisk = pygame.image.load(os.path.join('gra_o_kosmosie','tekstury', 'obraz_2025-03-11_202421195-removebg-preview.png'))
    przycisk = pygame.transform.scale(przycisk, (300, 150))
    przycisk_rect = przycisk.get_rect(topleft=(230, 280))

    while True:
        okno.blit(tlo_menu, (0, 0))
        pixel_font = pygame.font.Font('gra_o_kosmosie\\inne\\PressStart2P-Regular.ttf', 23)
        tekst_startu = pixel_font.render("Kliknij przycisk, aby rozpoczonc", True, kolor_bialy)
        okno.blit(tekst_startu, (10, 100))
        tekst_info3 = pixel_font.render("Pod ESC masz instrukcje gry ", True, kolor_bialy)
        okno.blit(tekst_info3, (60, 600))
        okno.blit(przycisk, przycisk_rect.topleft)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if przycisk_rect.collidepoint(event.pos):
                    return

def menu_pauzy(level):
    pauza = True
    pixel_font = pygame.font.Font('gra_o_kosmosie\\inne\\PressStart2P-Regular.ttf', 23)
    
    while pauza:
        okno.blit(tlo_do_przegranej, (0, 0))
        tekst_info = pixel_font.render("ogl gra jest zapauzowana", True, kolor_bialy)
        tekst_info2 = pixel_font.render("-zeby wrucic do gry kliknij esc", True, kolor_bialy)
        tekst_info3 = pixel_font.render("-zeby wyjsc f1", True, kolor_bialy)
        tekst_info4 = pixel_font.render("-pod Shiftem masz dashe btw", True, kolor_bialy)
        
        okno.blit(tekst_info, (100, 100))
        okno.blit(tekst_info2, (20, 200))
        okno.blit(tekst_info3, (20, 250))
        okno.blit(tekst_info4, (20, 300))
        okno.blit(stonks_on_top, (0, 350))
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                zapisz_wynik_levela(level)
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pauza = False
                if event.key == pygame.K_F1:
                    zapisz_wynik_levela(level)
                    pygame.quit()
                    quit()

def wczytaj_liczbe_rund():
    rounds_file = 'gra_o_kosmosie/rounds.txt'
    
    if not os.path.exists(rounds_file):
        with open(rounds_file, 'w') as file:
            file.write('0')
        return 0
    else:
        try:
            with open(rounds_file, 'r') as file:
                rounds = file.read().strip()
                return int(rounds)
        except ValueError:  
            print("Błąd wczytywania liczby rund, ustawiono 0")
            return 0

def zapisz_wynik_levela(level):
    najlepszy_wynik = wczytaj_liczbe_rund()
    
    if level > najlepszy_wynik:
        with open('gra_o_kosmosie/rounds.txt', 'w') as file:
            file.write(str(level))

def main():
    menu_startowe()
    sound_track.play(-1)
    najlepszy_wynik = wczytaj_liczbe_rund()
    dziala = True
    czas = pygame.time.Clock()
    fps = 60
    level = 0
    zycia = 5
    pixel_font = pygame.font.Font('gra_o_kosmosie\\inne\\PressStart2P-Regular.ttf', 25)
    gracz = Gracz(300, 650)
    predkosc_gracza = 4
    przeciwnicy = []
    lasery_przeciwnikow = []
    potki = []
    dlugosc_fali = 5
    predkosc_przeciwnika = 1
    laser_speed = 8
    przegrana = False
    licznik_potek = 0 
    
    def narysuj_okno():
        okno.blit(tlo, (0, 0))
        tekst_levelu = pixel_font.render(f'level:{level}', True, kolor_bialy)
        okno.blit(tekst_levelu, (10, 10))
        tekst_zycia = pixel_font.render(f'zycia:{zycia}', True, kolor_bialy)
        okno.blit(tekst_zycia, (570, 10))
        tekst_naj_levelu = pixel_font.render(f"najlepszy wynik:{najlepszy_wynik}", True, kolor_bialy)
        okno.blit(tekst_naj_levelu, (170, 720))

        for przeciwnik in przeciwnicy:
            przeciwnik.draw(okno)

        for laser in lasery_przeciwnikow:
            laser.rysowanie(okno)

        for potka in potki:
            potka.rysuj(okno)

        gracz.narysuj_tabliczke_zdrowia(okno)
        
        if gracz.dash_cooldown_timer > 0:
            cooldown_procent = gracz.dash_cooldown_timer / gracz.dash_cooldown_max
            pygame.draw.rect(okno, (100, 100, 100), (gracz.x, gracz.y - 20, gracz.szerokosc_statku(), 5))
            pygame.draw.rect(okno, (0, 255, 0), (gracz.x, gracz.y - 20, gracz.szerokosc_statku() * (1 - cooldown_procent), 5))
            
        pygame.display.update()

    while dziala:
        czas.tick(fps)
        
        if zycia <= 0 or gracz.hp <= 0:
            przegrana = True
            Przegrana(level)
            dziala = False
            main()

        licznik_potek += 1
        if gracz.hp < 80 and licznik_potek >= 200:
            nowa_potka = Potka(random.randint(50, szerokosc_okna - 50), 
                              random.randint(50, wysokosc_okna - 50))
            potki.append(nowa_potka)
            licznik_potek = 0

        if len(przeciwnicy) == 0:
            level += 1
            zapisz_wynik_levela(level)
            dlugosc_fali += 5
            for i in range(dlugosc_fali):
                przeciwnik = Przeciwnicy(random.randrange(50, szerokosc_okna - 100), 
                                        random.randrange(-1500, -100),
                                        random.choice(["zielony", "czerwony", "niebieski"]))
                przeciwnicy.append(przeciwnik)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                dziala = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT and gracz.dash_cooldown_timer <= 0:
                    if pygame.key.get_pressed()[pygame.K_a]:
                        gracz.dash(-1)
                    elif pygame.key.get_pressed()[pygame.K_d]:
                        gracz.dash(1)
                if event.key == pygame.K_ESCAPE:
                    menu_pauzy(level)

        przyciski = pygame.key.get_pressed()
        if not gracz.dash_active:
            if przyciski[pygame.K_a] and gracz.x - predkosc_gracza > 0:
                gracz.x -= predkosc_gracza
            if przyciski[pygame.K_d] and gracz.x + predkosc_gracza + gracz.szerokosc_statku() < szerokosc_okna:
                gracz.x += predkosc_gracza
            if przyciski[pygame.K_w] and gracz.y - predkosc_gracza > 0:
                gracz.y -= predkosc_gracza
            if przyciski[pygame.K_s] and gracz.y + predkosc_gracza + gracz.wysokosc_statku() < wysokosc_okna:
                gracz.y += predkosc_gracza
            if przyciski[pygame.K_SPACE]:
                gracz.strzelanie()
                

        gracz.update_dash()
        gracz.ruszanie_laserow(-laser_speed, przeciwnicy)

        for p in przeciwnicy[:]:
            p.poruszanie(predkosc_przeciwnika)
            p.cool_down()
            
            laser_przeciwnika = p.strzelanie()
            if laser_przeciwnika:
                lasery_przeciwnikow.append(laser_przeciwnika)
            
            if p.y + p.wysokosc_statku() > wysokosc_okna:
                zycia -= 1
                przeciwnicy.remove(p)
                
            if zderzenie(gracz, p):
                gracz.hp -= 20
                przeciwnicy.remove(p)

        for laser in lasery_przeciwnikow[:]:
            laser.poruszanie(laser_speed)
            if laser.za_ekranem():
                lasery_przeciwnikow.remove(laser)
            elif zderzenie(gracz, laser):
                gracz.hp -= 10
                lasery_przeciwnikow.remove(laser)

        for potka in potki[:]:
            potka.aktualizuj()
            if potka.kolizja(gracz):
                gracz.hp = min(gracz.hp + 30, gracz.max_hp)
                potki.remove(potka)
            elif not potka.aktywna:
                potki.remove(potka)

        narysuj_okno()

    zapisz_wynik_levela(level)
    pygame.quit()

if __name__ == "__main__":
    main()