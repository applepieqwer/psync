rm -f $2
ffmpeg -i $1 -s:v hd480 -c:v libx264 -crf 28 -c:a aac -b:a 128k -preset ultrafast -strict experimental $2
