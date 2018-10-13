'''
from PIL import Image
from PIL import ImageEnhance
import random

class Splatter:
    opacity = 1
    alpha = 255
    outline = Image.open('splatter-original.png')

    def __init__(self):
        color = "%06x" % random.randint(0, 0xFFFFFF)
        self.outline.putalpha(alpha)
        self.outline.colorize(color)
        self.outline.show()

    def colorize(self, color):
        self.outline.paste(color)

    def fade(self):
        if self.alpha > 0 and self.alpha != -1:
            self.alpha -= 2
            self.outline.putalpha(alpha).show()

each frame of hand
detect palm or fist
paste splatter over palm coordinate of frame

time of pil to opencv?
v/v?
'''

import cv2
import random

class Splatter:
    def __init__(self, color=None):
        self.outline = cv2.imread('splatter-original.png', -1)
        print(self.outline.shape)
        cv2.cvtColor(self.outline, cv2.COLOR_BGRA2RGBA) #remember to try to convert frame to RGBA also
        if color == None:
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        else:
            self.color = color
        print(self.color)
        self.outline[:, :, 0] = self.color[0]
        self.outline[:, :, 1] = self.color[1]
        self.outline[:, :, 2] = self.color[2]
        #self.outline[:, :, 0:3] = self.color #not sure if this works reee numpy indexing
        self.opacity = 1

    def fade(self):
        if self.opacity > 0:
            self.opacity -= 0.1
