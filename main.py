#!/usr/bin/env python3

WINDOW_TITLE = 'Minecraft 1.17.1'
POSITION_REGEX = 'Position: (\d+),(\d+)'
GEOMETRY_REGEX = 'Geometry: (\d+)x(\d+)'

import cv2
import numpy as np
import pyautogui as gui
import pytesseract as tess
import re
import time
from subprocess import getoutput
from PIL.ImageGrab import grab

def compile_re():
    global pos_re, geo_re
    pos_re = re.compile(POSITION_REGEX)
    geo_re = re.compile(GEOMETRY_REGEX)

def get_xy(regex, string):
    match = regex.search(string)
    return int(match.group(1)), int(match.group(2))

def get_window_bbox():
    global pos_re, geo_re
    win_info = getoutput(
        'xdotool search -name "%s" getwindowgeometry'
        % WINDOW_TITLE
    )
    try:
        width, height = get_xy(geo_re, win_info)
        x0, y0 = get_xy(pos_re, win_info)
    except AttributeError:
        return (0, 0, 0, 0)
    x1, y1 = x0 + width, y0 + height
    # get lower right part only
    x0 += width // 2
    y0 += height // 2
    return (x0, y0, x1, y1)


def get_screenshot():
    img = grab(bbox=get_window_bbox())
    img = np.array(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1]
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    return img

def get_text(img):
    return tess.image_to_string(
        img,
        lang='mc',
        config='--tessdata-dir ./tesseract'
    ).split('\n')

def recast_fishing_rod():
    gui.rightClick(0, 0)
    time.sleep(0.2)
    gui.rightClick(0, 0)

def main():
    # needed for fullscreen to work
    gui.FAILSAFE = False
    compile_re()
    counter = 0
    print('Running...')
    print('Ctrl + C to stop.')
    try:
        while True:
            screen = get_screenshot()
            text = get_text(screen)
            # NOT A TYPO! OCR detects 'e' instead of 'a'
            if 'Fishing Bobber spleshes' in text:
                counter += 1
                recast_fishing_rod()
                time.sleep(1.5)
            time.sleep(0.2)
    except KeyboardInterrupt:
        print()
        print('Stopped.')
        print('Caught %d %s.' % (counter, 'items' if counter != 1 else 'item'))


if __name__ == '__main__':
    main()