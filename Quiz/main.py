##i##
import pygame
from os import path
import sys
import serial
import time
from math import floor
path_name = path.split(path.dirname(__file__))[0]
if path_name not in sys.path:
    sys.path.append(path_name)
print("adding pygine path:", path_name)
import pygine
from menus import port_selection_menu
from menus import quiz_selection_menu
from Quiz import Quiz, get_quiz_list
from objects.Answer_Correct_Selection import *
from objects.Leader_Board import Leader_Board
vec2 = pygame.math.Vector2
vec3 = pygame.math.Vector3
project_name = 'Quiz'
##ni##

##e## game values and pygame init
width = 1200  # <attr={"name":"Screenwidth","type":"int","default":1280,"low":200,"high":4000}>
height = 750  # <attr={"name":"Screenheight","type":"int","default":720,"low":200,"high":4000}>
FPS = 60  # <attr={"name":"Frames per second","type":"int","default":60,"low":20,"high":240}>
pygame.init()
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
title = "Quiz"  # <attr={"name":"Window title","type":"string","default":"Game"}>
pygame.display.set_caption(title)
clock = pygame.time.Clock()

ALLOW_DUMMY = True #<attr={"name":"Allow keyboard as dummy for testing", "type":"bool",  "default":True}>

NUM_BUZZERS = 8
TEAMS = {"Rot":(245, 60, 35),"Orange":(219, 139, 11),"Gelb":(205, 160, 0),"Grün":(0, 156, 5),"Türkis":(25, 180, 150),"Blau":(35, 68, 255),"Lila":(130, 9, 179),"Pink":(235, 0, 235)}

