#!/usr/bin/bash

# generate a code table representing NON-UTF CODEPOINT and UTF CODEPOINT from tinke-genarated code table(in xml) 

# input:
#   <CharInfo Char="七" Code="8eb5" Index="123" Width="12" />
# output:
#	 0x8eb5=0x4E03 (8eb5 in sjis, 4e03 in utf)

# note:  first line is skipped 

tinke_ct=$1
while read line
do
	char=$(echo $line | awk -F\" '{print $2}')
	sjis_hex=$(echo $line | awk -F\" '{print $4}')
	utf_hex=$(printf "%X" \"$char\")

	echo "0x$sjis_hex 0x$utf_hex"
done < $tinke_ct
	
