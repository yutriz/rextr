import os 
import json
import argparse
import subprocess
from pathlib import Path
from collections import defaultdict
from typing import Union, List, Optional, Dict


from compress import lzss_compress
from pyutils.logger import Logger

import ndspy.lz10
import numpy as np

from font import NFTR, CharFont, BitImage, get_appended_nftr

NDSTOOL_BIN_PATH = "./dependencies/ndstool/ndstool"
REXTR_BIN_PATH = "./build/rextr"

LESS_LOG = True

FORCE_IGNORE_CHARACTERS = [
    '\n'
]

# get corresponding json file "foo.recog.json" from "foo.rtz"
def getCorrespongdingJsonFilepath(scn_filepath: str | Path):
    p = Path(scn_filepath)
    
    return p.parent / (p.stem + ".recog.json")


def _call_ndstool_unpack(rom_filepath: Union[Path, str]):
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

    cmd = [str(k) for k in cmd]

    result = subprocess.run(
        cmd, 
        capture_output=True, text=True
    )
    Logger.print("Cmd: " + " ".join(cmd))
    Logger.subprocess_print(result)
    Logger.print(f"Rom extracted to {str(output_dir_)}")

def _call_ndstool_repack(
    unpacked_root_dir: Union[Path,str],
    output_filepath: Union[Path, str]
):

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

    cmd = [str(k) for k in cmd]

    result = subprocess.run(
        cmd, 
        capture_output=True, text=True
    )

    Logger.print("Cmd: " + " ".join(cmd))
    Logger.subprocess_print(result)
    Logger.print(f"Rom repacked to {str(output_filepath)}")

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
    args: List[str]
):
    args_ = args

    cmd = [REXTR_BIN_PATH, *args_]
    result = subprocess.run(
        cmd,
        capture_output=True, text=True
    )

    Logger.print("Cmd: " + " ".join(cmd))
    Logger.subprocess_print(result)

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

    args = [str(k) for k in args]

    _call_rextr_with_args(args=args)

def _get_translated_characters(recog_json_filepaths: List[str]) -> Dict[str, int]:
    chara_map = defaultdict(int)

    TRANSLATED_KEY = "translated_text"
        
    for filepath in recog_json_filepaths:
        with open(filepath, "r") as f:
            data = json.load(f)

        blocks = data["blocks"]
        blocks = [ blk for blk in blocks 
                    if blk["recognized"] 
                    and blk["translated"] 
                ]
        for blk in blocks:
            tled: str = blk[TRANSLATED_KEY]

            for chara in tled:
                chara_map[chara] = chara_map[chara] + 1
    
    return chara_map

def _get_appended_nftr(
    recog_json_filepaths,
    nftr_font_filepath,
    ttf_font_filepath
):
    used_characters = list(_get_translated_characters(recog_json_filepaths).keys())
    for c in FORCE_IGNORE_CHARACTERS:
        if c in used_characters:
            used_characters.remove(c)
    
    return get_appended_nftr(
        nftr_font_filepath, used_characters, ttf_font_filepath
    )

def _rewrite_scenes(
    raw_filepaths: List[str],
    appended_conv_filepath: str,
):
    args = [
        "-r", 
        "-c", appended_conv_filepath,
        "--raws", *raw_filepaths
    ]

    args = [str(k) for k in args]
    
    _call_rextr_with_args(args)

def repack_rom(
    scn_filepaths: List[str],
    appended_conv_filepath: str,
    unpacked_root_dir: str,
    output_filepath: str,
    clean_dir: str = None
):
    # decompress if rtz is uncompressed 
    for scn_path in scn_filepaths:
        if scn_path.endswith(".dec"): # decompressed by other tool(tool name?)
            continue

        try:
            decompressed = ndspy.lz10.decompressFromFile(scn_path)
            with open(scn_path, "wb") as f:
                f.write(decompressed)
        except:
            Logger.print(f"{scn_path} is already decompressed, doing nothing")

    _rewrite_scenes(
        scn_filepaths,
        appended_conv_filepath
    )

    # compress: note ndspy.lz10 can decompress but can't compress
    for scn_path in scn_filepaths:
        lzss_compress(scn_path, scn_path)

    # clear recog.json
    if not clean_dir:
        clean_dir: Path = Path(unpacked_root_dir) / "data" / "scnrts"
        for f in clean_dir.rglob("*.recog.json"):
            if f.is_file():
                f.unlink()

    _call_ndstool_repack(
        unpacked_root_dir,
        output_filepath
    )


