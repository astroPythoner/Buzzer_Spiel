from pygine.world_2d import World_2d
from pygine.controllers import Controller,Keyboard,Keyboard_as_Controller,Keyboard_with_Mouse,Mouse,Controller_Handler,get_controller_list,is_controlling_thing
from pygine.menus import Menu_creator,get_controller_list_from_controller_menu,get_num_players_from_player_menu
from pygine.background import Background
from pygine.file_manager import get_file_path,get_img_folder,get_level_folder,get_background_folder,get_menu_folder,load_image,load_image_sequence,search_file
from pygine.draw_and_others import get_match_font,draw_text,get_text_rect,split_text_into_lines_fitting_width,draw_center_rect,draw_bar,get_image_fit_into_rect,draw_image_fitting_onto_surface

#controller keys
A = "A"
B = "B"
X = "X"
Y = "Y"
SHOULDER_LEFT = "SH_LEFT"
SHOULDER_RIGHT = "SH_RIGHT"
START = "START"
SELECT = "SELECT"
X_AXIS = "AXIS_X"
Y_AXIS = "AXIS_Y"

#background styles
EMPTY_BACKGROUND = "no background"
UNI_COLOR = "uni_colored"
TWO_COLORED = "two_colored"
IMAGE = "image"
MOVING_IMAGE = "moving_image"
TILEMAP = "tilemap"
POINT_ANIMATION = "point_animation"

# menu slide styles
POINT = "point"
LINE = "line"

# positions
CENTER = "center"
TOP = "top"
BOTTOM = "bottom"
LEFT = "left"
RIGHT = "right"
LEFT_TOP = "left_top"
RIGHT_TOP = "right_top"
LEFT_BOTTOM = "left_bottom"
RIGHT_BOTTOM = "right_bottom"

# build in menu names
PLAYER_SELECTION = "pygine build in menu - Player selection"
CONTROLLER_SELECTION = "pygine build in menu - Controller selection"
SETTINGS = "pygine build in menu - Settings"
