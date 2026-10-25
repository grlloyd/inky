# A 7-segment bedside clock for the 7.3" Spectra 6 Inky Impression (E673).
# Each minute only the digits that changed are redrawn with a partial refresh, so the rest of the
# screen doesn't flash. On the hour the whole screen gets a full refresh to clear any ghosting.

import time
from datetime import datetime

from PIL import Image, ImageDraw

from inky.inky_e673 import Inky

inky_display = Inky()
WIDTH, HEIGHT = inky_display.width, inky_display.height

BACKGROUND = inky_display.BLACK
LIT = inky_display.RED

# Digit size and position (x positions are multiples of 4 to match the partial window alignment)
DIGIT_W, DIGIT_H = 152, 320
DIGIT_TOP = (HEIGHT - DIGIT_H) // 2
DIGIT_X = (28, 208, 440, 620)  # H H : M M
THICK = 30  # segment thickness
GAP = 3     # gap between neighbouring segments

# Which segments (a-g) are lit for each digit; " " is a blank leading zero
#  aaa
# f   b
#  ggg
# e   c
#  ddd
SEGMENTS = {
    "0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg",
    "5": "acdfg", "6": "acdefg", "7": "abc", "8": "abcdefg", "9": "abcdfg", " ": "",
}

image = Image.new("P", (WIDTH, HEIGHT), BACKGROUND)
draw = ImageDraw.Draw(image)


def horizontal(x0, x1, y):
    h = THICK // 2
    return [(x0, y), (x0 + h, y - h), (x1 - h, y - h), (x1, y), (x1 - h, y + h), (x0 + h, y + h)]


def vertical(x, y0, y1):
    h = THICK // 2
    return [(x, y0), (x + h, y0 + h), (x + h, y1 - h), (x, y1), (x - h, y1 - h), (x - h, y0 + h)]


def draw_digit(x, char):
    y = DIGIT_TOP
    draw.rectangle((x, y, x + DIGIT_W - 1, y + DIGIT_H - 1), fill=BACKGROUND)

    # Centre lines of the segments, keeping every segment inside the digit's box
    h = THICK // 2
    left, right = x + h, x + DIGIT_W - 1 - h
    top, mid, bottom = y + h, y + DIGIT_H // 2, y + DIGIT_H - 1 - h

    shapes = {
        "a": horizontal(left + GAP, right - GAP, top),
        "g": horizontal(left + GAP, right - GAP, mid),
        "d": horizontal(left + GAP, right - GAP, bottom),
        "f": vertical(left, top + GAP, mid - GAP),
        "b": vertical(right, top + GAP, mid - GAP),
        "e": vertical(left, mid + GAP, bottom - GAP),
        "c": vertical(right, mid + GAP, bottom - GAP),
    }
    for segment in SEGMENTS[char]:
        draw.polygon(shapes[segment], fill=LIT)


def draw_colon():
    cx = (DIGIT_X[1] + DIGIT_W + DIGIT_X[2]) // 2
    for cy in (DIGIT_TOP + DIGIT_H // 3, DIGIT_TOP + 2 * DIGIT_H // 3):
        draw.rectangle((cx - THICK // 2, cy - THICK // 2, cx + THICK // 2, cy + THICK // 2), fill=LIT)


def clock_digits(now):
    return f"{now.hour:2d}{now.minute:02d}"  # blank leading zero on the hour, like a bedside clock


draw_colon()
shown = None

while True:
    now = datetime.now()
    digits = clock_digits(now)

    for x, char in zip(DIGIT_X, digits):
        draw_digit(x, char)
    inky_display.set_image(image)

    if shown is None or now.minute == 0:
        inky_display.show()
    else:
        # One window spanning every digit that changed (usually just the last one)
        changed = [x for x, old, new in zip(DIGIT_X, shown, digits) if old != new]
        if changed:
            x0, x1 = min(changed), max(changed) + DIGIT_W
            inky_display.show(region=(x0, DIGIT_TOP, x1 - x0, DIGIT_H))

    shown = digits

    # Sleep until the start of the next minute (a refresh takes ~20s, so the time lands a little after)
    now = datetime.now()
    time.sleep(60 - now.second - now.microsecond / 1_000_000)
