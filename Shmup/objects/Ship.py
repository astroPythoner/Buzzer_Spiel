##i## Image files that belong to this object
# these should also be placed in the folder 'objects'
# the first filename is the default
# img/Enemies/enemyBlack1.png
# img/Enemies/enemyBlack2.png
# img/Enemies/enemyBlack3.png
# img/Enemies/enemyBlack4.png
# img/Enemies/enemyBlack5.png
# img/Enemies/enemyBlue1.png
# img/Enemies/enemyBlue2.png
# img/Enemies/enemyBlue3.png
# img/Enemies/enemyBlue4.png
# img/Enemies/enemyBlue5.png
# img/Enemies/enemyGreen1.png
# img/Enemies/enemyGreen2.png
# img/Enemies/enemyGreen3.png
# img/Enemies/enemyGreen4.png
# img/Enemies/enemyGreen5.png
# img/Enemies/enemyRed1.png
# img/Enemies/enemyRed2.png
# img/Enemies/enemyRed3.png
# img/Enemies/enemyRed4.png
# img/Enemies/enemyRed5.png
##ni##

from pygine.world_2d import World_2d
import pygame
vec2 = pygame.math.Vector2
vec3 = pygame.math.Vector3
from random import choice, randrange, random, uniform
from objects.Bullet import Bullet
import time

class Ship(World_2d.Objects.Object):
    def __init__(self, world:World_2d,images,bullet_image,group,shot_group,map_width,map_height,size,speed_min_down,speed_max_down,speed_max_side,bullet_time,pos=None):
        super(Ship,self).__init__(world,0,0,-90,None,choice(images),group)
        self.vel = vec2(0,0)
        self.last_bullet = time.time()+random()*bullet_time
        self.bullet_image = bullet_image
        self.world = world
        self.shot_group = shot_group
        self.bullet_time = bullet_time
        self.width, self.height = map_width, map_height
        self.size = size
        self.speeds = (speed_min_down,speed_max_down,speed_max_side)
        self.mob_size = 1.5
        self.recreate = True
        if pos is None:
            self.randomly_set_pos()
        else:
            self.pos = pos
            self.vel = vec2(uniform(-self.speeds[2], self.speeds[2]), uniform(self.speeds[0], self.speeds[1]))

    def randomly_set_pos(self):
        if self.recreate:
            self.pos = vec2(randrange(0, self.width), -45*(self.size/10))
            self.vel = vec2(uniform(-self.speeds[2], self.speeds[2]), uniform(self.speeds[0], self.speeds[1]))
        else:
            self.world.objects.delete_object(self)

    def update(self,fps):
        self.pos += self.vel*fps
        ##e## shoot bullet
        if time.time() - self.last_bullet > self.bullet_time:
            self.last_bullet = time.time()
            self.world.objects.add_object(Bullet(self.world,self.pos,self.bullet_image,self.shot_group,self.width,self.height,self.size,vec2(0,self.speeds[1]+2)))
        ##e## reposition when leaving map
        if self.pos.x < -45*(self.size/10) or self.pos.x > self.width+45*(self.size/10):
            self.randomly_set_pos()
        if self.pos.y > self.height+45*(self.size/10):
            self.randomly_set_pos()

    def draw(self,surface:pygame.Surface, offset:vec2, zoom:float):
        self.draw_image(surface,offset,zoom,update_rect=True,allow_update_maks=True,image_scale_factor=self.size/10)
