import pygame
import os
import csv
import scipy.interpolate as si
import importlib
import numpy as np
from math import sqrt
vec2 = pygame.math.Vector2
vec3 = pygame.math.Vector3

from pygine.background import Background
from pygine.menus import Menu, Menu_creator
from pygine.sounds import Sounds
from pygine.controllers import *

def bspline(cv, n=100, degree=3):
    cv = np.asarray(cv)
    count = cv.shape[0]
    degree = np.clip(degree,1,count-1)
    kv = np.array([0]*degree + list(range(count-degree+1)) + [count-degree]*degree,dtype='int')
    u = np.linspace(0,(count-degree),n)

    return np.array(si.splev(u, (kv,cv.T,degree))).T

class World_2d:
    """
    this is the main class for a two_dimensional game/animation containing sprites and graphics.
    """
    def __init__(self):
        self.objects = World_2d.Objects(self)
        self.__players = []
        self.__camera = None

        self.background = Background(self)
        self.menu = Menu(self)
        self.sounds = Sounds()
        self.controllers = Controller_Handler()

        self.__paused = False

        self.__last_zoom = 0
        self.__last_offset = vec2(0,0)

    class Player:
        """
        Player in the World

        see create_player method in World class for creating the player
        """

        def __init__(self, world, x: float, y: float, rot: float, file_image:Union[str,pygame.Surface]=None):
            self.__pos = vec2(x, y)
            self.__rot = 0

            self.__world = world

            self.rot = rot

            self.image = None
            self.__image_calc_zoom = 0
            self.__image_calc_rot = 0
            self.__image_needs_redraw = True
            self.orig_image = None
            if file_image is not None:
                if isinstance(file_image, pygame.Surface):
                    self.set_image(file_image)
                else:
                    self.load_image_file(file_image)
                self.rect = pygame.Rect(self.__pos, self.orig_image.get_size())
            else:
                self.rect = pygame.Rect(self.__pos, (10, 10))
            self.mask = None
            self.__maks_calc_pos = [0,0]

        def load_image_file(self, path: str):
            # load an image file for the object
            self.orig_image = pygame.image.load(path)
            self.__image_needs_redraw = True
        def set_image(self, image: pygame.Surface):
            self.orig_image = image
            self.__image_needs_redraw = True

        @property
        def pos(self) -> vec2:
            return self.__pos
        @pos.setter
        def pos(self, pos: vec2):
            if isinstance(pos, vec2):
                self.__pos = pos
            if isinstance(pos, tuple) or isinstance(pos, list):
                self.__pos = vec2(pos[0], pos[1])
        def change_pos(self, pos: vec2):
            """adds the vector pos to players position"""
            self.__pos += pos

        @property
        def rot(self) -> float:
            return self.__rot
        @rot.setter
        def rot(self, angle: float):
            self.__rot = angle
            if self.__rot < 0: self.__rot = 360 + angle
            if self.__rot > 360: self.__rot = angle
        def change_rotation(self, angle:float):
            """adds the given angle to rotation of the player"""
            self.rot = self.__rot + angle

        # update
        def update(self,player,events:[pygame.event], fps:float, *args):
            """this function is called every frame to move/update the player and should be overwritten"""
            pass

        # draw
        def draw(self,player,surface:pygame.Surface,offset:vec2,zoom:float):
            """this function is called every frame to draw the player and should be overwritten"""
            self.draw_image(surface,offset,zoom)
        def _draw_2d(self, screen:pygame.Surface, offset:vec2, zoom:float, color:[int,int,int], sight_color:[int,int,int], look:bool, size:float, sight_size:[int,int]):
            if "d" in look: # draw direction
                dir = vec2((sight_size[0], 0))
                dir = dir.rotate(self.__rot) + self.pos
                pygame.draw.line(screen, sight_color, self.pos * zoom + offset, dir * zoom + offset, sight_size[1])
            if "p" in look: # draw point for player
                pygame.draw.circle(screen, color, (int(self.pos.x * zoom + offset.x), int(self.pos.y * zoom + offset.y)), size)
            if "r" in look:# draw rect for player
                pygame.draw.rect(screen, color, (int(self.pos.x * zoom + offset.x), int(self.pos.y * zoom + offset.y), 10, 10))
        def draw_image(self, surface:pygame.Surface, offset:vec2, zoom:float, img_pos:str="center", update_rect:bool=True, allow_update_maks:bool=True, image_scale_factor:float=None):
            if self.orig_image is not None:
                if self.__image_calc_zoom != zoom or self.__image_calc_rot != self.__rot or self.__image_needs_redraw:
                    self.calc_image(zoom if image_scale_factor is None else zoom*image_scale_factor)
                    if allow_update_maks: self.calc_mask()
                pos = vec2(0, 0)
                if img_pos == "center":
                    pos = self.pos * zoom + offset - vec2(self.image.get_size()) / 2
                if img_pos == "top":
                    pos = self.pos * zoom + offset - vec2(self.image.get_width() / 2, 0)
                if img_pos == "bottom":
                    pos = self.pos * zoom + offset - vec2(self.image.get_width() / 2, self.image.get_height())
                if img_pos == "left_top":
                    pos = self.pos * zoom + offset
                if img_pos == "right_top":
                    pos = self.pos * zoom + offset - vec2(self.image.get_width(), 0)
                if img_pos == "left_bottom":
                    pos = self.pos * zoom + offset - vec2(0, self.image.get_height())
                if img_pos == "right_bottom":
                    pos = self.pos * zoom + offset - vec2(self.image.get_width(), self.image.get_height())
                if img_pos == "left":
                    pos = self.pos * zoom + offset - vec2(0, self.image.get_height()/2)
                if img_pos == "right":
                    pos = self.pos * zoom + offset - vec2(self.image.get_width(), self.image.get_height()/2)
                surface.blit(self.image, pos)
                if update_rect: self.rect = pygame.Rect(pos, self.image.get_size())
        def calc_image(self, zoom:float):
            size = (int(self.orig_image.get_width() * zoom), int(self.orig_image.get_height() * zoom))
            img = pygame.transform.rotate(pygame.transform.scale(self.orig_image, size), -self.rot - 90)
            self.__image_calc_rot = self.__rot
            self.__image_calc_zoom = zoom
            self.__image_needs_redraw = False
            self.image = img
        def calc_mask(self):
            self.mask = pygame.mask.from_surface(self.image)

        def __repr__(self):
            return "Player at position {} looking in direction {}".format(self.pos, self.rot)
        def __getitem__(self, item):
            if item == 0:
                return self.pos.x
            elif item == 1:
                return self.pos.y
            else:
                return self.rot

    class Camera:
        """
        Camera in the World:
        follows a path and renders images that can be combined to a movie

        see create_camera method in World class for creating the camera
        """

        def __init__(self, world, x: float, y: float, rot: float):
            self.__pos = vec2(x, y)
            self.__rot = 0

            self.__world = world

            self.rot = rot

            self.__movement_points = []  # list of movement points
            self.__movement_arrays = [[] for i in range(7)]  # list of values for each frame (calculated by spline)
            self.__pos_movement_arrays = 0  # current frame (position in array __movement_arrays)

        class MovementPoint():
            def __init__(self, x:float, y:float, rot:float, frame_num:int):
                self.x, self.y = x, y
                self.rot = rot
                self.frame_num = frame_num
            
            def __repr__(self):
                return "Camera MovementPoint at position {},{} witg rotation{}".format(self.x, self.y, self.rot)
            def __getitem__(self, item:int):
                if item == 0:
                    return self.x
                elif item == 1:
                    return self.y
                else:
                    return self.rot
            def __setitem__(self, key:int, value:float):
                if key == 0:
                    self.x = value
                elif key == 1:
                    self.y = value
                elif key == 3:
                    self.rot = value

        # change position on  path
        def walk_on_path(self, steps: int = 1):
            """
            continue walking on path
            :param steps: number of steps (negatic also possible)
            :return:
            """
            self.__pos_movement_arrays += steps
            if self.__pos_movement_arrays < 0: self.__pos_movement_arrays = 0
            if self.__pos_movement_arrays >= len(self.__movement_arrays[0]): self.__pos_movement_arrays = len(self.__movement_arrays[0]) - 1
            if len(self.__movement_arrays[0]) == 0: self.__pos_movement_arrays = 0
            self.__set_values_to_movement_point()
        def restart_path_from_start(self):
            """
            restart path from beginning
            :return:
            """
            self.__pos_movement_arrays = 0
            self.__set_values_to_movement_point()
        def set_path_pos(self, pos: int):
            """
            set position on path by value
            :param pos: number (int) of position camera should move to
            :return:
            """
            self.__pos_movement_arrays = pos
            if self.__pos_movement_arrays < 0: self.__pos_movement_arrays = 0
            if self.__pos_movement_arrays >= len(self.__movement_arrays[0]): self.__pos_movement_arrays = len(self.__movement_arrays[0]) - 1
            if len(self.movement_points) == 0: self.__pos_movement_arrays = 0
            self.__set_values_to_movement_point()
        def __set_values_to_movement_point(self):
            """set values pos,rot,spread to the one of the current movement point"""
            if len(self.__movement_arrays[0]) > self.__pos_movement_arrays:
                for i in range(3):
                    self[i] = float(self.__movement_arrays[i][self.__pos_movement_arrays])

        # change/get path
        def __sort_movement_points(self):
            self.__movement_points.sort(key=lambda x: x.frame_num)
        def __spline(self):
            arrays = [[] for j in range(7)]
            self.__movement_arrays = arrays
            for j in range(3):
                for mp in self.movement_points:
                    if mp[j] is not None:
                        arrays[j].append([int(mp[j]), int(mp.frame_num)])
                arrays[j] = np.array(arrays[j])
                try:
                    y, x = bspline(arrays[j], n=arrays[j][-1][1] * 10).T
                    self.__movement_arrays[j] = list(y)
                except Exception as e:
                    print(e)
                    self.__movement_arrays[j] = [self.movement_points[0][j]]
                if len(self.__movement_arrays[j]) < self.movement_points[-1].frame_num * 10:
                    for point in range(len(self.movement_points) - 1, -1, -1):
                        if self.__movement_points[point][j] is not None:
                            for i in range(len(self.__movement_arrays[j]), self.movement_points[-1].frame_num * 10 + 1):
                                self.__movement_arrays[j].append(self.movement_points[point][j])
                            break
        def update_spline(self):
            self.__sort_movement_points()
            self.__spline()

        def load_path_from_file(self, file_name: str):
            if os.path.isfile(file_name):
                with open(file_name) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    rows = list(csv_reader)
                    for row in rows:
                        if row[0] == "point":
                            file_to_num = lambda file: int(file) if file is not None and file != "" else None
                            self.add_movement_point(file_to_num(row[1]), file_to_num(row[2]), file_to_num(row[3]), file_to_num(row[4]), spline=False)
            self.__spline()
        def add_movement_point(self, x:float, y:float, rot:float, frame_num:int, spline:bool=True):
            self.__movement_points.append(self.MovementPoint(x, y, rot, frame_num))
            self.__sort_movement_points()
            if spline: self.__spline()
        def add_movement_point_from_object(self, object:MovementPoint, spline:bool=True):
            if isinstance(object, self.MovementPoint):
                self.__movement_points.append(object)
                self.__sort_movement_points()
                if spline: self.__spline()
        def clear_path(self):
            self.__movement_points = []
            self.__movement_arrays = [[] for i in range(4)]

        @property
        def movement_points(self) -> [MovementPoint]:
            return self.__movement_points
        @movement_points.setter
        def movement_points(self, points: [MovementPoint]):
            self.__movement_points = points
            self.__sort_movement_points()
            self.__spline()
        @property
        def num_movement_points(self) -> int:
            return len(self.movement_points)
        @property
        def movement_array(self):
            return self.__movement_arrays
        @property
        def num_frames(self) -> int:
            return len(self.__movement_arrays[0])
        @property
        def current_frame(self) -> int:
            return self.__pos_movement_arrays if len(self) != 0 else None

        @property
        def pos(self) -> vec2:
            return self.__pos
        @pos.setter
        def pos(self, pos: vec2):
            if isinstance(pos, vec2): self.__pos = pos
            if isinstance(pos, tuple) or isinstance(pos, list): self.__pos = vec2(pos[0], pos[1])
        def change_pos(self, pos: vec2):
            """adds the vector pos to players position"""
            self.__pos += pos

        @property
        def rot(self) -> float:
            return self.__rot
        @rot.setter
        def rot(self, angle: float):
            self.__rot = angle
            if self.__rot < 0: self.__rot = 360 + angle
            if self.__rot > 360: self.__rot = angle
        def change_rotation(self, angle:float):
            """adds the given angle to rotation of the player"""
            self.rot = self.__rot + angle

        def _draw_2d(self, screen:pygame.Surface, offset:vec2, zoom:float, color:[int,int,int], sight_color:[int,int,int], look:str, size:float, sight_size:[int,int], selected:Any, selected_color:[int,int,int]):
            if "p" in look:  # draw point for camera
                pygame.draw.circle(screen, color, (int(self.pos.x * zoom + offset.x), int(self.pos.y * zoom + offset.y)), size)
            if "d" in look: # draw direction
                dir = vec2((sight_size[0], 0))
                dir = dir.rotate(self.__rot) + self.pos
                pygame.draw.line(screen, sight_color, self.pos * zoom + offset, dir * zoom + offset, sight_size[1])
            if "l" in look:  # draw movement line
                for count, point in enumerate(self.__movement_points):
                    x = self.__movement_arrays[0][point.frame_num * 10] if point.x is None else point.x
                    y = self.__movement_arrays[1][point.frame_num * 10] if point.y is None else point.y
                    angle = self.__movement_arrays[3][point.frame_num * 10] if point.rot is None else point.rot
                    pos = vec2(x, y)
                    if selected == point:
                        cl = selected_color
                        dir = vec2((sight_size[0], 0))
                        dir = dir.rotate(angle) + pos
                        pygame.draw.line(screen, sight_color, pos * zoom + offset, dir * zoom + offset, sight_size[1])
                    else:
                        cl = color
                    if count != 0: pygame.draw.line(screen, color, previous_pos * zoom + offset, pos * zoom + offset)
                    pygame.draw.circle(screen, cl, (int(x * zoom + offset.x), int(y * zoom + offset.y)), size)
                    previous_pos = pos
                for count in range(len(self.__movement_arrays[0])):
                    if count != 0:
                        pygame.draw.line(screen, color, vec2(self.__movement_arrays[0][count - 1], self.__movement_arrays[1][count - 1]) * zoom + offset, vec2(self.__movement_arrays[0][count], self.__movement_arrays[1][count]) * zoom + offset)
                    if count % 10 == 0:
                        pos = vec2(self.__movement_arrays[0][count], self.__movement_arrays[1][count]) * zoom + offset
                        pygame.draw.circle(screen, color, (int(pos.x), int(pos.y)), 2)

        def __repr__(self):
            return "Camera at position {} looking in direction {}".format(self.pos, self.rot)
        def __getitem__(self, item:int):
            if item == 0:
                return self.pos.x
            elif item == 1:
                return self.pos.y
            else:
                return self.rot
        def __setitem__(self, key:int, value:float):
            if key == 0 and value is not None:
                self.pos.x = value
            elif key == 1 and value is not None:
                self.pos.y = value
            elif key == 2 and value is not None:
                self.rot = value
        def __delitem__(self, key:Union[int,MovementPoint]):
            if isinstance(key, int):
                del self.__movement_points[key]
            elif isinstance(key, self.MovementPoint):
                del self.__movement_points[self.__movement_points.index(key)]
        def __len__(self):
            return self.num_frames

    class Objects:
        """
        Objects in the world:
        This calls holds all the objects in the world
        The class of the single objects is defined below but can be inherited by the object class in your project
        """

        class Object(pygame.sprite.Sprite):
            """
            The class for objects located in the world.
            The logic and movement of the objects should be added in the file of the object in your project folder
            """
            def __init__(self, world, x: float, y: float, rot: float, name: str = None, file_image:Union[str,pygame.Surface]=None, group:pygame.sprite.Group=None, file_name: str = None):
                if group is None:
                    self.groups = world.objects.sprite_group
                    pygame.sprite.Sprite.__init__(self, self.groups)
                else:
                    self.groups = world.objects.sprite_group, group
                    pygame.sprite.Sprite.__init__(self, self.groups)

                if name is not None and name not in world.objects.names:
                    self.name = name
                else:
                    i = -1
                    while True:
                        i += 1
                        if "object{}".format(i) not in world.objects.names:
                            self.name = "object{}".format(i)
                            break

                self.__pos = vec2((x, y))
                self.__rot = rot

                self.__world = world

                self.image = None
                self.__image_calc_zoom = 0
                self.__image_calc_rot = 0
                self.__image_needs_redraw = True
                self.orig_image = None
                if file_image is not None:
                    if isinstance(file_image,pygame.Surface):
                        self.set_image(file_image)
                    else:
                        self.load_image_file(file_image)
                    self.rect = pygame.Rect(self.__pos,self.orig_image.get_size())
                else:
                    self.rect = pygame.Rect(self.__pos, (10, 10))
                self.mask = None
                self.__maks_calc_pos = [0, 0]

                self.file_name = file_name

            def load_image_file(self,path:str):
                # load an image file for the object
                self.orig_image = pygame.image.load(path)
                self.__image_needs_redraw = True
            def set_image(self,image:pygame.Surface):
                self.orig_image = image
                self.__image_needs_redraw = True

            # position
            @property
            def pos(self) -> vec2: return self.__pos
            @pos.setter
            def pos(self, pos:vec2):
                if isinstance(pos, vec2): self.__pos = pos
                if isinstance(pos, tuple) or isinstance(pos, list): self.__pos = vec2((pos[0], pos[1]))
            def change_pos(self, pos:vec2):
                """adds the vector pos to players position"""
                self.__pos += pos

            # rotation
            @property
            def rot(self) -> float:return self.__rot
            @rot.setter
            def rot(self, angle: float):
                self.__rot = angle
                if self.__rot < 0: self.__rot = 360 + angle
                if self.__rot > 360: self.__rot = angle
            def change_rotation(self, angle: float):
                """adds the given angle to rotation of the player"""
                self.rot = self.__rot + angle

            # update
            def update(self,fps:float):
                """this function is called every frame and should be overwritten to move/interact/... the object"""
                pass

            # draw
            def draw(self,surface:pygame.Surface,offset:vec2,zoom:float):
                """this function is called every frame and should be overwritten to draw the object"""
                pygame.draw.circle(surface,(255,0,0),self.pos+offset,10*zoom)
                pass

            def draw_image(self, surface:pygame.Surface, offset:vec2, zoom:float, img_pos:str="center", update_rect:bool=True, allow_update_maks:bool=True, image_scale_factor:float=None):
                if self.orig_image is not None:
                    if self.__image_calc_zoom != zoom or self.__image_calc_rot != self.__rot or self.__image_needs_redraw:
                        self.calc_image(zoom if image_scale_factor is None else zoom*image_scale_factor)
                        if allow_update_maks: self.calc_mask()
                    pos = vec2(0, 0)
                    if img_pos == "center":
                        pos = self.pos * zoom + offset - vec2(self.image.get_size()) / 2
                    if img_pos == "top":
                        pos = self.pos * zoom + offset - vec2(self.image.get_width() / 2, 0)
                    if img_pos == "bottom":
                        pos = self.pos * zoom + offset - vec2(self.image.get_width() / 2, self.image.get_height())
                    if img_pos == "left_top":
                        pos = self.pos * zoom + offset
                    if img_pos == "right_top":
                        pos = self.pos * zoom + offset - vec2(self.image.get_width(), 0)
                    if img_pos == "left_bottom":
                        pos = self.pos * zoom + offset - vec2(0, self.image.get_height())
                    if img_pos == "right_bottom":
                        pos = self.pos * zoom + offset - vec2(self.image.get_width(), self.image.get_height())
                    if img_pos == "left":
                        pos = self.pos * zoom + offset - vec2(0, self.image.get_height() / 2)
                    if img_pos == "right":
                        pos = self.pos * zoom + offset - vec2(self.image.get_width(), self.image.get_height() / 2)
                    surface.blit(self.image, pos)
                    if update_rect: self.rect = pygame.Rect(pos, self.image.get_size())
            def calc_image(self, zoom:float):
                size = (int(self.orig_image.get_width() * zoom), int(self.orig_image.get_height() * zoom))
                img = pygame.transform.rotate(pygame.transform.scale(self.orig_image, size), -self.rot - 90)
                self.__image_calc_rot = self.__rot
                self.__image_calc_zoom = zoom
                self.__image_needs_redraw = False
                self.image = img
            def calc_mask(self):
                self.mask = pygame.mask.from_surface(self.image)

        class Editor_Object(Object):
            def __init__(self, name, world, pos, rot, image):
                super(World_2d.Objects.Editor_Object, self).__init__(world, pos.x, pos.y, rot, None, image, None, name)
            def update_image(self, add_obj_names, add_obj_orig_images):
                if self.file_name in add_obj_names:
                    self.set_image(add_obj_orig_images[add_obj_names.index(self.file_name)])

        def __init__(self, world):
            self.__world = world
            self.__objects = []
            self.__iter = 0
            self.sprite_group = pygame.sprite.Group()

        def add_object(self,object:Object):
            self.__objects.append(object)
        def delete_object(self,object:Object):
            object.kill()
            if object in self.__objects: del self.__objects[self.__objects.index(object)]
        def delete_object_by_index(self,index:int):
            del self.__objects[index]
        def delete_object_by_name(self, name:str):
            for object in self.__objects:
                if object.name == name:
                    self.delete_object(object)
        def delete_all(self):
            self.__objects = []

        @property
        def num_objects(self) -> int:
            return len(self.__objects)
        @property
        def all_objects(self) -> [Object]:
            return self.__objects
        def get_object_by_index(self,index:int):
            return self.__objects[index]
        def get_object_by_name(self,name:str):
            for object in self.__objects:
                if object.name == name:
                    return object

        @property
        def names(self) -> [str]:
            for object in self.__objects:
                yield object.name

        def __len__(self):
            return self.num_objects
        def __getitem__(self, item:Union[int,str]):
            if isinstance(item,int):
                return self.get_object_by_index(item)
            elif isinstance(item,str):
                return self.get_object_by_name(item)
        def __delitem__(self, key:Union[int,str,Object]):
            if isinstance(key,int):
                self.delete_object_by_index(key)
            elif isinstance(key,str):
                self.delete_object_by_name(key)
            elif isinstance(key,World_2d.Objects.Object):
                self.delete_object(key)
        def __del__(self):
            self.delete_all()
        def __iter__(self):
            self.__iter = 0
            return self
        def __next__(self):
            if self.__iter < len(self):
                self.__iter += 1
                return self.__objects[self.__iter - 1]
            else:
                raise StopIteration

        def _update(self,fps:float):
            for object in self.__objects: object.update(fps)
        def _draw(self,offset:vec2,surface:pygame.Surface,zoom:float):
            for object in self.__objects:
                object.draw(surface,offset,zoom)
        def _draw_2d(self,offset:vec2,surface,zoom,selected_color:[int,int,int],selected:Any):
            for object in self.__objects:
                object.draw_image(surface,offset,zoom)
                if object == selected:
                    pygame.draw.circle(surface, selected_color, object.pos*zoom+offset, 10)
                    pygame.draw.circle(surface, selected_color, object.pos*zoom+offset, 15, 3)
    
    # create map
    def load_map(self, map_file:str, object_folder:str=None, recreate_player_only_if_not_exists:bool=True, recreate_camera_only_if_not_exsists:bool=True, add_camera_path:bool=True, draw_loading_screen:bool=False, screen:pygame.Surface=None, color:tuple=(255, 255, 255), editor_objects=False):
        """
        This function loads a map from a csv file, if set it draws a loading bar on the given screen in given color
        :param map_file: name of csv file
        :param object_folder: folder where object files are located
        :param recreate_player_only_if_not_exsists/recreate_camera_only_if_not_exsists: if True player/camera is created if it doesn't exsist, else always created
        :param add_camera_path: if True adds camera path if in file, else camerapath stays as it is
        :param draw_loading_screen: True for drawing an loading screen
        :param screen: only needed when drawing loading screen: surface to draw on
        :param color: color of the loading bar
        :return: None
        """
        if screen: orig = screen.copy()
        def draw_loading(total:int,current:int,text:str):
            if draw_loading_screen and screen:
                screen.blit(orig,(0,0))
                font = pygame.font.Font(pygame.font.match_font("arial"), 25)
                text_surface = font.render(text, True, color)
                text_rect = text_surface.get_rect()
                text_rect.center = (screen.get_width()/2, screen.get_height()/2)
                screen.blit(text_surface, text_rect)
                pygame.draw.line(screen, color, (100, screen.get_height()/2+50), (100 + (int((screen.get_width() - 200) / total) * current), screen.get_height()/2+50), 5)
                pygame.display.flip()
        try:
            with open(map_file) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                rows = list(csv_reader)
                loading_screen_status = 0
                loading_screen_length = len(rows)
                for row in rows:
                    loading_screen_status += 1
                    # player
                    if row[0] == "player":
                        if not (recreate_player_only_if_not_exists and self.has_player):
                            self.create_player(int(row[1]), int(row[2]), int(row[3]))
                    # camera
                    if row[0] == "camera":
                        if not (recreate_camera_only_if_not_exsists and self.has_camera):
                            self.create_camera(int(row[1]), int(row[2]), int(row[3]))
                        if add_camera_path and len(row) > 4:
                            self.camera.load_path_from_file(os.path.join(os.path.dirname(map_file),row[4]))
                    # object
                    if row[0] == "object":
                        if editor_objects:
                            new_object = World_2d.Objects.Editor_Object(row[1],self,vec2(int(row[2]),int(row[3])),int(row[4]),None)
                            self.objects.add_object(new_object)
                        elif object_folder is not None and object_folder != "":
                            object_folder = object_folder[object_folder.rfind("projects"):]
                            if not object_folder.startswith("projects"):
                                raise Exception("load_map: please give object folder from /projects/... on")
                            file_name = os.path.join(object_folder,row[1])
                            exec("import {} as obj".format(".".join(file_name.split(os.path.sep))))
                            eval("importlib.reload(obj)")
                            new_object = eval("obj.get(self)")
                            if not isinstance(new_object, World_2d.Objects.Object) or new_object is None:
                                raise Exception("could not load object "+row[1]+", check if get() method is available and returns a World_2d.Objects.Object object")
                            else:
                                self.objects.add_object(new_object)
                    draw_loading(loading_screen_length,loading_screen_status,"Loading Map")
            self.create_player(0,0,0,True)
            self.create_camera(0,0,0,True)
        except Exception as e:
            raise Exception("world could not be loaded from file {} - Error:{}".format(map_file,e.args))
        finally:
            self.create_player(0,0,0,only_if_not_already_exists=True)
            self.create_camera(0,0,0,only_if_not_already_exists=True)
    def save_map(self,folder:str,file_name:str,save_camera_path_if_exists:bool=True):
        if not file_name.endswith(".csv"): file_name = file_name+".csv"
        with open(os.path.join(folder, file_name), mode="w", newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            # player
            for player in self.__players:
                csvwriter.writerow(['player', int(player.pos.x), int(player.pos.y),int(player.rot)])
            # camera with path
            if len(self.camera) != 0 and save_camera_path_if_exists:
                csvwriter.writerow(
                    ['camera', int(self.camera.pos.x), int(self.camera.pos.y),
                     int(self.camera.rot), file_name[:-4] + "_camera.csv"])
                with open(os.path.join(folder, file_name[:-4] + "_camera.csv"), "w", newline='') as csvfile2:
                    csvwriter2 = csv.writer(csvfile2)
                    for movement_point in self.camera.movement_points:
                        int_to_file = lambda num: int(num) if num is not None else None
                        csvwriter2.writerow(["point", int_to_file(movement_point.x), int_to_file(movement_point.y),int_to_file(movement_point.rot),int_to_file(movement_point.frame_num)])
            # no path
            else:
                csvwriter.writerow(['camera', int(self.camera.pos.x), int(self.camera.pos.y),int(self.camera.rot)])
            # objects
            for obj in self.objects.all_objects:
                if obj.file_name is not None:
                    csvwriter.writerow(['object', obj.file_name, int(obj.pos.x), int(obj.pos.y), int(obj.rot)])
    def load_background(self, file_name: str):
        file_name = file_name[file_name.rfind("projects"):]
        if not file_name.startswith("projects"):
            raise Exception("load_background: please give file name from /projects/... on")
        exec("import {} as bg".format(".".join(file_name[:-3].split(os.path.sep))))
        eval("importlib.reload(bg)")
        backgr = eval("bg.get()")
        if not isinstance(backgr, Background) or backgr is None:
            raise Exception("could not load background, check if get() method is available and returns a Background object")
        else:
            backgr.set_world(self)
            self.background = backgr
    def load_menu(self, file_name: str, start: bool = False):
        file_name = file_name[file_name.rfind("projects"):]
        if not file_name.startswith("projects"):
            raise Exception("load_menu: please give file name from /projects/... on")
        exec("import {} as mn".format(".".join(file_name[:-3].split(os.path.sep))))
        eval("importlib.reload(mn)")
        menu = eval("mn.get()")
        if not isinstance(menu, Menu_creator) or menu is None:
            raise Exception("could not load menu, check if get() method is available and returns a Menu_creator object")
        else:
            self.menu.load_menu(menu)
            if start: self.menu.begin_menu()
    def create_player(self,x:float,y:float,rot:float,file_image=None,only_if_not_already_exists:bool=False,allow_only_one_player:bool=False):
        """
        create player in the world
        :param x: start pos x
        :param y: start pos y
        :param rot: direction player is looking towards
        :param only_if_not_already_exists: if True player is only created when there is not already a player in the world
        :param allow_only_one_player: if True a player wont be added but the first one replaced
        :return: None
        """
        if only_if_not_already_exists and not self.has_player or not only_if_not_already_exists:
            if allow_only_one_player and len(self.__players) > 0:
                self.__players[0] = World_2d.Player(self, x, y, rot, file_image)
            else:
                self.__players.append(World_2d.Player(self, x, y, rot, file_image))
    def create_camera(self,x:float,y:float,rot:float,only_if_not_already_exists:bool=False):
        """
        create camera in the world
        :param x: start pos x
        :param y: start pos y
        :param rot: direction player is looking towards
        :param only_if_not_already_exists: if True camera is only created when there is not already a camera in the world
        :return: None
        """
        if only_if_not_already_exists and not self.has_camera or not only_if_not_already_exists:
            self.__camera = World_2d.Camera(self, x, y, rot)
    
    # delete things
    def delete_player(self,all:bool=True,player_num:int=0):
        """deletes players: if all is True all players are deleted, else only the player_num"""
        if all:
            self.__players = []
        else:
            del self.__players[player_num]
    def delete_camera(self):
        del self.__camera
        self.__camera = None
    def clear_world(self, player: bool = False, camera: bool = False, camera_path: bool = False, objects: bool = False):
        """
        delete everything in the world if wanted even player
        :param world: true for deleting walls and light
        :param player: true for deleting all players
        :param camera: true for deleting camera
        :param camera_path: true for clearing camera path
        :return: None
        """
        if player:
            self.delete_player()
        if camera:
            self.delete_camera()
        if camera_path and self.has_camera:
            self.camera.clear_path()
        if objects:
            self.objects.delete_all()

    @property
    def player(self):
        """returns None if there is no player, the player if there is only one player, or a list of the players if there is more than one"""
        if len(self.__players) == 0:
            return None
        if len(self.__players) == 1:
            return self.__players[0]
        else:
            return self.__players
    @property
    def player_list(self):
        """returns a list of player, if there is no player, the list is empty"""
        return self.__players
    @property
    def has_player(self) -> bool:
        return len(self.__players) > 0
    @property
    def num_players(self) -> int: return len(self.__players)
    @property
    def camera(self) -> Camera: return self.__camera
    @property
    def has_camera(self) -> bool: return self.__camera is not None

    @property
    def zoom(self) -> float: return self.__last_zoom
    @property
    def offset(self) -> vec2:
        return self.__last_offset
    @property
    def paused(self) -> bool:
        return self.menu.get_paused() or self.__paused

    def pause_game(self):
        self.__paused = True
    def resume_game(self):
        self.__paused = False

    # set camera/player to the values of the player/camera
    def set_camera_to_player_values(self,player_num:int=0):
        """sets position and view direction / view angle to the values from the player"""
        if bool(self):
            self.camera.pos = self.__players[player_num].pos
            self.camera.rot = self.__players[player_num].rot
    def set_player_to_camera_values(self,player_num:int=0):
        """sets position and view direction / view angle to the values from the player"""
        if bool(self):
            self.__players[player_num].pos = self.camera.pos
            self.__players[player_num].rot = self.camera.rot

    # update everything (movement,objects) in one function
    def update_game(self, events:[pygame.event], fps:float, *args) -> [[str, {str: Optional[Union[str, int]]}], bool]:
        """
        updates player
        :param events: list of event (pygame.events.get())
        :param fps: current fps count
        :return: None
        """
        if not self.paused:
            for player in self.__players:
                player.update(player, events, fps, *args)
            self.objects._update(fps)
        return self.menu.update([self.controllers.event(event) for event in events])
    def update_movie(self, events:[pygame.event], *args) -> [[str, {str: Optional[Union[str, int]]}], bool]:
        """
        moves camera to next position
        :param events: list of event (pygame.events.get())
        :return:
        """
        if not self.paused:
            self.camera.walk_on_path(*args)
            self.objects._update()
        return self.menu.update([self.controllers.event(event) for event in events])

    # render
    def draw_2d(self, surface:pygame.Surface,
                background_color:tuple=(0, 0, 0),
                player_color:tuple=(80, 200, 80), player_sight_color:tuple=(90, 175, 90),
                camera_color:tuple=(80,80,200), camera_sight_color:tuple=(90,90,175),
                draw_background=True, center_pos:vec2=None, zoom:float=0.5,
                player_look:str="prd", player_size:int=5, player_sight_size:tuple=(40, 2),
                camera_look:str="", camera_size:int=5, camera_sight_size:tuple=(30,2),
                selected=None, selected_color:tuple=(180,50,50)):
        """
        draw a top view map of the game with your own colors, sizes, ...
        :param surface: surface to draw on
        :param background_color: color of the ground
        :param player_color: color of the player
        :param player_sight_color: color of the lines showing the players viewing direction
        :param camera_color:
        :param camera_sight_color:
        :param draw_background: false for disabling drawing the background
        :param center_pos: point of map that is in the center of the screen, if None player is in the center
        :param zoom: zooming of the map (1=orig size, <1=see more of map, >1 zoom into map)
        :param player_look: string with letters deciding how player should be drawn (p=player as point, r=player as rectangle, d=line showing direction player is looking at). letters con also be combined. Empty string for not drawing player
        :param player_size: size of rect or point showing player
        :param player_sight_size: width of lines showing view of player
        :param camera_look: string with letters (p=draw point, s=lines showing view direction, l=draw movement line) letters con also be combined. Empty string for not drawing camera
        :param camera_size: size of point showing camera
        :param camera_sight_size: length of walls showing camera view
        :param selected: if not None the given object will be drawn in other color
        :param selected_color: color of the object if selected is given
        :return: None
        """

        if center_pos == None:
            if self.player is not None:
                center_pos = vec2((surface.get_width() / 2, surface.get_height() / 2)) - self.player.pos * zoom
            else:
                center_pos = vec2((surface.get_width() / 2, surface.get_height() / 2))

        # draw background
        if draw_background: surface.fill(background_color)

        # draw_player
        for player in self.__players:
            player._draw_2d(surface, center_pos, zoom, selected_color if selected == self.player else player_color, selected_color if selected == self.player else player_sight_color, player_look, player_size, player_sight_size)
        if self.camera is not None:
            self.camera._draw_2d(surface, center_pos, zoom, selected_color if selected == self.camera else camera_color, selected_color if selected == self.camera else camera_sight_color, camera_look, camera_size, camera_sight_size, selected, selected_color)

        # draw objects
        self.objects._draw_2d(center_pos, surface, zoom, selected_color,selected)
    def draw(self, surface:pygame.Surface, offset:vec2=vec2(0,0), do_background:bool=True, save:bool=False, file_name:str="unnamed.png"):
        """
        draws the game on a pygame window
        :param surface: surface to draw on
        :param player: if true draw from player offset, else from camera offset
        :param do_background: if True draws sky and floor on surface
        :param save: if True save result as file
        :param: filename in case save = True
        :return: None
        """
        # background
        _offset = None
        zoom = None
        if do_background:
            values = self.background.draw(surface)
            if values is not None:
                offset = values[0]
                zoom = values[1]

        if not isinstance(_offset,vec2) or _offset is None:
            _offset = offset
        if zoom is None:
            zoom = 1
        self.__last_zoom = zoom
        self.__last_offset = _offset

        self.objects._draw(_offset,surface,zoom)
        for player in self.__players:
            player.draw(player,surface,_offset,zoom)

        self.menu.draw(surface)
        
        # save if wanted
        if save: pygame.image.save(surface,file_name)
    def draw_rects(self, surface:pygame.Surface, player_rect:bool=True,object_color:[int,int,int]=(0,0,0),player_color:[int,int,int]=(255,0,0),width:int=1):
        if player_rect:
            for player in self.__players:
                pygame.draw.rect(surface,player_color,player.rect,width)
        for object in self.objects: pygame.draw.rect(surface,object_color,object.rect,width)

    # magic functions
    def __repr__(self):
        return "two_dimensional-World with {} Objects".format(len(self.objects))
    def __bool__(self):
        """return True if world has camera AND player"""
        return self.has_player and self.has_camera
    def __getitem__(self, item):
        if isinstance(item, int):
            self.objects.get_object_by_index(item)
        elif isinstance(item, str):
            self.objects.get_object_by_name(item)
    def __delitem__(self, key):
        if isinstance(key,int):
            self.objects.delete_object_by_index(key)
        elif isinstance(key,str):
            self.objects.delete_object_by_name(key)
    def __contains__(self, item):
        return item in self.objects.all_objects
    def __len__(self):
        return self.objects.num_objects