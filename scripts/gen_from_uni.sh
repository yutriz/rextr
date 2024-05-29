#!/usr/bin/bash
# with gen_ct_rv
# generate a unicode.org style .TXT file from .TBL file

printf "# unicode.org style .TXT from $1\n"

while read line
do
	xx_hex=$(echo $line | awk -F\= '{print $1}')
	char=$(echo $line | awk -F\= '{print $2}')
    utf_hex=$(printf "%X" \"$char\")
    printf "0x$utf_hex 0x$xx_hex\n"
done < $1
