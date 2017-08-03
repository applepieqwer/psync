import MySQLdb
from psync_func import dict2insert,debuglog,move_file,rm_file

def sql_replace_did(fid,did):
	sql = "REPLACE INTO `file_distribute` (`fid`,`did`) VALUES (%s,%s)"%(fid,did)
	debuglog(sql)
	cur.execute(sql)
	db.commit()

def sql_replace_did(fid,did):
	sql = "DELETE FROM `file_distribute` WHERE `file_distribute`.`fid` = %s AND `file_distribute`.`did` = %s LIMIT 1"%(fid,did)
	debuglog(sql)
	cur.execute(sql)
	db.commit()

def update_did(obj,Config):
	if not obj.has_key('did'):
		debuglog('Warning: did not set')
		raise UserWarning,'did not set'
		return obj
	if not obj.has_key('fid'):
		debuglog('Warning: fid not set')
		raise UserWarning,'fid not set'
		return obj
	did = Config.read('did')
	if did not in obj['did']:
		sql_replace_did(obj['fid'],did)
	else:
		sql_delete_did(obj['fid'],did)
	return obj

def read_did(obj,Config):
	if not obj.has_key('fid'):
		debuglog('Warning: fid not set')
		raise UserWarning,'fid not set'
		return obj
	else:
		sql = "SELECT `did` FROM `file_distribute` WHERE `fid` = %s"%obj['fid']
		debuglog(sql)
		cur.execute(sql)
		rss = cur.fetchall()
		obj['did'] = []
		for rs in rss:
			obj['did'].append(rs['did'])
		return obj

def import_did(obj,Config):
	if not obj.has_key('did'):
		debuglog('Warning: did not set')
		raise UserWarning,'did not set'
		return obj
	else:
		if Config.read('did') not in obj['did']:
			obj = move_file(obj,Config)
			obj['did'].append(Config.read('did'))
			obj = update_did(obj,Config)
		else:
			obj = rm_file(obj,Config)
		return obj

def check_did(obj,Config):
	if not obj.has_key('did'):
		return read_did(obj,Config)
	else:
		if obj.has_key('fhashcheck') and obj['fhashcheck'] == False:
			did = Config.read('did')
			if did in obj['did']:
				debuglog('fhash check is False, remove did %s'%did)
				obj['did'].remove(did)
				return update_did(obj,Config)
			else:
				return obj

def do(obj,Config):
	mission = obj['mission']
	if mission == 'import':
		obj = read_did(obj,Config)
		return import_did(obj,Config)
	if mission == 'lazycheck':
		return check_did(obj,Config)

