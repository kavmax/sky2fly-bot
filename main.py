import cv2
import time
import pyautogui
from utils.window import *
from utils.actions import *
from classes.Game import Game

game = Game()
game.leave_base_by_direction("s")
print(game.state)
