# Tools for ROM Text Extraction and Repacking

## Make:
```
mkdir build && cd build
cmake ../ && make
```
## Usage: 

There are three principle types of pointers used in locating data: 
> 1. Standard. Start counting from the start of the file. Sometimes known as linear pointers although the term does technically encompass the second type.
> 2. Offset. Start counting from some point in the file (quite often the start of the proper data/end of the header).
> 3. Relative. Start counting from where the actual pointer is at (if the pointer reads 30h and is located at 20h the data in question is likely at 50h). 
> 
> --GBA and DS ROM hacking guide - 2016 edition

*This tool is used for type of offset pointer only for now*

To generate a json file which consists of recognized texts in Shift-JIS

```
quickextr -i extracted_file 
```

Here are some samples of generated json files https://github.com/yutriz/SN1_SCNs

*Then translate the text in json file*

to insert translated texts(in UTF-8) into the original file

```
quickrepack -i corresponding_json_file -r original_rawfile
```

Note: This should work well with english translation since all alphabetic letters and most of the punctions can be represented in ASCII which is supported by game itself. However, with non-english translation, a mapping from the original japanese encoding to encoding of your language is required to prevent potential crash(I dont quite understand it though and I'm not familiar with disassbmbly). Also, to correctly display translated text, a font of supported format such as NFTR where all charecters in translated text are included is required to replace original font.

Thus to specify an encoding used to repack:  

```
quickrepack_enc -r oringinal_rawfile -i corresponding_json_file -c your_cjk_character_conversion_table(in unicode.org style)
```

use --help option to check more 

## Todo
1. auto non-english encoding coversion
2. supports of other types of pointer

## WORKING