DATE=$(date -I)
SQL_NAME="psync-$DATE.sql"
rm -f "$SQL_NAME.bz2"
mysqldump -upsync -p123456 -h192.168.1.1 psync > $SQL_NAME
bzip2 $SQL_NAME
ln -f "$SQL_NAME.bz2" psync.sql.bz2
