##i## Image files that belong to this object
# these should also be placed in the folder 'objects'
# the first filename is the default
# img/Explosions/regularExplosion00.png
# img/Explosions/regularExplosion01.png
# img/Explosions/regularExplosion02.png
# img/Explosions/regularExplosion03.png
# img/Explosions/regularExplosion04.png
# img/Explosions/regularExplosion05.png
# img/Explosions/regularExplosion06.png
# img/Explosions/regularExplosion07.png
# img/Explosions/regularExplosion08.png
# img/Explosions/sonicExplosion00.png
# img/Explosions/sonicExplosion01.png
# img/Explosions/sonicExplosion02.png
# img/Explosions/sonicExplosion03.png
# img/Explosions/sonicExplosion04.png
# img/Explosions/sonicExplosion05.png
# img/Explosions/sonicExplosion06.png
# img/Explosions/sonicExplosion07.png
# img/Explosions/sonicExplosion08.png
##ni##

from pygine.world_2d import World_2d
import pygame
from time import time
vec2 = pygame.math.Vector2
vec3 = pygame.math.Vector3

class Explosion(World_2d.Objects.Object):
    def __init__(self, world:World_2d, pos, images, size):
        super(Explosion,self).__init__(world,pos.x,pos.y,-90,None,images[0],None)
        self.images = images
        self.image_num = 0
        self.objects = world.objects
        self.size = size
        self.last_img_swath = time()

    def update(self,fps):
        if time() - self.last_img_swath > 1/8:
            self.set_image(self.images[self.image_num])
            self.image_num += 1
            if self.image_num == len(self.images):
                self.image_num = len(self.images)-1
                self.objects.delete_object(self)

    def draw(self,surface:pygame.Surface, offset:vec2, zoom:float):
        self.draw_image(surface,offset,zoom, allow_update_maks=False, update_rect=False, image_scale_factor=self.size/10)
