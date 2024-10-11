import nftr_utils

import re
from PIL import Image, ImageDraw, ImageFont
import numpy as np 
import argparse



def uint8_to_2bpp(num):
    if num > 200:
        return 3
    else:
        return 0

def wrapper_2bpp(uint8_data_array):
    arr_len = len(uint8_data_array)
    assert(arr_len%2==0 and arr_len>=4)
    arr_bytes = []
    # check none 
    for i in range(0, arr_len, 4):
        uint8_x4 = uint8_data_array[i:i+4]
        b8 = 0
        b8 += uint8_to_2bpp(uint8_x4[0]) << 6
        b8 += uint8_to_2bpp(uint8_x4[1]) << 4
        b8 += uint8_to_2bpp(uint8_x4[2]) << 2
        b8 += uint8_to_2bpp(uint8_x4[3])
        arr_bytes.append(b8)
    # padding to 4 bytes
    while (len(arr_bytes)%4 != 0):
        arr_bytes.append(0)
    return bytearray(arr_bytes)

def chr2bin(chr, font):
    img = Image.new("RGB", (font_size, font_size))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), chr, font=font)
    img = img.convert('L')
    nparr = np.array(img).flatten()
    return wrapper_2bpp(nparr)

# return a list [[dst_hex, src_chr], ...]
def read_table(fn):
    res = []
    with open(fn, 'r', encoding='utf-8') as table:
        line = table.readline()
        while line:
            ret = re.findall(r'(.*?)=(.*)', line)
            res.append([int(ret[0][0], 16), ret[0][1]]) 
            line = table.readline()
    return res

def tbl2sth(table, tile_num_start, font):
    tile  = open('tile.bin', 'wb')
    width = open('width.bin', 'wb')
    pamc  = open('pamc.bin', 'wb')
    
    tile_num = len(table)
    tile_nos = int.to_bytes(tile_num, length=2, byteorder='little')
    for i in table:
        tile.write(chr2bin(i[1], font))
        width.write(b'\x00\x0c\x0c')
        tile_nos += int.to_bytes(i[0], length=2, byteorder='little')
        tile_no_start += 1 
        tile_nos += int.to_bytes(tile_num_start, length=2, byteorder='little')
        
    bs = b'PAMC'

    #bs_skip_chunk_size 
    bsscs =  int.to_bytes(table[0][0], length=2, byteorder='little')
    bsscs += int.to_bytes(table[tile_num-1][0], length=2, byteorder='little')
    # map type
    bsscs += b'\x02\x00\x00\x00'
    # next map offset
    bsscs += b'\x00\x00\x00\x00'

    chunk_size = 0x8 + len(bsscs) + len(tile_nos)
    pamc.write(bs+int.to_bytes(chunk_size, length=4, byteorder='little')+bsscs+tile_nos)

    tile.close()
    width.close()
    pamc.close()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--font", required=True, help="font file")
    parser.add_argument("-s", "--size", default=12, help="font size")
    args = parser.parse_args()
    return args


if __name__=="__main__":
    args = parse_args()
    font_size = args.size 
    font = ImageFont.truetype(args.font, font_size)
    # UNFINISHED

