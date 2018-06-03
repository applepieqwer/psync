r=`cat /dev/urandom | tr -cd 'a-f0-9' | head -c 32`
d=thumbs/
t=${d}${r}
ffmpeg -i $1 -vf select='isnan(prev_selected_t)+gte(t-prev_selected_t\,6)' -vsync 2 -vframes 10 ${t}-%03d.png
convert -delay 100 -loop 0 -quality 95  -resize '200x200^' -gravity center -extent 200x200  ${t}-*.png $2
rm -f ${t}-*.png
