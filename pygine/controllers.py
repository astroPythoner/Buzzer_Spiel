import pygame
import platform
from typing import Any, List, Optional, Sequence, Text, Tuple, Union, overload, Iterable

#Pins-Mapping: (A, B, X, Y, SELECT, START, SHOULDER_LEFT, SHOULDER_RIGHT, AXIS_X, AXIS_Y)
joystick_mappings = {
            'USB Gamepad__Darwin': {
                'name'      : "USB Gamepad",
                'A'         : 1,
                'B'         : 2,
                'X'         : 0,
                'Y'         : 3,
                'SELECT'    : 8,
                'START'     : 9,
                'SH_LEFT'   : 4,
                'SH_RIGHT'  : 5,
                'AXIS_X'    : 3,
                'AXIS_Y'    : 4
            },
            'USB Gamepad': {
                'name'      : "USB Gamepad",
                'A'         : 1,
                'B'         : 2,
                'X'         : 0,
                'Y'         : 3,
                'SELECT'    : 8,
                'START'     : 9,
                'SH_LEFT'   : 4,
                'SH_RIGHT'  : 5,
                'AXIS_X'    : 0,
                'AXIS_Y'    : 1
            },
            'GPIO Controller 1': {
                'name'      : "Builtin Controller",
                'A'         : 0,
                'B'         : 1,
                'X'         : 3,
                'Y'         : 4,
                'SELECT'    : 10,
                'START'     : 11,
                'SH_LEFT'   : 7,
                'SH_RIGHT'  : 6,
                'AXIS_X'    : 0,
                'AXIS_Y'    : 1
            },
            'Controller (Xbox One For Windows)': {
                'name'      : "X-Box Controller",
                'A'         : 0,
                'B'         : 1,
                'X'         : 2,
                'Y'         : 3,
                'SELECT'    : 6,
                'START'     : 7,
                'SH_LEFT'   : 4,
                'SH_RIGHT'  : 5,
                'AXIS_X'    : 0,
                'AXIS_Y'    : 1
            },
            'Sony Interactive Entertainment Controller': {
                'name'      : "Playstation 1 Controller",
                'A'         : 1,
                'B'         : 2,
                'X'         : 0,
                'Y'         : 3,
                'SELECT'    : 8,
                'START'     : 9,
                'SH_LEFT'   : 6,
                'SH_RIGHT'  : 7,
                'AXIS_X'    : 0,
                'AXIS_Y'    : 1
            },
            'Gasia Co.,Ltd PS(R) Gamepad': {
                'name'      : "Playstation 2 Controller",
                'A'         : 1,
                'B'         : 2,
                'X'         : 0,
                'Y'         : 3,
                'SELECT'    : 8,
                'START'     : 9,
                'SH_LEFT'   : 6,
                'SH_RIGHT'  : 7,
                'AXIS_X'    : 0,
                'AXIS_Y'    : 1
            },
            'PLAYSTATION(R)3 Controller': {
                'name'      : "Playstation 3 Controller",
                'A'         : 13,
                'B'         : 14,
                'X'         : 12,
                'Y'         : 15,
                'SELECT'    : 0,
                'START'     : 3,
                'SH_LEFT'   : 10,
                'SH_RIGHT'  : 11,
                'AXIS_X'    : 0,
                'AXIS_Y'    : 1
            },
            'MY-POWER CO.,LTD. SPEEDLINK COMPETITION PRO': {
                'name'      : "Jostick",
                'A'         : 0,
                'B'         : 1,
                'X'         : None,
                'Y'         : None,
                'SELECT'    : 2,
                'START'     : 3,
                'SH_LEFT'   : None,
                'SH_RIGHT'  : None,
                'AXIS_X'    : 0,
                'AXIS_Y'    : 1
            },
            'SPEEDLINK COMPETITION PRO Game Controller for Android': {
                'name'      : "Joystick",
                'A'         : 0,
                'B'         : 1,
                'X'         : None,
                'Y'         : None,
                'SELECT'    : 2,
                'START'     : 3,
                'SH_LEFT'   : None,
                'SH_RIGHT'  : None,
                'AXIS_X'    : 0,
                'AXIS_Y'    : 1
            }
        }

