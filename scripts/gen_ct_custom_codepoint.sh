#!/usr/bin/bash
#  remapping characters to custom CodePoint in given 2d ranges
#  ONLY ONE CHARACTER PER LINE ALLOWED 
#  e.g.  
#  give input file like:
#   中
#   文
#   ...
#  given row start at ee, end at f0
#        col start at 40, end at 50
#  output: 
#   ee40=中
#   ee41=文
#   ...
#   ee50=...
#   ef40=...
#   ...


ARGS=`getopt -a -o f:r:t:c:v:h --long file:,rows:,rowe:,cols:,cole:,help -- "$@"`
eval set -- "${ARGS}"

while :
do
    case $1 in
        -f|--file)
            nd=$2
            shift
            ;;
        -r|--rows)
            rs=$(printf "%d" "0x$2")
            shift
            ;;
        -t|--rowe)
            re=$(printf "%d" "0x$2")
            shift
            ;;
        -c|--cols)
            cs=$(printf "%d" "0x$2")
            shift
            ;;
        -v|--cole)
            ce=$(printf "%d" "0x$2")
            shift
            ;;
        -h|--help)
            echo "
#  remapping characters to custom CodePoint in given 2d ranges
#  ONLY ONE CHARACTER PER LINE ALLOWED 
#  e.g.  
#  give input file like:
#   中
#   文
#   ...
#  given row start at ee, end at f0
#        col start at 40, end at 50
#  output: 
#   ee40=中
#   ee41=文
#   ...
#   ee50=...
#   ef40=...
#   ...
            "
            echo "$0 -f file -r row_start -t row_end -c col_start -v col_end"
            exit 1
            ;;
        --)
            break;;
        *) 
            exit 1
            ;;
    esac
shift
done

# all decimal when doing cal 
current_row=$rs
current_col=$cs

while read line; 
do 
    char=$(echo $line); 
    row_hex=$(printf "%X" "$current_row"); 
    col_hex=$(printf "%X" "$current_col"); 
    printf "$row_hex$col_hex=$char\n"

    if [ $current_col -lt $ce ]  
    then 
        current_col=$(($current_col+1))
    else
        current_col=$cs
        # no check 
        current_row=$(($current_row+1))
    fi
done < $nd