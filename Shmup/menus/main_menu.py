import pygine

def get(won:bool=True,level:int=0,endless:bool=False):
    menu = pygine.Menu_creator("Main")
    menu.add_space("Space Invaders",50,(255, 255, 255),45)
    if won is not None:
        if won:
            menu.add_space("Gewonnen!!!", 30, (30, 220, 70), 30)
        else:
            menu.add_space("Oooops! Verloren", 50, (230, 70, 15), 30)
    menu.add_horizontal_selection("Mode", [pygine.Menu_creator.get_value("Level", False), pygine.Menu_creator.get_value("Endless", True)], 1, 1, [endless], (255, 255, 255), 25, (255, 255, 255), 15, (150, 200, 175), 15)
    menu.add_space("",20,(255, 255, 255),25)
    menu.add_loop_selection("Level", pygine.Menu_creator.get_value_range("{}", 1, 30), [level], (255, 255, 255), 25, (150, 200, 175), 15)
    return menu

