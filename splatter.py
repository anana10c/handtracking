import cv2
import random
# from threading import Timer

class Splatter:

    def __init__(self, topleft, bottomright, color=None):
        imgnum = str(random.randint(1,8))
        self.outline = cv2.imread(str('splatter-'+imgnum+'.png'), -1)
        self.outline = cv2.resize(self.outline, (bottomright[0]-topleft[0], bottomright[1]-topleft[1]), interpolation = cv2.INTER_AREA)
        cv2.cvtColor(self.outline, cv2.COLOR_BGRA2RGBA) #remember to try to convert frame to RGBA also
        if color == None:
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        else:
            self.color = color
        self.outline[:, :, 0:3][self.outline[:, :, 3] != 0] = self.color
        self.outline[:, :, 0:3][self.outline[:, :, 3] == 0] = (0, 0, 0)
        self.opacity = 1
        self.topleft = topleft
        self.bottomright = bottomright

    def fade(self):
        #self.outline[self.outline[:, :, 3] >= 4] -= 4
        if self.opacity > 0:
            self.opacity -= 0.1
        if self.opacity < 0:
            self.opacity = 0
