rm -f $2
ffmpeg -i $1 -s:v qvga -c:v libx264 -crf 28 -c:a aac -b:a 12k -preset ultrafast -strict experimental $2
