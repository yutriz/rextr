import os 
import re
import json
import argparse
import ndspy.lz10
import numpy as np
from typing import Union, List, Optional, Dict
from collections import defaultdict
from pathlib import Path

from font import NFTR, CharFont, BitImage
from font.bits_utils import bit_depth_descale

def _call_ndstool_unpack(rom_filepath: Union[Path, str]):
    NDSTOOL_BIN_PATH = "./dependencies/ndstool/ndstool"
    OUTPUT_DIR = "./res/roms"

    if isinstance(rom_filepath, str):
        rom_filepath = Path(rom_filepath)

    rom_name = rom_filepath.stem

    output_dir_ = Path(
        os.path.join(
            OUTPUT_DIR, rom_name
        )
    )
    output_dir_.mkdir(parents=True, exist_ok=True)

    cmd = [
        NDSTOOL_BIN_PATH, 
        "-x", rom_filepath,
        "-9", os.path.join(output_dir_, "arm9.bin"),
        "-7", os.path.join(output_dir_, "arm7.bin"),
        "-y9", os.path.join(output_dir_, "y9.bin"),
        "-y7", os.path.join(output_dir_, "y7.bin"),
        "-d", os.path.join(output_dir_, "data"),
        "-y", os.path.join(output_dir_, "overlay"),
        "-t", os.path.join(output_dir_, "banner.bin"),
        "-h", os.path.join(output_dir_, "header.bin"),
    ]

    cmd = [re.escape(str(k)) for k in cmd]

    os.system(" ".join(cmd))
    print(f"Rom extracted to {str(output_dir_)}")

def _call_ndstool_repack(
    unpacked_root_dir: Union[Path,str],
    output_filepath: Union[Path, str]
):
    NDSTOOL_BIN_PATH = "./dependencies/ndstool/ndstool"
    OUTPUT_DIR = "./res/roms"

    if isinstance(output_filepath, str):
        output_filepath = Path(output_filepath)

    output_filepath.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        NDSTOOL_BIN_PATH, 
        "-c", output_filepath,
        "-9", os.path.join(unpacked_root_dir, "arm9.bin"),
        "-7", os.path.join(unpacked_root_dir, "arm7.bin"),
        "-y9", os.path.join(unpacked_root_dir, "y9.bin"),
        "-y7", os.path.join(unpacked_root_dir, "y7.bin"),
        "-d", os.path.join(unpacked_root_dir, "data"),
        "-y", os.path.join(unpacked_root_dir, "overlay"),
        "-t", os.path.join(unpacked_root_dir, "banner.bin"),
        "-h", os.path.join(unpacked_root_dir, "header.bin"),
    ]

    cmd = [re.escape(str(k)) for k in cmd]

    os.system(" ".join(cmd))
    print(f"Rom repacked to {str(output_filepath)}")

def get_character_conversion_table(
    nftr_filepath: str,
    output_filepath: str = ""
):
    nftr_ = NFTR(nftr_filepath)

    if args.output == "": 
        # output 
        _p = Path(nftr_filepath)
        output_filepath = str(_p.stem) + "_conv_table.txt"
        output_filepath = _p.parent / output_filepath
    else: 
        output_filepath = args.output
    
    nftr_.get_shiftJIS_to_unicode_conversion(output_filepath)

def _call_rextr_with_args(
    args: Union[List[str], str]
):
    REXTR_BIN_PATH = "./build/rextr"
    args_ = args
    if isinstance(args, List):
        args_ = " ".join(args)

    os.system(
        REXTR_BIN_PATH + " " + args_
    )

def extract_scenes(
    scn_filepaths: List[str],
    conversion_filepath: Optional[str] = None
):
    for scn_path in scn_filepaths:
        if scn_path.endswith(".dec"):
            continue

        decompressed = ndspy.lz10.decompressFromFile(scn_path)
        with open(scn_path, "wb") as f:
            f.write(decompressed)

    args = [
        "-e", "--cjk_only", *scn_filepaths
    ]
    
    if conversion_filepath is not None:
        args = ["-c", conversion_filepath] + args

    args = [re.escape(str(k)) for k in args]

    _call_rextr_with_args(args=args)

def _get_translated_characters(recog_json_filepaths: List[str]) -> Dict[str, int]:
    chara_map = defaultdict(int)

    TRANSLATED_KEY = "recogn_text"
    # TRANSLATED_KEY = "translated_text"
        
    for filepath in recog_json_filepaths:
        with open(filepath, "r") as f:
            data = json.load(f)

        blocks = data["blocks"]
        blocks = [ blk for blk in blocks 
                    if blk["recognized"] 
                    # and blk["translated"] 
                ]
        for blk in blocks:
            tled: str = blk[TRANSLATED_KEY]

            for chara in tled:
                chara_map[chara] = chara_map[chara] + 1
    
    return chara_map

