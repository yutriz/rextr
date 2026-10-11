# A wrapper for dependencies/Nintendo_DS_Compressors

import enum
import subprocess
from pathlib import Path

from pyutils.logger import Logger

# Note 1: You maybe need to compile it first
# Note 2: already an absolute path
LZSS_EXECUTABLE_FILEPATH = Path(__file__).resolve().parent / "../dependencies/Nintendo_DS_Compressors/lzss"

COMPRESS_FLAGS = ["-evn", "-ewn", "-evf", "-ewf", "-evo", "-ewo"]

DEFAULT_COMPRESS_FLAG = COMPRESS_FLAGS[0]

def _call_lzss_with_args(args: list):
    result = subprocess.run(
        args=[LZSS_EXECUTABLE_FILEPATH, *args],
        capture_output=True, text=True
    )
    Logger.subprocess_print(result)

def lzss_compress(input: str | Path, output: str | Path):
    args = [ 
        DEFAULT_COMPRESS_FLAG, input, output
    ]

    _call_lzss_with_args(args)

def lzss_decompress(input: str | Path, output: str | Path):
    args = [ 
        "-d", input, output
    ]

    _call_lzss_with_args(args)