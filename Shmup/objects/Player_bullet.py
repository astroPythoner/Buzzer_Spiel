##i## Image files that belong to this object
# these should also be placed in the folder 'objects'
# the first filename is the default
# img/Player/Lasers/laserBlue_big.png
# img/Player/Lasers/laserGreen_big.png
# img/Player/Lasers/laserRed_big.png
##ni##

from pygine.world_2d import World_2d
from pygine import BOTTOM
import pygame
vec2 = pygame.math.Vector2
vec3 = pygame.math.Vector3

class Player_Bullet(World_2d.Objects.Object):
    def __init__(self, world:World_2d,x_pos,img,group,map_width,map_height,size,speed_up,speed_side=0):
        super(Player_Bullet,self).__init__(world,x_pos,map_height-85,-90,None,img,group)
        self.vel = vec2(speed_side,-speed_up)
        self.world = world
        self.width, self.height = map_width, map_height
        self.size = size
        self.mask = pygame.mask.from_surface(img)

    def update(self,fps):
        self.pos += self.vel * fps
        if self.pos.y < 0:
            self.world.objects.delete_object(self)

    def draw(self,surface:pygame.Surface, offset:vec2, zoom:float):
        self.draw_image(surface,offset,zoom,img_pos=BOTTOM,update_rect=True,allow_update_maks=False,image_scale_factor=self.size/10)