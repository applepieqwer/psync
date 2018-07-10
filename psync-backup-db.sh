DATE=$(date -I)
SQL_NAME="psync-$DATE.sql"
rm -f "$SQL_NAME.bz2"
mysqldump -upsync -p -hpsync.db.6677333.hostedresource.com psync > $SQL_NAME
bzip2 $SQL_NAME
ln -f "$SQL_NAME.bz2" psync.sql.bz2
