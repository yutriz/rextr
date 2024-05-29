#!/usr/bin/bash
# gen_ct_utf.sh nodupl(1 char/line)

# noduplicate
nd=$1

i=0;
while read line; 
do 
    char=$(echo $line); 
    utf_hex=$(printf '%X' \"$char\"); 
    printf "$utf_hex=$char\n";
done < $nd