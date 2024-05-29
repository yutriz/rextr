from PIL import Image
from PIL import ImageFilter
import numpy as np


""" 
Sharpen is ENOUGH
# given depth=8, depth=2 wanted
# 
# and only black -> gray -> white
#           0b11    0b01    0b00
#           255      85       0
# 1 2 4 8 16 32 64 128 256
# 
def threshold(val):
    if val<42:
        return 0
    if val<190:
        return 0
    return 255 
"""

image = Image.open('full_crop.jpg')

image = image.filter(ImageFilter.SHARPEN)
image = image.filter(ImageFilter.SHARPEN)

image.save('full_enenhanced.bmp')


