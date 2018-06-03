rm -f $2
avconv -i $1 -s:v qvga -c:v libx264 -crf 28 -c:a aac -b:a 128k -preset fast -strict experimental $2
