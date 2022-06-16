import os
import cv2
import time
import operator
import numpy as np
import pyautogui
import pyperclip
import utils.window as wnd

from utils.constants import *
from utils.coordinates import *


class Coordinate:
    def __init__(self):
        self.state = None
        self.templates = []

        self.init_templates()

    def get_coordinates_via_click(self, window):
        pyautogui.click(
            window.right - 120,
            window.top + 190
        )

        time.sleep(0.01)
        # Select chat text
        pyautogui.hotkey("ctrl", "a")
        # Copy selected
        pyautogui.hotkey("ctrl", "c")
        # Delete selected
        pyautogui.press("del")
        pyautogui.click(10, 400)

        # (Периферия, 9:55)
        # (Периферия, 61:37)
        copied_text = pyperclip.paste()
        # ['(Периферия,', '9:55)'] -> ['9:55']
        coords_text = copied_text.split()[1][:-1]
        # ['9', '55']
        coords_splitted = coords_text.split(":")
        x, y = int(coords_splitted[0]), int(coords_splitted[1])

        return x, y

    def init_templates(self):
        dirpath = f"{PRJ_PATH}/templates/compass_coords"
        filenames = os.listdir(dirpath)
        self.templates = [cv2.imread(f"{dirpath}/{filename}", 0)[1:-1, :] for filename in filenames]

    def get_coords_via_read_frame(self, image_rgb, cropped=False):
        compass_frame = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)

        if not cropped:
            compass_frame = compass_frame[185:192, -126:-90]

        coords_found = []

        # For each template
        for idx, template in enumerate(self.templates):
            # If found 4 coords
            if len(coords_found) == 4:
                break

            match_res = cv2.matchTemplate(compass_frame, template, cv2.TM_CCOEFF_NORMED)

            # Find where match is more 0.96
            exact_matches = np.where(match_res >= 0.96)
            # Convert to individual points
            exact_locations = list(zip(*exact_matches[::-1]))

            # Push if locations are present
            if len(exact_locations):
                for location in exact_locations:
                    # x, y, i
                    coords_found.append((*location, idx))

        # Convert coords to readable values
        sorted_locations = sorted(coords_found, key=operator.itemgetter(0))

        if len(sorted_locations) == 4:
            x, y = sorted_locations[0][2] * 10 + sorted_locations[1][2], \
                   sorted_locations[2][2] * 10 + sorted_locations[3][2]
        elif len(sorted_locations) == 3:
            if sorted_locations[0][0] <= 6:
                x = sorted_locations[0][2] * 10 + sorted_locations[1][2]
                y = sorted_locations[2][2]
            else:
                x = sorted_locations[0][2]
                y = sorted_locations[1][2] * 10 + sorted_locations[2][2]
        elif len(sorted_locations) == 2:
            x, y = sorted_locations[0][2], sorted_locations[1][2]
        else:
            y, x = -1, -1

        # TODO: I`ve changed here. 16 06 2022
        return x, y

    def run_test(self):
        dirname = f"{PRJ_PATH}/tests/compass_coords"
        image_filenames = os.listdir(dirname)
        images_rgb = [cv2.imread(f"{dirname}/{filename}")[:, :, ::-1] for filename in image_filenames]

        errors_y, errors_x = 0, 0
        all_len = len(image_filenames)

        start_time = time.time()
        for idx, image_rgb in enumerate(images_rgb):
            x_pred, y_pred = self.get_coords_via_read_frame(image_rgb, cropped=True)
            x_true, y_true = int(image_filenames[idx][:2]), int(image_filenames[idx][2:4])

            if y_true != y_pred:
                errors_y += 1
            if x_true != x_pred:
                errors_x += 1

            print(f"{image_filenames[idx]}, y_true: {y_true}, x_true: {x_true} y_pred: {y_pred}, y_true: {y_true}")

        total_time = time.time() - start_time
        print(f"Time: {total_time}, errors x: {errors_x/all_len}, y: {errors_y/all_len}")
        print(f"Total len: {all_len}, time for 1: {total_time/all_len}")

    def save_coords_to_test(self, image_rgb, window):
        image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)

        compass_frame = image_rgb[185:192, -126:-90]
        cv2.imshow("Compass frame", compass_frame)

        if cv2.waitKey(1) & 0xFF == ord("s"):
            original_coords = self.get_coordinates_via_click(window)
            orig_x_text = f"0{original_coords[0]}" if original_coords[0] < 10 else f"{original_coords[0]}"
            orig_y_text = f"0{original_coords[1]}" if original_coords[1] < 10 else f"{original_coords[1]}"
            original_coords_text = f"{orig_x_text}{orig_y_text}"

            cv2.imwrite(
                f"{PRJ_PATH}/tests/compass_coords/"
                f"{original_coords_text}_{int(time.time())}.png", compass_frame)


if __name__ == "__main__":
    window = wnd.init_window("Sky2Fly")
    coordinate = Coordinate()

    while True:
        frame_rgb = wnd.read_window_frame(window, grayscale=False)
        coordinate.save_coords_to_test(frame_rgb, window)
        print(coordinate.get_coords_via_read_frame(frame_rgb))
