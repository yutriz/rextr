#!/usr/bin/bash
# generate a unicode.org style .TXT file from .TBL file
# TBL be like CODEPOINT=CHAR, eg 95ca=别 to 0x522B=0x95ca (left utf, right non-utf)

printf "# unicode.org style .TXT from $1\n"

while read line
do
	xx_hex=$(echo $line | awk -F\= '{print $1}')
	char=$(echo $line | awk -F\= '{print $2}')
    utf_hex=$(printf "%X" \"$char\")
    printf "0x$utf_hex 0x$xx_hex\n"
done < $1
