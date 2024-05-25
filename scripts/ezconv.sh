#!/usr/bin/bash

echo "usage:"
echo "    cp \${char} " 
echo "    char \${codepoint} (without 0x)" 


to_hex() {
    upper=${1^^}
    echo "ibase=16;$upper" | bc
}

cp() {
    printf "0x%2X\n" "\"$1"
}

char() {
    printf "\u$(printf "%x" "0x$1")\n"
}

#char() {
#    echo $1 | xxd -r -p
#}
