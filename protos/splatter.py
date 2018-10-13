from PIL import Image
from PIL import ImageEnhance
import random

class Splatter:
    opacity = 1

    def __init__(self):
        outline = Image.open('splatter-original.png')
        color = "%06x" % random.randint(0, 0xFFFFFF)
        outline.colorize(color)
        outline.show()

    def colorize(self, color):
        self.paste(color)

    def fade(self):
        self = self.enhance(opacity)
        if self.opacity > 0
            self.opacity -= 0.1
    
'''
each frame of hand
detect palm or fist
paste splatter over palm coordinate of frame

time of pil to opencv?
v/v?
'''
