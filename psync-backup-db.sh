DATE=$(date -I)
SQL_NAME="psync-$DATE.sql"
rm -f "$SQL_NAME.bz2"
mysqldump -v --compress -upsync -p -h p3plcpnl1112.prod.phx3.secureserver.net psync > $SQL_NAME
bzip2 $SQL_NAME
ln -f "$SQL_NAME.bz2" psync.sql.bz2
