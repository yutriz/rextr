# http://problemkaputt.de/gbatek.htm#dscartridgenitrofontresourceformat, 

class HDWC:
    # 2 Last Tile Number  (should be NumTiles-1)
    # the -1ed one 
    m_tile_n_end   = 0
    # array of bytes
    m_tile_arr = []
    # 4 Unknown/unused (zero)
    # HDWCs
    #   10h+N*3  1    Left Spacing (to be inserted left of character bitmap)
    #   11h+N*3  1    Width of Character Bitmap (excluding left/right spacing)
    #   12h+N*3  1    Total Width of Character (including left/right spacing)
    #   ...      ...  Padding to 4-byte boundary (zerofilled)
    def __init__(self, tile_n_end, tile_arr):
        self.m_tile_n_end = tile_n_end
        self.m_tile_arr = tile_arr # copy? pointer?  ignore it for now

    def to_bytes(self):
        bs = b'HDWC'
        chunk_size = 0x10 + (self.m_tile_n_end+1)*3
        # padding to 4 bytes
        while chunk_size%4!=0:
            chunk_size += 1
        bs += int.to_bytes(chunk_size, length=4, byteorder='little')
        bs += int.to_bytes(0, length=2, byteorder='little')
        bs += int.to_bytes(self.tile_n_end, length=2, byteorder='little')
        bs += b'\x00\x00\x00\x00'
        for i in self.m_tile_arr:
            bs += i
        padding = chunk_size-len(bs)
        for i in range(padding):
            bs += b'\x00'
        return bs

def read_HDWC(fn, offset = -1):
    f = open(fn, 'rb')
    if offset != -1:
        f.seek(offset, 0)
    while f.readable():
        if f.read(1) != b'H':
            continue
        if f.read(1) != b'D':
            continue
        if f.read(1) != b'W':
            continue
        if f.read(1) != b'C':
            continue
        print("HDWC found at offset 0x", hex(f.tell()-4))
        break
    chunk_size   = int.from_bytes(f.read(4), 'little')
    # should be 0000h
    tile_n_start = int.from_bytes(f.read(2), 'little')
    assert(tile_n_start==0)
    # should be NumTiles-1
    tile_n_end   = int.from_bytes(f.read(2), 'little')
    # 4 Unknown/unused (zero)
    f.read(4)
    arr_LWT = []
    i = 0
    tile_n_total = tile_n_end + 1
    while i<tile_n_total: 
        arr_LWT.append(f.read(3))
        i += 1
    f.close()
    return HDWC(tile_n_end, arr_LWT)

class PLGC:
    m_tile_w   = 0x0c
    m_tile_h   = 0x0c
    m_tile_bpp = 0x02
    m_ul_loc = 0x0a
    m_max_prop_w  = 0x0c
    m_tile_rotate = 0x00
    # array of bytes
    m_tile_arr = []

    def __init__(self, tile_w, tile_h, tile_bpp, tile_arr, ul_loc=0x0a, max_prop_w=0x0c, tile_rotate=0x00):
        self.m_tile_w = tile_w
        self.m_tile_h = tile_h
        self.m_tile_bpp = tile_bpp
        self.m_ul_loc = ul_loc
        self.m_max_prop_w = max_prop_w
        self.m_tile_rotate = tile_rotate
        self.m_tile_arr = tile_arr # copy? pointer?  ignore it for now 
    def to_bytes(self):
        bs = b'PLGC' 
        tile_size = (self.m_tile_w*self.m_tile_h*self.m_tile_bpp+7) // 8
        chunk_size = 0x10 + len(self.m_tile_arr)*tile_size 
        # padding to 4 bytes
        while chunk_size%4!=0:
            chunk_size += 1
        bs += int.to_bytes(chunk_size, length=4, byteorder='little')
        bs += int.to_bytes(self.m_tile_w, length=1)
        bs += int.to_bytes(self.m_tile_h, length=1)
        bs += int.to_bytes(tile_size, length=2, byteorder='little')
        bs += int.to_bytes(self.m_ul_loc, length=1)
        bs += int.to_bytes(self.m_max_prop_w, length=1)
        bs += int.to_bytes(self.m_tile_bpp, length=1)
        bs += int.to_bytes(self.m_tile_rotate, length=1)
        for i in self.m_tile_arr:
            bs += i
        padding = chunk_size-len(bs)
        for i in range(padding):
            bs += b'\x00'
        return bs

def read_PLGC(fn, offset = -1):
    f = open(fn, 'rb')
    if offset != -1:
        f.seek(offset, 0)
    while f.readable():
        if f.read(1) != b'P':
            continue
        if f.read(1) != b'L':
            continue
        if f.read(1) != b'G':
            continue
        if f.read(1) != b'C':
            continue
        print("PLGC found at offset 0x", hex(f.tell()-4))
        break
    chunk_size = int.from_bytes(f.read(4), 'little')
    tile_width = int.from_bytes(f.read(1), 'little')
    tile_height = int.from_bytes(f.read(1), 'little')
    tile_size = int.from_bytes(f.read(2), 'little')
    underline = int.from_bytes(f.read(1), 'little')
    # Max proportional Width including left/right spacing
    max_prop_w = int.from_bytes(f.read(1), 'little')
    tile_depth = int.from_bytes(f.read(1), 'little')
    tile_rotate = int.from_bytes(f.read(1), 'little')
    # asuming no padding 
    tile_num = (chunk_size-0x10)//tile_size
    tile_arr = []
    for i in range(tile_num):   
        tile_arr.append(f.read(tile_size))
    f.close()
    return PLGC(tile_width, tile_height, tile_depth, tile_arr, underline, max_prop_w, tile_rotate)