class Game:
    def __init__(self):

        ##e## create a World object and load a world from file <255,154,100>
        self.world = pygine.World_2d()
        self.world.controllers.add_controller(pygine.Keyboard_with_Mouse())
        self.world.menu.build_settings_menu = self.settings_menu
        self.world.menu.apply_settings = self.apply_settings

        ##e## make background
        self.world.background.set_style(pygine.IMAGE)
        self.world.background.image_background.set_image_from_file(pygine.get_file_path(project_name,["img","plug_in.png"]))
        self.world.background.image_background.set_resize_full(True,True)
        self.world.background.point_background.set_background_color((0, 0, 50))
        self.world.background.point_background.set_line_color((0, 45, 150))
        self.world.background.point_background.set_node_color((5, 30, 125))
        self.world.background.point_background.set_connection_distance(100)
        self.world.background.point_background.set_line_width(5)
        self.world.background.point_background.set_node_size(8)
        self.world.background.point_background.set_max_speed(2)

        ##e## connection to arduino
        self.arduino_image = pygine.load_image(project_name, ["img", "arduino.png"])
        self.arduino:serial.Serial = None
        self.in_connection_selection = False  # ports are selected
        self.connection_team_selection_window = None
        self.connection_warning = ""
        self.connecting_offset, self.connecting_zoom = vec2(0,0), 1
        self.connection_rects = [pygame.Rect(124,121,22,54),pygame.Rect(207,121,22,54),pygame.Rect(124,188,22,54),pygame.Rect(207,188,22,54),pygame.Rect(124,258,22,54),pygame.Rect(207,258,22,54),pygame.Rect(124,325,22,54),pygame.Rect(207,325,22,54)]
        self.enabled_buttons = [True for i in range(NUM_BUZZERS)]
        self.naming_player_selected = 0
        self.player_names = [f"Spieler {i+1}" for i in range(8)]
        self.teams = list(TEAMS.keys())

        ##e## question
        self.quiz_list = get_quiz_list(project_name)
        self.quiz:Quiz = None
        self.in_asking_question = False  # question is shown and asked
        self.in_asking_correct = False  # waiting for game leader to click whether answer was correct or not
        self.in_showing_results = False  # showing results of answer
        self.in_show_quiz_result = False  # showing result of quiz
        self.answering_player = 0
        self.points = [0 for i in range(NUM_BUZZERS)]
        self.leader_board = None

        self.text_size = 1
        self.world.menu.start_menu(port_selection_menu.get(ALLOW_DUMMY))
        ##c##

    def loop(self):
        fps = clock.tick(FPS)/FPS
        screen.fill((255,255,255))

        ##e## input from player (pygame events) <164,255,100>
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                if self.arduino is not None and self.arduino != "DUMMY":
                    self.arduino.write(b'o\n')
                pygame.quit()
            else:
                self.handle_event(event)
        self.check_button_pressed()

        ##e## update movement, ... <255,90,255>
        if self.in_connection_selection and self.world.menu.get_paused():
            self.in_connection_selection = False
        else:
            selected_in_menu, go_back = self.world.update_game(events,fps)
            if selected_in_menu is not None: self.menu_selection(selected_in_menu)
        self.update(events, fps, self.world.paused)

        ##e## render and flip display <164,255,255>
        self.world.draw(screen)
        self.draw()
        pygame.display.flip()
        ##c##

    def handle_event(self, event:pygame.event):
        global screen
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((max([1000, event.w]), max([575, event.h])), pygame.RESIZABLE)
            if self.quiz is not None and (self.in_asking_question or self.in_showing_results):
                self.quiz.set_question_attributes((max([1000, event.w]), max([575, event.h])),self.text_size)  # recalculate all the sizes needed to draw the question
        elif self.arduino == "DUMMY" and self.in_asking_question:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                self.in_asking_question = False
                self.in_asking_correct = True
                add_correct_selection(self.world, screen)
                self.quiz.answer_given()
                self.answering_player = 0
        elif not self.world.menu.get_paused():
            if self.in_connection_selection:
                # select ports and name players
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.connection_warning = ""
                    if event.pos[0] < screen.get_width()/2:
                        for count,rect in enumerate(self.connection_rects):
                            click_rect = pygame.Rect(self.connecting_offset+vec2(rect.topleft)*self.connecting_zoom,vec2(rect.size)*self.connecting_zoom)
                            if click_rect.collidepoint(event.pos):
                                self.enabled_buttons[count] = not self.enabled_buttons[count]
                                if self.arduino != "DUMMY":
                                    text = "c"+"".join([str(int(enabled)) for enabled in self.enabled_buttons])+"\n"
                                    self.arduino.write(text.encode("ascii"))
                                break
                    else:
                        found = False
                        y_start = int(screen.get_height()/2 - (NUM_BUZZERS*55)/2)
                        for num in range(NUM_BUZZERS):
                            if pygame.Rect(int(screen.get_width()*(3/4)-75), y_start+num*55-20, 250, 40).collidepoint(event.pos):
                                found = True
                                self.connection_team_selection_window = None
                                self.naming_player_selected = num
                                self.player_names[self.naming_player_selected] = ""
                            if pygame.Rect(int(screen.get_width()*(3/4)-120),y_start+num*55-15,30,30).collidepoint(event.pos):
                                found = True
                                self.connection_team_selection_window = num
                            if (count:=self.connection_team_selection_window) is not None:
                                if count == num:
                                    if pygame.Rect(screen.get_width() * 3 / 4 - 250, y_start + count * 55 - 60, 120, 120).collidepoint(event.pos):
                                        found = True
                                        self.connection_team_selection_window = None
                                        new_color_idx = floor((event.pos[0]-screen.get_width()*3/4+250)/37) + floor((event.pos[1]-y_start-count*55+60)/37)*3
                                        if new_color_idx < len(TEAMS):
                                            self.teams[num] = list(TEAMS.keys())[new_color_idx]
                        if not found:
                            self.connection_team_selection_window = None
                            self.naming_player_selected = None
                if event.type == pygame.KEYDOWN:
                    warning = self.connection_warning
                    self.connection_warning = ""
                    if event.key == pygame.K_SPACE:
                        warning_found = False
                        if True not in self.enabled_buttons:
                            warning_found = True
                            self.connection_warning = "Keine Buttons gewählt"
                        for num in range(NUM_BUZZERS):
                            if self.enabled_buttons[num] and self.player_names[num] == "" and not warning_found:
                                warning_found = True
                                self.connection_warning = "Mindestens 1 aktiver Spieler hat keinen Name"
                        if self.naming_player_selected is not None and warning != "Drücke nochmal Leertaste für weiter" and not warning_found:
                            warning_found = True
                            self.connection_warning = "Drücke nochmal Leertaste für weiter"
                        if not warning_found:
                            self.world.background.set_style(pygine.IMAGE)
                            self.world.background.image_background.keep_ratio()
                            self.world.background.image_background.set_image_from_surface(pygine.load_image(project_name, ["img", "default_background.png"]))
                            self.world.background.image_background.set_resize_full(False, False)
                            self.world.menu.start_menu(quiz_selection_menu.get(self.quiz_list))
                            if self.arduino != "DUMMY":
                                self.arduino.write(b'o\n')
                                text = "t" + "".join([str(list(TEAMS.keys()).index(t)) for t in self.teams]) + "\n"
                                self.arduino.write(text.encode("ascii"))
                    # name players
                    elif event.type == pygame.KEYDOWN and self.naming_player_selected is not None:
                        if event.key == pygame.K_RETURN: self.naming_player_selected = None
                        elif event.key == pygame.K_TAB:
                            if pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]: self.naming_player_selected -= 1
                            else: self.naming_player_selected += 1
                            if self.naming_player_selected >= NUM_BUZZERS: self.naming_player_selected = NUM_BUZZERS - 1
                            elif self.naming_player_selected < 0: self.naming_player_selected = 0
                            else: self.player_names[self.naming_player_selected] = ""
                        else:
                            if event.key == pygame.K_BACKSPACE:
                                self.player_names[self.naming_player_selected] = self.player_names[self.naming_player_selected][:-1]
                            elif len(self.player_names[self.naming_player_selected]) < 12:
                                self.player_names[self.naming_player_selected] += event.unicode
            elif event.type == pygame.KEYDOWN and not self.world.menu.get_paused() and event.key == pygame.K_s:
                self.world.menu.start_settings_menu()
            elif self.in_asking_correct:
                # select answer correct or wrong
                if event.type == pygame.MOUSEBUTTONDOWN:
                    correct = None
                    if pygame.Rect(screen.get_width() * (1 / 3) - 87, screen.get_height() / 2 - 25, 175, 50).collidepoint(event.pos): correct = False
                    if pygame.Rect(screen.get_width() * (2 / 3) - 87, screen.get_height() / 2 - 25, 175, 50).collidepoint(event.pos): correct = True
                    if correct is not None:
                        before = self.get_leader_board()
                        self.points[self.answering_player] += self.quiz.get_points(correct)
                        after = self.get_leader_board()
                        self.in_asking_correct = False
                        if self.quiz.next_question(correct,screen.get_size(),self.text_size): self.in_show_quiz_result = True
                        else: self.in_showing_results = True
                        self.world.objects[0].show_results(correct,screen)
                        self.world.objects[-1].show_results(correct,screen)
                        if self.get_using_teams():
                            self.leader_board = Leader_Board(self.world, self.teams[self.answering_player], before, after, screen, self.get_using_teams(), {self.player_names[num]:self.teams[num] for num in range(NUM_BUZZERS)}, self.player_names, self.quiz.text_color, self.quiz.rect_color,self.quiz.text_on_rect_color, self.text_size, self.in_show_quiz_result)
                        else:
                            self.leader_board = Leader_Board(self.world,self.player_names[self.answering_player],before,after,screen, self.get_using_teams(), {self.player_names[num]:self.teams[num] for num in range(NUM_BUZZERS)}, self.player_names, self.quiz.text_color, self.quiz.rect_color,self.quiz.text_on_rect_color, self.text_size, self.in_show_quiz_result)
                        self.world.objects.add_object(self.leader_board)
                        if self.arduino != "DUMMY": self.arduino.write(b'o\n')
            elif self.in_showing_results:
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    self.world.objects.delete_all()
                    self.in_showing_results = False
                    self.in_asking_question = True
                    if self.arduino != "DUMMY": self.arduino.write(b's\n')
            elif self.in_show_quiz_result:
                if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN) and time.time()-self.leader_board.time > 3:
                    self.world.objects.delete_all()
                    self.in_show_quiz_result = False
                    if self.arduino != "DUMMY": self.arduino.write(b'i\n')
                    self.points = [0 for i in range(NUM_BUZZERS)]
                    self.world.background.set_style(pygine.EMPTY_BACKGROUND)
                    self.in_connection_selection = True
                    self.naming_player_selected = None
    def menu_selection(self, selected_in_menu: dict):
        """reacts to selection of port or quiz"""
        if selected_in_menu[0] == "ports":
            port_info = list(selected_in_menu[1].values())[0]
            if port_info == "DUMMY":
                print("Using Dummy game not probably playable")
                self.arduino = "DUMMY"
            else:
                print(port_info.device)
                self.arduino = serial.Serial(port=port_info.device, baudrate=9600,timeout=1)
                if not self.arduino.isOpen(): self.arduino.open()
                self.arduino.read_until(b"\n")
                self.arduino.write(b"r\n")
                self.arduino.write(b"i\n")
            self.in_connection_selection = True
            self.player_names[self.naming_player_selected] = ""
            self.world.background.set_style(pygine.EMPTY_BACKGROUND)
        elif selected_in_menu[0] == "quize":
            self.quiz = Quiz(list(selected_in_menu[1].values())[0].file_name,project_name)
            self.world.background.set_style(pygine.IMAGE)
            self.world.background.image_background.set_image_from_surface(pygine.load_image(project_name, ["img", self.quiz.background]))
            self.world.background.image_background.set_resize_full(False, False)
            self.quiz.start_question(screen.get_size(),self.text_size)
            self.in_asking_question = True
            if self.arduino != "DUMMY": self.arduino.write(b's\n')
    def check_button_pressed(self):
        """when in_asking_question, check whether button was pressed and if yes start correct selection"""
        if self.in_asking_question and self.arduino != "DUMMY":
            self.arduino.reset_input_buffer()
            self.arduino.write(b'g\n')
            try:
                pressed_button = int(self.arduino.read_until(b'\n').rstrip())
                if pressed_button != 0:
                    self.in_asking_question = False
                    self.in_asking_correct = True
                    add_correct_selection(self.world,screen)
                    self.quiz.answer_given()
                    self.answering_player = pressed_button-1
            except Exception:
                pass

    def update(self, events, fps, paused):
        pass

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
                pygine.draw_text(right_surf, "Namen und Teams auswählen", 18, int(right_surf.get_width()/2), 50 * self.connecting_zoom, rect_place=pygine.CENTER)
                y_start = int(screen.get_height()/2 - (NUM_BUZZERS*55)/2)
                for count,name in enumerate(self.player_names):
                    color = (0,0,0) if self.enabled_buttons[count] else (140,140,140)
                    pygine.draw_text(right_surf,str(count+1)+":",25,int(right_surf.get_width()/2-145),y_start+count*55,rect_place=pygine.RIGHT,color=color)
                    pygame.draw.circle(right_surf,TEAMS[self.teams[count]],(int(right_surf.get_width()/2-105),y_start+count*55),15)
                    if self.naming_player_selected == count: pygame.draw.rect(right_surf, (30,70,230), (int(right_surf.get_width()/2-75), y_start+count*55-20, 250, 40), 3)
                    else: pygame.draw.rect(right_surf,color,(int(right_surf.get_width()/2-75),y_start+count*55-20,250,40),2)
                    pygine.draw_text(right_surf,name,30,int(right_surf.get_width()/2-72),y_start+count*55,rect_place=pygine.LEFT,color=color)
                screen.blit(right_surf, (screen.get_width()/2, 0))
                if (count:=self.connection_team_selection_window) is not None:
                    pygame.draw.rect(screen, (255, 255, 255), (screen.get_width() * 3 / 4 - 130 - 120, y_start + count * 55 - 60, 120, 120))
                    pygame.draw.rect(screen, (0, 0, 0), (screen.get_width() * 3 / 4 - 130 - 120, y_start + count * 55 - 60, 120, 120),2)
                    pygame.draw.line(screen, (0, 0, 0), (screen.get_width() * 3 / 4 - 130, y_start + count * 55 - 5), (screen.get_width() * 3 / 4 - 120, y_start + count * 55), 2)
                    pygame.draw.line(screen, (0, 0, 0), (screen.get_width() * 3 / 4 - 130, y_start + count * 55 + 5), (screen.get_width() * 3 / 4 - 120, y_start + count * 55), 2)
                    for num, color in enumerate(TEAMS):
                        pygame.draw.circle(screen,TEAMS[color],(screen.get_width() *3/4 - 227 + (num%3)*37, y_start + count*55 + floor(num/3)*37 - 37),15)
                #warning
                if self.connection_warning != "":
                    pygame.draw.rect(screen, (252, 51, 35), (screen.get_width()/2-screen.get_width()/3,screen.get_height()-50,screen.get_width()*(2/3),37), border_radius=8)
                    pygine.draw_text(screen,self.connection_warning,27,screen.get_width()/2,screen.get_height()-45,rect_place=pygine.TOP)
                else:
                    pygine.draw_text(screen, "Weiter mit Start/Leertaste", 20, screen.get_width()/2, screen.get_height()-15, color=(0,0,0), rect_place="center")
            elif self.in_asking_question:
                self.quiz.draw(screen)
            elif self.in_asking_correct or self.in_showing_results or (self.in_show_quiz_result and self.leader_board.get_draw_on_top()):
                text = f"{self.teams[self.answering_player]} - {self.player_names[self.answering_player]}" if self.get_using_teams() else f"{self.player_names[self.answering_player]}"
                pygine.draw_text(screen, text, 35*self.text_size, screen.get_width()/2, 50, color=self.quiz.text_color, rect_place=pygine.CENTER)
                if self.in_showing_results:
                    pygine.draw_text(screen,"weiter",27,screen.get_width()-15,screen.get_height()-15,color=(150,150,150),rect_place=pygine.RIGHT_BOTTOM)
            if self.in_show_quiz_result:
                pygine.draw_text(screen,"neues Quiz",27,screen.get_width()-15,screen.get_height()-15,color=(150,150,150),rect_place=pygine.RIGHT_BOTTOM)

    def get_using_teams(self) -> bool:
        teams = {team:0 for team in self.teams}
        for num in range(NUM_BUZZERS):
            if self.enabled_buttons[num]:
                teams[self.teams[num]] += 1
                if teams[self.teams[num]] > 1:
                    return True
        return False

    def get_leader_board(self):
        if self.get_using_teams():
            dict = {}
            for num in range(NUM_BUZZERS):
                if self.enabled_buttons[num]:
                    if not self.teams[num] in dict:
                        dict[self.teams[num]] = 0
                    dict[self.teams[num]] += self.points[num]
        else:
            dict = {self.player_names[i]:self.points[i] for i in range(8) if self.enabled_buttons[i]}
        return sorted(dict.items(), key=lambda item: item[1], reverse=True)

    def settings_menu(self):
        menu = pygine.Menu_creator("settings")
        menu.add_slide("Textgröße",pygine.Menu_creator.get_value_range("{}",0.2,2.0,0.05,2),selected_values=[int(self.text_size/0.05)-4],not_selected_style="",show_not_selected_text=False,show_min_max_text=True)
        return menu
    def apply_settings(self,selected_in_menu):
        self.text_size = float(list(selected_in_menu[1].values())[0])
        if self.quiz is not None and (self.in_asking_question or self.in_showing_results):
            self.quiz.set_question_attributes(screen.get_size(),self.text_size)

##e## create and start game <250,250,164>
if __name__ == '__main__':
    g = Game()
    while True: g.loop()
