from psync_func import dict2insert,debuglog,file_sql2obj,file_obj2sql_insert
from time import sleep
from random import randint

#for mission == 'import':
#find fid with fhash file
#if fid is set ,then read file info from db with fid
#if fid is not set, find fid with fhash , if fhash is not found, then insert new file, set new fid. 
# obj['fid'] --------the fid


def new_fid(obj,Config):
	if not obj.has_key('fhash'):
		debuglog('Warning: fhash not set')
		raise UserWarning,'fhash not set'
		return obj
	else:
		sql = "select * from `file` where `fhash`= '%s'"%obj['fhash']
		rss = db.fetchall(sql) 
		if len(rss) > 0:
			debuglog('fhash found')
			obj.update(file_sql2obj(rss[0]))
			return obj
		else:
			debuglog('fhash not found')
			temp = file_obj2sql_insert(obj)
			sql = dict2insert('file',temp) %tuple(temp.values())
			db.execute(sql)
			obj['fid'] = int(db.lastrowid())
			return obj

def old_fid(obj,Config):
	sql = "select * from `file` where `fid`= '%d'"%obj['fid']
	rss = db.fetchall(sql) 
	if len(rss) > 0:
		debuglog('fid found')
		obj.update(file_sql2obj(rss[0]))
		return obj
	else:
		debuglog('fid not found')
		raise UserWarning('fid %d not found'%obj['fid'])
		return obj

def rand_fid(obj,Config):
	#sleep rand time for sql server cool down
	sleep(randint(0,5))
	sql = "SELECT `fid` from `file_distribute` WHERE `did`='%d' ORDER BY `dtime` LIMIT %d,1"%(Config.read('did'),randint(0,9)) 
	rss = db.fetchall(sql) 
	if len(rss) > 0:
		debuglog('rand fid found')
		obj['fid'] = rss[0]['fid']
		return old_fid(obj,Config)
	else:
		debuglog('rand fid not found')
		raise UserWarning('fid not found')
		return obj

def rand_convert_fid(obj,Config):
	#sleep rand time for sql server cool down
	sleep(randint(0,5))
	sql = "SELECT `file`.`fid` as `fid` FROM `file` left join  `file_converter` on (`file`.`fid` = `file_converter`.`fid`) right join `file_distribute` on (`file`.`fid` = `file_distribute`.`fid`) where `file_distribute`.`did`='%d' and `file_converter`.`did` is null LIMIT %d,1"%(Config.read('did'),randint(0,9)) 
	rss = db.fetchall(sql) 
	if len(rss) > 0:
		debuglog('rand fid found')
		obj['fid'] = rss[0]['fid']
		return old_fid(obj,Config)
	else:
		debuglog('rand convert fid not found, use rand fid')
		return rand_fid(obj,Config)

def rand_convert_fid_2(obj,Config):
	return obj
	#SELECT `fid`,count(`cid`) as `cid_count` FROM `file_converter` join `file` using (`fid`)  where `ftype` = 'image/jpeg'  group by `fid` having `cid_count` < 3  order by `fid` 
	

def do(obj,Config):
	mission = obj['mission']
	if mission in ['import']:
		if not obj.has_key('fid'):
			return new_fid(obj,Config)
		else:
			return old_fid(obj,Config)
	if mission in ['lazytag','lazycheck','lazygps']:
		if not obj.has_key('fid'):
			return rand_fid(obj,Config)
		else:
			return old_fid(obj,Config)
	if mission in ['convert']:
		if not obj.has_key('fid'):
			return rand_convert_fid(obj,Config)
		else:
			return old_fid(obj,Config)
