from os.path import dirname, join, isfile
from os import walk
import pygame.image as image

FOLDER = dirname(dirname(__file__))
PROJECT_FOLDER = FOLDER
print(PROJECT_FOLDER)

def get_file_path(project_name: str, paths) -> str:
    pr_folder = join(PROJECT_FOLDER, project_name)
    return join(pr_folder, *paths)


def get_img_folder(project_name: str) -> str:
    pr_folder = join(PROJECT_FOLDER, project_name)
    return join(pr_folder, "img")


def get_level_folder(project_name: str) -> str:
    pr_folder = join(PROJECT_FOLDER, project_name)
    return join(pr_folder, "level")


def get_background_folder(project_name: str) -> str:
    pr_folder = join(PROJECT_FOLDER, project_name)
    return join(pr_folder, "backgrounds")


def get_menu_folder(project_name: str) -> str:
    pr_folder = join(PROJECT_FOLDER, project_name)
    return join(pr_folder, "menus")


def search_file(project_name: str, file_name: str) -> str:
    pr_folder = join(PROJECT_FOLDER, project_name)
    """searches file throughout the whole project, not recommended as it might take a long time in big projects"""
    for root, dirs, files_ in walk(pr_folder):
        for file in files_:
            if file == file_name:
                return join(root, file)
    return None

def load_image(project_name:str,paths:[str]) -> image:
    return image.load(get_file_path(project_name,paths))

def load_image_sequence(project_name: str, paths:[str], file_name:str, from_:int=0, to_:int=1) -> [image]:
    """load a sequence of images and return a list of pygame surfaces.
    Set file_name like "image{}.png" and the function will replace {} with to numbers (from_-to_) and load the images
    No error will be raised, when a file is not found, the result will be an empty list"""
    r = []
    for num in range(from_,to_):
        file = get_file_path(project_name,paths+[file_name.format(num)])
        if isfile(file):
            r.append(image.load(file))
    return r
