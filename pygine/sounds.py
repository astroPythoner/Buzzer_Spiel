import pygame

class Sounds():
    def __init__(self):
        super(Sounds).__init__()
        self.__background_music_volume = 0.5
        self.__sound_volume = 0.8
        self.__sounds = {}

    def new_sound(self, unique_name:str, filename:str, play:bool=False):
        """add a new sound from file name and give it a unique name
        exception will be raised when name is already in use
        if play is Ture sound will be played once after creation"""
        sound = pygame.mixer.Sound(filename)
        sound.set_volume(self.__sound_volume)
        if unique_name in self.__sounds:
            raise Exception("Sound name already exists")
        self.__sounds[unique_name] = sound
        if play: sound.play()

    def play_sound(self, name:str):
        """plays the sound with the unique name"""
        self.__sounds[name].play()

    def load_background_music(self, file_name:str):
        """loads background music from file"""
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.set_volume(self.__background_music_volume)
        pygame.mixer.music.play(-1)

    def set_background_music_volume(self, value:float):
        """sets volume of the background (0-1) value will be forced to be in the range"""
        self.__background_music_volume = min([max([value,0]),1])
        pygame.mixer.music.set_volume(self.__background_music_volume)
    def set_sound_volume(self, value:float):
        """sets volume of the sounds (0-1) value will be forced to be in the range"""
        self.__sound_volume = min([max([value,0]),1])
        for s in list(self.__sounds.values()):
            s.set_volume(self.__sound_volume)

    @property
    def background_music_volume(self) -> float: return self.__background_music_volume
    @property
    def sound_volume(self) -> float: return self.__sound_volume

    def get_background_music(self) -> pygame.mixer.music:
        return pygame.mixer.music

    def get_sound(self, name:str) -> pygame.mixer.Sound:
        return self.__sounds[name]

    def get_all_sounds(self) -> [pygame.mixer.Sound]:
        return list(self.__sounds.values())

    def get_names(self) -> [str]:
        return list(self.__sounds.keys())

    def __getitem__(self, item:str):
        return self.get_sound(item)