USAGE_PRINT_INFO = """
    # unpack a .nds file using ndstool
    python %(prog)s --unpack foo.nds

    # extract character conversions from a .nftr file
    python %(prog)s --get_character_conv foo.nftr -o output_conversions.txt

    # extract text from SN NDS scnrtz files
    python %(prog)s --extract_scns -c conversions.txt path_to_scn_foo1.rtz path_to_scn_foo2.rtz 

    # repack a .nds file
    python %(prog)s --repack --unpacked_root_dir ./res/roms/sn1 -o translated.nds
        --ttf_file font.ttf --nftr ./res/roms/sn1/font.nftr
        ./res/roms/sn1/data/scnrts/translated_1.rtz # corresponding to translated_1.recog.json
        ./res/roms/sn1/data/scnrts/translated_2.rtz
        ...
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage=USAGE_PRINT_INFO
    )

    parser.add_argument("files", type=str, nargs="*")
    parser.add_argument("-o", "--output", type=str, default="", help="output filepath for ANY")

    parser.add_argument("--unpack", action="store_true", help="[unpack]unpack a .nds rom")
    parser.add_argument("--get_character_conv", action="store_true", 
                        help="[cp_conv]dump shiftJIS to Unicode conversion in nftr font file")
    parser.add_argument("--extract_scns", action="store_true", help="[extr]extracted recognized characters in file")
    parser.add_argument("--repack", action="store_true", help="repack translated rom")

    parser.add_argument("--ttf_file", type=str, default="", help="[repack]")
    parser.add_argument("--nftr_file", type=str, default="", help="[repack]")
    parser.add_argument("--unpacked_root_dir", type=str, default="", help="[repack]")
    parser.add_argument("-c", "--conv", type=str, nargs="?", default=None,
                        help="[extr]conversion.txt filepath")

    args = parser.parse_args()

    files = args.files

    # TODO: one phrase failed, other files should remain unchanged
    
    if args.unpack:
        assert(len(files) == 1)
        _call_ndstool_unpack(files[0])
    elif args.get_character_conv:
        assert(len(files) == 1)
        output_filepath = args.output
        get_character_conversion_table(
            files[0],
            output_filepath
        )
        print(
            "[NOTICE] Sometimes there might be additional character conversions that are not included in "
            ".nftr files (e.g. new line symbol) and they can be added to character conversion .txt file. "
            "Checking rom manually is recommanded."
        )
    elif args.extract_scns:
        extract_scenes(
            files,
            args.conv
        )
    elif args.repack and not files:
         _call_ndstool_repack(
            args.unpacked_root_dir,
            args.output
        )
    elif args.repack:
        # try find scn_file-corresponding translated.json 
        raw_scn_filepaths = files.copy()

        json_filepaths = [
            str(
                getCorrespongdingJsonFilepath(scn_filepath)
            ) for scn_filepath in raw_scn_filepaths
        ]

        # check json file integrity
        for j_fpath in json_filepaths:
            with open(j_fpath, 'rb') as f:
                data = json.load(f)
                block_data = data["blocks"]
                for blk in block_data:
                    tl: str = blk["translated_text"]
                    if not tl:
                        raise Exception(f"{blk} contains an empty translation text, stopped")  

        nftr_, utf2custom_conv = _get_appended_nftr(
            json_filepaths,
            args.nftr_file,
            args.ttf_file
        )

        tmp_conv_filepath = "./tmp/utf2custom_conv.txt"
        tmp_conv_filepath = Path(tmp_conv_filepath)
        tmp_conv_filepath.parent.mkdir(exist_ok=True, parents=True)
        with open(tmp_conv_filepath, 'w') as f:
            f.write("# unicode to custom codepoint\n")
            for unicode_codepoint, custom_codepoint in utf2custom_conv.items():
                f.write(f"0x{unicode_codepoint:x}    0x{custom_codepoint:x}\n")
    
        with open("./tmp/appended.NFTR", "wb") as f:
            f.write(nftr_.dump())

        # overwrite original NFTR file, make sure you have a backup for original one 
        with open(args.nftr_file, "wb") as f:
            f.write(nftr_.dump())

        repack_rom(
            raw_scn_filepaths,
            tmp_conv_filepath,
            args.unpacked_root_dir,
            args.output
        )
    else:
        print("No command specified. Exit")