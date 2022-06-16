import math
import operator

import cv2
import pyautogui
import numpy as np
import utils.window as wnd
import pyperclip
import time
import utils.window as wnd
from utils.constants import *
from utils.coordinates import *
from classes.Coordinate import Coordinate
from classes.Direction import Direction
from classes.Controller import Controller


class Navigator:
    def __init__(self):
        self.state = None
        self.window = wnd.init_window("Sky2Fly")
        self.coordinate = Coordinate()
        self.direction = Direction()

    def leave_base_by_direction(self, direction):
        pyautogui.click(
            self.window.right + COMPASS[direction][1],
            self.window.top + COMPASS[direction][0]
        )
        self.state = PLAYER_ON_FLY
        print(f"Navigator leave base. State: {self.state}")

    def get_position(self, frame_rgb):
        start_time = time.time()

        x, y = self.coordinate.get_coords_via_read_frame(frame_rgb)
        angle = self.direction.get_ship_angle(frame_rgb)[0]

        total_time = time.time() - start_time

        print(f"y:{y}, x:{x}, angle:{angle}, executed in {total_time}")

    def get_target_degrees(self, x_targ, y_targ, frame_rgb=None):
        if frame_rgb is None:
            frame_rgb = wnd.read_window_frame(self.window, grayscale=False)

        x_curr, y_curr = self.coordinate.get_coordinates_via_click(self.window)
        pc, pt = (0, 0), (x_targ - x_curr, y_curr - y_targ)
        ang1 = np.arctan2(*pc[::-1])
        ang2 = np.arctan2(*pt[::-1])
        return int(np.rad2deg((ang2 - ang1) % (2 * np.pi)))

    def choose_turn_position(self, target_angle, ship_angle):
        d = abs(target_angle-ship_angle)
        turn_idx = np.argmin([d, 360-d])
        turn_distance = np.min([d, 360-d])

        if turn_idx == 0:
            turn_key = "A"
        else:
            turn_key = "D"

        return turn_key, turn_distance

    def get_turn_distance(self, target_angle, ship_angle):
        d = abs(target_angle-ship_angle)
        return np.min([d, 360-d])

    def turn_ship_to_target(self, target_angle, ship_angle):
        turn_key, turn_distance = self.choose_turn_position(target_angle, ship_angle)
        while turn_distance >= 20:
            frame_rgb = wnd.read_window_frame(self.window, grayscale=False)
            pyautogui.keyDown(turn_key)

            ship_angle, acc = self.direction.get_ship_angle(frame_rgb)
            _, turn_distance = self.choose_turn_position(target_angle, ship_angle)
        else:
            print("Directions are equal (+-20 degrees)")
            pyautogui.keyUp(turn_key)

    def go_to(self, x_targ, y_targ):
        frame_rgb = wnd.read_window_frame(self.window, grayscale=False)
        controller = Controller(self.window)

        # Get angles
        target_angle = self.get_target_degrees(x_targ, y_targ, frame_rgb)
        ship_angle, acc = self.direction.get_ship_angle(frame_rgb)
        print(f"target_angle: {target_angle}, ship_angle: {ship_angle}")
        # Ship info
        x_curr, y_curr = self.coordinate.get_coordinates_via_click(self.window)
        turn_distance = self.get_turn_distance(target_angle, ship_angle)

        while not (x_curr == x_targ and y_curr == y_targ):
            frame_rgb = wnd.read_window_frame(self.window, grayscale=False)
            ship_angle, acc = self.direction.get_ship_angle(frame_rgb)
            target_angle = self.get_target_degrees(x_targ, y_targ, frame_rgb)

            if turn_distance > 20:
                self.turn_ship_to_target(target_angle, ship_angle)

            frame_rgb = wnd.read_window_frame(self.window, grayscale=False)
            ship_angle, acc = self.direction.get_ship_angle(frame_rgb)
            target_angle = self.get_target_degrees(x_targ, y_targ, frame_rgb)
            turn_distance = self.get_turn_distance(target_angle, ship_angle)

            # Set autoclickD
            controller.autopilot_by_angle(90, 250)

            # frame_rgb = wnd.read_window_frame(self.window, grayscale=False)
            x_curr, y_curr = self.coordinate.get_coordinates_via_click(self.window)
            print(f"Current x:{x_curr}, y:{y_curr}")
        else:
            print(f"I`m here x:{x_curr}, y:{y_curr}")


if __name__ == "__main__":
    window = wnd.init_window("Sky2Fly")
    navigator = Navigator()

    navigator.go_to(x_targ=69, y_targ=69)
