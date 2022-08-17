import pygame
vec2 = pygame.math.Vector2
from typing import Any, List, Optional, Sequence, Text, Tuple, Union, overload, Iterable
from pygine import controllers
keybrd = Union[controllers.Keyboard_as_Controller,controllers.Keyboard,controllers.Keyboard_with_Mouse,controllers.Mouse]
contr = Union[controllers.Controller,controllers.Keyboard_as_Controller,controllers.Keyboard,controllers.Keyboard_with_Mouse,controllers.Mouse]
color_attr = Tuple[int,int,int]

class Menu_creator:
    def __init__(self,name="unnamed menu"):
        self.__menu_objects = []
        self.__selected_values = []
        self.__num_rows = 0
        self.__num_columns = 0
        self.menu_name = name

    def add_vertical_selection(self,title=None,values=[], min_selected=None, max_selected=None, selected_values=[0],
                               title_color=(255,255,255),title_size=25,
                               not_selected_color=(255,255,255),not_selected_size=15,
                               selected_color=(150, 200, 175),selected_size=15):
        self.__menu_objects.append(["vertical",title,values,title_color,title_size,not_selected_color,not_selected_size,selected_color,selected_size,0 if min_selected is None else min_selected,len(values) if max_selected is None else min([max_selected,len(values)])])
        self.__selected_values.append([values[i] for i in selected_values])
        self.__num_rows += len(values)
        if self.__num_columns < 1: self.__num_columns = 1

    def add_horizontal_selection(self,title=None,values=[], min_selected=None, max_selected=None, selected_values=[0],
                                 title_color=(255,255,255),title_size=25,
                                 not_selected_color=(255,255,255),not_selected_size=15,
                                 selected_color=(150, 200, 175),selected_size=15):
        self.__menu_objects.append(["horizontal",title,values,title_color,title_size,not_selected_color,not_selected_size,selected_color,selected_size,0 if min_selected is None else min_selected,len(values) if max_selected is None else min([max_selected,len(values)])])
        self.__selected_values.append([values[i] for i in selected_values])
        self.__num_rows += 1
        if self.__num_columns < len(values): self.__num_columns = len(values)

    def add_loop_selection(self,title=None,values=[], selected_values=[0],title_color=(255,255,255),title_size=25,
                           text_color=(150, 200, 175),text_size=15):
        self.__menu_objects.append(["loop",title,values,title_color,title_size,text_color,text_size])
        self.__selected_values.append([values[i] for i in selected_values])
        self.__num_rows += 1
        if self.__num_columns < 1: self.__num_columns = 1

    def add_slide(self,title=None,values=[], min_selected = 1, max_selected=1, selected_values=[0], select_by_left_right = None,
                  title_color=(255,255,255),title_size=25,
                  line_color=(255,255,255),line_width=2,
                  not_selected_style_color=(255,255,255),not_selected_style_size=5,not_selected_style="point",not_selected_text_color=(255,255,255),not_selected_text_size=13,show_not_selected_text=True,
                  selected_style_color=(150,200,175),selected_style_size=8,selected_style="point",selected_text_color=(150,200,175),selected_text_size=15,show_selected_text=True,
                  min_max_text_color=(255,255,255),min_max_text_size=18,show_min_max_text=False,edge=50):
        self.__menu_objects.append(["slide",title,values,title_color,title_size,line_color,line_width,not_selected_style_color,not_selected_style_size,not_selected_style,not_selected_text_color,not_selected_text_size,show_not_selected_text,selected_style_color,selected_style_size,selected_style,selected_text_color,selected_text_size,show_selected_text,min_max_text_color,min_max_text_size,show_min_max_text,edge,0 if min_selected is None else min_selected,len(values) if max_selected is None else min([max_selected,len(values)]),(True if min_selected == 1 and max_selected == 1 else False) if select_by_left_right is None else select_by_left_right])
        self.__selected_values.append([values[i] for i in selected_values])
        self.__num_rows += 1
        if self.__num_columns < len(values): self.__num_columns = len(values)

    def add_space(self,title=None,height=20, title_color=(255,255,255),title_size=25):
        self.__menu_objects.append(["space",title,height,title_color,title_size])

    @staticmethod
    def get_value(name, value):
        return ["val",name,value]
    @staticmethod
    def get_value_range(name,min,max,step=1.0,round_digits=0):
        return_array = []
        value = min
        while value <= max:
            return_array.append(Menu_creator.get_value(name.format(value) if "{}" in name else name,str(value)))
            if round_digits == 0: value = int(value+step)
            else: value = round(value+step,round_digits)
        return return_array
    @staticmethod
    def get_num_values(name, value, min, max):
        return ["num",name,value,min,max]
    @staticmethod
    def get_btn_value(name, function):
        return ["btn", name, function]

    # get result
    def _get_menu(self):
        return (self.__selected_values,self.__num_rows,self.__num_columns,self.__menu_objects,self.menu_name)

    # make full menu at once
    def make_menu_from_menu_objects(self, menu_objects):
        for object in menu_objects:
            if object[0] == "vertical":
                self.__menu_objects.append(object)
                self.__selected_values.append([object[2][0]])
                self.__num_rows += len(object[2])
                if self.__num_columns < 1: self.__num_columns = 1
            if object[0] == "horizontal":
                self.__menu_objects.append(object)
                self.__selected_values.append([object[2][0]])
                self.__num_rows += 1
                if self.__num_columns < len(object[2]): self.__num_columns = len(object[2])
            if object[0] == "loop":
                self.__menu_objects.append(object)
                self.__selected_values.append([object[2][0]])
                self.__num_rows += 1
                if self.__num_columns < 1: self.__num_columns = 1
            if object[0] == "slide":
                self.__menu_objects.append(object)
                self.__selected_values.append([object[2][0]])
                self.__num_rows += 1
                if self.__num_columns < len(object[2]): self.__num_columns = len(object[2])
            if object[0] == "space":
                self.__menu_objects.append(object)

