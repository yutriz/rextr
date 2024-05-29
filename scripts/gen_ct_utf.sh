#!/usr/bin/bash
# gen_ct_utf.sh nodupl(1 char/line) start_index count

# noduplicate
nd=$1
# start index 
si=$2
#
count=$3

i=0;
printf "#\n"
while read line; 
do 
    if [ $i -lt $count ]
    then
        char=$(echo $line); 
        utf_hex=$(printf '%X' \"$char\"); 
        printf "0x$utf_hex 0x$si\n";
    fi
    si=$(($si+1));
    i=$(($i+1));
    
done < $nd