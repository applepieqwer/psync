#!/bin/bash
#######
#$1 is output dict
#$2 is file
#$2 filename is the pass key
#######
rm -f $1/$2.7z
rm -f $1/$2.7z.*
key=`basename $2`
7z a -aoa -p$key -v100m -mx0 $1/$2.7z $2
