import cv2
import numpy as np
from copy import deepcopy
from typing import Tuple, Any
from font.bits_utils import bit_array_to_byte_array, int_to_bit_array
from font.bits_utils import LUT_8_TO_2

class BitMappings:
    @staticmethod
    def func_1bit_to_2bit(i):
        if i == 0: return 0
        return 3
        
    @staticmethod
    def func_8bit_to_1bit(i):
        if i<128: return 0
        return 1

    @staticmethod
    def func_8bit_to_2bit(i):
        if i<64:  return 0
        if i<128: return 1
        if i<192: return 2
        return 3

    @staticmethod 
    def func_auto(bit_depth):
        pass

def padded_len(origin_len, depth):
    return ((origin_len -1) // depth + 1) * depth

def _np_bool_array_to_byte_array(
        image, 
        bit_depth = 1, 
        disable_mapping_func: bool = False,
        bit_mapping_func = None,
        byte_order_flag = "big"
    ):
    """
    @param bit_mapping_func: func(int) -> int
    """
    flatted = image.flatten()
    dtype = image.dtype

    if bit_depth == 1 or disable_mapping_func: 
        pass
    elif bit_mapping_func == None:
        # try to find a mapping function
        if bit_depth == 2:
            bit_mapping_func = BitMappings.func_1bit_to_2bit
        else:
            raise Exception("bit mapping function needed")
        
        # init
        bit_depth_appended = np.zeros((bit_depth, flatted.shape[0]) , dtype=dtype)
        for i in range(flatted.shape[-1]):
            mapped = bit_mapping_func(flatted[i])
            bits = int_to_bit_array(mapped, bit_length=bit_depth)
            bit_depth_appended[:, i] = bits

        # https://numpy.org/doc/stable/reference/generated/numpy.ndarray.flatten.html
        flatted = bit_depth_appended.flatten("f")
    
    pad_len = padded_len(flatted.shape[0], 8)
    padded_zeros = np.zeros(pad_len - flatted.shape[0], dtype=dtype) 
    flatted = np.append(flatted, padded_zeros)

    return bit_array_to_byte_array(flatted, byte_order_flag)

def _np_uint8_array_to_byte_array(
        image, 
        bit_depth = 1, 
        disable_mapping_func: bool = False,
        bit_mapping_func = None,
        byte_order_flag = "big"
    ):
    """
    @param bit_mapping_func: func(int) -> int
    """
    flatted = image.flatten()
    dtype = image.dtype

    if disable_mapping_func:
        pass
    elif bit_mapping_func == None:
        if bit_depth == 1:
            bit_mapping_func = BitMappings.func_8bit_to_1bit
        elif bit_depth == 2:
            bit_mapping_func = BitMappings.func_8bit_to_2bit
        else:
            raise Exception("bit mapping function needed")
        
    # init
    bit_depth_appended = np.zeros((bit_depth, flatted.shape[0]) , dtype=dtype)

    if not disable_mapping_func:
        for i in range(flatted.shape[-1]):
            val = flatted[i]
            val = bit_mapping_func(val)
            bits = int_to_bit_array(val, bit_length=bit_depth)
            bit_depth_appended[:, i] = bits
    else:
        for i in range(flatted.shape[-1]):
            val = flatted[i]
            bits = int_to_bit_array(val, bit_length=bit_depth)
            bit_depth_appended[:, i] = bits

    # https://numpy.org/doc/stable/reference/generated/numpy.ndarray.flatten.html
    flatted = bit_depth_appended.flatten("f")
    
    pad_len = padded_len(flatted.shape[0], 8)
    padded_zeros = np.zeros(pad_len - flatted.shape[0], dtype=dtype) 
    flatted = np.append(flatted, padded_zeros)

    return bit_array_to_byte_array(flatted, byte_order_flag)

def image_to_byte_array(
    image, 
    bit_depth=1, 
    disable_mapping_func: bool=False,
    bit_mapping_func=None, 
    byte_order_flag="big"
):
    if isinstance(image, np.ndarray):
        image_dtype = image.dtype
        assert(image_dtype in [bool, np.uint8])

        if image_dtype == bool:
            return _np_bool_array_to_byte_array(
                    image, 
                    bit_depth, 
                    disable_mapping_func,
                    bit_mapping_func, 
                    byte_order_flag)
        elif image_dtype == np.uint8:
            return _np_uint8_array_to_byte_array(
                    image, 
                    bit_depth, 
                    disable_mapping_func,
                    bit_mapping_func, 
                    byte_order_flag)
        
def create_character_shadow(
    image: np.ndarray,
    offset: Tuple = (1., 1.) # (height, width)
):
    """
    accept black background image
    """
    # convert to uint8
    data_type = image.dtype

    if data_type == np.uint8:
        pass
    elif data_type == bool:
        image = image.astype(np.uint8)
    else:
        raise NotImplementedError

    SHADOW_BRIGHTNESS = 0.5
    height = image.shape[0]
    width = image.shape[1]
    T = np.float32([[1., 0., offset[0]], [0., 1., offset[1]]])
    shadow = cv2.warpAffine(image, T, (width, height))

    shadow = shadow.astype(np.float32)
    shadow *= SHADOW_BRIGHTNESS
    shadow = shadow.astype(np.uint8)

    shaded = np.clip(
                shadow.astype(np.uint16) + image.astype(np.uint16),
                0,
                255
             ).astype(np.uint8)
    
    return shaded

def image_bit_depth_descale(
    image: np.ndarray,
    LUT = LUT_8_TO_2,
):
    assert(image.dtype == np.uint8)
    assert(len(LUT) == 256) # uint8

    lut = np.array(LUT)
    descaled = lut[image]

    return descaled

def get_left_spacing(
    image: np.ndarray,
    spacing: int # 0 or 255
) -> int:
    assert(spacing in [0, 255])
    width = image.shape[1]
    left_spacing = 0
    for w in range(width):
        if np.all(image[:, w] == spacing):
            left_spacing += 1
        else:
            break
    
    return left_spacing

def get_right_spacing(
    image: np.ndarray,
    spacing: int # 0 or 255
) -> int:
    assert(spacing in [0, 255])
    width = image.shape[1]
    left_spacing = 0
    for w in range(width)[::-1]:
        if np.all(image[:, w] == spacing):
            left_spacing += 1
        else:
            break
    
    return left_spacing

def get_width_excl_l_r_spacing(
    image: np.ndarray,
    spacing: int # 0 or 255
) -> int:
    assert(spacing in [0, 255])
    ls = get_left_spacing(image, spacing)
    rs = get_right_spacing(image, spacing)

    w = image.shape[1] - ls - rs 
    if w < 0: w = 0
    return w