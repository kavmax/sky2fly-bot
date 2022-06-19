import math
import operator

import cv2
import time
import pyperclip
import pyautogui
import numpy as np
import utils.window as wnd
from threading import Thread
from utils.constants import *
from classes.Coordinate import Coordinate
from classes.Direction import Direction
from classes.ActionController import ActionController


class Navigator:
    def __init__(self):
        self.state = None
        self.window = wnd.init_window("Sky2Fly")
        self.coordinate = Coordinate()
        self.direction = Direction()

        self.x_targ, self.y_targ = -1, -1
        self.x_curr, self.y_curr = -1, -1
        self.curr_angle, self.targ_angle = -1, -1
        self.targ_turn_distance = -1
        self.turn_allowed_error = 15

        self.updater = Thread(target=self.updater, daemon=True)
        self.updater.start()

    def updater(self):
        print("Navigator updater started")
        while True:
            self.update_variables()
            time.sleep(0.1)
            # self.get_info()

    def update_variables(self):
        frame_rgb = wnd.read_window_frame(self.window, grayscale=False)
        self.x_curr, self.y_curr = self.coordinate.get_coords(frame_rgb)
        self.curr_angle, _ = self.direction.get_ship_angle(frame_rgb)
        self.targ_angle = self.direction.get_targ_angle(self.x_targ, self.y_targ, self.x_curr, self.y_curr)
        self.targ_turn_distance = self.get_turn_distance()

    def get_info(self):
        print(f"self.x_curr: {self.x_curr}, self.y_curr: {self.y_curr}\n"
              f"self.x_targ: {self.x_targ}, self.y_targ: {self.y_targ}\n"
              f"self.curr_angle: {self.curr_angle}, self.targ_angle: {self.targ_angle}\n"
              f"self.targ_turn_distance: {self.targ_turn_distance}\n"
              f"turn_key: {self.choose_turn_position()}")

    def leave_base_by_direction(self, direction):
        pyautogui.click(
            self.window.right + COMPASS[direction][1],
            self.window.top + COMPASS[direction][0]
        )
        print(f"Navigator leave base. State: {self.state}")

    def choose_turn_position(self):
        if self.targ_turn_distance > 0:
            return "A"
        else:
            return "D"

    def get_turn_distance(self):
        diff = (self.targ_angle - self.curr_angle + 180) % 360 - 180
        distance = diff + 360 if diff < -180 else diff
        return distance

    def turn_ship_to_target(self):
        turn_key = self.choose_turn_position()

        while abs(self.targ_turn_distance) >= self.turn_allowed_error:
            if abs(self.targ_turn_distance) < 90:
                pyautogui.press("w")
            else:
                pyautogui.press("s")

            pyautogui.keyDown(turn_key)
        else:
            print(f"Directions are equal (+-{self.turn_allowed_error} degrees)")
            pyautogui.keyUp(turn_key)

    def go_to_target(self, x_targ, y_targ, allowed_error=0):
        self.x_targ, self.y_targ = x_targ, y_targ

        controller = ActionController(self.window)

        while not (self.x_curr - allowed_error <= self.x_targ <= self.x_curr + allowed_error and
                   self.y_curr - allowed_error <= self.y_targ <= self.y_curr + allowed_error):
            if abs(self.targ_turn_distance) > self.turn_allowed_error:
                self.turn_ship_to_target()
                time.sleep(0.1)
            else:
                # Set` autoclick
                controller.autopilot_by_angle(90, 250)
                print(f"Current x:{self.x_curr}, y:{self.y_curr}")
        else:
            pyautogui.keyUp("w")
            pyautogui.keyUp("s")
            print(f"I`m here x:{self.x_curr}, y:{self.y_curr}")


if __name__ == "__main__":
    window = wnd.init_window("Sky2Fly")
    navigator = Navigator()

    # while True:
    #     time.sleep(1)
    #     navigator.get_info()
    #     break

    # navigator.go_to_target(x_targ=17, y_targ=37, allowed_error=2)
    # navigator.go_to_target(x_targ=88, y_targ=88, allowed_error=2)
