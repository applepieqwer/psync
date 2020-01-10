from psync_func import obj2dst,obj2convert,convert2path,debuglog,obj_is_video
import os

#convert file
#check cid , run convert cmd and update cid
# obj['cid'] 

def do_convert(cmd,obj,Config,d):
	s = obj2dst(obj,Config)
	cmd = cmd.replace('{SRC}',s).replace('{TARGET}',d)
	debuglog(cmd)
	if obj_is_video(obj,Config):
		halt_db(Config)
		r = os.system(cmd)
		init_db(Config)
		return r
	else:
		return os.system(cmd)


def read_cid(obj,Config):
	if not obj.has_key('fid'):
		debuglog('Warning: fid not set')
		raise UserWarning,'fid not set'
		return obj
	did = Config.read('did')
	if did not in obj['did']:
		debuglog('Warning: did not set')
		raise UserWarning,'did not set'
		return obj
	else:
		sql = "SELECT `cid` FROM `file_converter` WHERE `fid` = %s and `did` = %s "%(obj['fid'],Config.read('did'))
		rss = db.fetchall(sql)
		obj['cid'] = []
		for rs in rss:
			obj['cid'].append(rs['cid'])
		return obj

def update_cid(obj,Config):
	if not obj.has_key('cid'):
		debuglog('Warning: cid not set, run read_cid first')
		raise UserWarning,'cid not set'
		return obj
	else:
		did = Config.read('did')
		for cid in obj['cid']:
			sql = "SELECT `ctarget` FROM `converter` WHERE `cid` = %d "%cid
			ctarget = db.fetchone(sql)['ctarget']
			sql = "REPLACE INTO `file_converter` (`fid`,`cid`,`did`,`result`) VALUES (%s,%s,%s,'%s')"%(obj['fid'],cid,did,convert2path(obj['fhash'],cid,ctarget))
			db.execute(sql)
		return obj

def check_cid(obj,Config):
	if not obj.has_key('cid'):
		debuglog('Warning: cid not set, run read_cid first')
		raise UserWarning,'cid not set'
		return obj
	else:
		sql = "SELECT `cid`,`cvalue`,`ctarget` FROM `converter` WHERE `ctype` = '%s' "%obj['ftype']
		rss = db.fetchall(sql)
		for rs in rss:
			cid = rs['cid']
			ctarget = rs['ctarget']
			convert_target = obj2convert(obj,Config,cid,ctarget)
			if cid in obj['cid']:
				if not os.path.isfile(convert_target):
					cmd = do_convert(rs['cvalue'],obj,Config,convert_target)
			else:
				cmd = do_convert(rs['cvalue'],obj,Config,convert_target)
				obj['cid'].append(cid)
		return obj

def do(obj,Config):
	mission = obj['mission']
	if mission in ['convert']:
		obj = read_cid(obj,Config)
		obj = check_cid(obj,Config)
		return update_cid(obj,Config)
	return obj
