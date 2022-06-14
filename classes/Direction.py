import os
import cv2
import time
import numpy as np
import utils.window as wnd
import utils.math_template_rotation_hsv as hsv_matcher
from utils.constants import *


class Direction:
    def __init__(self):
        self.template_masked, self.template_dir = [], 0
        self.template_w, self.template_h = 0, 0
        self.rot_interval = 5
        self.delta_err = 10

        self.init_template()

    def init_template(self):
        self.template_dir = 272
        self.template_masked = cv2.cvtColor(cv2.imread(
            f"{PRJ_PATH}/templates/arrow_direction/template-272.png"), cv2.COLOR_BGR2RGB)

        self.template_h, self.template_w, _ = self.template_masked.shape

    def get_angle(self, image_rgb, cropped=False):
        # Find arrow frame
        if not cropped:
            image_rgb = image_rgb[110:128, -118:-100]

        image_rgb = cv2.resize(image_rgb, (self.template_h, self.template_w))
        image_masked = hsv_matcher.add_hsv_mask(image_rgb)
        # image_masked_rgb = cv2.cvtColor(image_masked, cv2.COLOR_GRAY2RGB)

        result = hsv_matcher.modified_match_template(image_masked, self.template_masked,
                                                     method="TM_CCOEFF_NORMED",
                                                     matched_thresh=0.5, rgbdiff_thresh=500,
                                                     rot_range=[0, 360], rot_interval=self.rot_interval,
                                                     scale_range=[100, 101], scale_interval=10,
                                                     rm_redundant=True, minmax=True)

        if len(result):
            result[0][1] = (result[0][1] + self.template_dir) % 360
            return result[0][1], result[0][3]

    def run_test(self):
        dirname = f"{PRJ_PATH}/tests/compass_arrow"
        image_filenames = os.listdir(dirname)
        image_filenames = image_filenames[:]
        print(image_filenames)

        img_rgb = [cv2.imread(f"{dirname}/{file_name}")[:, :, ::-1] for file_name in image_filenames]

        start_time = time.time()

        test_len = len(image_filenames)
        errors, no_pred = 0, 0

        for idx, image in enumerate(img_rgb):
            res = self.get_angle(image, cropped=True)

            actual_degree = int(image_filenames[idx].split("_")[0]) % 355
            pred_degree = res[0]

            degree_diff = abs(actual_degree - pred_degree)
            confidence = round(res[1], 2)
            has_error = False

            if not (pred_degree - self.delta_err <= actual_degree <= pred_degree + self.delta_err):
                errors += 1
                has_error = True

            print(f"Deg: {actual_degree}|{pred_degree},  \t(diff: {degree_diff}, conf: {confidence}, err: {has_error})")

        total_time = time.time() - start_time
        print(f"Time {total_time}, "
              f"errors: {errors / test_len}, no pred: {no_pred / test_len}")
        print(f"Test len: {len(image_filenames)}, time for one: {total_time / len(image_filenames)}")

        cv2.imshow("image", cv2.resize(img_rgb[0], (self.template_h, self.template_w)))
        cv2.imshow("template", self.template_masked)
        cv2.waitKey(0)


if __name__ == "__main__":
    # window = wnd.init_window("Sky2Fly")
    direction = Direction()
    direction.run_test()

    # while True:
    #     frame = wnd.read_window_frame(window, grayscale=False)
    #     print(direction.get_angle(frame))
    #
    #     if cv2.waitKey(50) & 0xFF == 27:
    #         break
