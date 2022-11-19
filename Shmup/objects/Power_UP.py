##i## Image files that belong to this object
# these should also be placed in the folder 'objects'
# the first filename is the default
# img/Power_Ups/bolt_gold.png
# img/Power_Ups/shield_gold.png
# img/Power_Ups/star_gold.png
##ni##

from pygine.world_2d import World_2d
from pygine import TOP
import pygame
vec2 = pygame.math.Vector2
vec3 = pygame.math.Vector3

class PowerUp(World_2d.Objects.Object):
    def __init__(self, world:World_2d,pos,img,group,map_height,size,speed,type):
        super(PowerUp,self).__init__(world,pos.x,pos.y,-90,None,img,group)
        self.vel = vec2(0,speed)
        self.world = world
        self.height = map_height
        self.size = size
        self.type = type  # 0 -> bolt, 1 -> shield, 2 -> star

    def update(self,fps):
        self.pos += self.vel * fps
        if self.pos.y > self.height:
            self.world.objects.delete_object(self)

    def draw(self,surface:pygame.Surface, offset:vec2, zoom:float):
        self.draw_image(surface,offset,zoom,img_pos=TOP,update_rect=True,allow_update_maks=False,image_scale_factor=self.size/10)