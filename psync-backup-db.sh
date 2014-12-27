DATE=$(date -I)
SQL_NAME="psync-$DATE.sql"
mysqldump -upsync -p123456 -h192.168.1.1 psync > $SQL_NAME
bzip2 $SQL_NAME
