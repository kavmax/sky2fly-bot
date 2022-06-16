import time

import cv2
import math

import numpy as np
import pyautogui
import utils.window as wnd


class Controller:
    def __init__(self, window):
        self.window = window
        self.ship_speed = 571
        self.px_per_sec = 0.015

    def click_by_angle(self, angle, ship_x=479, ship_y=489, click_type="left"):
        center_radius = 31
        x, y = self.angle_to_xy(angle, center_radius)
        click_x, click_y = ship_x + x, ship_y + y

        if click_type == "left":
            pyautogui.leftClick(click_x, click_y)
        elif click_type == "right":
            pyautogui.rightClick(click_x, click_y)

    @staticmethod
    def angle_to_xy(angle, radius=31):
        in_rads = (360 - angle) * math.pi / 180
        y, x = int(radius * math.sin(in_rads)), int(radius * math.cos(in_rads))
        return x, y

    def draw_circle_by_angle(self, from_angle=0, to_angle=360):
        frame = np.zeros((100, 100))
        h, w = frame.shape
        h2, w2 = int(h/2), int(w/2)

        for i in range(from_angle, to_angle + 1):
            x, y = self.angle_to_xy(i, 30)
            frame[y-h2, x-w2] = 255

        cv2.imshow("Angel 360", frame)
        cv2.waitKey(0)

    def test_ship_finder(self, window):
        w, h = window.right, window.bottom
        sw2, sh2 = int(w/2) - 4, int(h/2) - 34

        radius = 31

        print(sw2, sh2)

        # pyautogui.moveTo(w, h)
        # x, y = self.angle_to_xy(0, radius)
        # pyautogui.moveTo(sw2 + x, sh2 + y)

        for i in range(370):
            if i % 10 == 0:
                x, y = self.angle_to_xy(i, radius)
                pyautogui.moveTo(sw2 + x, sh2 + y)

    def autopilot_by_frame_coords(self, x, y, distance=0):
        sleep_time = distance * self.px_per_sec + 2
        print(f"Sleep time: {sleep_time}")
        pyautogui.doubleClick(x, y)
        time.sleep(sleep_time)
        print(f"Wake up")

    def autopilot_by_angle(self, angle, radius):
        x, y = self.angle_to_xy(angle, radius)

        ship_x, ship_y = wnd.get_ship_center(self.window)

        pyautogui.doubleClick(ship_x, ship_y+y)
        for i in range(2):
            pyautogui.rightClick(ship_x, ship_y-15)
            time.sleep(0.4)


if __name__ == "__main__":
    window = wnd.init_window("Sky2Fly")
    frame = wnd.read_window_frame(window, grayscale=False)

    controller = Controller(window)


    x, y = controller.angle_to_xy(275)
    ship_x, ship_y = wnd.get_ship_center(window)

    controller.autopilot_by_frame_coords(500, 800)

    # for i in range(370):
    #     if i % 15 == 0:
    #         controller.click_by_angle(angle=i)
            # print(f"Angel: {i}, points: {controller.angle_to_xy(i, 32)}")
