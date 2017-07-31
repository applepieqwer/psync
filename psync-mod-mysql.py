import MySQLdb
from base64 import b64encode,b64decode

#make the local obj sync with database
#if obj['fid'] not found and obj['fhash'] found then insert new or replace
#if obj['fid'] found and obj['fhash'] not found then select 
#if obj['fid'] found and obj['fhash'] found then check obj['mission'] for next step
#if obj['fid'] not found and obj['fhash'] not find then die
#
# obj['fid'] ------------file id in db

def __init__db(obj,Config):
	conn=MySQLdb.connect(host=Config.read('mysql_host'),user=Config.read('mysql_user'),passwd=Config.read('mysql_passwd'),db=Config.read('mysql_db'))
	cur=conn.cursor()
	return conn,cur

def select_with_fid(obj,Config):
	conn,cur = __init__db(obj,Config)
	sql = "select * from `file` where `fid`=%s"
	row_count = cur.execute(sql,obj['fid'])
	if row_count > 0:
		result=cur.fetchone()
		obj['fid'] = str(result[0])
		obj['fhash'] = str(result[1])
		obj['ftype'] = str(result[2])
		obj['ctime'] = str(result[3])
		obj['filename'] = b64decode(result[4])
		obj['filetime'] = result[5]
	else:
		#fid not found in db, return False
		return False
	return obj



def insert_with_fhash(obj,Config):
	print 'fhash:',obj['fhash']
	conn,cur = __init__db(obj,Config)
	sql = "select * from `file` where `fhash`='%s'"%obj['fhash']
	row_count = cur.execute(sql)
	if row_count > 0:
		result=cur.fetchone()
		obj['fid'] = str(result[0])
		obj['fhash'] = str(result[1])
		obj['ftype'] = str(result[2])
		obj['ctime'] = str(result[3])
		obj['filename'] = b64decode(result[4])
		obj['filetime'] = result[5]
	else:
		sql = "INSERT INTO `file` (`fhash`,`ftype`,`filename`,`filetime`) VALUES (%s,%s,%s,%s)"
		cur.execute(sql,(obj['fhash'],obj['ftype'],b64encode(obj['filename']),obj['filetime']))
		obj['fid'] = str(cur.lastrowid)
	conn.commit()
	cur.close()
	conn.close()
	return obj


def do(obj,Config):
	if not obj.has_key('fid') and not obj.has_key('fhash'):
		raise UserWarning,'fid and fhash not found'
		return False
	if obj.has_key('fid') and not obj.has_key('fhash'):	
		obj = select_with_fid(obj,Config)
		if obj == False:
			raise UserWarning,'fid not found in db'
			return False
	if not obj.has_key('fid') and obj.has_key('fhash'):
		obj = insert_with_fhash(obj,Config)
	if obj.has_key('fid') and obj.has_key('fhash'):
		if obj['mission'] == 'import':
			#let go and move the file
			obj['todo'] = 'debug'
		else:
			obj['todo'] = 'debug'
	return obj
	
