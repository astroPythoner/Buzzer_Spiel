import pygine
from pygame.math import Vector2

def get():
    backgrnd = pygine.Background(None)
    backgrnd.set_style('image')
    backgrnd.image_background.get_keep_ratio()
    backgrnd.image_background.set_image_from_file(pygine.get_file_path('Shmup', ['img', 'starfield.png']))
    backgrnd.image_background.set_resize_full(True,True)
    return backgrnd

