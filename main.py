import cv2
import time
import pyautogui
import utils.window as wnd
from utils.constants import *
from classes.Game import Game
from classes.Dataset import Dataset
from classes.Navigator import Navigator
from classes.Direction import Direction
from classes.Coordinate import Coordinate
from classes.Controller import Controller
from classes.ActionFollower import ActionFollower
from classes.MineralCollector import MineralCollector

window = wnd.init_window("Sky2Fly")
controller = Controller(window)
direction = Direction()
mineral_collector = MineralCollector(window)
navigator = Navigator()

found_minerals = 0

navigator.leave_base_by_direction("n")
time.sleep(3)

x_targ, y_targ = 9, 25
print("Go to minerals")
navigator.go_to(x_targ=x_targ, y_targ=y_targ)

while found_minerals < 150:
    mineral_collector.activate_collector_item()
    if mineral_collector.collector_item_is_working():
        frame_rgb = wnd.read_window_frame(window, grayscale=False)
        minerals = mineral_collector.find_minerals(frame_rgb)
        if len(minerals):
            (n_x, n_y), distance = mineral_collector.find_nearest_mineral(minerals)
            mineral_collector.show_minerals(minerals, frame_rgb[:, :, ::-1], (n_x, n_y), distance)
            controller.autopilot_by_frame_coords(n_x, n_y, distance)
            found_minerals += 1
            print(f"Found minerals: {found_minerals}")
        else:
            y_targ -= 1
            print(f"No minerals found, go to x:{x_targ}, y:{y_targ}")
            navigator.go_to(x_targ=x_targ, y_targ=y_targ)
    elif not mineral_collector.collector_item_in_cooldown():
        mineral_collector.activate_collector_item()
else:
    navigator.go_to(x_targ=15, y_targ=30)
    print("Go home")
    navigator.go_to(x_targ=15, y_targ=39)
