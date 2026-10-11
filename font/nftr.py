import os
import random
from enum import Enum
from typing import List, Dict

import numpy as np

from font.bit_image import BitImage
from font.char_font import CharFont
from font.vis_utils import visualize_distribution
from font.bits_utils import bit_depth_descale
from pyutils.logger import Logger, LogLevel

# IMPORTANT NOTE: (at least in NDS SN1/2 game)
#   Though it is not mentioned in https://problemkaputt.de/gbatek-ds-cartridge-nitro-font-resource-format.htm,
#   that in a type 2 CMap, an increase order is expected, breaking this would make
#   some characters can not be displayed correctly. (Guess it is searching by order, so
#   once the querying character number is greater than character number it finds first, it
#   will return undefined character immediately.) And in SN1/2 the last type 2 CMap has
#   its first_character set to 0x0000 and last_character to 0xffff, appending new characters
#   and then re-sorting them all becomes the easiest way.
# P.S. Any methods other than APPEND_TO_EXISTING_CMAP?
class TestFlag(Enum):
    APPEND_NEW_CMAP = 0,
    APPEND_TO_EXISTING_CMAP = 1,
    REPLACE_EXISTING_CMAP = 2
TEST_FLAG: TestFlag = TestFlag.APPEND_TO_EXISTING_CMAP

INVALID_CMAP_IDX = 777
APPEND_CODEPOINT_OUT_OF_ENCODING_RANGE = False

INVALID_TILE_NUMBERS = [ 0xffff ]

# TODO
# 1. append_type_1_cmap is incomplete.
# 2. 

class CMAP:
    chunk_size: int
    first_character: int
    last_character: int 
    num_of_characters: int
    map_type: int
    offset_to_next_map_p8: int

    # map type 0
    tile_num_for_first_chara: int

    # type 1
    tile_nums: int 

    # type 2
    num_of_custom_assigned_tiles: int
    custom_dict: Dict

    def __init__(self, byte_order_flag="little"):
        if byte_order_flag in ["little", "big"]:
            self.byte_order_flag = byte_order_flag
        else:
            raise Exception("byte order?")

    @classmethod
    def create_type_0_cmap(cls):
        raise Exception("No implemented")

    @classmethod
    def create_type_1_cmap(
        cls,
        first_char: int,
        sorted_tile_nums: List[int], 
        byte_order_flag="little"
    ):
        PAMC = b"PAMC"
        
        # sorted assertion
        last_char = -1
        for c in sorted_tile_nums:
            if c == 0xFFFF:
                continue
            if c > last_char:
                last_char = c
            else:
                raise Exception("input tile_nums is not sorted")
        
        c_map = cls(byte_order_flag)
        c_map.map_type = 1

        cls.first_character = first_char
        cls.last_character = first_char + len(sorted_tile_nums) - 1

        c_map.tile_nums = sorted_tile_nums

        chunk_size = 0x14 + 2 * len(c_map.tile_nums)
        if chunk_size % 4 != 0:
            chunk_size += 2
        c_map.chunk_size = chunk_size

        c_map.offset_to_next_map_p8 = 0 # to be modified

        return c_map

    @classmethod
    def create_type_2_cmap(
        cls,
        chara_tile_num_dict_sorted_by_chara: Dict[int, int],
        byte_order_flag="little"
    ):
        c_map = cls(byte_order_flag)

        sorted_dict_by_chara = chara_tile_num_dict_sorted_by_chara

        c_map.num_of_custom_assigned_tiles = len(sorted_dict_by_chara.keys())
        c_map.num_of_characters = c_map.num_of_custom_assigned_tiles
        
        c_map.custom_dict = { }
        for chara, tile_no in sorted_dict_by_chara.items():
            c_map.custom_dict[chara] = tile_no

        chunk_size = 0x14 + 2 + 4*len(sorted_dict_by_chara.keys())
        if chunk_size % 4 != 0:
            chunk_size += 2
        c_map.chunk_size = chunk_size
        c_map.first_character = list(sorted_dict_by_chara.keys())[0]
        c_map.last_character = list(sorted_dict_by_chara.keys())[-1]
        c_map.map_type = 2
        c_map.offset_to_next_map_p8 = 0

        return c_map

    @classmethod
    def from_file_pointer(cls, fp, offset, byte_order_flag="little"):
        c_map = cls(byte_order_flag)
        
        fp.seek(offset, os.SEEK_SET)

        # CMAP Header
        if (fp.read(4) != b"PAMC"):
            raise Exception("CMAP chunk format error")
        
        # Chunk Size (14h+...+padding)
        c_map.chunk_size = c_map.bytes_to_int(fp.read(4))

        # 2 bytes 
        c_map.first_character = c_map.bytes_to_int(fp.read(2))
        c_map.last_character = c_map.bytes_to_int(fp.read(2))
        c_map.num_of_characters = c_map.last_character - c_map.first_character + 1

        # Map Type (0, 1, 2)
        c_map.map_type = c_map.bytes_to_int(fp.read(4))

        # Offset to next Character Map, plus 8 （to the start of file)
        c_map.offset_to_next_map_p8 = c_map.bytes_to_int(fp.read(4)) # TO MODIFY

        # For Map Type0, Increasing TileNo's assigned to increasing CharNo's:
        #   14h      2    TileNo for First Char (and increasing for further chars)
        #   16h      2    Padding to 4-byte boundary (zerofilled)
        # For Map Type1, Custom TileNo's assigned to increasing CharNo's:
        #   14h+N*2  2    TileNo's for First..Last Char (FFFFh=None; no tile assigned)
        #   ...      0/2  Padding to 4-byte boundary (zerofilled)
        #   Note: TileNo can be invalid (0xffff), which means the character glyph doesn't exist.  
        # For Map Type2, Custom TileNo's assigned to custom CharNo's:
        #   14h      2    Number of following Char=Tile groups...
        #   16h+N*4  2    Character Number
        #   18h+N*4  2    Tile Number
        #   ...      2    Padding to 4-byte boundary (zerofilled)
        if c_map.map_type == 0:
            c_map.tile_num_for_first_chara = c_map.bytes_to_int(fp.read(2))
            _ = fp.read(2) # padding
        elif c_map.map_type == 1:
            c_map.tile_nums = []
            for i in range(c_map.num_of_characters):
                c_map.tile_nums.append(c_map.bytes_to_int(fp.read(2)))
            if len(c_map.tile_nums) % 4 != 0:
                _ = fp.read(2) # padding
        elif c_map.map_type == 2:
            c_map.num_of_custom_assigned_tiles = c_map.bytes_to_int(fp.read(2))
            c_map.num_of_characters = c_map.num_of_custom_assigned_tiles
            # character -> tile num
            c_map.custom_dict = {}
            for i in range(c_map.num_of_custom_assigned_tiles):
                char_no = c_map.bytes_to_int(fp.read(2))
                tile_no = c_map.bytes_to_int(fp.read(2))
                c_map.custom_dict[char_no] = tile_no
            _ = fp.read(2) # padding

        return c_map

    def bytes_to_int(self, bts):
        return int.from_bytes(bts, self.byte_order_flag)
    
    def int_to_bytes(self, integer, byte_length):
        return int.to_bytes(
                    integer, 
                    length = byte_length, 
                    byteorder=self.byte_order_flag
                )

    def dump(self):
        cmap_pack = b"PAMC" + \
                    self.int_to_bytes(self.chunk_size, 4) + \
                    self.int_to_bytes(self.first_character, 2) + \
                    self.int_to_bytes(self.last_character, 2) + \
                    self.int_to_bytes(self.map_type, 4) + \
                    self.int_to_bytes(self.offset_to_next_map_p8, 4)
        
        if self.map_type == 0:
            cmap_pack += self.int_to_bytes(self.tile_num_for_first_chara, 2) + \
                         self.int_to_bytes(0, 2)
        elif self.map_type == 1:
            for tn in self.tile_nums:
                cmap_pack += self.int_to_bytes(tn, 2)
            if len(self.tile_nums) % 2 != 0:
                cmap_pack += self.int_to_bytes(0, 2)
        elif self.map_type == 2:
            cmap_pack += self.int_to_bytes(
                self.num_of_custom_assigned_tiles, 2
            )
            for n_chara, n_tile in self.custom_dict.items():
                cmap_pack += self.int_to_bytes(n_chara, 2)
                cmap_pack += self.int_to_bytes(n_tile, 2)
            cmap_pack += self.int_to_bytes(0, 2)

        return cmap_pack