class Controller():
    """A controller has the keys A,B,X,Y, Left and Right shoulder, and a joystick, select and start"""
    def __init__(self,joystick:pygame.joystick.Joystick):
        self.__joystick = joystick
        self.__name = joystick.get_name().strip()

        self.__allow_axis_floats = False

        #mapping
        name_with_os = self.name + "__" + platform.system()
        if name_with_os in joystick_mappings.keys():
            self.__mapping = joystick_mappings[name_with_os]
            self.__name = self.__mapping["name"]
            self.__mapping_name = name_with_os
        elif self.name in joystick_mappings.keys():
            self.__mapping = joystick_mappings[self.name]
            self.__name = self.__mapping["name"]
            self.__mapping_name = self.name
        else:
            self.__mapping = None
            self.__mapping_name = None
            print("Warning: no mapping for that controller "+self.__name)

    @property
    def name(self) -> str: return self.__name
    @property
    def has_mapping(self) -> bool: return self.__mapping is not None
    @property
    def controller(self) -> pygame.joystick.Joystick: return self.__joystick

    def allow_axis_floats(self): self.__allow_axis_floats = True
    def dont_allow_axis_floats(self): self.__allow_axis_floats = False
    def get_allow_axis_floats(self) -> bool: return self.__allow_axis_floats

    def get_pressed(self) -> [str]:
        """returns a list of all the pressed buttons (axis are ignored)"""
        pressed = []
        if self.get_A(): pressed.append("A")
        if self.get_B(): pressed.append("B")
        if self.get_X(): pressed.append("X")
        if self.get_Y(): pressed.append("Y")
        if self.get_Select(): pressed.append("START")
        if self.get_Start(): pressed.append("SELECT")
        if self.get_Shoulder_left(): pressed.append("SH_LEFT")
        if self.get_Shoulder_right(): pressed.append("SH_RIGHT")
        return pressed

    def get_A(self) -> bool:
        return self.__get_button("A")
    def get_B(self) -> bool:
        return self.__get_button("B")
    def get_X(self) -> bool:
        return self.__get_button("X")
    def get_Y(self) -> bool:
        return self.__get_button("Y")
    def get_Select(self) -> bool:
        return self.__get_button("SELECT")
    def get_Start(self) -> bool:
        return self.__get_button("START")
    def get_Shoulder_left(self) -> bool:
        return self.__get_button("SH_LEFT")
    def get_Shoulder_right(self) -> bool:
        return self.__get_button("SH_RIGHT")
    def get_x_axis(self) -> Union[float,int]:
        return self.__get_axis("AXIS_X")
    def get_y_axis(self) -> Union[float,int]:
        return self.__get_axis("AXIS_Y")

    def __get_button(self,button_name:str) -> int:
        if self.__mapping is not None:
            return self.__joystick.get_button(self.__mapping[button_name])
    def __get_axis(self,axsis_name:str)  -> Union[float,int]:
        if self.__mapping is not None:
            val = self.__joystick.get_axis(self.__mapping[axsis_name])
            if self.__allow_axis_floats:
                return val
            else:
                result = 0
                if val < -0.9: result = -1
                elif val > 0.9: result = 1
                return result

    def get_axis_name(self,key:int) -> str:
        """returns the name of the given axis num"""
        if self.__mapping is not None:
            if self.__mapping["AXIS_Y"] == key: return "AXIS_Y"
            elif self.__mapping["AXIS_X"] == key: return "AXIS_X"
    def get_button_name(self,key:int) -> str:
        """returns the name of the given button num"""
        if self.__mapping is not None:
            if self.__mapping["A"] == key: return "A"
            elif self.__mapping["B"] == key: return "B"
            elif self.__mapping["X"] == key: return "X"
            elif self.__mapping["Y"] == key: return "Y"
            elif self.__mapping["SELECT"] == key: return "SELECT"
            elif self.__mapping["START"] == key: return "START"
            elif self.__mapping["SH_LEFT"] == key: return "SH_LEFT"
            elif self.__mapping["SH_RIGHT"] == key: return "SH_RIGHT"

