import os
import random
from enum import Enum
from typing import List, Dict

from font.bit_image import BitImage
from font.vis_utils import visualize_distribution

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
            print("unknow NFTR version {}".format(self.version))

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
        _ = fp.read(1)

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
        
        assert(
            (self.chunk_offsets["first_character_map"] == self.offset_to_chara_map_chunk_p8 - 8),
            f"seems offset to first character map doesn't match"
        )

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

    def find_character_glyph(self, chara):
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
    def append_type_0_cmap(self):
        raise NotImplementedError

    def append_type_1_cmap(
        self, 
        first_character: int,
        sorted_glyphs: List[BitImage],
        glyph_background: int = 0,
        byte_order_flag: str = "little"
    ):
        assert(
        (
            ((sorted_glyphs[0].width * sorted_glyphs[0].height * sorted_glyphs[0].bit_depth)+7)//8 == \
            self.tile_bytes_size
        ),
            "Appended tile size doesn't match"
        )

        # conflict check
        origin_conversion = self.get_shiftJIS_to_unicode_conversion()
        for i in range(len(sorted_glyphs)):
            if first_character+i in origin_conversion:
                raise Exception(f"Seems 0x{(first_character+i):x} already exists in original NFTR")
            else:
                continue

        # character glyph chunk
        self.chara_glyphs += sorted_glyphs
        last_tile_number = len(self.chara_glyphs) - 1
        sorted_tile_nums = [ i for i in range(last_tile_number+1, last_tile_number+1+len(sorted_glyphs)) ]

        c_map = CMAP.create_type_1_cmap(first_character, sorted_tile_nums, byte_order_flag)
        self.chara_maps.append(c_map)

        # character glyph chunk has padding or doesn't
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
                                
        for idx in range(len(self.chara_maps) - 1):
            decomp_res_size += self.chara_maps[idx].chunk_size
            self.chara_maps[idx].offset_to_next_map_p8 = decomp_res_size + 8

        self.chara_maps[-1].offset_to_next_map_p8 = 0

    def append_type_2_cmap(
        self, 
        chara_glyph_dict: Dict[int, BitImage],
        glyph_background: int = 0,
        byte_order_flag: str = "little"
    ):
        
        _glyph_check_random = chara_glyph_dict[
            random.choice(list(chara_glyph_dict.keys()))
        ]
        assert(
        (
            ((_glyph_check_random.width * _glyph_check_random.height * _glyph_check_random.bit_depth)+7)//8 == \
            self.tile_bytes_size
        ),
            "Appended tile size doesn't match"
        )

        # conflict check
        origin_conversion = self.get_shiftJIS_to_unicode_conversion()
        for chara, _ in chara_glyph_dict.items():
            if chara in origin_conversion:
                raise Exception(f"Seems 0x{chara:x} already exists in original NFTR")
            else:
                continue

        # character glyph chunk
        chara_glyph_dict_sorted = dict(
            sorted(
                chara_glyph_dict.items(), 
                key=lambda item: item[0]
            )
        )

        chara_tile_num_dict_sorted = { }
        last_tile_number = len(self.chara_glyphs) - 1
        for chara, glyph in chara_glyph_dict_sorted.items():
            self.chara_glyphs.append(glyph)
            chara_tile_num_dict_sorted[chara] = last_tile_number + 1
            last_tile_number += 1

        c_map = CMAP.create_type_2_cmap(chara_tile_num_dict_sorted, byte_order_flag)
        self.chara_maps.append(c_map)

        # character glyph chunk has padding or doesn't
        CGLP_CHUNK_HEADER_SIZE = 16 
        new_chara_glyph_chunk_size_without_padding = \
            self.tile_bytes_size * len(self.chara_glyphs) + CGLP_CHUNK_HEADER_SIZE
        # padding to 4
        new_chara_glyph_chunk_size = (new_chara_glyph_chunk_size_without_padding + 3) // 4 * 4
        self.chara_glyph_chunk_size = new_chara_glyph_chunk_size

        # Character width chunk
        CWDH_CHUNK_HEADER_SIZE = 16
        self.chara_width_num_last_tile = len(self.chara_glyphs) - 1
        for glyph in list(chara_glyph_dict_sorted.values()):
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
                                
        for idx in range(len(self.chara_maps) - 1):
            decomp_res_size += self.chara_maps[idx].chunk_size
            self.chara_maps[idx].offset_to_next_map_p8 = decomp_res_size + 8

        self.chara_maps[-1].offset_to_next_map_p8 = 0
    
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
                    print(f"{unicode_string} seems to contain more than one characters, skipped")
                    
            except UnicodeDecodeError:
                # Happens if the integer(s) do not form a valid Shift JIS sequence
                print(f"0x{sjis_codepoint:x} seems unable to be converted UTF-8 code point, replaced with a \"△\" (0x25b3)")
                conversion[sjis_codepoint] = ord("△")

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
                    self.int_to_bytes(0, 1) + \
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