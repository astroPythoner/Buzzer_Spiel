##i## Image files that belong to this object
##i## Image files that belong to this object
# these should also be placed in the folder 'objects'
# the first filename is the default
##ni##

from pygine.world_2d import World_2d
import pygame
vec2 = pygame.math.Vector2
vec3 = pygame.math.Vector3
import pygine
import time

class Leader_Board(World_2d.Objects.Object):
    def __init__(self, world:World_2d,player,before,after,screen,using_teams,teams,players,text_color,rect_color,text_on_rect_color,text_size,quiz_result=False):
        super(Leader_Board,self).__init__(world,0,0,0,None,None,None)
        self.world = world
        self.text_color = text_color
        self.rect_color = rect_color
        self.text_on_rect_color = text_on_rect_color
        self.text_size = text_size
        self.quiz_result = quiz_result
        self.using_teams = using_teams
        self.teams = teams
        self.players = players
        self.after = after
        self.start_pos, self.end_pos, self.names, self.points = [], [], [], []
        pos_before,pos_after = [i[0] for i in before].index(player), [i[0] for i in after].index(player)
        for count,player in enumerate(before):
            pos = int(screen.get_height() * (1 / 3) + 50*self.text_size * count)
            dest = pos
            if pos_before > pos_after:
                if pos_after <= count < pos_before: dest += 50*self.text_size
                if count == pos_before: dest -= (pos_before-pos_after)*50*self.text_size
            else:
                if pos_before < count <= pos_after: dest -= 50*self.text_size
                if count == pos_before: dest += (pos_after-pos_before)*50*self.text_size
            self.start_pos.append(pos)
            self.end_pos.append(dest)
            self.names.append(f"{[i[0] for i in after].index(player[0])+1}. {player[0]}")
            self.points.append(player[1])
        self.player_idx = pos_before
        self.player_start_points,self.player_end_points  = [i[1] for i in before][pos_before], [i[1] for i in after][pos_after]
        self.time = time.time()
        self.width = 0
        for name in self.names:
            rect = pygine.get_text_rect(name,42*self.text_size)
            if rect.width > self.width: self.width = rect.width
        self.width += 65*self.text_size

    def update(self,fps):
        pass

    def percent_over(self):
        if time.time()-self.time > 1: return 1
        return min([time.time()-self.time,1])

    def get_draw_on_top(self):
        return not self.quiz_result # or time.time()-self.time < 2

    def draw(self,surface:pygame.Surface, offset:vec2, zoom:float):
        p = self.percent_over()
        if self.get_draw_on_top():
            # all players except of answering one
            for count,pos in enumerate(self.start_pos):
                if count != self.player_idx:
                    pos = self.start_pos[count] + (self.end_pos[count]-self.start_pos[count])*p
                    pygame.draw.rect(surface, self.rect_color, (int(surface.get_width() / 2 - self.width/2), int(pos-22*self.text_size), self.width, 44*self.text_size), border_radius=int(8*self.text_size))
                    pygine.draw_text(surface, self.names[count],30*self.text_size,int(surface.get_width() / 2 - self.width/2 +8), int(pos),rect_place=pygine.LEFT,color=self.text_on_rect_color)
                    pygine.draw_text(surface, str(round(self.points[count])), 30*self.text_size, int(surface.get_width() / 2 + self.width/2 -8), int(pos), rect_place=pygine.RIGHT, color=self.text_on_rect_color)
            # answering player
            size = 1 + ((1-p) if p > 0.5 else p)
            points = self.player_start_points + (self.player_end_points-self.player_start_points)*p
            color = (100, 200, 100) if self.player_end_points > self.player_start_points else (200,100,100)
            pos = self.start_pos[self.player_idx] + (self.end_pos[self.player_idx] - self.start_pos[self.player_idx]) * p
            pygame.draw.rect(surface, color, (int(surface.get_width() / 2 - (self.width * size) / 2), int(pos - (44*self.text_size * size) / 2), int(self.width * size), int(44*self.text_size * size)), border_radius=int(8*self.text_size))
            pygine.draw_text(surface, self.names[self.player_idx], int(30*size*self.text_size), int(surface.get_width() / 2 - (self.width * size) / 2 + 8), int(pos), rect_place=pygine.LEFT, color=(255, 255, 255))
            pygine.draw_text(surface, str(round(points)), int(30*size*self.text_size), int(surface.get_width() / 2 + (self.width * size) / 2 - 8), int(pos), rect_place=pygine.RIGHT, color=(255, 255, 255))
        else:
            # Top 3 of players
            p = min((time.time()-self.time) * 2,1)
            for num,player in enumerate(self.after):
                pygine.draw_text(surface, "Quiz vorbei", 35*self.text_size, int(surface.get_width()/2), 50, color=(255, 255, 255), rect_place=pygine.CENTER)
                if num < 3:
                    color = [(226, 176, 7),(138, 149, 151),(191, 137, 112)][num]
                    orig = vec2(surface.get_width()/2,self.end_pos[num])
                    dest = [vec2(surface.get_width()*3/6,surface.get_height()*1/3),vec2(surface.get_width()*1/6,surface.get_height()*1/3+70),vec2(surface.get_width()*5/6,surface.get_height()*1/3+120)][num]
                    pos = orig+(dest-orig)*p
                    s = pygame.Surface((int(self.width),int((surface.get_height()-dest.y)*p)),pygame.SRCALPHA)
                    s.fill((0,0,0,150))
                    surface.blit(s,(int(dest.x-self.width/2),int(surface.get_height()-s.get_height())))
                    pygame.draw.rect(surface, color, (int(pos.x - self.width / 2), int(pos.y - 22*self.text_size), int(self.width), 44*self.text_size), border_radius=int(8*self.text_size))
                    pygine.draw_text(surface, player[0], 30*self.text_size, int(pos.x - self.width / 2 + 8), int(pos.y), rect_place=pygine.LEFT, color=(255, 255, 255))
                    pygine.draw_text(surface, str(round(player[1])), 30*self.text_size, int(pos.x + self.width / 2 - 8), int(pos.y), rect_place=pygine.RIGHT, color=(255, 255, 255))
                    # teams
                    teams = {t:0 for t in self.teams.values()}
                    if p >= 1 and self.using_teams:
                        for idx, name in enumerate(self.players):
                            if self.teams[name] == player[0]:
                                teams[self.teams[name]] += 1
                                pygine.draw_text(surface, name, 25*self.text_size, int(pos.x), int(pos.y)+teams[self.teams[name]]*35*self.text_size+12, rect_place=pygine.CENTER, color=(255, 255, 255))
                # other players
                else:
                    size = 0.65
                    pos = vec2(surface.get_width()*((num*2-5)/((len(self.after)-3)*2)),surface.get_height()-65*self.text_size)
                    pygame.draw.rect(surface, self.rect_color, (int(pos.x - (self.width * size) / 2), int(pos.y - (44*self.text_size * size) / 2), int(self.width * size), int(44*self.text_size * size)), border_radius=int(8*self.text_size))
                    pygine.draw_text(surface, str(num+1)+": "+player[0], int(30*self.text_size * size), int(pos.x - (self.width * size) / 2 + 8), int(pos.y), rect_place=pygine.LEFT, color=self.text_on_rect_color)
                    pygine.draw_text(surface, str(round(player[1])), int(30*self.text_size * size), int(pos.x + (self.width * size) / 2 - 8), int(pos.y), rect_place=pygine.RIGHT, color=self.text_on_rect_color)
