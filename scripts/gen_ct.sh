#/usr/bin/bash

tinke_ct=$1
while read line
do
	char=$(echo $line | awk -F\" '{print $2}')
	sjis_hex=$(echo $line | awk -F\" '{print $4}')
	utf_hex=$(printf "%X" \"$char\")

	echo "0x$sjis_hex 0x$utf_hex"
done < $tinke_ct
	
