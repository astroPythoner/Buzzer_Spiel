import pygame
vec2 = pygame.math.Vector2
from random import randrange, uniform
from os import sep
import pygine
from typing import Any, List, Optional, Sequence, Text, Tuple, Union, overload, Iterable
import pytmx
import abc

color_attr = Tuple[int,int,int]

class AbstractBackground(metaclass=abc.ABCMeta):
    """Use this class as a parent for building your own background"""

    @abc.abstractmethod
    def draw(self,surface:pygame.Surface):
        """overwrite this method to draw the background on the passed surface"""
        return NotImplemented

    @abc.abstractmethod
    def update(self, player,size:[int,int]) -> [vec2,float]:
        """overwrite this method to update the background and return an offset and the current zoom factor
        default values are vec2(0,0) for offset and 1 for zoom"""
        return NotImplemented

class Background():
    def __init__(self,world):
        self.__world = world

        # uni_colored
        self.uni_color_background = UniColorBackground()
        # two_colored
        self.two_color_background = TwoColorBackground()
        # image
        self.image_background = ImageBackground()
        # moving_image
        self.moving_image_background = MovingImageBackground()
        # tilemap
        self.tile_map_background = TilemapBackground()
        # point_animation
        self.point_background = PointBackgroud()

        self.__style = "uni_colored"
        self.__current_background = self.uni_color_background

    def set_style(self,style:str) -> None:
        """set the style of the background (ex.: pygine_3d.POINT_ANIMATION)"""
        styles = ["no background","two_colored","image","moving_image","tilemap","point_animation","uni_colored"]
        if style in styles:
            self.__style = style
            self.__current_background = [None,self.two_color_background,self.image_background,self.moving_image_background,self.tile_map_background,self.point_background,self.uni_color_background][styles.index(style)]
        else:
            raise Exception("Background type not known")
    def get_style(self) -> str:
        """return current styel of the background"""
        return self.__style
    def set_own_background(self,own_background:AbstractBackground,style_name:str="own background"):
        """Use the AbstractBackground Class to create your own background an add it with this function"""
        self.__current_background = own_background
        self.__style = style_name

    def set_world(self, world) -> None:
        """set the world, used to calculate the background"""
        if type(world) in [pygine.World_2d, pygine.World_3d]:
            self.__world = world

    def draw(self,surface:pygame.Surface) -> [vec2, float]:
        """update and draw the background"""
        # draw background
        if self.__style != "no background" and self.__current_background is not None:
            if self.__world is None: raise Exception("please add world to Background object with set_world()")
            values = self.__current_background.update(self.__world.player,surface.get_size())
            self.__current_background.draw(surface)
            return values

    # save
    def get_code(self) -> [str]:
        """return a list of code lines needed to get this background"""
        def __path_to_code(path):
            path = path[path.rfind("projects") + 9:]
            splited = path.split(sep)
            return "pygine.get_file_path('" + splited[0] + "',['" + "','".join(splited[1:]) + "'])"
        get_file_path = lambda file: "projects"+file.split("projects")[-1]
        code_lines = [
            "backgrnd = pygine.Background(None)",
            "backgrnd.set_style('"+self.__style+"')",
            "# unicolor",
            "backgrnd.uni_color_background.set_color({})".format(self.uni_color_background.get_color()),
            "# two colored",
            "backgrnd.two_color_background.set_sky_color({})".format(self.two_color_background.get_sky_color()),
            "backgrnd.two_color_background.set_floor_color({})".format(self.two_color_background.get_floor_color())
        ]
        code_lines.append("# image")
        if self.image_background.get_image_name() != "": code_lines.append("backgrnd.image_background.set_image_from_file({})".format(__path_to_code(get_file_path(self.image_background.get_image_name()))))
        if self.image_background.get_keep_ratio(): code_lines.append("backgrnd.image_background.keep_ratio()")
        else: code_lines.append("backgrnd.image_background.dont_keep_ratio()")
        code_lines.append("backgrnd.image_background.set_resize_full("+["False","True"][self.image_background.get_resize_full()[0]]+","+["False","True"][self.image_background.get_resize_full()[1]]+")")
        code_lines.append("# moving image")
        if self.moving_image_background.get_image_name() != "": code_lines.append("backgrnd.moving_image_background.set_image_from_file({})".format(__path_to_code(get_file_path(self.moving_image_background.get_image_name()))))
        code_lines.append("backgrnd.moving_image_background.set_offset(Vector2({},{}))".format(self.moving_image_background.get_offset().x,self.moving_image_background.get_offset().y))
        if self.moving_image_background.get_follow_player_x(): code_lines.append("backgrnd.moving_image_background.follow_player_x()")
        else: code_lines.append("backgrnd.moving_image_background.dont_follow_player_x()")
        if self.moving_image_background.get_follow_player_y(): code_lines.append("backgrnd.moving_image_background.follow_player_y()")
        else: code_lines.append("backgrnd.moving_image_background.dont_follow_player_y()")
        if self.moving_image_background.get_endless(): code_lines.append("backgrnd.moving_image_background.make_endless()")
        else: code_lines.append("backgrnd.moving_image_background.dont_make_endless()")
        if self.moving_image_background.get_endless_resize(): code_lines.append("backgrnd.moving_image_background.make_endless_resize()")
        else: code_lines.append("backgrnd.moving_image_background.dont_make_endless_resize()")
        code_lines.append("backgrnd.moving_image_background.set_resize_full("+["False","True"][self.moving_image_background.get_resize_full()[0]]+","+["False","True"][self.moving_image_background.get_resize_full()[1]]+")")
        code_lines.append("# tilemap")
        if self.tile_map_background.get_map_name() != "": code_lines.append("backgrnd.tile_map_background.load_map_from_file({})".format(__path_to_code(get_file_path(self.tile_map_background.get_map_name()))))
        code_lines.append("backgrnd.tile_map_background.set_offset(Vector2({},{}))".format(self.tile_map_background.get_offset().x, self.tile_map_background.get_offset().y))
        if self.tile_map_background.get_follow_player_x(): code_lines.append("backgrnd.tile_map_background.follow_player_x()")
        else: code_lines.append("backgrnd.tile_map_background.dont_follow_player_x()")
        if self.tile_map_background.get_follow_player_y(): code_lines.append("backgrnd.tile_map_background.follow_player_y()")
        else: code_lines.append("backgrnd.tile_map_background.dont_follow_player_y()")
        code_lines.extend([
            "# point animation"
            "backgrnd.point_background.set_num_node({})".format(self.point_background.get_num_nodes()),
            "backgrnd.point_background.set_background_color({})".format(self.point_background.get_background_color()),
            "backgrnd.point_background.set_line_color({})".format(self.point_background.get_line_color()),
            "backgrnd.point_background.set_node_color({})".format(self.point_background.get_node_color()),
            "backgrnd.point_background.set_connection_distance({})".format(self.point_background.get_connection_distance()),
            "backgrnd.point_background.set_line_width({})".format(self.point_background.get_line_width()),
            "backgrnd.point_background.set_node_size({})".format(self.point_background.get_node_size()),
            "backgrnd.point_background.set_max_speed({})".format(self.point_background.get_max_speed()),
        ])
        return code_lines
    def save_to_file(self, file:str):
        """saves file that creates this background
        Ignores whether there is already something in the file or not"""
        code_lines = ["import pygine","from pygame.math import Vector2", "", "def get():"]
        for line in self.get_code():
            code_lines.append("    " + line)
        code_lines.append("    return backgrnd")
        with open(file, 'w') as writer:
            for line in code_lines:
                writer.write(line + "\n")
    def overwrite_to_file(self, file:str):
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
                    code_lines.append("    return backgrnd")
                    code_lines.append("")
                if line.rstrip() == "":
                    in_get_method = False
        with open(file, 'w') as writer:
            for line in code_lines:
                writer.write(line + "\n")

