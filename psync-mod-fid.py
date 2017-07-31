import MySQLdb
from psync_func import dict2insert,debuglog
from base64 import b64encode,b64decode
#for mission == 'import':
#find fid with fhash file
#if fid is set ,then read file info from db with fid
#if fid is not set, find fid with fhash , if fhash is not found, then insert new file, set new fid. 
# obj['fid'] --------the fid

def file_sql2obj(rs):
	return {'fid':rs['fid'],
		'fhash':rs['fhash'],
		'ftype':rs['ftype'],
		'ctime':rs['ctime'],
		'filename':b64decode(rs['filename']),
		'filetime':rs['filetime']}

def file_obj2sql_insert(obj):
	return {'fhash':obj['fhash'],
		'ftype':obj['ftype'],
		'filename':b64encode(obj['filename']),
		'filetime':obj['filetime']}

def new_fid(obj,Config):
	if not obj.has_key('fhash'):
		debuglog('Warning: fhash not set')
		raise UserWarning,'fhash not set'
		return obj
	else:
		sql = "select * from `file` where `fhash`= '%s'"%obj['fhash']
		debuglog(sql)
		cur.execute(sql)
		rss = cur.fetchall() 
		if len(rss) > 0:
			debuglog('fhash found')
			obj.update(file_sql2obj(rss[0]))
			return obj
		else:
			debuglog('fhash not found')
			temp = file_obj2sql_insert(obj)
			sql = dict2insert('file',temp) %tuple(temp.values())
			debuglog(sql)
			cur.execute(sql)
			db.commit()
			obj['fid'] = int(cur.lastrowid)
			return obj

def old_fid(obj,Config):
	sql = "select * from `file` where `fid`= '%d'"%obj['fid']
	debuglog(sql)
	cur.execute(sql)
	rss = cur.fetchall() 
	if len(rss) > 0:
		debuglog('fid found')
		obj.update(file_sql2obj(rss[0]))
		return obj
	else:
		debuglog('fid not found')
		raise UserWarning('fid %d not found'%obj['fid'])
		return obj

def do(obj,Config):
	mission = obj['mission']
	if mission == 'import':
		if not obj.has_key('fid'):
			return new_fid(obj,Config)
		else:
			return old_fid(obj,Config)
