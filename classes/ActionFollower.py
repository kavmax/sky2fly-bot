import time
import cv2
import pickle
import pyautogui
import utils.window as wnd
import utils.constants as const
import keyboard

from pynput.mouse import Listener, Button, Controller


class ActionFollower:
    def __init__(self, action_name="unset_action_name"):
        self.last_action_time = time.time()
        self.actions_history = []

        self.record_status = False
        self.action_name = action_name

    def on_click(self, x, y, button, click_pressed):
        if keyboard.is_pressed("esc"):
            self.record_status = False

        if click_pressed:
            if self.record_status:
                # Esc - stop record
                self.actions_history.append([x, y, button, time.time() - self.last_action_time])
                self.last_action_time = time.time()
                filename = f"actions/{self.action_name}.act"
                with open(filename, "wb") as fp:
                    pickle.dump(self.actions_history, fp)
                    print(f"Dumping to {filename}:", self.actions_history)
            else:
                print("Record stopped.")

    def record_actions(self):
        self.last_action_time = time.time()
        self.record_status = True
        print("Press ESC + CLICK to stop recording.")

        with Listener(on_click=self.on_click) as listener:
            listener.join()

    def load_actions(self):
        with open(f"actions/{self.action_name}.act", "rb") as fp:
            self.actions_history = pickle.load(fp)

    def play_actions(self):
        mouse = Controller()

        print(self.actions_history)

        for action in self.actions_history:
            time.sleep(action[3])
            mouse.position = (action[0], action[1])
            mouse.click(action[2])

if __name__ == "__main__":
    # def on_click(x, y, button, pressed):
    #     print(x, y, button, pressed, keyboard.is_pressed("shift"))
    #
    # with Listener(on_click=on_click) as listener:
    #     listener.join()
    pass
