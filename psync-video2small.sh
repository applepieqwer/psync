rm -f $2
avconv -i $1 -s:v qvga -c:v libx264 -crf 28 -c:a aac -b:a 128k -preset ultrafast -strict experimental $2