def get_appended_nftr(
    recog_json_filepaths,
    nftr_font_filepath,
    ttf_font_filepath
):

    used_characters = list(_get_translated_characters(recog_json_filepaths).keys())
    print(used_characters)

    nftr_ = NFTR(nftr_font_filepath)
    original_conv = nftr_.get_shiftJIS_to_unicode_conversion()
    original_characters = list(original_conv.keys()) # sjis to unicode
    original_characters.sort()

    vacant_codepoints = []
    for idx in range(len(original_characters) - 1):
        this_character = original_characters[idx]
        if this_character < 0xff:
            continue
        
        next_character = original_characters[idx+1]

        is_adjacent = (this_character+1 == next_character)
        if not is_adjacent:
            vacant_codepoints += list(range(this_character+1, next_character))
        else:
            pass

        if len(vacant_codepoints) > len(used_characters):
            break
    
    if (nftr_.tile_width != nftr_.tile_height):
        print(f"{nftr_font_filepath} seems to have different tile width and height, using tile_width {nftr_.tile_width}")
    font_size = nftr_.tile_width
    
    ttf_font = CharFont(
        ttf_font_filepath, 
        size=font_size
    )

    new_mapping = {}
    appended_conv = {} # unicode to appended vacant codepoint 

    reversed_original_conv = {} # unicode to sjis
    for origin_codepoint, unicode_codepoint in original_conv.items():
        reversed_original_conv[unicode_codepoint] = origin_codepoint

    for idx, chara in enumerate(used_characters):
        # existing in original_conv 
        chara_ord = ord(chara)
        if chara_ord in list(reversed_original_conv.keys()):
            appended_conv[chara_ord] = reversed_original_conv[chara_ord]
            print(f"existing one: {chara}")
        # not existing, add to chara_glyphs
        else:
            appended_conv[chara_ord] = vacant_codepoints[idx]
            # in PIL.Image
            chara_image = ttf_font.character_image(
                chara,
                backgroud_color="black",
                top_left_pos=(0, -1),
                mode='L',
                charecter_shadow=True
            )
            chara_image_data = np.array(chara_image)

            # performance issue?
            for r in range(chara_image_data.shape[0]):
                for c in range(chara_image_data.shape[1]):
                    chara_image_data[r][c] = bit_depth_descale(chara_image_data[r][c], 8, 2)

            chara_bit_image = BitImage(
                chara_image_data,
                width=chara_image_data.shape[1],
                height=chara_image_data.shape[0],
                bit_depth=2
            )

            new_mapping[vacant_codepoints[idx]] = chara_bit_image

    nftr_.append_type_2_cmap(
        new_mapping,
        glyph_background=0
    )
    
    return (
        nftr_,
        appended_conv
    )

def _rewrite_scenes(
    raw_filepaths: List[str],
    appended_conv_filepath: str,
):
    args = [
        "-r", 
        "-c", appended_conv_filepath,
        "raws", *raw_filepaths
    ]

    args = [re.escape(str(k)) for k in args]

    _call_rextr_with_args(args)

def repack_rom(
    scn_filepaths: List[str],
    appended_conv_filepath: str,
    unpacked_root_dir: str,
    output_filepath: str,
):
    _rewrite_scenes(
        scn_filepaths,
        appended_conv_filepath
    )

    # compress
    for scn_path in scn_filepaths:
        compressed = ndspy.lz10.compressFromFile(scn_path)
        with open(scn_path, "wb") as f:
            f.write(compressed)

    _call_ndstool_repack(
        unpacked_root_dir,
        output_filepath
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("positional_args", type=str, nargs="*")
    parser.add_argument("-o", "--output", type=str, default="", help="output filepath for ANY")

    parser.add_argument("--unpack", action="store_true", help="unpack a .nds rom")
    parser.add_argument("--get_character_conv", action="store_true", 
                        help="dump shiftJIS to Unicode conversion in nftr font file")
    parser.add_argument("--extract_scns", action="store_true", help="extracted recognized characters in file")
    parser.add_argument("--repack", action="store_true", help="repack translated rom")

    parser.add_argument("--ttf_file", type=str, default="")
    parser.add_argument("--nftr_file", type=str, default="")
    parser.add_argument("--unpacked_root_dir", type=str, default="")
    parser.add_argument("-c", "--conv", type=str, nargs="?", default=None,
                        help="conversion.txt filepath")

    args = parser.parse_args()

    positional_args = args.positional_args
    
    if args.unpack:
        assert(len(positional_args) == 1)
        _call_ndstool_unpack(positional_args[0])
    elif args.get_character_conv:
        assert(len(positional_args) == 1)
        output_filepath = args.output
        get_character_conversion_table(
            positional_args[0],
            output_filepath
        )
    elif args.extract_scns:
        extract_scenes(
            positional_args,
            args.conv
        )
    elif args.repack:
        # try find scn_file-corresponding translated.json 
        raw_scn_filepaths = positional_args.copy()

        def getCorrespongdingJsonFilepath(scn_filepath):
            p = Path(scn_filepath)
            return p.parent / (p.stem + ".recog.json")

        json_filepaths = [
            str(
                getCorrespongdingJsonFilepath(scn_filepath)
            )
            for scn_filepath in raw_scn_filepaths
        ]

        nftr_, appended_conv = get_appended_nftr(
            json_filepaths,
            args.nftr_file,
            args.ttf_file
        )

        tmp_conv_filepath = "./.tmp/appened_conv.txt"
        tmp_conv_filepath = Path(tmp_conv_filepath)
        tmp_conv_filepath.parent.mkdir(exist_ok=True, parents=True)
        with open(tmp_conv_filepath, 'w') as f:
            f.write("# unicode to custom codepoint\n")
            for unicode_codepoint, custom_codepoint in appended_conv.items():
                f.write(f"0x{unicode_codepoint:x}    0x{custom_codepoint:x}\n")
    
        with open("./.tmp/appended.NFTR", "wb") as f:
            f.write(nftr_.dump())

        # overwrite original NFTR file 
        # with open(args.nftr_file, "wb") as f:
        #     f.write(nftr_.dump())

        repack_rom(
            raw_scn_filepaths,
            tmp_conv_filepath,
            args.unpacked_root_dir,
            args.output
        )