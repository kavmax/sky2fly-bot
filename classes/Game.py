import pyautogui
from utils.window import *
from utils.constants import *
from utils.coordinates import *
from classes.Navigator import Navigator


class Game(Navigator):
    def __init__(self):
        self.state = PLAYER_ON_BASE
        self.window = init_window("Sky2Fly")

        super(Navigator, self).__init__()