class UniColorBackground(AbstractBackground):
    def __init__(self):
        self.__color = (0,0,0)

    def set_color(self,color:[int,int,int]):
        self.__color = color
    def get_color(self) -> [int,int,int]:
        return self.__color

    def draw(self,surf:pygame.Surface):
        surf.fill(self.__color)
    def update(self, player,size:[int,int]) -> [vec2,float]:
        return vec2(0,0),1

class TwoColorBackground(AbstractBackground):
    def __init__(self):
        self.__sky_color = (135, 206, 235)
        self.__floor_color = (140, 90, 75)
    
    def set_sky_color(self,color:color_attr):self.__sky_color = color
    def get_sky_color(self) -> color_attr: return self.__sky_color
    def set_floor_color(self,color:color_attr):self.__floor_color = color
    def get_floor_color(self) -> color_attr: return self.__floor_color
        
    def draw(self,surf:pygame.Surface):
        size = surf.get_size()
        pygame.draw.rect(surf, self.__sky_color, pygame.Rect(0, 0, size[0], size[1] / 2))
        pygame.draw.rect(surf, self.__floor_color, pygame.Rect(0, size[1] / 2, size[0], size[1] / 2))
    def update(self, player, size: [int, int]) -> [vec2, float]:
            return vec2(0, 0), 1
        
