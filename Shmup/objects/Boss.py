##i## Image files that belong to this object
# these should also be placed in the folder 'objects'
# the first filename is the default
# img/Enemies/End-Boss/Black/ship_10.png
# img/Enemies/End-Boss/Black/ship_11.png
# img/Enemies/End-Boss/Black/ship_12.png
# img/Enemies/End-Boss/Blue/ship_13.png
# img/Enemies/End-Boss/Blue/ship_14.png
# img/Enemies/End-Boss/Blue/ship_15.png
# img/Enemies/End-Boss/Green/ship_16.png
# img/Enemies/End-Boss/Green/ship_17.png
# img/Enemies/End-Boss/Green/ship_18.png
# img/Enemies/End-Boss/Red/ship_19.png
# img/Enemies/End-Boss/Red/ship_20.png
# img/Enemies/End-Boss/Red/ship_21.png
##ni##

from objects.Bullet import Bullet
from objects.Ship import Ship
from pygine.world_2d import World_2d
import time
from random import randint
import pygame
vec2 = pygame.math.Vector2
vec3 = pygame.math.Vector3

MODE_SHOOT = "mode shoot"
MODE_ENEMY = "mode enemy"

boss_shoot_loc = {10:[(0,5),(61,48),(-61,48),(120,80),(-120,80)],
                  11:[(0,5),(61,48),(-61,48),(120,80),(-120,80)],
                  12:[(0,50),(58,55),(-58,55),(123,75),(-123,75)],
                  13:[(0,10),(32,32),(-32,32),(70,50),(-70,50)],
                  14:[(0,10),(40,25),(-40,25),(67,45),(-67,45)],
                  15:[(0,10),(25,42),(-25,42),(75,70),(-75,70)],
                  16:[(0,10),(37,32),(-37,32),(93,75),(-93,75)],
                  17:[(0,10),(57,54),(-57,54),(102,80),(-102,80)],
                  18:[(0,0),(52,46),(-52,46),(96,95),(-96,95)],
                  19:[(0,45),(58,55),(-58,55),(92,86),(-92,86)],
                  20:[(0,0),(67,32),(-67,32),(116,68),(-116,68)],
                  21:[(0,5),(48,25),(-48,25),(93,67),(-93,67)]}

class Boss(World_2d.Objects.Object):
    def __init__(self, world:World_2d, image, ship_num, size, bullet_image, ship_images, shot_group, ship_group, map_width, map_height, ship_size, ship_min_down, ship_max_down, ship_max_side, ship_shoot_time):
        super(Boss,self).__init__(world,map_width/2,-80,-90,None,image,None)
        self.size = size
        self.rot_speed = 1.5
        self.ship_num = ship_num
        self.map_width,self.map_height = map_width,map_height
        self.mode = MODE_SHOOT
        self.last_mode_change = time.time()
        self.last_shoot = time.time()
        self.world = world
        self.bullet_image = bullet_image
        self.ship_images = ship_images
        self.shot_group = shot_group
        self.ship_group = ship_group
        self.ship_size, self.ship_min_down, self.ship_max_down, self.ship_max_side, self.ship_shoot_time = ship_size,ship_min_down,ship_max_down,ship_max_side, ship_shoot_time
        self.x_speed = 4

    def update(self,fps):
        ##e## rotation
        self.change_rotation(self.rot_speed*fps)
        if self.rot > 315: self.rot_speed = -1.5
        if self.rot < 225: self.rot_speed = 1.5
        ##e## move onto map oand then sidewards
        if self.pos.y < self.map_height/4:
            self.pos.y += 5 * fps
        else:
            self.pos.x += self.x_speed * fps
            if self.pos.x < self.map_width*1/3:
                self.x_speed = 4
            if self.pos.x > self.map_width*2/3:
                self.x_speed = -4
        ##e## shoot
        if self.mode == MODE_SHOOT:
            if time.time()-self.last_shoot > 0.4:
                self.last_shoot = time.time()
                for j in boss_shoot_loc[self.ship_num]:
                    vector = pygame.math.Vector2(j)*(self.size/7)
                    vector = vector.rotate(self.rot+90)
                    self.world.objects.add_object(Bullet(self.world, self.pos + vector, self.bullet_image, self.shot_group, self.map_width, self.map_height, self.size, vec2(-15,0).rotate(self.rot)))
        ##e## release mobs
        else:
            if time.time() - self.last_shoot > 0.3:
                self.last_shoot = time.time()
                ship = Ship(self.world,self.ship_images,self.bullet_image,self.ship_group,self.shot_group,self.map_width,self.map_height,self.ship_size,self.ship_min_down,self.ship_max_down,self.ship_max_side,self.ship_shoot_time,vec2(self.pos))
                ship.recreate = False
                self.world.objects.add_object(ship)
        ##e## switch mode
        if time.time() - self.last_mode_change > 8:
            if self.mode == MODE_SHOOT: self.mode = MODE_ENEMY
            else: self.mode = MODE_SHOOT
            self.last_mode_change = time.time()

    def draw(self,surface:pygame.Surface, offset:vec2, zoom:float):
        self.draw_image(surface,offset,zoom,image_scale_factor=self.size/10,allow_update_maks=True)