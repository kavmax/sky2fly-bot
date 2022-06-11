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


def read_window_frame(window):
    # Important! To see frame, you need open window
    image = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
    return np.array(image)