class ImageBackground(AbstractBackground):
    def __init__(self):
        self.__image = None
        self.__image_name = ""
        self.__keep_ratio = True
        self.__size = None
        self.__resize_full_x = False
        self.__resize_full_y = False
        self.__scaled_image = None
        self.__scale_factor = 1
        self.__offset = vec2(0,0)

    def set_image_from_file(self,path:str):
        self.__image = pygame.image.load(path)
        self.__image_name = path
        self.__size = None
    def set_image_from_surface(self,surface:pygame.image):
        self.__image = surface
        self.__image_name = ""
        self.__size = None
    def get_image(self) -> pygame.image: return self.__image
    def get_image_name(self) -> str: return self.__image_name

    def update(self, player,size:[int,int]) -> [vec2, float]:
        # nothing to update just return calculated values
        return self.__offset,self.__scale_factor

    def keep_ratio(self):
        self.__keep_ratio = True
        self.__size = None
    def dont_keep_ratio(self):
        self.__keep_ratio = False
        self.__size = None
    def get_keep_ratio(self): return self.__keep_ratio
    def set_resize_full(self,x:bool=True,y:bool=True):
        self.__resize_full_x, self.__resize_full_y = x,y
        self.__size = None
    def get_resize_full(self) -> [bool,bool]:
        return self.__resize_full_x,self.__resize_full_y

    def draw(self,surf:pygame.Surface):
        if self.__image is not None:
            if self.__size is None or self.__size != surf.get_size():
                self.__size = surf.get_size()
                self.__scale_factor = 1
                if self.__keep_ratio:
                    orig_width,orig_height = self.__image.get_size()[0],self.__image.get_size()[1]
                    width,height = orig_width,orig_height
                    if self.__resize_full_x and self.__resize_full_y:
                        if width != self.__size[0]:
                            height = orig_height * (surf.get_width() / orig_width)
                            self.__scale_factor = (surf.get_width()) / orig_width
                            width = surf.get_width()
                        if height > self.__size[1]:
                            width = orig_width * (surf.get_height() / orig_height)
                            self.__scale_factor = (surf.get_height()) / orig_height
                            height = surf.get_height()
                    elif self.__resize_full_x:
                        if width != self.__size[0]:
                            height = orig_height * (surf.get_width() / orig_width)
                            self.__scale_factor = (surf.get_width()) / orig_width
                            width = surf.get_width()
                    elif self.__resize_full_y:
                        if height != self.__size[1]:
                            width = orig_width * (surf.get_height() / orig_height)
                            self.__scale_factor = (surf.get_height()) / orig_height
                            height = surf.get_height()
                    else:
                        if width < self.__size[0]:
                            height = orig_height * (self.__size[0] / orig_width)
                            self.__scale_factor = (self.__size[0] / orig_width)
                            width = self.__size[0]
                        if height < self.__size[1]:
                            width = width * (self.__size[1] / height)
                            self.__scale_factor *= (self.__size[1] / orig_height)
                            height = self.__size[1]
                    self.__scaled_image = pygame.transform.scale(self.__image, (int(width),int(height)))
                    self.__offset = vec2(int((self.__size[0]-width)/2),int((self.__size[1]-height)/2))
                else:
                    self.__scaled_image = pygame.transform.scale(self.__image,self.__size)
                    self.__offset = vec2(0,0)
            surf.blit(self.__scaled_image,self.__offset)

