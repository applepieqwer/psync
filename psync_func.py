import MySQLdb
from os import getpid,remove,lstat
import os
import exifread as exifreader
import __builtin__
from hashlib import sha1

#from shutil import copy2 as shutil_move
from shutil import move as shutil_move

def do_sha1(s):
	debuglog('hashing...')
	if not os.path.isfile(s):
		return ''
	read_size = 1024
	sha1Obj = sha1()
	with open(s,'rb') as f:
		data = f.read(read_size)
		while data:
			sha1Obj.update(data)
			data = f.read(read_size)
		return sha1Obj.hexdigest()

def readEXIFwidth(obj,Config):
	return readEXIF(obj,Config,'EXIF ExifImageWidth')

def readEXIFheight(obj,Config):
	return readEXIF(obj,Config,'EXIF ExifImageLength')

def readEXIForientation(obj,Config):
	return readEXIF(obj,Config,'Image Orientation')

def readEXIFmodel(obj,Config):
	return readEXIF(obj,Config,'Image Model')

def readEXIFdate(obj,Config):
	return readEXIF(obj,Config,'EXIF DateTimeOriginal')

def readEXIF(obj,Config,tag):
	dst = obj2dst(obj,Config)
	f = open(dst,'rb')
	tags = exifreader.process_file(f, stop_tag=tag)
	f.close()
	if tag in tags.keys():
		return tags[tag]
	else:
		debuglog(u'EXIF: \'%s\' not found in %s'%(tag,obj['fhash']))
		return False

def obj_is_video(obj,Config):
	return (obj['ftype'][:5] == 'video')

def obj_is_here(obj,Config):
	if 'did' in obj.keys():
		did = Config.read('did')
		if not did in obj['did']:
			debuglog('obj_is_here: obj[\'did\'] is NOT loaded')
			return False
	if os.path.isfile(obj2dst(obj,Config)):
		return True
	debuglog('obj_is_here: obj is NOT here')
	return False

def hash2path(h):
	return u'%s/%s' % (h[0], h)

def convert2path(h,cid,ctarget=u'{DST}'):
	d = u'convert/%s.%d' % (hash2path(h),cid)
	return ctarget.replace('{DST}',d)

def obj2dst(obj,Config):
	return u'%s/%s' % (Config.read('data_root'),hash2path(obj['fhash']))

def obj2convert(obj,Config,cid,ctarget=u'{DST}'):
	return u'%s/%s' % (Config.read('data_root'),convert2path(obj['fhash'],cid,ctarget))

def size_file(obj,Config):
	(mode, ino, dev, nlink, uid, gid, fsize, atime, mtime, ctime) = lstat(obj2dst(obj,Config))
	return fsize

def dict2insert(table,d):
	placeholders = ', '.join(['\'%s\''] * len(d))
	columns = ', '.join(['`%s`'] * len(d)) % tuple(d.keys())
	return "INSERT INTO `%s` ( %s ) VALUES ( %s )" % (table, columns, placeholders)

def move_file(obj,Config):
	dst = obj2dst(obj,Config)
	debuglog(u'moving %s \n=====> %s'%(obj['src'],dst))
	shutil_move(obj['src'],dst)
	obj['dst']=dst
	return obj

def rm_file(obj,Config):
	debuglog(u'RM! %s'%obj['src'])
	remove(obj['src'])
	del obj['src']
	return obj

client_id = 0
mod_name = ''
debug_switch = True

def debugset(mn,ds=True):
	global client_id,mod_name,debug_switch
	client_id = str(getpid())
	mod_name = str(mn)
	debug_switch = ds

def debuglog(msg):
	global client_id,mod_name,debug_switch
	if debug_switch:
		print 'debuglog[%s/%s]: %s'%(client_id,mod_name,msg)
	return msg

def init_db(Config):
	#connect the database
	try:
		mysql_host = Config.read('mysql_host')
		debuglog('Database %s connecting.'%mysql_host)
		__builtin__.db = MySQLdb.connect(host=mysql_host,user=Config.read('mysql_user'),passwd=Config.read('mysql_passwd'),db=Config.read('mysql_db'),charset='utf8')
		__builtin__.cur = db.cursor(cursorclass = MySQLdb.cursors.DictCursor) 	
		debuglog('Database %s ready.'%mysql_host)
		#update server stat here
	except MySQLdb.Error,e:
		debuglog("Mysql Init Error ")
		exit(-1)

def halt_db(Config):
	__builtin__.db.close()
