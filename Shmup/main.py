##i##
import threading

import pygame
from os import path
import sys
import serial
import time
from math import floor
from random import choice, random, randint
path_name = path.split(path.dirname(__file__))[0]
if path_name not in sys.path:
    sys.path.append(path_name)
print("adding pygine path:", path_name)
import pygine
from objects.Ship import Ship
from objects.Stone import Stone
from objects.Boss import Boss
from objects.Player_bullet import Player_Bullet
from objects.Power_UP import PowerUp
from objects.explosion import Explosion
from menus import port_selection_menu
import menus.main_menu as main_menu
vec2 = pygame.math.Vector2
vec3 = pygame.math.Vector3
project_name = 'Shmup'
##ni##

##e## game values and pygame init
width = 1200  #<attr={"name":"Screenwidth","type":"int","default":1200,"low":200,"high":4000}>
height = 750  #<attr={"name":"Screenheight","type":"int","default":900,"low":200,"high":4000}>
FPS = 60  #<attr={"name":"Frames per second","type":"int","default":60,"low":20,"high":240}>
pygame.init()
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE, pygame.DOUBLEBUF)
title = "Shmup  (c) pygine"  #<attr={"name":"Window title","type":"string","default":"Game  (c) pygine"}>
pygame.display.set_caption(title)
clock = pygame.time.Clock()

map_width = 1200
map_height = 750

needed_points = 150
player_size = 8
player_shoot_time = 0.3
player_bullet_speed = 18
player_speed = 24
player_health = 80
player_lives = 3
power_up_size = 10
power_up_speed = 17
power_up_chance = 0.1
star_gain = 15
shot_update_time = 4
shield_time = 4
num_mobs = 12
stone_size = 8
stone_speed_min_down = 7
stone_speed_max_down = 10
stone_speed_max_side = 3
ship_size = 6
ship_speed_min_down = 7
ship_speed_max_down = 10
ship_speed_max_side = 3
ship_bullet_time = 2
boss_size = 7
boss_health = 100
endless_num_mobs_to_kill = 25

ALLOW_DUMMY = True #<attr={"name":"Allow keyboard as dummy for testing", "type":"bool",  "default":True}>

NUM_BUZZERS = 8
TEAMS = [x for x in range(NUM_BUZZERS)]
arduino_pressed = ""


class Arduino_Read_Thread(threading.Thread):
    def __init__(self, arduino):
        threading.Thread.__init__(self)
        self.arduino = arduino
        self.stopped = False

    def run(self):
        global arduino_pressed
        while not self.stopped:
            if self.arduino != "DUMMY" and self.arduino is not None:
                arduino_pressed = self.arduino.readline().decode('ascii').rstrip()

