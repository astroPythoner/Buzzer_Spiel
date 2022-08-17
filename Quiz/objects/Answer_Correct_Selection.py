##i## Image files that belong to this object
# these should also be placed in the folder 'objects'
# the first filename is the default
##ni##

from pygine.world_2d import World_2d
import pygame
vec2 = pygame.math.Vector2
vec3 = pygame.math.Vector3
import pygine


class Correct_Selection(World_2d.Objects.Object):
    def __init__(self, world:World_2d,correct:bool,screen):
        super(Correct_Selection,self).__init__(world,0,0,0,None,None,None)
        self.correct = correct
        self.world = world
        self.vel = vec2(0, 0)
        self.screen = screen
        self.pos = vec2(screen.get_width() * ((2 if correct else 1) / 3),screen.get_height() / 2)
        self.destination = vec2(screen.get_width() / 2, 125)

    def update(self,fps):
        if self.vel == vec2(0,0):
            self.pos = vec2(self.screen.get_width() * ((2 if self.correct else 1) / 3), self.screen.get_height() / 2)
            self.destination = vec2(self.screen.get_width() / 2, 125)
        else:
            self.pos += self.vel * fps
            if self.pos.y <= self.destination.y:
                self.pos = vec2(self.screen.get_width() / 2, 125)
                self.destination = vec2(self.screen.get_width() / 2, 125)

    def show_results(self,correct:bool,screen):
        if correct == self.correct:
            self.destination = vec2(screen.get_width()/2,125)
            self.vel = (self.destination-self.pos)/10
        else:
            self.world.objects.delete_object(self)

    def draw(self,surface:pygame.Surface, offset:vec2, zoom:float):
        if not self.correct:
            pygame.draw.rect(surface, (180, 50, 50), (int(self.pos.x - 87), int(self.pos.y - 25), 175, 50), border_radius=8)
            pygine.draw_text(surface, "falsch", 35, int(self.pos.x), int(self.pos.y), color=(255, 255, 255), rect_place=pygine.CENTER)
        else:
            pygame.draw.rect(surface, (50, 180, 50), (int(self.pos.x - 87), int(self.pos.y - 25), 175, 50), border_radius=8)
            pygine.draw_text(surface, "richtig", 35, int(self.pos.x), int(self.pos.y), color=(255, 255, 255), rect_place=pygine.CENTER)


def add_correct_selection(world:World_2d,screen):
    world.objects.add_object(Correct_Selection(world,True,screen))
    world.objects.add_object(Correct_Selection(world,False,screen))