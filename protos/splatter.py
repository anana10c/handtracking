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


import cv2
import random

class Splatter:
    def __init__(self):
        outline = cv2.imread('splatter-original.png', -1)
        print(outline.shape)
        cv2.cvtColor(outline, cv2.COLOR_BGRA2RGBA) #remember to try to convert frame to RGBA also
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        print(color)
        outline[:, :, 0] = color[0]
        outline[:, :, 1] = color[1]
        outline[:, :, 2] = color[2]
        #outline[:, :, 0:3] = color #not sure if this works reee numpy indexing

    def fade(self):
        #alter alpha channel in opencv? is 0 or 255 transparent
        self = self.enhance(opacity)
        if self.opacity > 0:
            self.opacity -= 0.1
'''
