import MySQLdb
from psync_func import dict2insert,debuglog,move_file

def sql_replace_did(fid,did):
	sql = "REPLACE INTO `file_distribute` (`fid`,`did`) VALUES (%s,%s)"%(fid,did)
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
	sql_replace_did(obj['fid'],Config.read('did'))
	obj['did'].append(Config.read('did'))
	return obj

def new_did(obj,Config):
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
		return old_did(obj,Config)

def old_did(obj,Config):
	if not obj.has_key('did'):
		debuglog('Warning: did not set')
		raise UserWarning,'did not set'
		return obj
	else:
		if Config.read('did') not in obj['did']:
			obj = move_file(obj,Config)
			obj = update_did(obj,Config)
		return obj

def do(obj,Config):
	mission = obj['mission']
	if mission == 'import':
		if not obj.has_key('did'):
			return new_did(obj,Config)
		else:
			return old_did(obj,Config)