class Keyboard_as_Controller():
    """keyboard where keys are mapped to be a controller A,B,X,Y=Arrow keys, Joystick = w/a/s/d, left/right shoulder = q/e, select = return, start = space"""
    def __init__(self):
        self.__name = "Keyboard as Controller"

    @property
    def name(self) -> str: return self.__name
    @property
    def has_mapping(self) -> bool: return True

    def get_pressed(self) -> [str]:
        """returns a list of all the pressed buttons (axis are ignored)"""
        pressed = []
        if self.get_A(): pressed.append("A")
        if self.get_B(): pressed.append("B")
        if self.get_X(): pressed.append("X")
        if self.get_Y(): pressed.append("Y")
        if self.get_Select(): pressed.append("START")
        if self.get_Start(): pressed.append("SELECT")
        if self.get_Shoulder_left(): pressed.append("SH_LEFT")
        if self.get_Shoulder_right(): pressed.append("SH_RIGHT")
        return pressed

    def get_A(self) -> bool:
        return pygame.key.get_pressed()[pygame.K_RIGHT]
    def get_B(self) -> bool:
        return pygame.key.get_pressed()[pygame.K_DOWN]
    def get_X(self) -> bool:
        return pygame.key.get_pressed()[pygame.K_UP]
    def get_Y(self) -> bool:
        return pygame.key.get_pressed()[pygame.K_LEFT]
    def get_Select(self) -> bool:
        return pygame.key.get_pressed()[pygame.K_RETURN]
    def get_Start(self) -> bool:
        return pygame.key.get_pressed()[pygame.K_SPACE]
    def get_Shoulder_left(self) -> bool:
        return pygame.key.get_pressed()[pygame.K_q]
    def get_Shoulder_right(self) -> bool:
        return pygame.key.get_pressed()[pygame.K_e]
    def get_x_axis(self) -> int:
        if pygame.key.get_pressed()[pygame.K_a]: return -1
        if pygame.key.get_pressed()[pygame.K_d]: return 1
        return 0
    def get_y_axis(self) -> int:
        if pygame.key.get_pressed()[pygame.K_w]: return -1
        if pygame.key.get_pressed()[pygame.K_s]: return 1
        return 0

    def get_axis_name(self, key: int) -> str:
        """returns the name of the given axis num"""
        if pygame.K_w == key or pygame.K_s == key:
            return "AXIS_Y"
        elif pygame.K_a == key or pygame.K_d == key:
            return "AXIS_X"
    def get_button_name(self, key: int) -> str:
        """returns the name of the given button num"""
        if pygame.K_RIGHT == key:
            return "A"
        elif pygame.K_DOWN == key:
            return "B"
        elif pygame.K_UP == key:
            return "X"
        elif pygame.K_LEFT == key:
            return "Y"
        elif pygame.K_RETURN == key:
            return "SELECT"
        elif pygame.K_SPACE == key:
            return "START"
        elif pygame.K_q == key:
            return "SH_LEFT"
        elif pygame.K_e == key:
            return "SH_RIGHT"

class Keyboard():
    """keyboard where all keys are used"""
    def __init__(self):
        self.__name = "Keyboard"

    @property
    def name(self) -> str: return self.__name
    @property
    def has_mapping(self) -> bool: return True

    def get_pressed(self) -> [bool]:
        """returns a list of all the pressed buttons (same as pygame.key.get_pressed)"""
        return pygame.key.get_pressed()

class Keyboard_with_Mouse():
    """keyboard with all keys and a mouse (Movement, 3 buttons, and scrolling)"""
    def __init__(self):
        self.__name = "Keyboard with mouse"

    @property
    def name(self) -> str: return self.__name
    @property
    def has_mapping(self) -> bool: return True

    def get_pressed(self) -> [bool]:
        """returns a list of all the pressed buttons (same as pygame.key.get_pressed)"""
        return pygame.key.get_pressed()

class Mouse():
    """only the mouse with Movement, 3 buttons, and scrolling"""
    def __init__(self):
        self.__name = "Mouse"

    @property
    def name(self) -> str: return self.__name
    @property
    def has_mapping(self) -> bool: return True

    def get_pressed(self) -> [bool]:
        """returns a list of all the pressed buttons (same as pygame.mouse.get_pressed(5))"""
        return pygame.mouse.get_pressed(5)