class Menu:
    """a class for creating menus in your game
    The menus can be used ba mouse and controllers
    the controller select menu is a menu for selecting the players and controllers"""

    def __init__(self,world):
        self.__world = world
        self.__menu_opened = False
        self.__menu_name = "no menu"
        self.__pause_game = True
        self.__menu_objects = {}
        self.font = "arial"
        self.__selected_values = []
        self.__num_rows = 0
        self.__num_columns = 0
        self.__current_row = 0
        self.__current_column = 0
        self.current_selected_icon = "--"
        self.__height = 0
        self.__surf_size = [0,0]
        self.__allow_going_to_settings = True
        self.__in_settings = False
        self.__old_menu = []
        self.__in_player_selection = False
        self.__player_selection_settings = []
        self.__in_controller_selection = False
        self.__controller_selection_settings = []
        self.__theme_color = (0,0,0)
        self.darken_background = True
        self.__darken_opacity = 140

    # start new menu
    def start_player_selection(self,modes:{str:[int,int]}={"Multiplayer":[2,2],"Singleplayer":[1,1]},mode_title:str="Select mode",controller_title:str="Select Controllers",game_name:str=None,keyboard:keybrd=controllers.Keyboard_as_Controller()):
        num_controllers = len(controllers.get_controller_list(keyboard))
        new_modes = {}
        for name,mode in modes.items():
            if mode[0] <= num_controllers:
                new_modes[name] = mode
        if len(new_modes) == 0:
            raise Exception("There are not enough controllers for any of the modes")
        self.__player_selection_settings = [new_modes, mode_title, controller_title, game_name,keyboard]
        if len(new_modes) == 1:
            min_players = list(new_modes.values())[0][0]
            max_players = list(new_modes.values())[0][1]
            self.start_controller_selection(min_players,max_players,controller_title,game_name,keyboard)
        else:
            self.__in_player_selection = True
            self.__controller_selection_settings = [controller_title,game_name,keyboard]
            values = []
            for mode_name,num_players in new_modes.items():
                values.append(Menu_creator.get_value(mode_name,num_players))
            menu = Menu_creator("pygine build in menu - Player selection")
            if game_name != None: menu.add_space(game_name,30,title_size=45,title_color=self.__theme_color)
            menu.add_vertical_selection(mode_title, values, 1, 1, title_size=18,title_color=self.__theme_color,not_selected_color=self.__theme_color)
            self.start_menu(menu)
            self.__in_player_selection = True
    def start_controller_selection(self,min_selected:int=1,max_selected:int=1,title:str="Select Controllers",game_name:str=None,keyboard:keybrd=controllers.Keyboard_as_Controller()):
        values = []
        for contr in controllers.get_controller_list(keyboard):
            values.append(Menu_creator.get_value(contr.name, contr))
        if min_selected > len(values):
            raise Exception("not enough controllers for at least {} selected".format(min_selected))
        menu = Menu_creator("pygine build in menu - Controller selection")
        if game_name != None: menu.add_space(game_name, 30, title_size=45,title_color=self.__theme_color)
        menu.add_vertical_selection(title, values, min_selected, max_selected, list(range(min_selected)), title_size=18,title_color=self.__theme_color,not_selected_color=self.__theme_color)
        self.start_menu(menu)
        self.__in_controller_selection = True
    def start_settings_menu(self,save_old_settings:bool=False):
        if save_old_settings: self.__old_menu = [self.__selected_values,self.__num_rows,self.__num_columns,self.__menu_objects,self.__menu_name]
        else: self.__old_menu = []
        self.start_menu(self.build_settings_menu())
        self.__in_settings = True
    def load_menu(self,menu_creator:Menu_creator):
        self.__current_row = 0
        self.__current_column = 0
        self.__selected_values, self.__num_rows, self.__num_columns, self.__menu_objects, self.__menu_name = menu_creator._get_menu()
        self.__height = self.__get_height()
    def start_menu(self,menu_creator:Menu_creator):
        self.__in_controller_selection = False
        self.__in_player_selection = False
        self.__in_settings = False
        self.load_menu(menu_creator)
        self.__menu_opened = True

    # overwrite these functions for custom settings
    def build_settings_menu(self) -> Menu_creator:
        """overwrite this function to build a custom settings menu (returns a Menu_Creator object)
        also overwrite apply_settings for storing the results"""
        menu = Menu_creator("pygine build in menu - Settings")
        menu.add_space("Settings", 50, title_size=35, title_color=self.__theme_color)
        menu.add_slide("Music Volume", Menu_creator.get_value_range("Volume: {}", 0, 1, 0.05, round_digits=2), selected_values=[int(self.__world.sounds.background_music_volume * 20)], not_selected_style=None, show_not_selected_text=False, title_color=self.__theme_color, not_selected_style_color=self.__theme_color, not_selected_text_color=self.__theme_color, line_color=self.__theme_color)
        menu.add_space(height=10)
        menu.add_slide("Sound Volume", Menu_creator.get_value_range("Volume: {}", 0, 1, 0.05, round_digits=2), selected_values=[int(self.__world.sounds.sound_volume * 20)], not_selected_style=None, show_not_selected_text=False, title_color=self.__theme_color, not_selected_style_color=self.__theme_color, not_selected_text_color=self.__theme_color, line_color=self.__theme_color)
        return menu
    def apply_settings(self,selected_in_menu):
        """overwrite this function to store the selected things in settings (gets selected_in_menu passed as an attribute)
        also overwrite build_settings_menu customizing the settings menu"""
        self.__world.sounds.set_background_music_volume(float(list(selected_in_menu[1].values())[0]))
        self.__world.sounds.set_sound_volume(float(list(selected_in_menu[2].values())[0]))

    # quit and start current menu
    def quit_menu(self,going_back:bool=False) -> [[str, {str: Optional[Union[str, int]]}], bool]:
        """leaves menu, or goes back (for example from settings)
        do not use going_back as its only intended for build in menus"""
        results = [self.__menu_name]
        for obj in self.__selected_values:
            result_obj = {}
            for val in obj:
                result_obj[val[1]] = val[2]
            results.append(result_obj)
        if self.__in_settings:
            self.__in_settings = False
            # set the selected values
            self.apply_settings(results)
            if self.__old_menu:
                # return to old menu
                self.__selected_values, self.__num_rows, self.__num_columns, self.__menu_objects, self.__menu_name = self.__old_menu
                self.__height = self.__get_height()
                self.__old_menu = []
                return None, None
            else:
                # leave menu
                self.__menu_opened = False
                return results, going_back
        elif self.__in_player_selection:
            # start controller selection
            self.__in_player_selection = False
            min_players = list(results[1].values())[0][0]
            max_players = list(results[1].values())[0][1]
            self.start_controller_selection(min_players, max_players, *self.__controller_selection_settings)
            return results, going_back
        else:
            self.__in_controller_selection = False
            self.__menu_opened = False
            return results, going_back
    def begin_menu(self):
        """starts the menu after being paused"""
        self.__menu_opened = True
    def get_currently_in_menu(self) -> bool:
        """returns True if the menu is currently opened"""
        return self.__menu_opened
    
    # pause game when in menu
    def pause_game(self):
        """pause the game when in menu"""
        self.__pause_game = True
    def dont_pause_game(self):
        """do not pause the game when in menu"""
        self.__pause_game = False
    def get_pausing_game(self) -> bool:
        """whether the game is paused when in menu"""
        return self.__pause_game
    def get_paused(self):
        """return True if game should currently be paused by menu"""
        return self.__menu_opened and self.__pause_game
    
    # allow settings
    def allow_going_to_setting(self):
        """allow the user to access the settings from to current menu"""
        self.__allow_going_to_settings = True
    def dont_allow_going_to_setting(self):
        """dont allow the user to access the settings from to current menu"""
        self.__allow_going_to_settings = False
    def get_in_settings(self) -> bool:
        """returns True if the user is currently in the settings"""
        return self.__in_settings

    def set_theme_color(self,color:color_attr):
        """set the color for generated menus to see in front of background"""
        self.__theme_color = color
    def get_theme_color(self) -> color_attr:
        """return theme color (see: set_theme_color)"""
        return self.__theme_color
    def set_darken_opacity(self,opacity:int,darken_background:bool=None):
        """sets the opacity of the darkening of the background
        the opacity is between 0 and 255 (value will be forced into this range)
        pass darken_background to also turn the background darkening on or off"""
        if darken_background is not None: self.darken_background = darken_background
        self.__darken_opacity = min([max([opacity,0]),255])
    def get_darken_opacity(self) -> int:
        """return darken opacity (see: set_darken_opacity)"""
        return self.__darken_opacity
    
    # update from events
    def update(self, events:[[[int,contr,str,pygame.event]]]) -> [[str, {str: Optional[Union[str, int]]}], bool]:
        """update the menu from events
        returns the results of the menu if it was closed, else (None,None)"""
        def make_select(obj_num,item,object,min_index=9,max_index=10):
            if item in self.__selected_values[obj_num]:
                if len(self.__selected_values[obj_num]) > object[min_index]:
                    del self.__selected_values[obj_num][self.__selected_values[obj_num].index(item)]
            else:
                self.__selected_values[obj_num].append(item)
                if item[0] == "btn": item[2]()
                if len(self.__selected_values[obj_num]) > object[max_index]: del self.__selected_values[obj_num][0]

        def up_down(val):
            self.__current_row += val
            if self.__current_row < 0: self.__current_row = 0
            if self.__current_row >= self.__num_rows: self.__current_row = self.__num_rows - 1
            row_num = 0
            obj_num = -1
            for object in self.__menu_objects:
                if object[0] != "space": obj_num += 1
                if object[0] == "horizontal":
                    row_num += 1
                elif object[0] == "loop":
                    row_num += 1
                elif object[0] == "vertical":
                    row_num += 1 * len(object[2])
                elif object[0] == "slide":
                    if self.__current_row == row_num and not object[12]:
                        if self.__selected_values[obj_num][0] in object[2]:
                            self.__current_column = object[2].index(self.__selected_values[obj_num][0])
                    row_num += 1
        def left_right(val):
            row_num = 0
            obj_num = -1
            for object in self.__menu_objects:
                if object[0] != "space": obj_num += 1
                if object[0] == "horizontal" or object[0] == "slide":
                    if row_num == self.__current_row:
                        new_column = 0
                        for count in range(len(object[2])):
                            if self.__get_column_selected(count,len(object[2])):
                                new_column = max([min([count+val,len(object[2])-1]),0])
                                self.__current_column = int(((new_column+0.5) / len(object[2])) * self.__num_columns)
                                break
                        if self.__current_column < 0: self.__current_column = 0
                        if self.__current_column >= self.__num_columns: self.__current_column = self.__num_columns - 1
                        if object[0] == "slide" and object[25]:
                            if object[2][new_column] in self.__selected_values[obj_num]:
                                if len(self.__selected_values[obj_num]) > object[23]:
                                    del self.__selected_values[obj_num][self.__selected_values[obj_num].index(object[2][new_column])]
                            else:
                                self.__selected_values[obj_num].append(object[2][new_column])
                                if object[2][new_column][0] == "btn": object[2][new_column][2]()
                                if len(self.__selected_values[obj_num]) > object[24]: del self.__selected_values[obj_num][0]
                    row_num += 1
                elif object[0] == "vertical":
                    for count, item in enumerate(object[2]):
                        if row_num == self.__current_row:
                            if item[0] == "num":
                                is_selected = self.__selected_values[obj_num] == item
                                item[2] += val
                                if item[2] < item[3]: item[2] = item[3]
                                if item[2] > item[4]: item[2] = item[4]
                                if is_selected: self.__selected_values[obj_num] = item
                        row_num += 1
                elif object[0] == "loop":
                    if row_num == self.__current_row:
                        new_value_index = object[2].index(self.__selected_values[obj_num][0]) + val
                        if new_value_index < 0: new_value_index = len(object[2])-1
                        if new_value_index >= len(object[2]): new_value_index = 0
                        self.__selected_values[obj_num] = [object[2][new_value_index]]
                    row_num += 1
        def select():
            row_num = 0
            obj_num = -1
            for object in self.__menu_objects:
                if object[0] != "space": obj_num += 1
                if object[0] == "horizontal":
                    for count, item in enumerate(object[2]):
                        if row_num == self.__current_row and self.__get_column_selected(count,len(object[2])):
                            make_select(obj_num,item,object)
                    row_num += 1
                elif object[0] == "loop":
                    for count,item in enumerate(object[2]):
                        if row_num == self.__current_row:
                            if item in self.__selected_values[obj_num]:
                                if item[0] == "btn": item[2]()
                    row_num += 1
                elif object[0] == "vertical":
                    for count, item in enumerate(object[2]):
                        if row_num == self.__current_row:
                            make_select(obj_num,item,object)
                        row_num += 1
                elif object[0] == "slide":
                    for count, item in enumerate(object[2]):
                        if row_num == self.__current_row and self.__get_column_selected(count,len(object[2])):
                            make_select(obj_num,item,object,23,24)
                    row_num += 1
        def increase_decrease(val):
            row_num = 0
            obj_num = -1
            for obj_count,object in enumerate(self.__menu_objects):
                if object[0] != "space": obj_num += 1
                if object[0] == "horizontal":
                    for count, item in enumerate(object[2]):
                        if row_num == self.__current_row and self.__get_column_selected(count,len(object[2])):
                            if item[0] == "num":
                                is_selected = self.__selected_values[obj_num] == item
                                item[2] += val
                                if item[2] < item[3]: item[2] = item[3]
                                if item[2] > item[4]: item[2] = item[4]
                                if is_selected: self.__selected_values[obj_num] = item
                    row_num += 1
                elif object[0] == "loop":
                    for count, item in enumerate(object[2]):
                        if row_num == self.__current_row:
                            if item[0] == "num":
                                is_selected = self.__selected_values[obj_num] == item
                                item[2] += val
                                if item[2] < item[3]: item[2] = item[3]
                                if item[2] > item[4]: item[2] = item[4]
                                if is_selected: self.__selected_values[obj_num] = item
                    row_num += 1
                elif object[0] == "vertical":
                    for count, item in enumerate(object[2]):
                        if row_num == self.__current_row:
                            if item[0] == "num":
                                is_selected = self.__selected_values[obj_num] == item
                                item[2] += val
                                if item[2] < item[3]: item[2] = item[3]
                                if item[2] > item[4]: item[2] = item[4]
                                if is_selected: self.__selected_values[obj_num] = item
                        row_num += 1
                elif object[0] == "slide":
                    for count, item in enumerate(object[2]):
                        if row_num == self.__current_row and self.__get_column_selected(count,len(object[2])):
                            if item[0] == "num":
                                is_selected = self.__selected_values[obj_num] == item
                                item[2] += val
                                if item[2] < item[3]: item[2] = item[3]
                                if item[2] > item[4]: item[2] = item[4]
                                if is_selected: self.__selected_values[obj_num] = item
                    row_num += 1
        def go_back():
            if self.__in_controller_selection:
                if len(self.__player_selection_settings[0]) > 1:
                    self.__in_controller_selection = False
                    self.start_player_selection(*self.__player_selection_settings)
            else:
                self.quit_menu(going_back=True)

        if self.__menu_opened:
            for player_num,joy,btn_or_axis,event in events:
                if player_num is not None:
                    if isinstance(joy,controllers.Controller) or isinstance(joy,controllers.Keyboard_as_Controller):
                        if event.type == pygame.JOYAXISMOTION or event.type == pygame.JOYBUTTONDOWN or event.type == pygame.KEYDOWN:
                            if btn_or_axis == "AXIS_X": left_right(joy.get_x_axis())
                            elif btn_or_axis == "AXIS_Y": up_down(joy.get_y_axis())
                            elif btn_or_axis == "A" or btn_or_axis == "B": select()
                            elif btn_or_axis == "SH_LEFT": increase_decrease(-1)
                            elif btn_or_axis == "SH_RIGHT": increase_decrease(+1)
                            elif btn_or_axis == "START": return self.quit_menu()
                            elif btn_or_axis == "SELECT" and self.__allow_going_to_settings and not self.__in_settings: self.start_settings_menu(True)
                            elif btn_or_axis == "X" or btn_or_axis == "Y": go_back()
                    else:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_DOWN: up_down(+1)
                            elif event.key == pygame.K_UP: up_down(-1)
                            elif event.key == pygame.K_LEFT: left_right(-1)
                            elif event.key == pygame.K_RIGHT: left_right(+1)
                            elif event.key == pygame.K_RETURN: select()
                            elif event.key == pygame.K_MINUS: increase_decrease(-1)
                            elif event.key == pygame.K_PLUS: increase_decrease(+1)
                            elif event.key == pygame.K_SPACE: return self.quit_menu()
                            elif event.key == pygame.K_s and self.__allow_going_to_settings and not self.__in_settings: self.start_settings_menu(True)
                            elif event.key == pygame.K_BACKSPACE: go_back()
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            pos = vec2(event.pos)-vec2(0,(self.__surf_size[1]-self.__height)/2)
                            obj_num = -1
                            y = 0
                            for object in self.__menu_objects:
                                if object[0] == "space":
                                    y += object[2]
                                else:
                                    obj_num += 1
                                # title
                                if object[1] is not None and object[1] != "":
                                    y += object[4] + 10
                                # selection
                                if object[0] == "horizontal":
                                    height = max([object[6], object[8]]) + 5
                                    if y-height/2 < pos.y < y+height/2:
                                        num_items = len(object[2])
                                        for count, item in enumerate(object[2]):
                                            x_pos_min = self.__surf_size[0]*((count*2+0)/(num_items*2))
                                            x_pos_max = self.__surf_size[0]*((count*2+2)/(num_items*2))
                                            if x_pos_min < pos.x < x_pos_max:
                                                make_select(obj_num,item,object)
                                    y += height
                                elif object[0] == "vertical":
                                    for count, item in enumerate(object[2]):
                                        height = (max([object[6], object[8]]) + 5)
                                        if y-height/2 < pos.y < y+height/2:
                                            make_select(obj_num,item,object)
                                        y += height
                                elif object[0] == "loop":
                                    height = object[6] + 5
                                    if y-height/2 < pos.y < y+height/2:
                                        new_value_index = object[2].index(self.__selected_values[obj_num][0]) + (1 if event.button == 1 else -1)
                                        if new_value_index < 0: new_value_index = len(object[2]) - 1
                                        if new_value_index >= len(object[2]): new_value_index = 0
                                        self.__selected_values[obj_num] = [object[2][new_value_index]]
                                    y += height
                                elif object[0] == "slide":
                                    height = int(max([object[17] * 1.5 + 5 if object[18] else 0, object[11] * 1.5 + 5 if object[12] else 0, object[20] * 1.5 + 5 if object[21] else 0]))
                                    if y < pos.y < y+height:
                                        num_items = len(object[2])
                                        for count, item in enumerate(object[2]):
                                            x_pos_min = object[22] + ((self.__surf_size[0] - object[22] * 2) / (num_items - 1)) * (count-0.5)
                                            x_pos_max = object[22] + ((self.__surf_size[0] - object[22] * 2) / (num_items - 1)) * (count+0.5)
                                            if x_pos_min < pos.x < x_pos_max:
                                                make_select(obj_num,item,object,23,24)
                                    y += 20 + height
                                y += 20
                        elif event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
                            pos = vec2(event.pos) - vec2(0, (self.__surf_size[1] - self.__height) / 2)
                            obj_num = -1
                            y = 0
                            for object in self.__menu_objects:
                                if object[0] == "space":
                                    y += object[2]
                                else:
                                    obj_num += 1
                                # title
                                if object[1] is not None and object[1] != "":
                                    y += object[4] + 10
                                # selection
                                if object[0] == "horizontal":
                                    y += max([object[6], object[8]]) + 5
                                elif object[0] == "vertical":
                                    y += (max([object[6], object[8]]) + 5) * len(object[2])
                                elif object[0] == "loop":
                                    y += object[6] + 5
                                elif object[0] == "slide":
                                    height = int(max([object[17] * 1.5 + 5 if object[18] else 0, object[11] * 1.5 + 5 if object[12] else 0, object[20] * 1.5 + 5 if object[21] else 0]))
                                    if y < pos.y < y + height:
                                        num_items = len(object[2])
                                        for count, item in enumerate(object[2]):
                                            x_pos_min = object[22] + ((self.__surf_size[0] - object[22] * 2) / (num_items - 1)) * (count - 0.5)
                                            x_pos_max = object[22] + ((self.__surf_size[0] - object[22] * 2) / (num_items - 1)) * (count + 0.5)
                                            if x_pos_min < pos.x < x_pos_max:
                                                make_select(obj_num, item, object, 23, 24)
                                    y += 20 + height
                                y += 20
        return None, None
    
    # draw
    def __get_column_selected(self,column,max_column_in_row):
        return round((column/max_column_in_row)*self.__num_columns,4) <= self.__current_column < round(((column+1) / max_column_in_row) * self.__num_columns,4)
    def __get_match_font(self,font_name):
        f = pygame.font.match_font(font_name)
        if f is None: f = pygame.font.match_font(font_name + "ttf")
        if f is None: f = pygame.font.match_font(font_name + "ttc")
        return f
    def __draw_text(self, surf, text, size, x, y, color, rect_place="mid"):
        font = pygame.font.Font(self.__get_match_font(self.font), int(size))
        text_surface = font.render(str(text), True, color)
        text_rect = text_surface.get_rect()
        if rect_place == "left":
            text_rect.left = (x, y)
        elif rect_place == "mid":
            text_rect.center = (x, y)
        elif rect_place == "right":
            text_rect.right = (x, y)
        surf.blit(text_surface, text_rect)
        return text_rect
    def __get_height(self):
        y = 0
        for object in self.__menu_objects:
            if object[0] == "space":
                y += object[2]
            # title
            if object[1] is not None and object[1] != "":
                y += object[4] + 10
            # selection
            if object[0] == "horizontal":
                y += max([object[6], object[8]]) + 5
            elif object[0] == "vertical":
                y += ( max([object[6], object[8]]) + 5 )*len(object[2])
            elif object[0] == "loop":
                y += object[6] + 5
            elif object[0] == "slide":
                y += 20 + int(max([object[17] * 1.5 + 5 if object[18] else 0, object[11] * 1.5 + 5 if object[12] else 0, object[20] * 1.5 + 5 if object[21] else 0]))
            y += 20
        return y - 20
    def draw(self,surf:pygame.surface,darken_background:bool=None):
        """draws the menu onto the surface
        if passed it will set the darkening of the background, and already applies the new value"""
        # darken background
        if darken_background is not None: self.darken_background = darken_background
        if self.__menu_opened:
            if self.darken_background:
                s = pygame.surface.Surface(surf.get_size(), pygame.SRCALPHA)
                s.fill((0,0,0,self.__darken_opacity))
                surf.blit(s,(0,0))
        # menu
        y_positions = []
        size = surf.get_size()
        self.__surf_size = size
        center = surf.get_width()/2
        if self.__menu_opened:
            y = (size[1]-self.__height)/2
            y_positions.append(y)
            row_num = 0
            obj_num = -1
            for object in self.__menu_objects:
                # title
                if object[1] is not None and object[1] != "":
                    self.__draw_text(surf, object[1], object[4], center, y, object[3])
                    y += object[4]+10
                if object[0] == "space": y += object[2]
                else: obj_num += 1
                # selection
                if object[0] == "horizontal":
                    num_items = len(object[2])
                    for count,item in enumerate(object[2]):
                        text = str(item[1]) + ": " + str(item[2]) if item[0] == "num" else str(item[1])
                        text = (self.current_selected_icon+" "+text+" "+self.current_selected_icon) if row_num == self.__current_row and self.__get_column_selected(count,num_items) else text
                        x_pos = size[0]*((count*2+1)/(num_items*2))
                        if item in self.__selected_values[obj_num]:
                            self.__draw_text(surf,text,object[8],x_pos,y,object[7])
                        else:
                            self.__draw_text(surf,text,object[6],x_pos,y,object[5])
                    y += max([object[6],object[8]])+5
                    row_num += 1
                elif object[0] == "vertical":
                    for count,item in enumerate(object[2]):
                        text = str(item[1])+": "+str(item[2]) if item[0] == "num" else str(item[1])
                        text = (self.current_selected_icon+" "+text+" "+self.current_selected_icon) if row_num == self.__current_row else text
                        if item in self.__selected_values[obj_num]:
                            self.__draw_text(surf, text, object[8], center, y, object[7])
                        else:
                            self.__draw_text(surf, text, object[6], center, y, object[5])
                        y += max([object[6],object[8]])+5
                        row_num += 1
                elif object[0] == "loop":
                    for count,item in enumerate(object[2]):
                        if item in self.__selected_values[obj_num]:
                            text = str(item[1])+": " +str(item[2]) if item[0] == "num" else str(item[1])
                            text = (self.current_selected_icon+" " + text + " "+self.current_selected_icon) if row_num == self.__current_row else text
                            self.__draw_text(surf,text,object[6],center,y,object[5])
                    y += object[6]+5
                    row_num += 1
                elif object[0] == "slide":
                    if len(object[2]) > 1:
                        pygame.draw.line(surf, object[5],(object[22],y+10),(size[0]-object[22],y+10),object[6])
                        num_items = len(object[2])
                        for count,item in enumerate(object[2]):
                            x_pos = object[22]+((size[0]-object[22]*2)/(num_items-1))*count
                            text = str(item[1])+": "+str(item[2]) if item[0] == "num" else str(item[1])
                            text = (self.current_selected_icon+" " + text + " "+self.current_selected_icon) if row_num == self.__current_row and self.__get_column_selected(count,num_items) else text
                            if item in self.__selected_values[obj_num]:
                                if object[15] == "line":
                                    pygame.draw.line(surf,object[13],(x_pos,y),(x_pos,y+20),object[14])
                                if object[15] == "point":
                                    pygame.draw.circle(surf,object[13],(x_pos,y+10),object[14])
                                if object[18]:
                                    self.__draw_text(surf,text,object[17],x_pos,y+20+object[17]/2,object[16])
                            else:
                                if object[9] == "line":
                                    pygame.draw.line(surf,object[7],(x_pos,y),(x_pos,y+20),object[8])
                                if object[9] == "point":
                                    pygame.draw.circle(surf,object[7],(x_pos,y+10),object[8])
                                if object[12]:
                                    self.__draw_text(surf,text,object[11],x_pos,y+20+object[11]/2,object[10])
                        if object[21]:
                            self.__draw_text(surf, object[2][0][1], object[20], object[22], y + 20 + object[20]/2, object[19])
                            self.__draw_text(surf, object[2][-1][1], object[20], size[0]-object[22], y + 20+object[20]/2, object[19])
                        y += 20 + int(max([object[17]*1.5+5 if object[18] else 0,object[11]*1.5+5 if object[12] else 0,object[20]*1.5+5 if object[21] else 0]))
                    row_num += 1
                y_positions.append(y)
                y += 20
            pixel_color = surf.get_at((int(center),int(surf.get_height()-15)))
            if .2126 * (pixel_color.r/255) + .7152 * (pixel_color.g/255) + .0722 * (pixel_color.b/255) <= 0.5:
                self.__draw_text(surf, "Weiter mit Start/Leertaste (Select/S für Einstellungen)", 20, center, surf.get_height()-15, (255,255,255))
            else:
                self.__draw_text(surf, "Weiter mit Start/Leertaste (Select/S für Einstellungen)", 20, center, surf.get_height()-15, (0,0,0))
        return y_positions

    # get menu
    def get_current_menu_name(self) -> str: return self.__menu_name
    def _get_menu(self):
        return self.__menu_objects
    def _get_selection(self):
        return self.__selected_values
    def _get_current_column_and_row(self):
        return self.__current_column,self.__current_row

    # save
    def get_code(self) -> [str]:
        """return a list of code lines needed to get this menu"""
        code_lines = ["menu = pygine.Menu_creator()"]
        for menu_object in self._get_menu():
            line = ""
            # menu objects
            if menu_object[0] == "vertical":
                line += """menu.add_vertical_selection("{1}",{11},{9},{10},[0],{3},{4},{5},{6},{7},{8})"""
            elif menu_object[0] == "horizontal":
                line += """menu.add_horizontal_selection("{1}",{11},{9},{10},[0],{3},{4},{5},{6},{7},{8})"""
            elif menu_object[0] == "loop":
                line += """menu.add_loop_selection("{1}",{7},[0],{3},{4},{5},{6})"""
            elif menu_object[0] == "slide":
                line += """menu.add_slide("{1}",{26},{23},{24},[0],{25},{3},{4},{5},{6},{7},{8},pygine."""+menu_object[9].upper()+""",{10},{11},{12},{13},{14},pygine."""+menu_object[15].upper()+""",{16},{17},{18},{19},{20},{21},{22})"""
            elif menu_object[0] == "space":
                line += """menu.add_space("{1}",{2},{3},{4})"""
            # values
            if menu_object[0] != "space":
                value_string = "["
                for count,val in enumerate(menu_object[2]):
                    if val[0] == "val":
                        if type(val[2]) == int:
                            value_string += """pygine.Menu_creator.get_value("{1}",{2})""".format(*val)
                        else:
                            value_string += """pygine.Menu_creator.get_value("{1}","{2}")""".format(*val)
                    if val[0] == "num":
                        value_string += """pygine.Menu_creator.get_num_values("{1}",{2},{3},{4})""".format(*val)
                    if val[0] == "btn":
                        value_string += """pygine.Menu_creator.get_btn_value("{}",{})""".format(val[1],val[2].__name__)
                    value_string += ","
                value_string = value_string[:-1]
                value_string += "]"
                code_lines.append(line.format(*menu_object,value_string))
            else:
                code_lines.append(line.format(*menu_object))
        return code_lines
    def save_to_file(self,file:str):
        """saves file that creates this background
        Ignores whether there is already something in the file or not"""
        code_lines = ["import pygine","","def get():"]
        for line in self.get_code():
            code_lines.append("    "+line)
        code_lines.append("    return menu")
        with open(file, 'w') as writer:
            for line in code_lines:
                writer.write(line+"\n")
    def overwrite_to_file(self,file:str):
        """saves file that creates this background
        but only overwrites the get() method"""
        in_get_method = False
        code_lines = []
        with open(file, 'r') as reader:
            for line in reader.readlines():
                if not in_get_method:
                    code_lines.append(line.rstrip())
                if line.startswith("def get("):
                    in_get_method = True
                    for line in self.get_code():
                        code_lines.append("    " + line)
                    code_lines.append("    return menu")
                    code_lines.append("")
                if line.rstrip() == "":
                    in_get_method = False
        with open(file, 'w') as writer:
            for line in code_lines:
                writer.write(line+"\n")