class MovingImageBackground(AbstractBackground):
    def __init__(self):
        self.__image = None
        self.__image_name = ""
        self.__follow_player_x = False
        self.__follow_player_y = False
        self.__offset = vec2(0,0)
        self.__endless = False
        self.__endless_resize = True
        self.__resize_full_x = False
        self.__resize_full_y = False
        self.__size = None
        self.__scaled_image = None
        self.__scaled_size = (0,0)
        self.__scale_factor = 1
        self.__calc_image_pos = vec2(0,0)

    def set_image_from_file(self,path:str):
        self.__image = pygame.image.load(path)
        self.__image_name = path
        self.__size = None
    def set_image_from_surface(self,surface:pygame.image):
        self.__image = surface
        self.__image_name = ""
        self.__size = None
    def get_image(self) -> pygame.image: return self.__image
    def get_image_name(self) -> str: return self.__image_name

    def update(self,player,size:[int,int]) -> [vec2, float]:
        pos = player.pos
        if self.__size is not None:
            if self.__endless:
                self.__calc_image_pos = (vec2(pos.x, pos.y) * self.__scale_factor - (self.__offset if self.__offset != vec2(-1,-1) else vec2(size[0]/2,size[1]/2)))
                if not self.__follow_player_x:
                    self.__calc_image_pos.x = (self.__scaled_size[0] - size[0]) / 2
                if not self.__follow_player_y:
                    self.__calc_image_pos.y = (self.__scaled_size[1] - size[1]) / 2
                self.__calc_image_pos.x %= self.__scaled_size[0]
                self.__calc_image_pos.y %= self.__scaled_size[1]
                # return
                offset_pos = -1*(vec2(pos.x, pos.y)*self.__scale_factor - (self.__offset if self.__offset != vec2(-1,-1) else vec2(size[0]/2,size[1]/2)))
                if not self.__follow_player_x:
                    offset_pos.x = -(self.__scaled_size[0] - size[0]) / 2
                if not self.__follow_player_y:
                    offset_pos.y = -(self.__scaled_size[1] - size[1]) / 2
                return offset_pos, self.__scale_factor
            else:
                self.__calc_image_pos = -(vec2(pos.x,pos.y)*self.__scale_factor-(self.__offset if self.__offset != vec2(-1,-1) else vec2(size[0]/2,size[1]/2)))
                if self.__calc_image_pos.x > 0:
                    self.__calc_image_pos.x = 0
                if self.__calc_image_pos.y > 0:
                    self.__calc_image_pos.y = 0
                if self.__calc_image_pos.x < -(self.__scaled_size[0]-size[0]):
                    self.__calc_image_pos.x = -(self.__scaled_size[0]-size[0])
                if self.__calc_image_pos.y < -(self.__scaled_size[1]-size[1]):
                    self.__calc_image_pos.y = -(self.__scaled_size[1]-size[1])
                if not self.__follow_player_x:
                    self.__calc_image_pos.x = -(self.__scaled_size[0]-size[0])/2
                if not self.__follow_player_y:
                    self.__calc_image_pos.y = -(self.__scaled_size[1]-size[1])/2
                return self.__calc_image_pos, self.__scale_factor
        return vec2(0, 0), 1

    def set_offset(self,offset:vec2):self.__offset = offset
    def get_offset(self) -> vec2: return self.__offset
    def follow_player_x(self):self.__follow_player_x = True
    def dont_follow_player_x(self):self.__follow_player_x = False
    def get_follow_player_x(self) -> bool: return self.__follow_player_x
    def follow_player_y(self):self.__follow_player_y = True
    def dont_follow_player_y(self):self.__follow_player_y = False
    def get_follow_player_y(self) -> bool: return self.__follow_player_y
    def make_endless(self):
        self.__endless = True
        self.__size = None
    def dont_make_endless(self):
        self.__endless = False
        self.__size = None
    def get_endless(self) -> bool: return self.__endless
    def make_endless_resize(self):
        self.__endless_resize = True
        self.__size = None
    def dont_make_endless_resize(self):
        self.__endless_resize = False
        self.__size = None
    def get_endless_resize(self) -> False:
        return self.__endless_resize
    def set_resize_full(self,x:bool,y:bool):
        self.__resize_full_x, self.__resize_full_y = x,y
        self.__size = None
    def get_resize_full(self) -> [bool,bool]:
        return self.__resize_full_x,self.__resize_full_y

    def draw(self,surf:pygame.Surface):
        if self.__image is not None:
            if self.__size is None or self.__size != surf.get_size():
                self.__size = surf.get_size()
                width, height = self.__image.get_size()[0], self.__image.get_size()[1]
                self.__scale_factor = 1
                if not self.__endless or self.__endless_resize:
                    width, height = self.__image.get_size()[0], self.__image.get_size()[1]
                    if self.__resize_full_x and self.__resize_full_y:
                        if width != self.__size[0]:
                            height *= (surf.get_width()) / width
                            self.__scale_factor = (surf.get_width()) / width
                            width = surf.get_width()
                        if height > self.__size[1]:
                            width *= (surf.get_height()) / height
                            self.__scale_factor = (surf.get_height()) / height
                            height = surf.get_height()
                    elif self.__resize_full_x:
                        if width != self.__size[0]:
                            height *= (surf.get_width()) / width
                            self.__scale_factor = (surf.get_width()) / width
                            width = surf.get_width()
                    elif self.__resize_full_y:
                        if height != self.__size[1]:
                            width *= (surf.get_height()) / height
                            self.__scale_factor = (surf.get_height()) / height
                            height = surf.get_height()
                    else:
                        if width < self.__size[0]:
                            height *= (surf.get_width()) / width
                            self.__scale_factor = (surf.get_width()) / width
                            width = surf.get_width()
                        if height < surf.get_height():
                            width *= (surf.get_height()) / height
                            self.__scale_factor = (surf.get_height()) / height
                            height = surf.get_height()
                self.__scaled_size = (int(width), int(height))
                self.__scaled_image = pygame.transform.scale(self.__image, self.__scaled_size)
            if self.__endless:
                x = -self.__calc_image_pos.x
                while x < surf.get_width():
                    y = -self.__calc_image_pos.y
                    while y < surf.get_height():
                        surf.blit(self.__scaled_image, (x,y))
                        y += self.__scaled_size[1]
                    x += self.__scaled_size[0]
            else:
                surf.blit(self.__scaled_image,self.__calc_image_pos)