def merge_CMAP(cmaps: List[CMAP]):
    """
        return a dict {chara: (cmap_idx, tile_idx)}
    """
    ret_dict = {}
    for i in range(len(cmaps)):
        if cmaps[i].map_type == 0:
            tile_num = cmaps[i].tile_num_for_first_chara
            for chara in range(cmaps[i].first_character, cmaps[i].last_character + 1):
                ret_dict[chara] = (i, tile_num)
                tile_num += 1
        elif cmaps[i].map_type == 1:
            tile_num_idx = 0
            for chara in range(cmaps[i].first_character, cmaps[i].last_character + 1):
                ret_dict[chara] = (i, cmaps[i].tile_nums[tile_num_idx])
                tile_num_idx += 1
        elif cmaps[i].map_type == 2:
            for chara in cmaps[i].custom_dict.keys():
                ret_dict[chara] = (i, cmaps[i].custom_dict[chara])
        
    return ret_dict

#############################################################
class NFTR:
    """
        REF: https://problemkaputt.de/gbatek-ds-cartridge-nitro-font-resource-format.htm 
    """
    def __init__(self, file_path: str):
        with open(file_path, "rb") as fp:
            self.get_header_chunk(fp)
            self.get_font_info_chunk(fp)
            self.get_character_glyph_chunk(fp)
            self.get_character_width_chunk(fp)
            self.get_character_map_chunks(fp)
        
    class FLAGS(Enum): 
        # chunk
        CHUNK_UNFOUND = -1,
        # byte order
        BO_BIG_ENDIAN = 0, # BO: byte order
        BO_LITTLE_ENDIAN = 1,
        # encoding
        ENC_UTF8 = 0,
        ENC_UNICODE = 1,
        ENC_SJIS = 2,
        ENC_CP1552 = 3,   

    chunk_offsets = {
        "header":                FLAGS.CHUNK_UNFOUND,
        "font_info":             FLAGS.CHUNK_UNFOUND,
        "character_glyph":       FLAGS.CHUNK_UNFOUND,
        "character_width":       FLAGS.CHUNK_UNFOUND,
        "first_character_map":   FLAGS.CHUNK_UNFOUND,
    }
    byte_order = FLAGS.BO_LITTLE_ENDIAN
    
    def bytes_to_int(self, bts):
        if self.byte_order == NFTR.FLAGS.BO_LITTLE_ENDIAN:
            byte_order_flag = "little"
        elif self.byte_order == NFTR.FLAGS.BO_LITTLE_ENDIAN:
            byte_order_flag = "big"

        return int.from_bytes(bts, byte_order_flag)

    def int_to_bytes(self, integer, byte_length):
        return int.to_bytes(
            integer, 
            length = byte_length, 
            byteorder=self.byte_order_flag
        )

    # NFTR chunk
    def get_header_chunk(self, fp, offset=0):
        fp.seek(offset, os.SEEK_SET)

        # Header
        if (fp.read(4) != b"RTFN"):
            raise Exception("Not a Nitro Font file")

        self.chunk_offsets["header"] = 0

        # Byte Order -> FEFFh
        bo_b1 = fp.read(1) # byte order indicator byte 1
        bo_b2 = fp.read(1)
        if bo_b1 == b"\xff" and bo_b2 == b"\xfe":
            self.byte_order = NFTR.FLAGS.BO_LITTLE_ENDIAN
        elif bo_b1 == b"\xfe" and bo_b2 == b"\xff":
            self.byte_order = NFTR.FLAGS.BO_BIG_ENDIAN
        else:
            raise Exception("No byte order found")

        if self.byte_order == NFTR.FLAGS.BO_LITTLE_ENDIAN:
            self.byte_order_flag = "little"
        if self.byte_order == NFTR.FLAGS.BO_BIG_ENDIAN:
            self.byte_order_flag = "big"
        
        # Version
        self.version = self.bytes_to_int(fp.read(2))
        if not (self.version in [ 0x100, 0x101, 0x102 ]):
            Logger.print("unknow NFTR version {}".format(self.version), log_level=LogLevel.WARNING)

        # Decompressed Resource Size
        self.decomp_res_size = self.bytes_to_int(fp.read(4)) # TO MODIFY

        # Offset to "FNIF" Chunk, aka Size of "RTFN" Chunk (0010h)
        self.chunk_offsets["font_info"] = self.bytes_to_int(fp.read(2))
    
        # Total number of following Chunks (0003h+NumCharMaps) (0018h)
        self.num_of_following_chunk = self.bytes_to_int(fp.read(2)) # TO MODIFY

        assert(fp.tell() == 16)

    # FINF chunk
    def get_font_info_chunk(self, fp, offset=-1):
        if (offset == -1 and self.chunk_offsets["font_info"]):
            offset = self.chunk_offsets["font_info"]
        fp.seek(offset, os.SEEK_SET)

        # FNIF Header
        if (fp.read(4) != b"FNIF"):
            raise Exception("FINF format error")
        
        # Chunk Size (1Ch or 20h)
        font_info_chunk_size = self.bytes_to_int(fp.read(4))
        if (font_info_chunk_size in [0x1c, 0x20]):
            self.font_info_chunk_size = font_info_chunk_size
        else:
            raise Exception("unknown font_info_chunk_size")

        # unknow/unused
        _ = fp.read(1)

        # Height or Height+/-1, unsure
        self.height = self.bytes_to_int(fp.read(1))

        # Unknown (usually 00h, or sometimes 1Fh maybe for chr(3Fh)="?")
        _ = fp.read(1)

        # Unknown/unused (zero)
        _ = fp.read(2)

        # Width or Width+1, unsure
        self.width = self.bytes_to_int(fp.read(1))

        # Width_bis (?) 
        self.width_bis = self.bytes_to_int(fp.read(1)) # unknow, but keep it 

        # encoding
        enc = self.bytes_to_int(fp.read(1))
        if enc == 0:
            self.encoding = NFTR.FLAGS.ENC_UTF8
        elif enc == 1:
            self.encoding = NFTR.FLAGS.ENC_UNICODE
        elif enc == 2:
            self.encoding = NFTR.FLAGS.ENC_SJIS
        elif enc == 3:
            self.encoding = NFTR.FLAGS.ENC_CP1552
        
        # Offset to Character Glyph chunk, plus 8
        self.offset_to_chara_glyph_chunk_p8 = \
            self.bytes_to_int(fp.read(4))  # TO MODIFY
        
        # Offset to Character Width chunk, plus 8
        self.offset_to_chara_width_chunk_p8 = \
            self.bytes_to_int(fp.read(4))  # TO MODIFY
    
        # Offset to first Character Map chunk, plus 8
        self.offset_to_chara_map_chunk_p8 = \
            self.bytes_to_int(fp.read(4))  # TO MODIFY
    
        if self.font_info_chunk_size == 0x20:
            self.tile_height = self.bytes_to_int(fp.read(1))
            # Max Width or so +/-?   
            self.max_width = self.bytes_to_int(fp.read(1))
            # Underline location   
            self.underline_location = self.bytes_to_int(fp.read(1))
            # unknow/unused
            _ = self.bytes_to_int(fp.read(1))

        assert(fp.tell() == (offset + self.font_info_chunk_size))
        self.chunk_offsets["character_glyph"] = fp.tell()

    # CGLP (Character Glyph Chunk) (Tile Bitmaps)
    def get_character_glyph_chunk(self, fp, offset=-1):
        if (offset == -1 and self.chunk_offsets["character_glyph"]):
            offset = self.chunk_offsets["character_glyph"]
        fp.seek(offset, os.SEEK_SET)

        # FNIF Header
        if (fp.read(4) != b"PLGC"):
            raise Exception("CGLP format error")
    
        # Chunk Size (10h+NumTiles*siz+padding)
        self.chara_glyph_chunk_size = self.bytes_to_int(fp.read(4)) # TO MODIFY

        # Tile Width in pixels
        self.tile_width = self.bytes_to_int(fp.read(1))
        # Tile height in pixels
        self.tile_height = self.bytes_to_int(fp.read(1))

        # Tile Size in bytes (siz=width*height*bpp+7)/8) = per character
        self.tile_bytes_size = self.bytes_to_int(fp.read(2))

        # underline location 
        self.chara_glyph_underline_location = self.bytes_to_int(fp.read(1))

        # Max proportional Width including left/right spacing
        self.max_proportional_width = self.bytes_to_int(fp.read(1))

        # Tile Depth (bits per pixel) (usually 1 or 2, sometimes 3)
        self.tile_depth = self.bytes_to_int(fp.read(1))

        # TODO
        # Tile Rotation (0=None/normal, other:
        # All tiles are starting on a byte boundary. However, the separate scanlines aren't
        # necessarily byte-aligned (for example, at 10pix width, a byte may contain rightmost
        # pixels of one line, followed by leftmost pixels of next line).
        # Bit7 of the first byte of a bitmap is the MSB of the upper-left pixel, 
        # bit6..0 are then containing the LSB(s) of the pixel (if bpp>1), followed by 
        # the next pixels of the scanline, followed by further scanlines; 
        # the data is arranged as straight Width*Height bitmap (without splitting into 8x8 sub-tiles).
        # Colors are ranging from Zero (transparent/background color) to all bit(s) set (solid/text color).
        # The meaning of the Tile Rotation entry is unclear
        # (one source claims 0=0', 1=90', 2=270', 3=180', and another source claims 0=0', 2=90', 
        # 4=180', 6=270', and for both sources, it's unclear 
        # if the rotation is meant to be clockwise or anti-clockwise).
        
        self.tile_rotation = self.bytes_to_int(fp.read(1))

        # bytes data stored 
        self.chara_glyphs: List[BitImage] = []
        
        cur_offset = 0x10
        while cur_offset < self.chara_glyph_chunk_size:
            data = fp.read(self.tile_bytes_size)
            glyph = BitImage(
                        data, 
                        self.tile_width, 
                        self.tile_height,
                        self.tile_depth
                    )
            self.chara_glyphs.append(glyph)
            cur_offset += self.tile_bytes_size

        self.chunk_offsets["character_width"] = offset + self.chara_glyph_chunk_size

    # CWDH chunk
    def get_character_width_chunk(self, fp, offset=-1):
        if offset == -1:
            offset = self.chunk_offsets["character_width"] 
        fp.seek(offset, os.SEEK_SET)
        
        # HDWC Header
        if (fp.read(4) != b"HDWC"):
            raise Exception("CWDH format error")
        
        # Character Width Chunk size
        self.chara_width_chunk_size = self.bytes_to_int(fp.read(4)) # TO MODIFY

        # First Tile Number (should be 0000h)
        self.chara_width_num_first_tile = self.bytes_to_int(fp.read(2))
        assert(self.chara_width_num_first_tile == 0)

        # Last Tile Number  (should be NumTiles-1)
        self.chara_width_num_last_tile = self.bytes_to_int(fp.read(2)) # TO MODIFY

        # unknown/unused
        _ = fp.read(4)
        
        self.tile_width_tiles = [] # TO MODIFY MORE
        # below are tile bitmaps (Padding to 4-byte bound)
        for idx in range(self.chara_width_num_last_tile + 1):
            ls =  self.bytes_to_int(fp.read(1)) # Left Spacing (to be inserted left of character bitmap)
            wcb = self.bytes_to_int(fp.read(1)) # Width of Character Bitmap (excluding left/right spacing)
            twc = self.bytes_to_int(fp.read(1)) # Total Width of Character (including left/right spacing)
            self.tile_width_tiles.append([ls, wcb, twc])

        paddings = (self.chara_width_num_last_tile + 1) * 3 // 4 * 4 + 4 \
                    - (self.chara_width_num_last_tile + 1) * 3

        fp.read(paddings)

        if self.chara_glyph_chunk_size == 0x10 + (self.chara_width_num_last_tile + 1)*3 + paddings \
           and fp.tell() != (offset + self.chara_width_chunk_size):
            raise Exception("chunk size error in character wdith chunk")

        self.chunk_offsets["first_character_map"] = offset + self.chara_width_chunk_size
        
        assert self.chunk_offsets["first_character_map"] == self.offset_to_chara_map_chunk_p8 - 8, \
            f"seems offset to first character map doesn't match"

    # CMAP chunk
    # Character Map(s) - Translation Tables for ASCII/JIS/etc to Tile Numbers?
    def get_character_map_chunks(self, fp, offset=-1):
        if offset == -1:
            offset = self.chunk_offsets["first_character_map"] 
        fp.seek(offset, os.SEEK_SET)
       
        if self.byte_order == NFTR.FLAGS.BO_LITTLE_ENDIAN:
            bo_flag = "little"
        elif self.byte_order == NFTR.FLAGS.BO_BIG_ENDIAN:
            bo_flag = "big"
        
        self.chara_maps: List[CMAP] = []
        next_char_map_offset = offset 

        while True:
            char_map = CMAP.from_file_pointer(
                                fp, 
                                offset=next_char_map_offset, 
                                byte_order_flag=bo_flag
                            )
            self.chara_maps.append(char_map)
            if char_map.offset_to_next_map_p8 != 0:
                next_char_map_offset = char_map.offset_to_next_map_p8 - 8
            else:
                break
        
        self.merged_cmaps = merge_CMAP(self.chara_maps)

    def find_character_glyph(self, chara) -> BitImage:
        if chara in list(self.merged_cmaps.keys()):
            tp = self.merged_cmaps[chara]
            cmap_idx, tile_idx = tp[0], tp[1]
            return self.chara_glyphs[tile_idx]
        else:
            raise Exception("character not in NFTR")
        
    def print_info(self):
        for i in range(len(self.chara_maps)):
            cm = self.chara_maps[i]
            print(f"character map {i}:")
            print(f"  first character: {cm.first_character:x}")
            print(f"  last  character: {cm.last_character:x}")
            print(f"  num of characters: {cm.num_of_characters}")
            
            # Map Type (0, 1, 2)
            if cm.map_type == 0:
                print("  Type: Increasing TileNo's assigned to increasing CharNo's")
            elif cm.map_type == 1:
                print("  Type: Custom TileNo's assigned to increasing CharNo's")
            elif cm.map_type == 2:
                print("  Type: Custom TileNo's assigned to custom CharNo's")
            print("")

    ######################## nftr append ####################################


    def _assure_new_characters(
        self, chara_glyph_dict: Dict[int, BitImage]
    ) -> Dict[int, BitImage]:
        """
            ### Note: This will modify input chara_glyph_dict.
            remove characters that satisfy conditions below: 
            1. exist in CMaps of old NFTR
            2. do bind to a valid tile
            3. whose glyph tile size equals to that in NFTR 
        """
        
        # glyph bit image size check 
        _glyph_check_random = chara_glyph_dict[
            random.choice(list(chara_glyph_dict.keys()))
        ]
        glyph_tile_size_in_byte = (
           7 + (_glyph_check_random.width * _glyph_check_random.height * _glyph_check_random.bit_depth)
        ) // 8 
        if (glyph_tile_size_in_byte != self.tile_bytes_size):
            raise Exception("Appended tile size doesn't match")

        # conflict check
        origin_conversion = self.get_shiftJIS_to_unicode_conversion()
        existing_character_wo_glyph = []
        # those characters should not be in a new cmap
        duplicate_characters = [] 
        for chara, _ in chara_glyph_dict.items():
            # code point doesn't exist
            if not chara in origin_conversion:
                continue

            # exist, then check its tile
            q = self.merged_cmaps[chara]
            cmap_idx, tile_idx = q[0], q[1]
            if tile_idx in INVALID_TILE_NUMBERS:
                existing_character_wo_glyph.append(chara)
            else:
                Logger.print(
                    f"0x{chara:x} in original NFTR has its glyph already, will be removed", 
                    LogLevel.REGULAR
                )
            # chara now has a glyph tile no matter existing one or new one
            duplicate_characters.append(chara)

        # corresponding
        # existing_character_wo_glyph -> glyphs_to_be_added -> tile_numbers
        glyphs_to_be_added: list[BitImage] = [
            chara_glyph_dict[no_glyph_chara]
            for no_glyph_chara in existing_character_wo_glyph
        ]

        # glyphs already extracted, can remove redundant now
        for c in duplicate_characters:
            chara_glyph_dict.pop(c, None)

        last_tile_number = len(self.chara_glyphs) - 1
        tile_numbers = [
            last_tile_number + 1 + i
            for i in range(len(glyphs_to_be_added))
        ]

        self._append_character_glyphs_and_update_NFTR_info(
            glyphs_to_be_added
        )

        # modify origin cmap 
        for idx, no_glyph_chara in enumerate(existing_character_wo_glyph):
            q = self.merged_cmaps[no_glyph_chara]
            cmap_idx = q[0]

            map_type = self.chara_maps[cmap_idx].map_type
            if map_type == 0:
                raise Exception(
                    f"0x{chara:x} seems to be assigned with a invalid number \"{tile_idx}\""
                     "but it exists in a Type0 CMap which shouldn't allow a unassigned tile."
                )
            elif map_type == 1:
                _offset = no_glyph_chara - self.chara_maps[cmap_idx].first_character
                assert _offset < len(self.chara_maps[cmap_idx].tile_nums)
                assert self.chara_maps[cmap_idx].tile_nums[_offset] in INVALID_TILE_NUMBERS
                self.chara_maps[cmap_idx].tile_nums[_offset] = tile_numbers[idx]
                Logger.print(
                    f"0x{no_glyph_chara:x} exists in original NFTR but has no glyph. "
                    "Glyph of this character will be added.",
                    LogLevel.REGULAR
                )
            elif map_type == 2:
                assert self.chara_maps[cmap_idx].custom_dict[no_glyph_chara] in INVALID_TILE_NUMBERS 
                self.chara_maps[cmap_idx].custom_dict[no_glyph_chara] = tile_numbers[idx]
                Logger.print(
                    f"0x{no_glyph_chara:x} exists in original NFTR but has no glyph. "
                    "Glyph of this character will be added.",
                    LogLevel.REGULAR
                )
            else:
                raise Exception(f"Unknown map type \"{map_type}\" of chara_maps[{cmap_idx}].")

        Logger.print(
            f"Total {len(existing_character_wo_glyph)} tiles are assign with no-glyph-characters in original NFTR.",
            LogLevel.REGULAR
        )

        return chara_glyph_dict

    def _append_character_glyphs_and_update_NFTR_info(self,
        sorted_glyphs: List[BitImage], # record the character outside function
        glyph_background: int = 0
    ) -> None:
        """
        Usage:
            Case A: append a new cmap with corresponding tiles
                1. Prepare CMap and append the cmap to self.chara_maps
                2. Call this function to add new glyphs to self.chara_glyphs \
                    and update things like chunk sizes and offsets in NFTR
            Case B: add tiles without adding a new Cmap (i.e. adding tiles \
                to existing codepoints that have no tiles)
                1. Call this function and modify Character-TileNo in cmap
        Return: added tile numbers
        
        """
        
        self.chara_glyphs += sorted_glyphs

        CGLP_CHUNK_HEADER_SIZE = 16 
        new_chara_glyph_chunk_size_without_padding = \
            self.tile_bytes_size * len(self.chara_glyphs) + CGLP_CHUNK_HEADER_SIZE
        # padding to 4
        new_chara_glyph_chunk_size = (new_chara_glyph_chunk_size_without_padding + 3) // 4 * 4
        self.chara_glyph_chunk_size = new_chara_glyph_chunk_size

        # Character width chunk
        CWDH_CHUNK_HEADER_SIZE = 16
        self.chara_width_num_last_tile = len(self.chara_glyphs) - 1
        for glyph in sorted_glyphs:
            ls = glyph.get_left_spacing(glyph_background)
            cwb = glyph.get_character_width_ex_l_r_spacing(glyph_background)
            twc = glyph.width
            self.tile_width_tiles.append([ls, cwb, twc])
        new_chara_width_chunk_size_without_padding = \
            CWDH_CHUNK_HEADER_SIZE + 3 * len(self.tile_width_tiles)
        new_chara_width_chunk_size = (new_chara_width_chunk_size_without_padding + 3) // 4 * 4
        self.chara_width_chunk_size = new_chara_width_chunk_size

        # offset modification in bytes
        # usually this won't change
        NFTR_HEADER_SIZE = 16
        FNIF_HEADER_SIZE = self.font_info_chunk_size

        # usually this won't change
        self.offset_to_chara_glyph_chunk_p8 = \
            NFTR_HEADER_SIZE + FNIF_HEADER_SIZE + 8
        
        self.offset_to_chara_width_chunk_p8 = \
            self.offset_to_chara_glyph_chunk_p8 + self.chara_glyph_chunk_size 

        self.offset_to_chara_map_chunk_p8 = \
            self.offset_to_chara_width_chunk_p8 + self.chara_width_chunk_size 

        decomp_res_size = NFTR_HEADER_SIZE + FNIF_HEADER_SIZE + \
                          self.chara_glyph_chunk_size + \
                          self.chara_width_chunk_size

        # re locate
        for idx in range(len(self.chara_maps) - 1):
            decomp_res_size += self.chara_maps[idx].chunk_size
            self.chara_maps[idx].offset_to_next_map_p8 = decomp_res_size + 8
        self.chara_maps[-1].offset_to_next_map_p8 = 0

        self.decomp_res_size = decomp_res_size + self.chara_maps[-1].chunk_size

        self.num_of_following_chunk = 0x3 + len(self.chara_maps)

    def append_type_0_cmap(self):
        raise NotImplementedError

    def append_type_1_cmap(
        self, 
        first_character: int,
        sorted_glyphs: List[BitImage],
        glyph_background: int = 0,
        byte_order_flag: str = "little"
    ):
        assert \
            ((sorted_glyphs[0].width * sorted_glyphs[0].height * sorted_glyphs[0].bit_depth)+7)//8 == \
            self.tile_bytes_size, \
            "Appended tile size doesn't match"
        
        # conflict check
        origin_conversion = self.get_shiftJIS_to_unicode_conversion()
        for i in range(len(sorted_glyphs)):
            if first_character+i in origin_conversion:
                raise Exception(f"Seems 0x{(first_character+i):x} already exists in original NFTR")
            else:
                continue

        last_tile_number = len(self.chara_glyphs) - 1
        sorted_tile_nums = [ i for i in range(last_tile_number+1, last_tile_number+1+len(sorted_glyphs)) ]

        c_map = CMAP.create_type_1_cmap(first_character, sorted_tile_nums, byte_order_flag)
        self.chara_maps.append(c_map)

        self._append_character_glyphs_and_update_NFTR_info(
            sorted_glyphs,
            glyph_background=glyph_background
        )

    def append_type_2_cmap(
        self, 
        chara_glyph_dict: Dict[int, BitImage], 
        glyph_background: int = 0,
        byte_order_flag: str = "little"
    ):
        # character glyph chunk
        chara_glyph_dict_sorted = dict(
            sorted(
                chara_glyph_dict.items(), 
                key=lambda item: item[0]
            )
        )
        
        self._assure_new_characters(chara_glyph_dict_sorted)

        chara_tile_num_dict_sorted = { }

        sorted_glyphs = list(chara_glyph_dict_sorted.values())

        last_tile_number = len(self.chara_glyphs) - 1
        tile_numbers = [ 
            last_tile_number + 1 + i
            for i in range(len(sorted_glyphs))
        ]

        for idx, chara in enumerate(chara_glyph_dict_sorted.keys()):
            chara_tile_num_dict_sorted[chara] = tile_numbers[idx]

        c_map = CMAP.create_type_2_cmap(chara_tile_num_dict_sorted, byte_order_flag)
        self.chara_maps.append(c_map)

        self._append_character_glyphs_and_update_NFTR_info(
            sorted_glyphs,
            glyph_background=glyph_background
        )

        Logger.print(
            "{} new character glyph added.".format(len(tile_numbers)),
            LogLevel.REGULAR
        )

    def append_to_existing_type_2_cmap(
        self, 
        chara_glyph_dict: Dict[int, BitImage],
        glyph_background: int = 0,
    ):
        chara_glyph_dict_sorted = dict(
            sorted(
                chara_glyph_dict.items(), 
                key=lambda item: item[0]
            )
        )

        self._assure_new_characters(chara_glyph_dict_sorted)

        cmap_idx = INVALID_CMAP_IDX
        last_t2_cmap = self.chara_maps[-1]
        for i in reversed(range(len(self.chara_maps))):
            if self.chara_maps[i].map_type == 2:
                last_t2_cmap = self.chara_maps[i]
                cmap_idx = i
                break
        if cmap_idx == INVALID_CMAP_IDX:
            raise Exception("No existing type2 CMAP in current NFTR.")

        last_tile_number = len(self.chara_glyphs) - 1
        new_tile_numbers = [
            last_tile_number + 1 + i
            for i in range(len(chara_glyph_dict_sorted))
        ]

        for idx, chara in enumerate(chara_glyph_dict_sorted.keys()):
            self.chara_maps[cmap_idx].custom_dict[chara] = new_tile_numbers[idx]

        self.chara_maps[cmap_idx].custom_dict = dict(
            sorted(
                self.chara_maps[cmap_idx].custom_dict.items(),
                key=lambda item: item[0]
            )
        )

        self.chara_maps[cmap_idx].num_of_custom_assigned_tiles += len(chara_glyph_dict_sorted)
        self.chara_maps[cmap_idx].num_of_characters = \
            self.chara_maps[cmap_idx].num_of_custom_assigned_tiles
        chunk_size = 0x14 + 2 + 4*len(self.chara_maps[cmap_idx].custom_dict)
        if chunk_size % 4 != 0:
            chunk_size += 2
        self.chara_maps[cmap_idx].chunk_size = chunk_size

        if self.chara_maps[cmap_idx].first_character > list(chara_glyph_dict_sorted.keys())[0]:
            self.chara_maps[cmap_idx].first_character = list(chara_glyph_dict_sorted.keys())[0]
        if self.chara_maps[cmap_idx].last_character < list(chara_glyph_dict_sorted.keys())[-1]:
            self.chara_maps[cmap_idx].last_character = list(chara_glyph_dict_sorted.keys())[-1]

        self._append_character_glyphs_and_update_NFTR_info(
            list(chara_glyph_dict_sorted.values()),
            glyph_background=glyph_background
        )

        Logger.print(
            "{} new character glyph added.".format(len(new_tile_numbers)),
            LogLevel.REGULAR
        )

    def replace_existing_type_2_cmap(
        self, 
        chara_glyph_dict: Dict[int, BitImage],
    ): 
        """
            ### DONT 
            test funnction, to be updated. 
        """
        self._assure_new_characters(chara_glyph_dict)

        cmap_idx = INVALID_CMAP_IDX
        last_t2_cmap = self.chara_maps[-1]
        for i in reversed(range(len(self.chara_maps))):
            if self.chara_maps[i].map_type == 2:
                last_t2_cmap = self.chara_maps[i]
                cmap_idx = i
                break
        if cmap_idx == INVALID_CMAP_IDX:
            raise Exception("No exis")

        chara_glyph_dict_sorted = dict(
            sorted(
                chara_glyph_dict.items(),
                key=lambda item: item[0]
            )
        )

        chara_no_s = list(last_t2_cmap.custom_dict.keys())
        tile_no_s = [last_t2_cmap.custom_dict[c] for c in chara_no_s]

        new_chara_no_s = list(chara_glyph_dict_sorted.keys())
        for idx, tile_no in enumerate(tile_no_s):
            if (idx < len(chara_glyph_dict_sorted)):
                # replace glyph in chara_glyph
                self.chara_glyphs[tile_no] = chara_glyph_dict_sorted[new_chara_no_s[idx]]
                last_t2_cmap.custom_dict.pop(chara_no_s[idx], None)
                last_t2_cmap.custom_dict[new_chara_no_s[idx]] = tile_no
            else:
                break

        self.merged_cmaps = merge_CMAP(self.chara_maps)
    
    def get_shiftJIS_to_unicode_conversion(self, output_path=None):
        sjis_codepoints = self.merged_cmaps.keys()

        conversion = {}

        for sjis_codepoint in sjis_codepoints:
            if sjis_codepoint <= 0xFF:
                # Single-byte character (0x00 to 0xFF)
                sjis_bytes = sjis_codepoint.to_bytes(1, 'big')
            elif 0x100 <= sjis_codepoint <= 0xFFFF:
                # Double-byte character (0x100 to 0xFFFF).
                sjis_bytes = sjis_codepoint.to_bytes(2, 'big')
            else:
                raise Exception(f"SJIS code point should be less than 0xFFFF, but input is 0x{sjis_codepoints:x}")

            try:
                # Decode the bytes object to a Unicode string
                unicode_string = sjis_bytes.decode('shift_jis')
                
                # Get the Unicode code point (integer) from the character string
                if len(unicode_string) == 1:
                    conversion[sjis_codepoint] = ord(unicode_string)
                else:
                    Logger.print(
                        f"{unicode_string} seems to contain more than one characters, skipped", 
                        LogLevel.WARNING
                    )
                    
            except UnicodeDecodeError:
                # Happens if the integer(s) do not form a valid Shift JIS sequence
                conversion[sjis_codepoint] = ord("△")
                # Logger.print(
                #     f"0x{sjis_codepoint:x} seems unable to be converted UTF-8 code point, replaced with a \"△\" (0x25b3)",
                #     LogLevel.WARNING
                # )

        if output_path is None:
            return conversion
        
        with open(output_path, "w") as f:
            f.write("# ntfr extracted\n")
            for sjis_codepoint in list(conversion.keys()):
                f.write(f"0x{sjis_codepoint:x}    0x{conversion[sjis_codepoint]:x}\n")

    def dump(self):
        # NFTR chunk
        bo_indicator = 0xFEFF
        if self.byte_order == NFTR.FLAGS.BO_BIG_ENDIAN:
            bo_indicator = 0xFFFE

        nftr_pack = b"RTFN" + \
                    self.int_to_bytes(bo_indicator, 2) + \
                    self.int_to_bytes(self.version, 2) + \
                    self.int_to_bytes(self.decomp_res_size, 4) + \
                    self.int_to_bytes(self.chunk_offsets["font_info"], 2) + \
                    self.int_to_bytes(self.num_of_following_chunk, 2)
        
        # FINF chunk
        enc_indicator = 0 # utf8
        if self.encoding == NFTR.FLAGS.ENC_UNICODE:
            enc_indicator = 1
        elif self.encoding == NFTR.FLAGS.ENC_SJIS:
            enc_indicator = 2
        elif self.encoding == NFTR.FLAGS.ENC_CP1552:
            enc_indicator = 3

        finf_pack = b"FNIF" + \
                    self.int_to_bytes(self.font_info_chunk_size, 4) + \
                    self.int_to_bytes(0, 1) + \
                    self.int_to_bytes(self.height, 1) + \
                    self.int_to_bytes(0, 1) + \
                    self.int_to_bytes(0, 2) + \
                    self.int_to_bytes(self.width, 1) + \
                    self.int_to_bytes(self.width_bis, 1) + \
                    self.int_to_bytes(enc_indicator, 1) + \
                    self.int_to_bytes(self.offset_to_chara_glyph_chunk_p8, 4) + \
                    self.int_to_bytes(self.offset_to_chara_width_chunk_p8, 4) + \
                    self.int_to_bytes(self.offset_to_chara_map_chunk_p8, 4)
        if self.font_info_chunk_size == 0x20:
            finf_pack += self.int_to_bytes(self.tile_width, 1) + \
                         self.int_to_bytes(self.max_width, 1) + \
                         self.int_to_bytes(self.underline_location, 1) + \
                         self.int_to_bytes(0, 1)
        
        # CGLP chunk
        cglp_pack = b"PLGC" + \
                     self.int_to_bytes(self.chara_glyph_chunk_size, 4) + \
                     self.int_to_bytes(self.tile_width, 1) + \
                     self.int_to_bytes(self.tile_height, 1) + \
                     self.int_to_bytes(self.tile_bytes_size, 2) + \
                     self.int_to_bytes(self.chara_glyph_underline_location, 1) + \
                     self.int_to_bytes(self.max_proportional_width, 1) + \
                     self.int_to_bytes(self.tile_depth, 1) + \
                     self.int_to_bytes(self.tile_rotation, 1)
        
        tile_bitmaps_byte_len = 0
        for glyph in self.chara_glyphs:
            bts = glyph.to_bytes(bit_depth=2)
            cglp_pack += bts
            tile_bitmaps_byte_len += len(bts)

        # padding
        padding_len = int((tile_bitmaps_byte_len + 3) / 4) * 4 - tile_bitmaps_byte_len
        if padding_len > 0:
            cglp_pack += self.int_to_bytes(0, padding_len)

        # CWDH chunk 
        cwdh_pack = b"HDWC" + \
                     self.int_to_bytes(self.chara_width_chunk_size, 4) + \
                     self.int_to_bytes(self.chara_width_num_first_tile, 2) + \
                     self.int_to_bytes(self.chara_width_num_last_tile, 2) + \
                     self.int_to_bytes(0, 4)
        
        wt_byte_len = 0
        for wt in self.tile_width_tiles:
            wt_bytes = self.int_to_bytes(wt[0], 1) + \
                       self.int_to_bytes(wt[1], 1) + \
                       self.int_to_bytes(wt[2], 1)
            cwdh_pack += wt_bytes
            wt_byte_len += 3

        padding_len = (wt_byte_len + 3) // 4 * 4 - wt_byte_len
        if padding_len > 0:
            cwdh_pack += self.int_to_bytes(0, padding_len)

        cmap_packs = b""
        for char_map in self.chara_maps:
            cmap_packs += char_map.dump()
        
        return nftr_pack + finf_pack + cglp_pack + cwdh_pack + cmap_packs

    def visualize_distribution(self):
        visualize_distribution(list(self.merged_cmaps.keys()))