def get_num_players_from_player_menu(selected_in_menu):
    """pass in the results of the player selection menu and returns a tuple of (min num players,max num players)
    raises an Exception when the passed selection is not fom a selection menu"""
    if selected_in_menu[0] != "pygine build in menu - Player selection":
        raise Exception("passed selection is not from a player selection")
    return list(selected_in_menu[1].values())[0]

def get_controller_list_from_controller_menu(selected_in_menu):
    """pass in the results of the controller selection menu and returns a list of the selected controllers
    raises an Exception when the passed selection is not fom a controller menu"""
    if selected_in_menu[0] != "pygine build in menu - Controller selection":
        raise Exception("passed selection is not from a controller selection")
    return list(selected_in_menu[1].values())


if __name__ == '__main__':
    # test menus
    pygame.init()
    screen = pygame.display.set_mode((800, 600),pygame.RESIZABLE)

    cntr = controllers.Controller_Handler(None,controllers.Keyboard_with_Mouse())
    class B:
        background_music_volume = 0.5
        sound_volume = 0.8
        def set_background_music_volume(self,val): B.background_music_volume = val
        def set_sound_volume(self, val): B.sound_volume = val
    class A: sounds = B()
    handler = Menu(A())
    handler.set_theme_color((255,255,255))
    menu = Menu_creator()
    menu.add_vertical_selection("Vertical",[Menu_creator.get_value("value1","value1"),Menu_creator.get_num_values("number1",5,0,10),Menu_creator.get_btn_value("press here 1",lambda: print("hi 1"))])
    menu.add_horizontal_selection("horizontal",[Menu_creator.get_value("value2","value2"),Menu_creator.get_num_values("number2",6,0,10),Menu_creator.get_btn_value("press here 2",lambda: print("hi 2"))])
    menu.add_loop_selection("loop",[Menu_creator.get_value("value3","value3"),Menu_creator.get_num_values("number3",7,0,10),Menu_creator.get_btn_value("press here 3",lambda: print("hi 3"))])
    menu.add_slide("slide",[Menu_creator.get_value("value4","value4"),Menu_creator.get_num_values("number4",4,0,10),Menu_creator.get_btn_value("press here 4",lambda: print("hi 4"))])
    menu.add_slide("Level selection",Menu_creator.get_value_range("Level {}",1,50),show_min_max_text=True,show_not_selected_text=False,show_selected_text=True,not_selected_style=None,edge=100)
    handler.start_menu(menu)
    #handler.start_player_selection(game_name="Game")#modes={None:[1,2]})

    while True:
        screen.fill((0,0,0))
        handler.draw(screen)
        event = pygame.event.get()
        for ev in event:
            if ev.type == pygame.QUIT: pygame.quit()
            if ev.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((ev.w,ev.h),pygame.RESIZABLE)
        selected_things, go_back = handler.update([cntr.event(ev) for ev in event])
        if selected_things is not None:
            print(selected_things)
            pygame.quit()
        pygame.display.flip()
