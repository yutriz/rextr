from copy import deepcopy

LUT_1_TO_2 = [0, 3]
LUT_1_TO_4 = [0, 15]
LUT_1_TO_8 = [0, 255] 

LUT_2_TO_4 = [0, 5, 10, 15]
LUT_2_TO_8 = [0, 85, 170, 255]

def _f_LUT_8_TO_2():
    lut = []
    for i in range(0, 256):
        if i<64: lut.append(0)
        elif i<128: lut.append(1)
        elif i<192: lut.append(2)
        else: lut.append(3)
    return lut

LUT_8_TO_2 = _f_LUT_8_TO_2()


def int_to_bit_array(i, bit_length):
    bit_array = []
    for j in range(bit_length):
        bit_array.append((i >> (bit_length - j - 1) ) & 1)
    
    return bit_array

def bit_depth_scale(in_val, in_bits: int, out_bits: int):
    """
        Ugly
        int_bits: 2 or mutliple of 4
        out_bits: should be multiple of 8 

        ???: 
            no good 
            2 bit: 00   
                   01   0000 1000 -> 8
                   10   1000 0000 -> 128   
                   11   1000 1000 -> 136   
            4 bit: 0000  
                   0001  0000 0010 -> 2
                   0010  0000 1000 -> 8
                   0100  0010 0000 -> 32
                   1000  1000 0000 -> 128
    """
    if in_bits == 1:
        if in_val == 0b0:
            return 0
        if in_val == 0b1:
            return 255

    if in_bits == 2:
        if in_val == 0b00:
            return 0
        elif in_val == 0b01:
            return  85
        elif in_val == 0b10:
            return  170
        elif in_val == 0b11:
            return  255

    assert(in_bits % 4 == 0)
    assert(out_bits % 8 == 0)

    slice_bits = out_bits // in_bits
    shift_bits = slice_bits - 1
    
    ret = 0
    for i in range(in_bits):
        ret |= ((in_val >> i) & 0b1) << (slice_bits * i + shift_bits)

    return ret

def bit_depth_descale(in_val, in_bits: int, out_bits: int):
    """
    e.g. 127(0b10000000) --> 0b10
    """

    if out_bits == 2:
        if in_val >= 254:
            return 3
        elif in_val >= 200:
            return 2
        elif in_val >= 100:
            return 1
        else:
            return 0
    
    else:
        raise NotImplementedError

def byte_array_to_bit_array(in_bytes, bit_depth, byte_order_flag="big"):
    """
    in_bytes: array-like, each element is in range [0, 255) (<=0xff)
    bits_depth: 
        e.g. [ 0xFE(0b11111110) ] 
        depth = 1: [1, 1, 1, 1, 1, 1, 1, 0]  
        depth = 2: [3, 3, 3, 2]
        depth = 3: pad to 0b111,111,100 [7, 7, 4]
    """
    # assert(byte_order_flag in ["little", "big"])
    assert(byte_order_flag in ["big"])
    # little endian emented yet

    bits_in_array = []
    for i in range(len(in_bytes)):
        bits_in_array += [ ((in_bytes[i]>>b) & 1) for b in range(7, -1, -1) ] 

    val_in_array = []
    for i in range(0, len(bits_in_array), bit_depth):
        bits = bits_in_array[i:i+bit_depth]

        # padding 
        while(len(bits) % bit_depth != 0):
            bits.append(0)

        val = 0
        for b in range(bit_depth): 
            val += bits[b] << (bit_depth - b - 1)
        val_in_array.append(val)

    return val_in_array

def bytearray_to_bit_array(in_bytes, bit_depth, byte_order_flag="big"):
    return byte_array_to_bit_array(in_bytes, bit_depth, byte_order_flag)

def bit_array_to_byte_array(bit_array, byte_order_flag="big"):
    if byte_order_flag == "little":
        raise NotImplementedError

    # big endian: as the bit array is 
    
    # make a copy
    bit_array = deepcopy(bit_array)

    # padding
    while(len(bit_array) % 8 != 0):
        bit_array.append(0)

    byte_array = []
    for i in range(0, len(bit_array), 8):
        val = 0
        for j in range(8):
            val += int(bit_array[i+7-j] << j)
        byte_array.append(val)
    
    return byte_array

def bit_array_to_bytearray(bit_array, byte_order_flag="big"):
    """
    bytearray is a python buildin class
    """
    ba = bytearray()
    byte_array = bit_array_to_bytearray(bit_array, byte_order_flag)
    for i in byte_array:
        ba.append(i)

    return ba