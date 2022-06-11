import pyautogui
from utils.constants import *
from utils.coordinates import *


class Navigator:
    def __init__(self):
        self.state = None
        self.window = None

    def leave_base_by_direction(self, direction):
        if self.state == PLAYER_ON_BASE:
            pyautogui.click(
                self.window.right + COMPASS[direction][1],
                self.window.top + COMPASS[direction][0]
            )
            self.state = PLAYER_ON_FLY
            print(f"Navigator leave base. State: {self.state}")
