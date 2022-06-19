import cv2
import time
import utils.window as wnd
from classes.Navigator import Navigator
from classes.ActionController import ActionController
from classes.MineralCollector import MineralCollector

window = wnd.init_window("Sky2Fly")
controller = ActionController(window)
mineral_collector = MineralCollector(window, collector_item_key="5")

navigator = Navigator()

found_minerals = 0

start_time = time.time()

navigator.leave_base_by_direction("w")
time.sleep(3)

mineral_coords = [
    # (17, 9),
    (10, 9), (9, 8),
    (10, 9), (9, 8),
    (10, 9), (9, 8),
    (10, 9), (9, 8),
    (10, 9), (9, 8),
    (10, 9), (9, 8),
    (10, 9), (9, 8),
    (10, 9), (9, 8),
]

print("Go to minerals")
x_targ, y_targ = mineral_coords[0][0], mineral_coords[0][1]

navigator.go_to_target(x_targ=x_targ, y_targ=y_targ, allowed_error=1)
mineral_coords.pop()
mineral_collector.start_collector_item_activator()

clicks_count = 275

while found_minerals < clicks_count:
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
            if len(mineral_coords):
                x_targ, y_targ = mineral_coords[0][0], mineral_coords[0][1]
                mineral_coords.pop()
                print(f"No minerals found, go to x:{x_targ}, y:{y_targ}")
                navigator.go_to_target(x_targ=x_targ, y_targ=y_targ)
            else:
                found_minerals = clicks_count
                print(f"Mineral spots are empty. Stop collecting")
else:
    mineral_collector.stop_collector_item_activator()
    print(f"Collected all minerals. Go home..")
    total_time = time.time() - start_time
    print(f"Total time: {total_time}")
    navigator.go_to_target(x_targ=21, y_targ=8)