# return 
def get_appended_nftr(
    nftr_font_filepath: str,
    used_characters: list,
    ttf_font_filepath: str,
) -> tuple[NFTR, dict]:
    # shift jis table: http://charset.7jp.net/sjis.html
    # standard: https://encoding.spec.whatwg.org/#shift_jis-decoder
    #  0x00 as second byte is not allowed
    #  range 0xa000 to 0xdf00 is also not allowed

    ##### restriction
    def sjis_valid(cp: int) -> bool:
        row_byte = cp & 0xFF
        col_byte = (cp >> 8) & 0xFF 

        valid_row = (0x81 <= row_byte and row_byte <= 0x9F) or (0x81 <= row_byte and row_byte <= 0x9F) 
        valid_col = (0x40 <= col_byte and col_byte <= 0x7E) or (0x80 <= col_byte and col_byte <= 0xFC)
          
        if valid_row and valid_col:
            return True
        else:
            return False
    #####

    nftr_ = NFTR(nftr_font_filepath)
    original_conv = nftr_.get_shiftJIS_to_unicode_conversion()
    original_characters = list(original_conv.keys()) # sjis to unicode
    original_characters.sort()

    Logger.print("{} characters used in translation text.".format(len(used_characters)))

    # find enough vacant in origin codepoint table (even some might not be used then)
    vacant_codepoints = []
    for idx in range(len(original_characters) - 1):
        this_character = original_characters[idx]
        if this_character < 0xff:
            continue
        
        next_character = original_characters[idx+1]

        is_adjacent = (this_character+1 == next_character)
        if not is_adjacent:
            candicates = list(range(this_character+1, next_character))
            candicates = [ c for c in candicates if sjis_valid(c)]
            vacant_codepoints += candicates
        else:
            pass

        if len(vacant_codepoints) >= len(used_characters):
            break

    if len(vacant_codepoints) < len(used_characters):
        if not APPEND_CODEPOINT_OUT_OF_ENCODING_RANGE:
            raise Exception(
                "Vacant code points ({}) in original NFTR not capable of including all new added characters({})."
                .format(len(vacant_codepoints), len(used_characters))
            )
        else:
            # vacant cp not enough
            last_char = original_characters[-1]
            to_append = len(used_characters) - len(vacant_codepoints)
            for i in range(to_append):
                appended_vacancy = last_char + i + 1
                vacant_codepoints.append(appended_vacancy)

    ####
    if (nftr_.tile_width != nftr_.tile_height):
        Logger.print(
            f"{nftr_font_filepath} seems to have different tile width and height, using tile_width {nftr_.tile_width}",
            log_level=LogLevel.WARNING
        )
    font_size = nftr_.tile_width
    ttf_font = CharFont(
        ttf_font_filepath, 
        size=font_size
    )

    #### 
    new_mapping = {}
    appended_conv = {} # unicode to appended vacant codepoint 

    reversed_original_conv = {} # unicode to sjis
    for origin_codepoint, unicode_codepoint in original_conv.items():
        reversed_original_conv[unicode_codepoint] = origin_codepoint

    vacant_idx = 0
    for idx, chara in enumerate(used_characters):
        utf_chara_ord = ord(chara)

        # existing in original_conv 
        if utf_chara_ord in list(reversed_original_conv.keys()):
            appended_conv[utf_chara_ord] = reversed_original_conv[utf_chara_ord]
            # Logger.print(f"existing one: {chara}", LogLevel.WARNING)
        else: 
            appended_conv[utf_chara_ord] = vacant_codepoints[vacant_idx]
            vacant_idx += 1 # won't overflow

        # in PIL.Image
        chara_image = ttf_font.character_image(
            chara,
            backgroud_color="black",
            top_left_pos=(0, -1),
            mode='L',
            charecter_shadow=True
        )
        chara_image_data = np.array(chara_image)

        # bad performance?
        for r in range(chara_image_data.shape[0]):
            for c in range(chara_image_data.shape[1]):
                chara_image_data[r][c] = bit_depth_descale(chara_image_data[r][c], 8, 2)

        chara_bit_image = BitImage(
            chara_image_data,
            width=chara_image_data.shape[1],
            height=chara_image_data.shape[0],
            bit_depth=2
        )

        new_mapping[appended_conv[utf_chara_ord]] = chara_bit_image

    if TEST_FLAG == TestFlag.APPEND_NEW_CMAP:
        nftr_.append_type_2_cmap(
            new_mapping,
            glyph_background=0
        )
    elif TEST_FLAG == TestFlag.APPEND_TO_EXISTING_CMAP:
        nftr_.append_to_existing_type_2_cmap(
            new_mapping,
            glyph_background=0
        )
    elif TEST_FLAG == TestFlag.REPLACE_EXISTING_CMAP:
        nftr_.replace_existing_type_2_cmap(
            new_mapping
        )

    return (nftr_, appended_conv)