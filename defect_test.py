#!/usr/bin/python3
# -*- encoding: utf-8 -*-

import cv2
import numpy as np
import os.path

img = cv2.imread(os.path.join(os.getcwd(), 'star.jpeg'))
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Get bi-level image out of grayscale img_gray
ret, thresh = cv2.threshold(img_gray, 127, 255, 0)

# Find contours using mode 2 and method 1
_, contours, hierarchy = cv2.findContours(thresh, 2, 1)
cnt = contours[0]

# Gets convex hull for set of points
hull = cv2.convexHull(cnt, returnPoints=False)
defects = cv2.convexityDefects(cnt, hull)

for i in range(defects.shape[0]):
    s, e, f, d = defects[i, 0]
    start = tuple(cnt[s][0])
    end = tuple(cnt[e][0])
    far = tuple(cnt[f][0])
    cv2.line(img, start, end, [0, 255, 0], 2)
    cv2.circle(img, far, 5, [0, 0, 255], -1)

cv2.imshow('Image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
