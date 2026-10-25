# This example shows a partial refresh on the 7.3" Spectra 6 Inky Impression (E673).
# The whole screen is drawn once, then only a small box is redrawn each time.

import time

from font_fredoka_one import FredokaOne
from PIL import Image, ImageDraw, ImageFont

from inky.inky_e673 import Inky

inky_display = Inky()

BOX = (40, 40, 400, 120)  # x, y, width, height of the area to update

image = Image.new("P", (inky_display.width, inky_display.height), inky_display.WHITE)
draw = ImageDraw.Draw(image)
font = ImageFont.truetype(FredokaOne, 72)

draw.rectangle((0, 300, inky_display.width, inky_display.height), fill=inky_display.BLUE)
draw.text((40, 320), "Partial refresh", inky_display.WHITE, font)

inky_display.set_image(image)
inky_display.show()

x, y, w, h = BOX
for count, colour in enumerate((inky_display.RED, inky_display.GREEN, inky_display.BLACK), start=1):
    draw.rectangle((x, y, x + w - 1, y + h - 1), fill=inky_display.WHITE, outline=colour, width=6)
    draw.text((x + 20, y + 10), f"Update {count}", colour, font)

    inky_display.set_image(image)
    t_start = time.monotonic()
    inky_display.show(region=BOX)
    print(f"Partial update {count} took {time.monotonic() - t_start:.1f}s")
