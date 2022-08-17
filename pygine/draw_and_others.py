import pygame
from typing import Any, List, Optional, Sequence, Text, Tuple, Union, overload, Iterable

vec2 = pygame.math.Vector2


def get_match_font(font_name: str) -> pygame.font:
    """get a pygame font from name (see pygame.font.match_font)"""
    f = pygame.font.match_font(font_name)
    if f is None: f = pygame.font.match_font(font_name + "ttf")
    if f is None: f = pygame.font.match_font(font_name + "ttc")
    return f


default_font = get_match_font("arial")

def draw_text(surf: pygame.surface, text: str, size: int, x: int, y: int, font_name: str = None, color: [int, int, int] = (0, 0, 0), rect_place: str = "left_top") -> pygame.rect:
    """draw the text onto the surface at the pos (x,y) rectplace in the color
    pass font_name for other fonts, or None for default font (arial)
    return the Rect of the text
    """
    if font_name is None: font = pygame.font.Font(default_font, int(size))
    else: font = pygame.font.Font(get_match_font(font_name), int(size))
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    if rect_place == "center":
        text_rect.center = (x, y)
    if rect_place == "top":
        text_rect.midtop = (x, y)
    if rect_place == "button":
        text_rect.midbottom = (x, y)
    if rect_place == "left_top":
        text_rect.topleft = (x, y)
    if rect_place == "right_top":
        text_rect.topright = (x, y)
    if rect_place == "left_bottom":
        text_rect.bottomleft = (x, y)
    if rect_place == "right_bottom":
        text_rect.bottomright = (x, y)
    if rect_place == "left":
        text_rect.midleft = (x, y)
    if rect_place == "right":
        text_rect.midright = (x, y)

    if surf is not None: surf.blit(text_surface, text_rect)
    return text_rect


def get_text_rect(text: str, size: int, font_name: str = None) -> pygame.Rect:
    """returns the same rect as pygine.draw_text but doesn't need time for rendering the text"""
    if font_name is None: font = pygame.font.Font(default_font,int(size))
    else: font = pygame.font.Font(get_match_font(font_name), int(size))
    text_surface = font.render(str(text), True, (0,0,0))
    return text_surface.get_rect()


def split_text_into_lines_fitting_width(text: str, text_size: int, width: int) -> Sequence[str]:
    lines = [""]
    current_line = 0
    for word in text.split(" "):
        lines[current_line] += " " + word if len(lines[current_line]) > 0 else word
        if get_text_rect(lines[current_line],text_size).width > width - 50:
            lines[current_line] = lines[current_line][:-len(word) - 1]
            current_line += 1
            lines.append(word)
    return lines


def draw_center_rect(surf: pygame.Surface, pixel_pos: vec2, color: [int, int, int, int]):
    """┌────────┐  • = pixel_pos
       │ • ───┐ │  draws 4 rects around the center rect, defined by pixel_pos
       │ └────┘ │
       └────────┘"""
    pygame.draw.rect(surf, color, (0, 0, surf.get_width(), int(pixel_pos.y)))
    pygame.draw.rect(surf, color, (0, 0, int(pixel_pos.x), surf.get_height()))
    pygame.draw.rect(surf, color, (0, int(surf.get_height() - pixel_pos.y), surf.get_width(), int(pixel_pos.y)))
    pygame.draw.rect(surf, color, (int(surf.get_width() - pixel_pos.x), 0, int(pixel_pos.x), surf.get_height()))


def draw_bar(surf: pygame.Surface, vertical: bool, length: int, width: int, filled: float, pos: vec2, inner_color, outer_color=(0, 0, 0), ret_pos: str = "left_top", surrounding_width: int = 2):
    """┌─────────┬────┐
       │         │    │
       └─────────┴────┘
       draw a bar on the surf
       :param vertical: if True vertical else horizontal
       :param width: width of the bar
       :param length: length of the bar
       :param filled: filled part of bar from 0 to 1 (value will be forced into range)
       :param pos: pos if the bar
       :param inner_color: color of inside
       :param outer_color: color of the surrounding
       :param ret_pos: where the passed pos is on the bar (e.x pygine.LEFT_TOP)
       :param surrounding_width: width of the surrounding rect"""
    if vertical:
        w = width
        h = length
    else:
        w = length
        h = width
    if ret_pos == "center":
        p = pos - vec2(w / 2, h / 2)
    elif ret_pos == "top":
        p = pos - vec2(w / 2, 0)
    elif ret_pos == "bottom":
        p = pos - vec2(w / 2, h)
    elif ret_pos == "left_top":
        p = pos
    elif ret_pos == "right_top":
        p = pos - vec2(w, 0)
    elif ret_pos == "left_bottom":
        p = pos - vec2(0, h)
    elif ret_pos == "right_bottom":
        p = pos - vec2(w, h)
    elif ret_pos == "left":
        p = pos - vec2(0, h / 2)
    elif ret_pos == "right":
        p = pos - vec2(w, h / 2)
    filled = min([max([filled, 0]), 1])
    if vertical:
        pygame.draw.rect(surf, inner_color, (vec2(p.x, p.y + h * (1 - filled)), vec2(w, h * filled)))
        pygame.draw.rect(surf, outer_color, (p, vec2(w, h)), surrounding_width)
    else:
        pygame.draw.rect(surf, inner_color, (p, vec2(w * filled, h)))
        pygame.draw.rect(surf, outer_color, (p, vec2(w, h)), surrounding_width)


def get_image_fit_into_rect(img: pygame.Surface, rect: pygame.Rect) -> [pygame.Surface, vec2, float]:
    """resizes a image to fit onto surface by keeping the aspect ratio (image can get smaller and bigger)
    returns the resized image and and the left top pos of the image on the rect as well as the scale factor"""
    img_w, img_h = img.get_size()
    rect_w, rect_h = rect.size
    new_size = [img_w, img_h]
    factor = 1
    if new_size[0] != rect_w:
        factor = rect_w / img_w
        new_size[1] = img_h * factor
        new_size[0] = rect_w
    if new_size[1] > rect_h:
        factor = rect_h / img_h
        new_size[0] = img_w * factor
        new_size[1] = rect_h
    return pygame.transform.scale(img, (int(new_size[0]), int(new_size[1]))), vec2(rect_w / 2 - new_size[0] / 2, rect_h / 2 - new_size[1] / 2), factor


def draw_image_fitting_onto_surface(surf: pygame.Surface, img: pygame.Surface):
    """draws the image to fit onto surface but keeping the aspect ratio (image can get smaller and bigger)"""
    img, pos, factor = get_image_fit_into_rect(img, surf.get_rect())
    surf.blit(img, pos)
    return img, pos, factor


# more functions to be added in future

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE, pygame.DOUBLEBUF)
    draw_center_rect(screen, vec2(75, 50), (255, 0, 0))
    draw_bar(screen, True, 200, 30, 0.8, vec2(10, 50), (0, 255, 0))
    draw_bar(screen, False, 200, 30, 0.8, vec2(50, 10), (0, 255, 0))
    pygame.display.flip()
    while True:
        ev = pygame.event.get()
        for e in ev:
            if e.type == pygame.QUIT:
                pygame.quit()