class Game:
    def __init__(self):

        ##e## create a World object and load a world from file <255,154,100>
        self.world = pygine.World_2d()

        ##e## make background
        self.world.background.set_style(pygine.IMAGE)
        self.world.background.image_background.set_image_from_file(pygine.get_file_path(project_name, ["img", "plug_in.png"]))
        self.world.background.image_background.set_resize_full(True, True)
        self.world.background.point_background.set_background_color((0, 0, 50))
        self.world.background.point_background.set_line_color((0, 45, 150))
        self.world.background.point_background.set_node_color((5, 30, 125))
        self.world.background.point_background.set_connection_distance(100)
        self.world.background.point_background.set_line_width(5)
        self.world.background.point_background.set_node_size(8)
        self.world.background.point_background.set_max_speed(2)

        ##e## add keyboard to inputs
        self.world.controllers.add_controller(pygine.Keyboard())
        ##e## connection to arduino
        self.arduino_image = pygine.load_image(project_name, ["img", "arduino.png"])
        self.arduino: serial.Serial = None
        self.in_connection_selection = False  # ports are selected
        self.connection_team_selection_window = None
        self.connection_warning = ""
        self.connecting_offset, self.connecting_zoom = vec2(0, 0), 1
        self.connection_rects = [pygame.Rect(124, 121, 22, 54), pygame.Rect(207, 121, 22, 54), pygame.Rect(124, 188, 22, 54), pygame.Rect(207, 188, 22, 54), pygame.Rect(124, 258, 22, 54), pygame.Rect(207, 258, 22, 54), pygame.Rect(124, 325, 22, 54), pygame.Rect(207, 325, 22, 54)]
        self.enabled_buttons = [True for i in range(NUM_BUZZERS)]
        self.space_ships = [pygine.load_image(project_name, ["img", "Player", f"playerShip1_{color}.png"]) for color in ["black", "blue", "green", "red"]]

        ##e## load background_music
        self.world.sounds.load_background_music(pygine.get_file_path(project_name,["snd","tgfcoder-FrozenJam-SeamlessLoop.ogg"]))
        self.world.sounds.new_sound("player die",pygine.get_file_path(project_name,["snd","rumble1.ogg"]))
        self.world.sounds.new_sound("small explosion", pygine.get_file_path(project_name, ["snd", "expl3.wav"]))
        self.world.sounds.new_sound("big explosion", pygine.get_file_path(project_name, ["snd", "expl6.wav"]))
        self.world.sounds.new_sound("power-up", pygine.get_file_path(project_name, ["snd", "pow4.wav"]))
        self.world.sounds.new_sound("shield", pygine.get_file_path(project_name, ["snd", "pow5.wav"]))
        self.world.sounds.new_sound("shoot", pygine.get_file_path(project_name, ["snd", "pew.wav"]))

        self.power_up_images = [pygine.load_image(project_name, ["img", "Power_Ups", "bolt_gold.png"]), pygine.load_image(project_name, ["img", "Power_Ups", "shield_gold.png"]), pygine.load_image(project_name, ["img", "Power_Ups", "star_gold.png"])]
        self.shield = pygine.load_image(project_name, ["img", "Shields", "shield2.png"])
        self.big_explosion_images = pygine.load_image_sequence(project_name, ["img", "Explosions"], "sonicExplosion0{}.png", 0, 9)
        self.small_explosion_images = pygine.load_image_sequence(project_name, ["img", "Explosions"], "regularExplosion0{}.png", 0, 9)

        self.space_ship_index_mapping = []
        self.num_players = 1
        self.endless = False
        self.level = 1

        self.arduino_thread = None

        self.start_game(True)

        self.world.menu.start_menu(port_selection_menu.get(ALLOW_DUMMY))
        ##c##

    def loop(self):
        fps = clock.tick(FPS)/FPS
        screen.fill((255, 255, 255))

        ##e## input from player (pygame events) <164,255,100>
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
            else:
                self.handle_event(event)
        if not self.in_connection_selection:
            self.check_key_pressed()

        ##e## update movement, ... <255,90,255>
        if self.in_connection_selection and self.world.menu.get_paused():
            self.in_connection_selection = False
        else:
            selected_in_menu, go_back = self.world.update_game(events,fps)
            if selected_in_menu is not None: self.menu_selection(selected_in_menu)
        self.update(events, fps, self.world.paused)

        ##e## render and flip display <164,255,255>
        self.world.draw(screen)
        pygine.draw_center_rect(screen, self.world.offset, (50, 50, 50))
        self.draw()
        pygame.display.flip()
        ##c##

    def set_level_attr_according_to_level(self):
        global needed_points,player_shoot_time,player_bullet_speed,player_speed,player_health,player_lives,power_up_speed,power_up_chance,star_gain,shot_update_time,shield_time,num_mobs,ship_bullet_time,boss_health
        global stone_speed_min_down,stone_speed_max_down,stone_speed_max_side,ship_speed_min_down,ship_speed_max_down,ship_speed_max_side
        needed_points = ((100/30)*self.level + 150)*(self.num_players*(2/3))
        player_shoot_time = (0.15/30)*self.level + 0.3
        player_bullet_speed = (-4/30)*self.level + 18
        player_speed = ((-5/30)*self.level + 24)*max(1.0,map_width/1000)
        player_health = (-20/30)*self.level + 80
        player_lives = 3 if self.level <= 10 else (2 if self.level <= 20 else 1)
        power_up_speed = ((3/30)*self.level + 12)*max(1.0,map_width/1000)
        power_up_chance = (-0.05/30)*self.level + 0.1
        star_gain = (-5/30)*self.level + 15
        shot_update_time = (-1.5/30)*self.level + 4
        shield_time = (-1.5/30)*self.level + 4
        num_mobs = int(((3/30)*self.level + 12)*(self.num_players*(1/3)))*(max(1,map_width//1000))
        ship_bullet_time = ((-0.8/30)*self.level + 2)*max(1.0,map_width/1000)
        boss_health = ((50/30)*self.level + 100)*(self.num_players*(2/3))
        stone_speed_min_down = ((3/30)*self.level + 7)*max(1.0,map_width/1000)
        stone_speed_max_down = ((3/30)*self.level + 11)*max(1.0,map_width/1000)
        stone_speed_max_side = ((-1.5/30)*self.level + 3)*max(1.0,map_width/1000)
        ship_speed_min_down = ((3/30)*self.level + 5)*max(1.0,map_width/1000)
        ship_speed_max_down = ((3/30)*self.level + 9)*max(1.0,map_width/1000)
        ship_speed_max_side = ((-1.5/30)*self.level + 3)*max(1.0,map_width/1000)
        endless_num_mobs_to_kill = int(((10/30)*self.level + 25)*(self.num_players*(2/3)))

    def start_game(self,first=False,from_endless=False):
        self.set_level_attr_according_to_level()

        if not from_endless:
            self.mobs = pygame.sprite.Group()
            self.ship_bullets = pygame.sprite.Group()
            self.player_bullets = pygame.sprite.Group()
            self.power_ups = pygame.sprite.Group()

        self.stone_color = choice(["Brown","Grey"])
        self.stone_images = pygine.load_image_sequence(project_name, ["img", "Meteors"], "meteor" + self.stone_color + "_big{}.png", 1, 3) + \
                            pygine.load_image_sequence(project_name, ["img", "Meteors"], "meteor" + self.stone_color + "_med{}.png", 1, 3) + \
                            pygine.load_image_sequence(project_name, ["img", "Meteors"], "meteor" + self.stone_color + "_small{}.png", 1, 3)

        self.ship_color = choice(["Black","Blue","Green","Red"])
        self.ship_images = pygine.load_image_sequence(project_name, ["img", "Enemies"], "enemy" + self.ship_color + "{}.png", 1, 6)
        self.ship_bullet_images = pygine.load_image(project_name, ["img", "Enemies", "Bullets", f"laser{self.ship_color}.png"])

        self.boss = None
        self.boss_health = boss_health
        self.boss_num = randint([10,13,16,19][["Black","Blue","Green","Red"].index(self.ship_color)],[12,15,18,21][["Black","Blue","Green","Red"].index(self.ship_color)])
        self.boss_image = pygine.load_image(project_name, ["img", "Enemies", "End-Boss", self.ship_color, f"ship_{self.boss_num}.png"])

        self.level_bar_color = [(99, 89, 109),(62, 136, 161),(124, 152, 101),(187, 108, 46)][["Black","Blue","Green","Red"].index(self.ship_color)]
        self.boss_bar_color = [(62, 62, 62),(20, 145, 200),(100, 165, 20),(175, 60, 60)][["Black","Blue","Green","Red"].index(self.ship_color)]

        if first:
            pass
        elif from_endless:
            self.endless_mode = 0
            self.endless_count = 0
            for x in range(num_mobs):
                self.world.objects.add_object(Stone(self.world,self.stone_images,self.mobs,map_width,map_height,stone_size,stone_speed_min_down,stone_speed_max_down,stone_speed_max_side))
        else:
            self.points = 0
            self.endless_count = 0
            self.endless_mode = 0
            self.num_players = len(self.world.player_list)
            self.world.clear_world(True,True,True,True)
            self.load_world()
            self.load_player()
            colors = ["black", "blue", "green", "red"]
            for num, player in enumerate(self.world.player_list):
                if self.arduino == "DUMMY":
                    player.color = choice(colors)
                    del colors[colors.index(player.color)]
                else:
                    player.color = colors[self.space_ship_index_mapping[num]]
                img = pygine.load_image(project_name, ["img", "Player", f"playerShip1_{player.color}.png"])
                player.shot_image = pygine.load_image(project_name, ["img", "Player", "Lasers", f"laser_{player.color}_big.png"])
                player.shot_image_small = pygine.load_image(project_name, ["img", "Player", "Lasers", f"laser_{player.color}_small.png"])
                player.set_image(img)
                player.small_img = pygame.transform.scale(img,(50,38))
                player.health_bar_color = [(30, 30, 30),(54, 187, 245),(113, 201, 55),(159, 66, 62)][["black", "blue", "green", "red"].index(player.color)]
                player.health = player_health
                player.lives = player_lives
                player.die_time = 0
                player.vel = vec2(0,0)
                player.last_shoot = 0
                player.num_shots = 1
                player.last_shoot_update = time.time()
                player.has_shield = False
                player.shield_time = 0

    def load_world(self):
        for x in range(num_mobs):
            if self.endless:
                self.world.objects.add_object(Stone(self.world,self.stone_images,self.mobs,map_width,map_height,stone_size,stone_speed_min_down,stone_speed_max_down,stone_speed_max_side))
            else:
                if self.level % 5 == 0:
                    self.world.objects.add_object(Ship(self.world,self.ship_images,self.ship_bullet_images,self.mobs,self.ship_bullets,map_width,map_height,ship_size,ship_speed_min_down,ship_speed_max_down,ship_speed_max_side,ship_bullet_time))
                else:
                    self.world.objects.add_object(Stone(self.world,self.stone_images,self.mobs,map_width,map_height,stone_size,stone_speed_min_down,stone_speed_max_down,stone_speed_max_side))
    def load_player(self):
        for _ in range(self.num_players):
            self.world.create_player(map_width/2,map_height-10,-90)
        for player in self.world.player_list:
            player.draw = self.draw_player
            player.update = self.update_player

    def handle_event(self, event:pygame.event):
        if event.type == pygame.WINDOWCLOSE:
            if self.arduino_thread is not None:
                self.arduino_thread.stopped = True
        if self.in_connection_selection:
            # select ports and name players
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.connection_warning = ""
                if event.pos[0] < screen.get_width() / 2:
                    for count, rect in enumerate(self.connection_rects):
                        click_rect = pygame.Rect(self.connecting_offset + vec2(rect.topleft) * self.connecting_zoom, vec2(rect.size) * self.connecting_zoom)
                        if click_rect.collidepoint(event.pos):
                            self.enabled_buttons[count] = not self.enabled_buttons[count]
                            if self.arduino != "DUMMY":
                                text = "c" + "".join([str(int(enabled)) for enabled in self.enabled_buttons]) + "\n"
                                self.arduino.write(text.encode("ascii"))
                            break
                else:
                    found = False
                    for num in range(len(self.space_ships)*2):
                        if not found:
                            if (count := self.connection_team_selection_window) is not None:
                                if count == num:
                                    if num % 2 == 0:
                                        pos = count / 2
                                        for num in range(NUM_BUZZERS):
                                            if pygame.Rect(screen.get_width() / 2 + 262 + (num % 3) * 37, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * pos - 22 + floor(num / 3) * 37, 30, 30).collidepoint(event.pos):
                                                TEAMS[count] = num
                                                found = True
                                                self.connection_team_selection_window = None
                                                break
                                    else:
                                        pos = floor(count / 2)
                                        for num in range(NUM_BUZZERS):
                                            if pygame.Rect(screen.get_width() / 2 + 262 + (num % 3) * 37, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * pos + 8 + floor(num / 3) * 37, 30, 30).collidepoint(event.pos):
                                                TEAMS[count] = num
                                                found = True
                                                self.connection_team_selection_window = None
                                                break
                    for num in range(len(self.space_ships)):
                        if not found:
                            if pygame.Rect(screen.get_width()/2 + 150, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * num + 15, 130, 30).collidepoint(event.pos):
                                found = True
                                self.connection_team_selection_window = 2*num
                                break
                            if pygame.Rect(screen.get_width()/2 + 150, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * num + 45, 130, 30).collidepoint(event.pos):
                                found = True
                                self.connection_team_selection_window = 2*num+1
                                break
                    if not found:
                        self.connection_team_selection_window = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.connection_warning = ""
                    warning_found = False
                    if True not in self.enabled_buttons:
                        warning_found = True
                        self.connection_warning = "Keine Buttons gewählt"
                    for num in range(len(self.space_ships)):
                        if self.enabled_buttons[TEAMS[2*num]] + self.enabled_buttons[TEAMS[2*num+1]] == 1:
                            warning_found = True
                            self.connection_warning = "Ein aktiver und ein inaktiver Buzzer bei Spieler "+str(num+1)
                    for buzzer in self.enabled_buttons:
                        if TEAMS.count(buzzer) > 1:
                            warning_found = True
                            self.connection_warning = "Buzzer "+str(buzzer+1)+" wird mehrfach verwendet"
                        if TEAMS.count(buzzer) == 0:
                            warning_found = True
                            self.connection_warning = "Buzzer "+str(buzzer+1)+" ist aktiv wird aber nicht verwendet"
                    if not warning_found:
                        self.world.background.set_style(pygine.POINT_ANIMATION)
                        self.world.menu.start_menu(main_menu.get(None, self.level-1, self.endless))
                        if self.arduino != "DUMMY":
                            self.arduino.write(b'o\n')
                            text = "l"
                            for buzzer, enabled in enumerate(self.enabled_buttons):
                                if enabled:
                                    if buzzer in TEAMS:
                                        if TEAMS.index(buzzer) % 2 == 0:
                                            text += "1"
                                        else:
                                            text += "2"
                                    else:
                                        text += "0"
                            self.arduino.write(text.encode("ascii"))
                            self.world.background.set_style(pygine.POINT_ANIMATION)
                            self.world.menu.start_menu(main_menu.get(None, self.level - 1, self.endless))
        else:
            if event.type == pygame.WINDOWFOCUSLOST:
                self.world.pause_game()
            elif event.type == pygame.WINDOWFOCUSGAINED:
                self.world.resume_game()
            player_num, controller, btn_or_axis, event = self.world.controllers.event(event)
            if player_num is not None:
                if isinstance(controller, pygine.controllers.Controller) or isinstance(controller, pygine.controllers.Keyboard_as_Controller):
                    if event.type == pygame.JOYAXISMOTION or event.type == pygame.JOYBUTTONDOWN or event.type == pygame.KEYDOWN:
                        if btn_or_axis == pygine.SELECT:
                            for player in self.world.player_list: player.health,player.lives = 0, 0
                else:
                    if event.type == pygame.KEYDOWN:
                        if btn_or_axis == pygame.K_ESCAPE:
                            for player in self.world.player_list: player.health,player.lives = 0, 0

    def check_key_pressed(self):
        def shoot(player):
            if time.time() - player.last_shoot > player_shoot_time:
                player.last_shoot = time.time()
                #self.world.sounds.play_sound("shoot")
                if player.num_shots != 2:
                    self.world.objects.add_object(Player_Bullet(self.world,player.pos.x,player.shot_image,self.player_bullets,map_width,map_height,player_size*1.2,player_bullet_speed))
                if player.num_shots > 1:
                    self.world.objects.add_object(Player_Bullet(self.world, player.pos.x-25, player.shot_image, self.player_bullets, map_width, map_height, player_size*1.2, player_bullet_speed))
                    self.world.objects.add_object(Player_Bullet(self.world, player.pos.x+25, player.shot_image, self.player_bullets, map_width, map_height, player_size*1.2, player_bullet_speed))
                if player.num_shots > 3:
                    self.world.objects.add_object(Player_Bullet(self.world, player.pos.x-25, player.shot_image_small, self.player_bullets, map_width, map_height, player_size*0.5, player_bullet_speed, -2.5))
                    self.world.objects.add_object(Player_Bullet(self.world, player.pos.x+25, player.shot_image_small, self.player_bullets, map_width, map_height, player_size*0.5, player_bullet_speed, 2.5))
        if not self.world.menu.get_paused():
            for num, player in enumerate(self.world.player_list):
                if not time.time() - player.die_time < 2:
                    if self.arduino == "DUMMY":
                        for contr_num, controller in enumerate(self.world.controllers.all_controllers):
                            if contr_num == num:
                                pressed = controller.get_pressed()
                                if isinstance(controller, pygine.controllers.Controller) or isinstance(controller, pygine.controllers.Keyboard_as_Controller):
                                    axis = controller.get_x_axis()
                                    if axis == -1 or pygine.SHOULDER_LEFT in pressed: player.vel.x = -player_speed
                                    elif axis == 1 or pygine.SHOULDER_RIGHT in pressed: player.vel.x = player_speed
                                    else: player.vel.x = 0
                                    if pygine.A in pressed or pygine.B in pressed or pygine.X in pressed or pygine.Y in pressed: shoot(player)
                                else:
                                    if pressed[pygame.K_LEFT]: player.vel.x = -player_speed
                                    elif pressed[pygame.K_RIGHT]: player.vel.x = player_speed
                                    else: player.vel.x = 0
                                    if pressed[pygame.K_SPACE]: shoot(player)
                    elif len(arduino_pressed) == NUM_BUZZERS:
                        left_pressed = arduino_pressed[TEAMS[2 * self.space_ship_index_mapping[num]]] == "1"
                        right_pressed = arduino_pressed[TEAMS[2 * self.space_ship_index_mapping[num] + 1]] == "1"
                        if left_pressed and not right_pressed:
                            player.vel.x = -player_speed
                        elif right_pressed and not left_pressed:
                            player.vel.x = player_speed
                        else:
                            player.vel.x = 0
                        shoot(player)
    def menu_selection(self, selected_in_menu: dict):
        if selected_in_menu[0] == "ports":
            port_info = list(selected_in_menu[1].values())[0]
            if port_info == "DUMMY":
                self.arduino = "DUMMY"
                self.world.background.set_style(pygine.POINT_ANIMATION)
                self.world.menu.start_menu(main_menu.get(None,self.level-1,self.endless))
            else:
                print(port_info.device)
                self.arduino = serial.Serial(port=port_info.device, baudrate=9600, timeout=1)
                if not self.arduino.isOpen(): self.arduino.open()
                self.arduino.read_until(b"\n")
                self.arduino.write(b"r\n")
                self.arduino.write(b"i\n")
                self.in_connection_selection = True
                self.world.background.set_style(pygine.EMPTY_BACKGROUND)
        elif selected_in_menu[0] == "Main":
            self.endless = bool(list(selected_in_menu[1].values())[0])
            self.level = int(list(selected_in_menu[2].values())[0])
            global map_width, map_height
            map_width = screen.get_width()
            map_height = screen.get_height()
            if self.arduino == "DUMMY":
                self.world.create_player(0, 0, 0)
                self.num_players = len(self.world.player_list)
            else:
                self.space_ship_index_mapping = []
                for num in range(len(self.space_ships)):
                    if self.enabled_buttons[TEAMS[2 * num]] + self.enabled_buttons[TEAMS[2 * num + 1]] == 2:
                        self.world.create_player(0,0,0)
                        self.space_ship_index_mapping.append(num)
                self.num_players = len(self.world.player_list)
                self.arduino.write(b'v')
                self.arduino_thread = Arduino_Read_Thread(self.arduino)
                self.arduino_thread.start()
            self.start_game()

    def update(self, events, fps, paused):
        if self.world.menu.get_paused():
            self.world.objects._update(fps)
        elif self.in_connection_selection:
            pass
        elif not paused:
            for player in self.world.player_list:
                if not player.has_shield:
                    for hit in pygame.sprite.spritecollide(player,self.ship_bullets, False):
                        player.health -= 3
                        self.world.objects.add_object(Explosion(self.world, hit.pos, self.small_explosion_images, player_size * 0.3))
                        self.world.objects.delete_object(hit)
                    if len(pygame.sprite.spritecollide(player, self.mobs, False)) > 0:
                        for mob in self.mobs:
                            if player.mask is not None and mob.mask is not None:
                                hit = pygame.sprite.collide_mask(player,mob)
                                if hit:
                                    self.world.sounds.play_sound("small explosion")
                                    player.health -= 3 * mob.mob_size
                                    self.world.objects.add_object(Explosion(self.world, mob.pos, self.small_explosion_images, player_size * 0.5))
                                    mob.randomly_set_pos()
                for hit in pygame.sprite.spritecollide(player,self.power_ups, False):
                    if hit.type == 0:
                        if player.num_shots < 5: player.num_shots += 1
                        player.last_shoot_update = time.time()
                        self.world.sounds.play_sound("power-up")
                    elif hit.type == 1:
                        player.has_shield = True
                        player.shield_time = time.time()
                        self.world.sounds.play_sound("shield")
                    elif hit.type == 2:
                        player.health += star_gain
                        if player.health > player_health: player.health = player_health
                        self.world.sounds.play_sound("power-up")
                    self.world.objects.delete_object(hit)
            for mob in self.mobs:
                for hit in pygame.sprite.spritecollide(mob, self.player_bullets, False):
                    self.points += mob.mob_size
                    self.endless_count += 1
                    self.world.sounds.play_sound("small explosion")
                    self.world.objects.delete_object(hit)
                    if random() <= power_up_chance:
                        r = choice(range(3))
                        self.world.objects.add_object(PowerUp(self.world, mob.pos,self.power_up_images[r],self.power_ups,map_height,power_up_size,power_up_speed,r))
                    self.world.objects.add_object(Explosion(self.world, hit.pos, self.small_explosion_images, mob.mob_size*1.75))
                    mob.randomly_set_pos()
            if self.boss is not None and self.boss.mask is not None:
                if pygame.sprite.spritecollide(self.boss,self.player_bullets,False):
                    for shot in self.player_bullets:
                        hit = pygame.sprite.collide_mask(self.boss,shot)
                        if hit:
                            self.world.objects.add_object(Explosion(self.world,shot.pos-vec2(0,20*(player_size/10)),self.small_explosion_images,boss_size*0.3))
                            self.boss_health -= 1
                            self.world.objects.delete_object(shot)

    def update_player(self, player:pygine.World_2d.Player, events, fps, *args):
        player.pos += player.vel*fps
        if player.pos.x < 0: player.pos.x = 0
        if player.pos.x > map_width: player.pos.x = map_width
        if player.num_shots > 1 and time.time() - player.last_shoot_update > shot_update_time:
            player.num_shots -= 1
            player.last_shoot_update = time.time()
        if player.has_shield and time.time() - player.shield_time > shield_time:
            player.has_shield = False
        if player.health <= 0:
            self.world.objects.add_object(Explosion(self.world, player.pos, self.big_explosion_images, player_size*2))
            player.lives -= 1
            player.health = player_health
            player.die_time = time.time()
            player.has_shield = True
            player.shield_time = time.time()
            player.pos = vec2(map_width/2,map_height-10)
            player.vel = vec2(0,0)
            self.world.sounds.play_sound("player die")
            if player.lives <= 0:
                if self.level > 30: self.level += 1
                self.world.objects.add_object(Explosion(self.world, player.pos, self.big_explosion_images, player_size*3))
                self.world.delete_player()
                self.world.menu.start_menu(main_menu.get(False,self.level-1,self.endless))
        if self.endless:
            if self.boss is None:
                if self.endless_count > endless_num_mobs_to_kill:
                    self.endless_mode += 1
                    self.endless_count = 0
                    for mob in self.mobs: mob.recreate = False
                    if self.endless_mode == 1:
                        for x in range(num_mobs):
                            self.world.objects.add_object(Ship(self.world, self.ship_images, self.ship_bullet_images, self.mobs, self.ship_bullets, map_width, map_height, ship_size, ship_speed_min_down, ship_speed_max_down, ship_speed_max_side, ship_bullet_time))
                    else:
                        self.endless_mode = 0
                        for mob in self.mobs: mob.recreate = False
                        self.boss = Boss(self.world,self.boss_image,self.boss_num,boss_size,self.ship_bullet_images,self.ship_images,self.ship_bullets,self.mobs,map_width,map_height,ship_size,ship_speed_min_down,ship_speed_max_down,ship_speed_max_side,ship_bullet_time)
                        self.world.objects.add_object(self.boss)
            elif self.boss_health <= 0:
                self.world.sounds.play_sound("big explosion")
                self.world.objects.add_object(Explosion(self.world,self.boss.pos,self.big_explosion_images,boss_size*3))
                self.world.objects.delete_object(self.boss)
                self.start_game(from_endless=True)
        else:
            if self.points >= needed_points:
                if self.level % 10 == 0:
                    if self.boss is None:
                        for mob in self.mobs: mob.recreate = False
                        self.boss = Boss(self.world,self.boss_image, self.boss_num, boss_size, self.ship_bullet_images, self.ship_images, self.ship_bullets, self.mobs, map_width, map_height, ship_size, ship_speed_min_down, ship_speed_max_down, ship_speed_max_side, ship_bullet_time)
                        self.world.objects.add_object(self.boss)
                    elif self.boss_health <= 0:
                        self.world.sounds.play_sound("big explosion")
                        self.world.objects.add_object(Explosion(self.world, self.boss.pos, self.big_explosion_images, boss_size * 3))
                        self.world.objects.delete_object(self.boss)
                        if self.level > 30: self.level += 1
                        self.world.objects.add_object(Explosion(self.world, player.pos, self.big_explosion_images, player_size * 3))
                        self.world.delete_player()
                        self.world.menu.start_menu(main_menu.get(True, self.level - 1, self.endless))
                else:
                    if self.level > 30: self.level += 1
                    self.world.objects.add_object(Explosion(self.world, player.pos, self.big_explosion_images, player_size * 3))
                    self.world.delete_player()
                    self.world.menu.start_menu(main_menu.get(True, self.level - 1, self.endless))

    def draw(self):
        if not self.world.menu.get_paused():
            if self.in_connection_selection:
                # ports
                left_surf = pygame.Surface((int(screen.get_width()/2),screen.get_height()),pygame.SRCALPHA)
                _,self.connecting_offset,self.connecting_zoom = pygine.draw_image_fitting_onto_surface(left_surf,self.arduino_image)
                pygine.draw_text(left_surf,"Wähle aus, welche Anschlüsse du verwendest",18,int(left_surf.get_width()/2),50*self.connecting_zoom,rect_place=pygine.CENTER)
                for count,rect in enumerate(self.connection_rects):
                    if self.enabled_buttons[count]:
                        pygame.draw.rect(left_surf,(255,0,0),(self.connecting_offset+vec2(rect.topleft)*self.connecting_zoom,vec2(rect.size)*self.connecting_zoom))
                screen.blit(left_surf,(0,0))
                s = pygame.surface.Surface(screen.get_size(), pygame.SRCALPHA)
                s.fill((0, 0, 0, 75))
                screen.blit(s, (0, 0))
                # naming
                right_surf = pygame.Surface((int(screen.get_width() / 2), screen.get_height()), pygame.SRCALPHA)
                pygine.draw_text(right_surf, "Teams und Raumschiff auswählen", 18, int(right_surf.get_width()/2), 50 * self.connecting_zoom, rect_place=pygine.CENTER)
                for (count,ship) in enumerate(self.space_ships):
                    right_surf.blit(ship,vec2(40,(screen.get_height()-len(self.space_ships)*100)/2+100*count))
                    pygine.draw_text(right_surf, "links: "+str(TEAMS[2*count]+1), 28, 150, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * count + 30, rect_place=pygine.LEFT)
                    pygine.draw_text(right_surf, "rechts: "+str(TEAMS[2*count+1]+1), 28, 150, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * count + 60, rect_place=pygine.LEFT)
                screen.blit(right_surf, (screen.get_width()/2, 0))
                if (count:=self.connection_team_selection_window) is not None:
                    if count % 2 == 0:
                        count = count/2
                        pygame.draw.rect(screen, (255, 255, 255), (screen.get_width() / 2 + 255, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * count - 30, 120, 120))
                        pygame.draw.rect(screen, (0, 0, 0), (screen.get_width() / 2 + 255, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * count - 30, 120, 120),2)
                        pygame.draw.line(screen, (0, 0, 0), (screen.get_width() / 2 + 255, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * count + 25), (screen.get_width() / 2 + 250, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * count + 30))
                        pygame.draw.line(screen, (0, 0, 0), (screen.get_width() / 2 + 255, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * count + 35), (screen.get_width() / 2 + 250, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * count + 30))
                        for num in range(NUM_BUZZERS):
                            pygine.draw_text(screen, str(num+1), 25, screen.get_width() / 2 + 277 + (num%3)*37, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * count - 7 + floor(num/3)*37, rect_place=pygine.CENTER)
                    else:
                        count = floor(count/2)
                        pygame.draw.rect(screen, (255, 255, 255), (screen.get_width() / 2 + 255, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * count, 120, 120))
                        pygame.draw.rect(screen, (0, 0, 0), (screen.get_width() / 2 + 255, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * count, 120, 120), 2)
                        pygame.draw.line(screen, (0, 0, 0), (screen.get_width() / 2 + 255, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * count + 55), (screen.get_width() / 2 + 250, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * count + 60))
                        pygame.draw.line(screen, (0, 0, 0), (screen.get_width() / 2 + 255, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * count + 65), (screen.get_width() / 2 + 250, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * count + 60))
                        for num in range(NUM_BUZZERS):
                            pygine.draw_text(screen, str(num + 1), 25, screen.get_width() / 2 + 277 + (num % 3) * 37, (screen.get_height() - len(self.space_ships) * 100) / 2 + 100 * count + 23 + floor(num / 3) * 37, rect_place=pygine.CENTER)
                #warning
                if self.connection_warning != "":
                    pygame.draw.rect(screen, (252, 51, 35), (screen.get_width()/2-screen.get_width()/3,screen.get_height()-50,screen.get_width()*(2/3),37), border_radius=8)
                    pygine.draw_text(screen,self.connection_warning,27,screen.get_width()/2,screen.get_height()-45,rect_place=pygine.TOP)
                else:
                    pygine.draw_text(screen, "Weiter mit Start/Leertaste", 20, screen.get_width()/2, screen.get_height()-15, color=(0,0,0), rect_place=pygine.CENTER)
            else:
                if not self.endless:
                    filled = self.points / needed_points
                    pygine.draw_bar(screen, True, screen.get_height() - 50, 30, filled, vec2(15, 25), self.level_bar_color)
                if self.boss is not None:
                    filled = self.boss_health / boss_health
                    pygine.draw_bar(screen, True, screen.get_height() - 50, 30, filled, vec2(15 if self.endless else 55, 25), self.boss_bar_color)
                for num,player in enumerate(self.world.player_list):
                    filled = player.health / player_health
                    pygine.draw_bar(screen, True, screen.get_height() - 50, 30, filled, vec2(screen.get_width() - 45 - 40 * num, 25), player.health_bar_color)
                    for live_num in range(player.lives):
                        screen.blit(player.small_img,(screen.get_width()-55-len(self.world.player_list)*40-(player.small_img.get_width()+5)*num,screen.get_height()-50-(player.small_img.get_height()+5)*live_num))

    def draw_player(self, player:pygine.World_2d.Player, surface:pygame.surface, offset:vec2, zoom:float):
        player.draw_image(surface, offset, zoom, pygine.BOTTOM, image_scale_factor=player_size / 10)
        if player.lives > 0 and player.has_shield and (time.time() - player.shield_time < shield_time*2/3 and not time.time() - player.die_time < 2 or (time.time() - player.shield_time) % 0.5 <= 0.25):
            screen.blit(self.shield,player.rect.midtop-vec2(self.shield.get_width()/2,25))


##ni## do not change code from here on####

##e## create and start game <250,250,164>
if __name__ == '__main__':
    g = Game()
    while True: g.loop()