contr = Union[Controller,Keyboard_as_Controller,Keyboard,Keyboard_with_Mouse,Mouse]
keybrd = Union[Keyboard_as_Controller,Keyboard,Keyboard_with_Mouse,Mouse]
contr_list = [contr]

class Controller_Handler():
    """Handles a group of controllers
    the event() function gets a pygame event and returns the player that had that event, its controller and the pressed key/axis"""
    def __init__(self,controllers:contr_list=None,add_keyboard:keybrd=None):
        """if controllers is None all selected controllers will be used else make own controller list
        if passed a keyboard will be added"""
        self.set_controllers(controllers,add_keyboard)

    def set_controllers(self,controllers:contr_list=None,add_keyboard:keybrd=None):
        """set the list of controllers
        if controllers is None all selected controllers will be used else make own controller list
        if passed a keyboard will be added"""
        if controllers == None:
            self.__controllers = get_controller_list(add_keyboard)
        else:
            self.__controllers = [contr for contr in controllers if is_controlling_thing(contr)]

        keyboard_joys = 0
        mouse_joys = 0
        for joy in self.__controllers:
            if isinstance(joy,Keyboard_as_Controller) or isinstance(joy,Keyboard) or isinstance(joy,Keyboard_with_Mouse):
                keyboard_joys += 1
            if isinstance(joy,Keyboard_with_Mouse) or isinstance(joy,Mouse):
                mouse_joys += 1
        if keyboard_joys > 1 or mouse_joys > 1:
            raise Exception("You can only use the keyboard and mouse as a controller once")
    def add_controller(self,controller:contr):
        """add controller to also receive its inputs"""
        if is_controlling_thing(controller):
            self.__controllers.append(controller)

            keyboard_joys = 0
            mouse_joys = 0
            for joy in self.__controllers:
                if isinstance(joy,Keyboard_as_Controller) or isinstance(joy,Keyboard) or isinstance(joy,Keyboard_with_Mouse):
                    keyboard_joys += 1
                if isinstance(joy,Keyboard_with_Mouse) or isinstance(joy,Mouse):
                    mouse_joys += 1
            if keyboard_joys > 1 or mouse_joys > 1:
                raise Exception("You can only use the keyboard and mouse as a controller once")

    def event(self,event:pygame.event) -> [int,contr,str,pygame.event]:
        """pass a pygame event object and get
        - the player number that made the event
        - the controller object of the player
        - the pressed key r axis
        - and the passed event
        all the return values are None if the events is ignored"""
        if event.type in [pygame.JOYAXISMOTION,pygame.JOYBUTTONUP,pygame.JOYBUTTONDOWN]:
            for player, joy in enumerate(self.__controllers):
                if isinstance(joy,Controller):
                    if joy.controller.get_id() == event.joy:
                        if event.type == pygame.JOYBUTTONUP or event.type == pygame.JOYBUTTONDOWN:
                            return (player,joy,joy.get_button_name(event.button),event)
                        elif event.type == pygame.JOYAXISMOTION:
                            return (player,joy,joy.get_axis_name(event.axis),event)
        if event.type in [pygame.KEYUP,pygame.KEYDOWN]:
            for player, joy in enumerate(self.__controllers):
                if isinstance(joy,Keyboard_as_Controller):
                    if event.key in [pygame.K_w,pygame.K_a,pygame.K_s,pygame.K_d]:
                        return (player,joy,joy.get_axis_name(event.key),event)
                    else:
                        return (player,joy,joy.get_button_name(event.key),event)
                elif isinstance(joy,Keyboard) or isinstance(joy,Keyboard_with_Mouse):
                    return (player,joy,event.key,event)
        if event.type in [pygame.MOUSEBUTTONUP,pygame.MOUSEBUTTONDOWN]:
            for player, joy in enumerate(self.__controllers):
                if isinstance(joy,Keyboard_with_Mouse) or isinstance(joy, Mouse):
                    return (player,joy,event.button,event)
        if event.type == pygame.MOUSEMOTION:
            for player, joy in enumerate(self.__controllers):
                if isinstance(joy,Keyboard_with_Mouse) or isinstance(joy, Mouse):
                    return (player,joy,event.rel,event)

        return (None,None,None,None)

    def is_there_a_controller_without_mapping(self) -> bool:
        """returns True if there is a controller without mapping"""
        for joy in self.__controllers:
            if not joy.has_mapping: return True
        return False
    def set_all_controller_allow_axis_floats(self):
        for joy in self.__controllers:
            if isinstance(joy,Controller):
                joy.allow_axis_floats()
    def set_all_controller_dont_allow_axis_floats(self):
        for joy in self.__controllers:
            if isinstance(joy,Controller):
                joy.dont_allow_axis_floats()

    @property
    def num_controllers(self) -> int: return len(self.__controllers)
    @property
    def all_controllers(self) -> contr_list: return self.__controllers
    @property
    def names(self) -> [str] : return [contr.name for contr in self.__controllers]

    def __len__(self) -> int:
        return self.num_controllers
    def __getitem__(self, item:Union[str,int]):
        if isinstance(item,str):
            for joy in self.__controllers:
                if joy.name == item: return joy
        elif isinstance(item,int):
            return self.__controllers[int]