class TilemapBackground(AbstractBackground):
    def __init__(self):
        self.__map = None
        self.__map_name = ""
        self.__follow_player_x = False
        self.__follow_player_y = False
        self.__offset = vec2(0, 0)
        self.__size = None
        self.__scaled_map = None
        self.__scaled_size = (0, 0)
        self.__scale_factor = 1
        self.__calc_map_pos = vec2(0, 0)

    def load_map_from_file(self, path):
        self.__map_name = path
        self.__size = None
        tmxdata = pytmx.load_pygame(path, pixelalpha=True)
        width = tmxdata.width * tmxdata.tilewidth
        height = tmxdata.height * tmxdata.tileheight

        self.__map = pygame.Surface((width, height))
        for layer in tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = tmxdata.get_tile_image_by_gid(gid)
                    if tile: self.__map.blit(tile, (x * tmxdata.tilewidth, y * tmxdata.tileheight))
    def set_map(self,surf:pygame.Surface):
        self.__map = surf
        self.__map_name = ""
        self.__size = None
    def get_map(self) -> pygame.image: return self.__map
    def get_map_name(self) -> str: return self.__map_name

    def update(self, player, size:[int,int]) -> [vec2,float]:
        pos = player.pos
        self.__calc_map_pos = -(vec2(pos.x, pos.y) * self.__scale_factor - (self.__offset if self.__offset != vec2(-1,-1) else vec2(size[0]/2,size[1]/2)))
        if self.__calc_map_pos.x > 0:
            self.__calc_map_pos.x = 0
        if self.__calc_map_pos.y > 0:
            self.__calc_map_pos.y = 0
        if self.__calc_map_pos.x < -(self.__scaled_size[0] - size[0]):
            self.__calc_map_pos.x = -(self.__scaled_size[0] - size[0])
        if self.__calc_map_pos.y < -(self.__scaled_size[1] - size[1]):
            self.__calc_map_pos.y = -(self.__scaled_size[1] - size[1])
        if not self.__follow_player_x:
            self.__calc_map_pos.x = -(self.__scaled_size[0]-size[0])/2
        if not self.__follow_player_y:
            self.__calc_map_pos.y = -(self.__scaled_size[1]-size[1])/2
        return self.__calc_map_pos, self.__scale_factor

    def set_offset(self, offset:vec2):self.__offset = offset
    def get_offset(self) -> vec2: return self.__offset
    def follow_player_x(self):self.__follow_player_x = True
    def dont_follow_player_x(self):self.__follow_player_x = False
    def get_follow_player_x(self) -> bool: return self.__follow_player_x
    def follow_player_y(self):self.__follow_player_y = True
    def dont_follow_player_y(self):self.__follow_player_y = False
    def get_follow_player_y(self) -> bool: return self.__follow_player_y

    def draw(self, surf:pygame.Surface):
        if self.__map is not None:
            if self.__size is None or self.__size != surf.get_size():
                self.__size = surf.get_size()
                width, height = self.__map.get_size()[0], self.__map.get_size()[1]
                self.__scale_factor = 1
                if width < self.__size[0]:
                    height *= (surf.get_width()) / width
                    self.__scale_factor = (surf.get_width()) / width
                    width = surf.get_width()
                if height < surf.get_height():
                    width *= (surf.get_height()) / height
                    self.__scale_factor = (surf.get_height()) / height
                    height = surf.get_height()
                self.__scaled_size = (int(width), int(height))
                self.__scaled_map = pygame.transform.scale(self.__map, self.__scaled_size)
            surf.blit(self.__scaled_map,self.__calc_map_pos)

