import cv2
import math
import time
import pyautogui
import utils.window as wnd
import numpy as np
from utils.constants import *
from threading import Thread


class MineralCollector:
    def __init__(self, window, collector_item_key="5"):
        self.window = window
        self.collector_item_activated_at = time.time() - 10**2
        self.collector_cooldown = 13
        self.collector_working_time = 10
        self.collector_item_key = collector_item_key
        self.thread_working_flag = False
        self.collector_item_activator_thread = Thread(target=self.collector_item_activator, daemon=True)
        self.collector_item_activator_thread.start()

    def start_collector_item_activator(self):
        self.thread_working_flag = True

    def stop_collector_item_activator(self):
        self.thread_working_flag = False

    def collector_item_activator(self):
        while True:
            if self.thread_working_flag:
                if not self.collector_item_in_cooldown():
                    self.activate_collector_item()
            time.sleep(1)

    def activate_collector_item(self):
        self.collector_item_activated_at = time.time()
        pyautogui.press(self.collector_item_key)

    def collector_item_is_working(self):
        delta_time = time.time() - self.collector_item_activated_at
        return self.collector_working_time > delta_time

    def collector_item_in_cooldown(self):
        delta_time = time.time() - self.collector_item_activated_at
        return self.collector_cooldown > delta_time

    def find_nearest_mineral(self, mineral_coords):
        ship_x, ship_y = wnd.get_ship_center(self.window)
        distances = [math.dist([ship_x, ship_y], [m_x, m_y]) for m_x, m_y in mineral_coords]
        min_dist_idx = np.argmin(distances)
        return mineral_coords[min_dist_idx], distances[min_dist_idx]

    @staticmethod
    def find_minerals(frame_rgb):
        color_mask = cv2.inRange(frame_rgb, np.array([35, 70, 55]),
                                 np.array([90, 205, 255]))
        frame_masked = cv2.bitwise_and(frame_rgb, frame_rgb, mask=color_mask)
        frame_gray = cv2.cvtColor(frame_masked, cv2.COLOR_BGR2GRAY)

        template = cv2.imread(f"{PRJ_PATH}/templates/minerals/pf.png", 0)
        template_h, template_w = template.shape

        match_results = cv2.matchTemplate(frame_gray, template, cv2.TM_CCOEFF_NORMED)
        valid_matches = np.where(match_results >= 0.7)

        found_matches = list(zip(*valid_matches[::-1]))

        rectangles = []

        for match in found_matches:
            match_x, match_y = int(match[0]), int(match[1])
            rect = [match_x, match_y, template_w, template_h]
            rectangles.append(rect)
            rectangles.append(rect)

        rectangles, _ = cv2.groupRectangles(rectangles, 1, 0.5)

        points = [(x+15, y+15) for (x, y, w, h) in rectangles]

        return points

    def show_minerals(self, minerals, frame_bgr, nearest_mineral, distance):
        h, w, _ = frame_bgr.shape
        x_curr, y_curr = wnd.get_ship_center(self.window)
        n_x, n_y = nearest_mineral[0], nearest_mineral[1]

        for mineral in minerals:
            x, y = mineral[:2]
            cv2.rectangle(frame_bgr, (x, y), (x + 5, y + 5), (255, 0, 0), 5)
            cv2.line(frame_bgr, (x_curr, y_curr), (x, y), (255, 0, 0), 3)

        cv2.rectangle(frame_bgr, (n_x, n_y), (n_x + 5, n_y + 5), (0, 0, 255), 7)
        cv2.line(frame_bgr, (x_curr, y_curr), (n_x, n_y), (0, 0, 255), 7)

        cv2.namedWindow("Minerals")
        cv2.moveWindow("Minerals", 1100, 100)
        cv2.imshow("Minerals", cv2.resize(frame_bgr, (int(h / 4), int(w / 4))))
        cv2.waitKey(1)


if __name__ == '__main__':

    window = wnd.init_window("Sky2Fly")
    collector = MineralCollector(window)

    time.sleep(4)
    collector.start_collector_item_activator()

    while True:
        print(f"working: {collector.collector_item_is_working()}, cooldown: {collector.collector_item_in_cooldown()}")
        # collector.stop_collector_item_activator()

    # while True:
    #     frame_bgr = wnd.read_window_frame(window, grayscale=False)[:, :, ::-1]
    #     # frame_bgr = cv2.imread("../tests/minerals/pf_1655305772.png")[:, :, ::-1]
    #
    #     mineral_coords = collector.find_minerals(frame_rgb=frame_bgr[:, :, ::-1])
    #
    #     if len(mineral_coords):
    #         nearest_mineral = collector.find_nearest_mineral(mineral_coords)
    #         (n_x, n_y), distance = nearest_mineral[0], nearest_mineral[1]
    #
    #         collector.show_minerals(mineral_coords, frame_bgr, (n_x, n_y), distance)
    #     else:
    #         print("No minerals found")
