import numpy as np
import cv2

NUM_RENDERS = 20

for i in range(NUM_RENDERS):
    im = cv2.imread("smoke_render%s.png" % (i+1))
    b_channel, g_channel, r_channel = cv2.split(im)
    im_BGRA = cv2.merge((b_channel, g_channel, g_channel, np.abs(255 - (r_channel - g_channel))))
    cv2.imwrite('./smoke_render_alpha%s.png' % (i+1), im_BGRA)

print("FIN!")