class PointBackgroud(AbstractBackground):
    
    class Node:
        def __init__(self, max_speed, background):
            self.__pos = pygame.Vector2(randrange(0, background.width), randrange(0, background.height))
            self.__vel = pygame.Vector2(uniform(-max_speed, max_speed), uniform(-max_speed, max_speed))
            self.__bg = background
        def update(self):
            self.__pos += self.__vel
            if self.__pos.x < 0 or self.__pos.x > self.__bg.width:
                self.__vel.x = -self.__vel.x
            if self.__pos.y < 0 or self.__pos.y > self.__bg.height:
                self.__vel.y = -self.__vel.y
        def pos(self) -> pygame.Vector2:
            return self.__pos
        def reposition(self):
            self.__pos = pygame.Vector2(randrange(0, self.__bg.width), randrange(0, self.__bg.height))
        def change_max_speed(self,max_speed):
            self.__vel = pygame.Vector2(uniform(-max_speed, max_speed), uniform(-max_speed, max_speed))

    def __init__(self):
        self.width = 500
        self.height = 350
        self.__max_speed = 3
        self.__node_color = (255, 0, 0)
        self.__background_color = (0,255,0)
        self.__line_color = (0,0,255)
        self.__connection_distance = 70
        self.__node_radius = 2
        self.__connection_line_width = 1

        self.__nodes = []
        for node_num in range(int(self.width*self.height/5000)):
            self.__nodes.append(PointBackgroud.Node(self.__max_speed, self))
        self.__calculate_colors_depending_on_distance()

    def __calculate_colors_depending_on_distance(self):
        add_two_colors = lambda color1, color2, transparency: int((color1 * (255 - transparency) + color2 * transparency) / 255)
        connection_multiplikator = -255 / ((2 / 3) * self.__connection_distance)
        connection_addition = 255 - connection_multiplikator * (1 / 3) * self.__connection_distance
        self.__colors = {}
        for dist in range(self.__connection_distance):
            line_transparency = 255
            if dist > (1 / 3) * self.__connection_distance:
                line_transparency = connection_multiplikator * dist + connection_addition
            self.__colors[dist] = pygame.Color(add_two_colors(self.__background_color[0], self.__line_color[0], line_transparency),
                                               add_two_colors(self.__background_color[1], self.__line_color[1], line_transparency),
                                               add_two_colors(self.__background_color[2], self.__line_color[2], line_transparency))

    def update(self,player,size:[int,int]) -> [vec2,float]:
        self.set_size(width=size[0],height=size[1])
        for node in self.__nodes:
            node.update()
        return vec2(0,0), 1.0
    def randomly_reposition_nodes(self):
        for node in self.__nodes:
            node.reposition()
    def draw(self,surf:pygame.Surface,adjust_size=False):
        if adjust_size: self.set_size(surf.get_width(),surf.get_height())
        surf.fill(self.__background_color)
        # draw lines to other node
        for node in self.__nodes:
            for connect_node in self.__nodes:
                if node != connect_node:
                    distance = node.pos().distance_to(connect_node.pos())
                    if distance < self.__connection_distance:
                        pygame.draw.line(surf, self.__colors[int(distance)], (int(node.pos().x), int(node.pos().y)), (int(connect_node.pos().x), int(connect_node.pos().y)), self.__connection_line_width)
        # draw node
        for node in self.__nodes:
            pygame.draw.circle(surf, self.__node_color, (int(node.pos().x), int(node.pos().y)), self.__node_radius)

    # set sizes
    def set_size(self,width:int,height:int):
        self.width = width
        self.height = height
    def set_node_size(self, radius: int):
        self.__node_radius = radius
    def get_node_size(self) -> int: return self.__node_radius
    def set_line_width(self, width:int):
        self.__connection_line_width = width
    def get_line_width(self) -> int: return self.__connection_line_width
    
    # add or delete node
    def set_num_node(self,num:int):
        if num != 0:
            while num < len(self.__nodes):
                del self.__nodes[randrange(0, len(self.__nodes))]
            while num > len(self.__nodes):
                self.__nodes.append(PointBackgroud.Node(self.__max_speed, self))
    # set number of nodes so it fites to the screen size
    def set_num_node_fitting_size(self):
        num_node = int(self.width * self.height / 5000)
        self.set_num_node(num_node)
    def get_num_nodes(self) -> int: return len(self.__nodes)

    # set colors
    def set_node_color(self,color:color_attr):
        self.__node_color = color
    def get_node_color(self) -> color_attr: return self.__node_color
    def set_background_color(self,color:color_attr):
        self.__background_color = color
        self.__calculate_colors_depending_on_distance()
    def get_background_color(self) -> color_attr: return self.__background_color
    def set_line_color(self,color:color_attr):
        self.__line_color = color
        self.__calculate_colors_depending_on_distance()
    def get_line_color(self) -> color_attr: return self.__line_color

    # set max distance where node are connected
    def set_connection_distance(self,distance:int):
        self.__connection_distance = distance
        self.__calculate_colors_depending_on_distance()
    def get_connection_distance(self) -> int: return self.__connection_distance
    # set max speed of nodes
    def set_max_speed(self,max_speed:int):
        self.__max_speed = max_speed
        for node in self.__nodes:
            node.change_max_speed(self.__max_speed)
    def get_max_speed(self) -> int: return self.__max_speed

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((800, 600))

    backgrnd = Background(None)
    backgrnd.set_style("point_animation")
    backgrnd.point_background.set_size(*screen.get_size())
    backgrnd.point_background.set_num_node_fitting_size()

    while True:
        screen.fill((0, 0, 0))
        backgrnd.draw(screen)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit()
        pygame.display.flip()
        backgrnd.point_background.update(screen.get_size())