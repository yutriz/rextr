import cv2
import numpy as np
from font.bits_utils import bit_depth_scale, byte_array_to_bit_array
from font.bits_utils import LUT_2_TO_8
from font.image_utils import get_left_spacing, get_width_excl_l_r_spacing, image_to_byte_array

class BitImage:
    width: int
    height: int
    bit_depth: int
    data_in_bytes: bytes
    data: np.ndarray

    GRAY_CHANNELS: int = 8

    def __init__(self, image, width=12, height=12, bit_depth=2):
        """
            image: bytes | numpy | str (to be converted to bytes)
            width, height: in pixels
        """
        
        self.width = width 
        self.height = height
        self.bit_depth = bit_depth

        if isinstance(image, bytes):
            self.data_in_bytes = image
            data = byte_array_to_bit_array(image, bit_depth)
            data = self.array_truncate(data)
            self.data = np.asarray(data, dtype=np.uint8).reshape(width, height)
        elif isinstance(image, np.ndarray):
            self.data = image
        elif isinstance(image, str):
            raise NotImplementedError

    def array_truncate(self, val_array):
        supposed_array_length = self.width * self.height
        assert(len(val_array) >= supposed_array_length)
        return val_array[:supposed_array_length]
    
    def get_left_spacing(self, space=0):
        return get_left_spacing(self.data, space) 

    def get_character_width_ex_l_r_spacing(self, space):
        return get_width_excl_l_r_spacing(self.data, space)

    def show(
        self, 
        width=512, 
        height=512,
        scale: bool=True, # for less than 8 bits 
        invert: bool=False
    ):

        scaled = self.data.copy()
        # performance issue? 
        if scale:
            for r in range(scaled.shape[0]):
                for c in range(scaled.shape[1]):
                    scaled[r][c] = bit_depth_scale(scaled[r][c], self.bit_depth, self.GRAY_CHANNELS)

        if invert:
            scaled = 2**self.GRAY_CHANNELS - 1 - self.data

        resized_image = cv2.resize(scaled, (width, height), interpolation=cv2.INTER_NEAREST)
        cv2.imshow("bits image", resized_image)
        cv2.waitKey(20000)

    def to_bytes(
        self,
        bit_depth: int = 2
    ):
        byte_array = image_to_byte_array(
            self.data,
            bit_depth,
            disable_mapping_func=True
        )

        return bytes(byte_array)