##i## Image files that belong to this object
# these should also be placed in the folder 'objects'
# the first filename is the default
# img/Meteors/meteorBrown_big1.png
# img/Meteors/meteorBrown_big2.png
# img/Meteors/meteorBrown_med1.png
# img/Meteors/meteorBrown_med2.png
# img/Meteors/meteorBrown_small1.png
# img/Meteors/meteorBrown_small2.png
# img/Meteors/meteorBrown_tiny1.png
# img/Meteors/meteorGrey_big1.png
# img/Meteors/meteorGrey_big2.png
# img/Meteors/meteorGrey_med1.png
# img/Meteors/meteorGrey_med2.png
# img/Meteors/meteorGrey_small1.png
# img/Meteors/meteorGrey_small2.png
# img/Meteors/meteorGrey_tiny1.png
##ni##

from pygine.world_2d import World_2d
import pygame
vec2 = pygame.math.Vector2
vec3 = pygame.math.Vector3
from random import randrange, randint, uniform

class Stone(World_2d.Objects.Object):
    def __init__(self, world:World_2d,images,group,map_width,map_height,size,speed_min_down,speed_max_down,speed_max_side):
        super(Stone,self).__init__(world,0,0,-90,None,None,group)
        self.vel = vec2(0,0)
        self.world = world
        self.width,self.height = map_width,map_height
        self.size = size
        self.images = images
        self.speeds = (speed_min_down, speed_max_down, speed_max_side)
        self.mob_size = 0
        self.recreate = True
        self.randomly_set_pos()

    def randomly_set_pos(self):
        if self.recreate:
            random = randint(0,5)
            self.mob_size = 3 if random<=1 else (2 if random<=3 else 1)
            self.set_image(self.images[random])
            self.pos = vec2(randrange(0, self.width), -45*(self.size/10))
            self.vel = vec2(uniform(-self.speeds[2], self.speeds[2]), uniform(self.speeds[0], self.speeds[1]))
        else:
            self.world.objects.delete_object(self)

    def update(self, fps):
        self.change_rotation(5*fps)
        self.pos += self.vel * fps
        ##e## reposition when leaving map
        if self.pos.x < -45*(self.size/10) or self.pos.x > self.width + 45*(self.size/10):
            self.randomly_set_pos()
        if self.pos.y > self.height + 45*(self.size/10):
            self.randomly_set_pos()

    def draw(self,surface:pygame.Surface, offset:vec2, zoom:float):
        self.draw_image(surface,offset,zoom,update_rect=True,allow_update_maks=True,image_scale_factor=self.size/10)