import cv2
import numpy as np
import pyautogui
import pygetwindow as gw


def init_window(window_name):
    window = None

    for w in gw.getWindowsWithTitle("Sky2Fly"):
        if w.title == window_name:
            window = w
            break

    window.activate()
    return window


def read_window_frame(window, grayscale=True):
    # Important! To see frame, you need open window
    image = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))

    if grayscale:
        return cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    else:
        return np.array(image)[:, :, ::-1]


def get_ship_center(window):
    # All window
    w, h = window.right, window.bottom

    # Ship center
    ship_x, ship_y = int(w / 2) - 4, int(h / 2) - 34
    return ship_x, ship_y
