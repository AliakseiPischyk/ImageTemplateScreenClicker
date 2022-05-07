import time
import pyautogui
from pynput import keyboard
import cv2 as cv
import numpy as np


def get_desktop_screenshot_gray():
    return cv.cvtColor(np.array(pyautogui.screenshot()), cv.COLOR_RGB2GRAY)


class PatternDetector:
    claim_review_btn_img = None
    ok_btn_img = None
    threshold = None

    def __init__(self):
        self.claim_review_btn_img = cv.imread('images/claim_review_btn_img.png', 0)
        self.ok_btn_img = cv.imread('images/ok_btn_img.png', 0)
        self.threshold = 0.95

    def get_review_btn_coords(self):
        res = cv.matchTemplate(get_desktop_screenshot_gray(), self.claim_review_btn_img, cv.TM_CCOEFF_NORMED)
        return np.where(res >= self.threshold)

    def get_ok_btn_coords(self):
        res = cv.matchTemplate(get_desktop_screenshot_gray(), self.ok_btn_img, cv.TM_CCOEFF_NORMED)
        return np.where(res >= self.threshold)


class Waiter:
    is_paused = False;

    @staticmethod
    def on_pause_hotkey():
        print('Chilling')
        Waiter.is_paused = True

    @staticmethod
    def on_unpause_hotkey():
        print('Working')
        Waiter.is_paused = False

    @staticmethod
    def chill():
        while Waiter.is_paused:
            time.sleep(1)


class Clicker:
    detector = PatternDetector
    wait_between_reviews = None
    wait_between_ok = None
    wait_after_reviews_before_ok = None

    def __init__(self):
        self.detector = PatternDetector()
        self.wait_between_reviews = 1
        self.wait_between_ok = 0.1
        self.wait_after_reviews_before_ok = 3

    def increase_time_between_reviews(self):
        self.set_wait_time(self.wait_between_reviews*1.5, self.wait_between_ok, self.wait_after_reviews_before_ok)

    def decrease_time_between_reviews(self):
        self.set_wait_time(self.wait_between_reviews/1.5, self.wait_between_ok, self.wait_after_reviews_before_ok)

    def set_wait_time(self, for_reviews, for_ok, for_after_reviews_before_ok):
        print('Current wait time between reviews {}'.format(for_reviews))
        self.wait_between_reviews = for_reviews
        self.wait_between_ok = for_ok
        self.wait_after_reviews_before_ok = for_after_reviews_before_ok

    def click_reviews(self):
        review_btn_coords = self.detector.get_review_btn_coords()
        if len(review_btn_coords[0]) == 0 and len(review_btn_coords[1]) == 0:
            return

        lenx = len(review_btn_coords[0])
        leny = len(review_btn_coords[1])
        if lenx == 0 or leny == 0 or lenx != leny:
            return

        for i in range(0, lenx):
            time.sleep(self.wait_between_reviews)
            pyautogui.click(review_btn_coords[1][i], review_btn_coords[0][i])

    def click_oks(self):
        ok_btn_coords = self.detector.get_ok_btn_coords()
        lenx = len(ok_btn_coords[0])
        leny = len(ok_btn_coords[1])
        if lenx == 0 or leny == 0 or lenx != leny:
            return

        for i in range(0, lenx):
            time.sleep(self.wait_between_ok)
            pyautogui.click(ok_btn_coords[1][i], ok_btn_coords[0][i])

    def start(self):
        while True:
            Waiter.chill()
            self.click_reviews()
            time.sleep(self.wait_after_reviews_before_ok)
            Waiter.chill()
            self.click_oks()


if __name__ == '__main__':
    print('Started')



    clicker = Clicker()

    h = keyboard.GlobalHotKeys({
        '<ctrl>+<alt>+p': Waiter.on_pause_hotkey,
        '<ctrl>+<alt>+з': Waiter.on_pause_hotkey,
        '<ctrl>+<alt>+u': Waiter.on_unpause_hotkey,
        '<ctrl>+<alt>+г': Waiter.on_unpause_hotkey,
        '<ctrl>+<alt>+i': clicker.increase_time_between_reviews,
        '<ctrl>+<alt>+d': clicker.decrease_time_between_reviews})
    h.start()
    clicker.start()
