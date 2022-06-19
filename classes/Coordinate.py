import os
import cv2
import time
import operator
import numpy as np
import pyautogui
import pyperclip
import utils.window as wnd
from operator import itemgetter
from utils.constants import *


class Coordinate:
    def __init__(self):
        self.templates = []
        self.init_templates()

    def get_coords_via_click(self, window):
        pyautogui.click(
            window.right - 120,
            window.top + 190
        )

        # Select chat text
        pyautogui.hotkey("ctrl", "a")
        # Copy selected and delete
        pyautogui.hotkey("ctrl", "x")
        pyautogui.hotkey("esc")
        # pyautogui.click(10, 400)

        # (Периферия, 9:55)
        # (Периферия, 61:37)
        copied_text = pyperclip.paste()
        coords_splitted = copied_text.split(":")

        x, y = int(coords_splitted[0][-2:]), int(coords_splitted[1][:2])

        return x, y

    def get_coords_via_read_frame(self, image_rgb):
        image_masked = self.add_mask(image_rgb)

        # Remove left black pixels to first whites
        image_masked = self.remove_black_pixels_to_first_white(image_masked)

        all_matches = []
        coords_delimiter_at = 0

        # Find matches
        for idx, template in enumerate(self.templates):
            template_matches = self.find_template(image_masked, template)
            if len(template_matches):
                if idx != 10:  # 0-9
                    template_matches = [[template_match, idx] for template_match in template_matches]
                    all_matches.extend(template_matches)
                else:  # for :
                    coords_delimiter_at = template_matches[0][0]

        if len(all_matches):
            # Sort matches
            all_matches = sorted(all_matches, key=lambda x: x[0][0])

            # Remove 1 if it is 7 exactly
            all_matches = self.check_1_in_7_range(all_matches, image_masked)

            # Split x, y coords
            x_matches, y_matches = self.split_xy_matches(all_matches, coords_delimiter_at)

            x = x_matches[0][1] * 10 + x_matches[1][1] if len(x_matches) == 2 else x_matches[0][1]
            y = y_matches[0][1] * 10 + y_matches[1][1] if len(y_matches) == 2 else y_matches[0][1]

            return x, y

        return -1, -1

    @staticmethod
    def find_template(frame, template):
        true_matches = []
        template = template[2:]

        match_res = cv2.matchTemplate(frame, template, cv2.TM_CCORR_NORMED)

        # Find where match is more NN
        exact_matches = np.where(match_res >= 0.999)
        # Convert to individual points
        exact_locations = list(zip(*exact_matches[::-1]))

        # Push if locations are present
        if len(exact_locations):
            for location in exact_locations:
                # x, y
                true_matches.append((*location, ))

        return true_matches

    @staticmethod
    def check_1_in_7_range(all_matches, image_masked):
        # Check 1 (4x7) is in 7 (7x7) range
        for idx_1, match_1 in enumerate(all_matches):
            if match_1[1] == 1:
                for match_7 in all_matches:
                    if match_7[1] == 7:
                        if match_7[0][0] < match_1[0][0] <= match_7[0][0] + 5:
                            del all_matches[idx_1]
        return all_matches

    @staticmethod
    def split_xy_matches(all_matches, coords_delimiter_at):
        x_matches, y_matches = [], []

        for match in all_matches:
            if match[0][0] < coords_delimiter_at:
                x_matches.append(match)
            else:
                y_matches.append(match)

        return x_matches, y_matches

    @staticmethod
    def remove_black_pixels_to_first_white(image_masked):
        start_x = 0
        for i in range(image_masked.shape[1] - 1):
            if sum(image_masked[:, i:i+1]) != 0:
                return image_masked[:, i-1:]
        return image_masked

    def get_coords(self, image_rgb, cropped=False):
        if not cropped:
            image_rgb = image_rgb[185:192, -126:-90, :]

        return self.get_coords_via_read_frame(image_rgb)

    @staticmethod
    def add_mask(image_rgb):
        image_masked = cv2.bitwise_not(
            image_rgb,
            mask=cv2.inRange(image_rgb,
                             np.array([0, 0, 0]),
                             np.array([95, 40, 225])))

        if len(image_masked.shape) >= 3:
            image_masked = cv2.cvtColor(image_masked, cv2.COLOR_RGB2GRAY)

        image_masked[image_masked > 30] = 255
        image_masked[image_masked <= 30] = 0
        return image_masked

    def init_templates(self):
        dirpath = f"{PRJ_PATH}/templates/compass_coords"
        filenames = os.listdir(dirpath)

        for filename in filenames:
            template = cv2.imread(f"{dirpath}/{filename}")
            self.templates.append(self.add_mask(template))

    def run_test(self):
        dirname = f"{PRJ_PATH}/tests/compass_coords"
        image_filenames = os.listdir(dirname)
        images_rgb = [cv2.imread(f"{dirname}/{filename}")[:, :, ::-1] for filename in image_filenames]

        errors_y, errors_x = 0, 0
        all_len = len(images_rgb)

        start_time = time.time()
        for idx, image_rgb in enumerate(images_rgb):
            x_pred, y_pred = self.get_coords(image_rgb, cropped=True)
            x_true, y_true = int(image_filenames[idx][:2]), int(image_filenames[idx][2:4])

            if y_true != y_pred:
                errors_y += 1
            if x_true != x_pred:
                errors_x += 1

            if y_true != y_pred or x_true != x_pred:
                print(f"{image_filenames[idx]}, x_true: {x_true}, y_true: {y_true}, x_pred: {x_pred}, y_pred: {y_pred}")

        total_time = time.time() - start_time
        print(f"Time: {total_time}, errors x: {errors_x/all_len}, y: {errors_y/all_len}")
        print(f"Total len: {all_len}, time for 1: {total_time/all_len}")

    def save_coords_to_test(self, image_rgb, window):
        # image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)

        compass_frame = image_rgb[185:192, -126:-90]
        cv2.imshow("Compass frame", cv2.resize(compass_frame, (360, 70)))

        if cv2.waitKey(1) & 0xFF == ord("s"):
            original_coords = self.get_coords_via_click(window)
            orig_x_text = f"0{original_coords[0]}" if original_coords[0] < 10 else f"{original_coords[0]}"
            orig_y_text = f"0{original_coords[1]}" if original_coords[1] < 10 else f"{original_coords[1]}"
            original_coords_text = f"{orig_x_text}{orig_y_text}"
            filename =  f"{PRJ_PATH}/tests/compass_coords_rgb/" \
                        f"{original_coords_text}_{int(time.time())}.png"

            cv2.imwrite(filename, compass_frame)
            print(f"image saved {filename}")


if __name__ == "__main__":
    # window = wnd.init_window("Sky2Fly")
    coordinate = Coordinate()

    coordinate.run_test()
    # while True:
    #     frame = wnd.read_window_frame(window, grayscale=False)
    #     coordinate.save_coords_to_test(frame, window)

    # dirname = f"{PRJ_PATH}/tests/compass_coords_rgb"
    # filenames = os.listdir(dirname)[:]
    # frames = [cv2.imread(f"{dirname}/{filename}") for filename in filenames]

    # start_time = time.time()
    # for _ in range(1):
    #     frame = wnd.read_window_frame(window, grayscale=False)
    #     print(coordinate.get_coords(image_rgb=frame))
    # total_time = time.time() - start_time
    # print(total_time, total_time/100, 100)