def get_controller_list(add_keyboard:keybrd=None) -> contr_list:
    """returns a list of controller objects of the connected controllers, if passed a keyboard is added"""
    controllers = []
    for joy in range(pygame.joystick.get_count()):
        pygame_joystick = pygame.joystick.Joystick(joy)
        pygame_joystick.init()
        controllers.append(Controller(pygame_joystick))
    if add_keyboard is not None:
        controllers.append(add_keyboard)
    return controllers

def is_controlling_thing(object:Any) -> bool:
    """returns True if the passed object is a controller, mouse or keyboard"""
    return isinstance(object,Controller) or isinstance(object,Mouse) or isinstance(object,Keyboard) or isinstance(object,Keyboard_with_Mouse) or isinstance(object,Keyboard_as_Controller)


if __name__ == '__main__':
    # screen size
    WIDTH = 1400
    HEIGHT = 700
    FPS = 60

    # start pygame
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Test your controller here")
    clock = pygame.time.Clock()

    # colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)

    #
    f = "arial"
    font_name = pygame.font.match_font(f)
    if font_name is None: font_name = pygame.font.match_font(f + "ttf")
    if font_name is None: font_name = pygame.font.match_font(f + "ttc")

    class Game():
        def __init__(self):
            self.running = True
            self.pressed_button_texts = ["Press key on your controller"]
            self.joysticks = Controller_Handler(None,Keyboard_as_Controller())
            self.print_event = False

        def draw_text(self, surf, text, size, x, y, color=WHITE):
            font = pygame.font.Font(font_name, size)
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect()
            text_rect.midtop = (x, y)
            surf.blit(text_surface, text_rect)

        def start_game(self):
            while self.running:
                # clear screen
                screen.fill(BLACK)

                # check button _pressed and display
                self.detect_presses()
                self.draw_display()

                # flip display
                pygame.display.flip()

        def detect_presses(self):
            # detect key presses on all controllers
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                player, joy, btn_or_axis, event = self.joysticks.event(event)
                if not player is None:
                    if joy.has_mapping:
                        if self.print_event:
                            self.pressed_button_texts.append("Player {}: {}, event: {}".format(player,btn_or_axis,event))
                        else:
                            self.pressed_button_texts.append("Player {}: {}".format(player,btn_or_axis))
                        # quit game
                        if btn_or_axis == "START" and joy.get_Select() or btn_or_axis == "SELECT" and joy.get_Start():
                            self.running = False
                        elif btn_or_axis == "SELECT" and (event.type == pygame.KEYUP or event.type == pygame.JOYBUTTONUP):
                            self.print_event = not self.print_event
                    else:
                        self.pressed_button_texts.append("Player {}: event: {}".format(player, event))

            while len(self.pressed_button_texts) > 16:
                del self.pressed_button_texts[0]

        def draw_display(self):
            # show pressed buttons on display
            for num, text in enumerate(self.pressed_button_texts):
                self.draw_text(screen, text, 22, WIDTH / 2, num * 40)
            text = ", ".join(self.joysticks.names)
            self.draw_text(screen, str(len(self.joysticks)) + " Joysticks:" + text, 18, WIDTH / 2, HEIGHT - 35)


    game = Game()
    game.start_game()

    pygame.quit()