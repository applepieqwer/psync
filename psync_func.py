import MySQLdb
from collections import deque
from os import getpid,remove,lstat
import os
import exifread as exifreader
import __builtin__
from hashlib import sha1
import json
from time import sleep

try:
	import cPickle as pickle
except:
	import pickle

#from shutil import copy2 as shutil_move
from shutil import move as shutil_move

def saveEncoding(face_data,Config):
	filename = 'face.%d.encodings.pkl'%Config['did']
	if not os.path.isfile(filename):
		buf = {}
	else:
		readfile = open(filename, 'rb')
		buf = pickle.load(readfile)
		readfile.close()
	buf.update(face_data)
	writefile = open(filename, 'wb')
	pickle.dump(buf,writefile,-1)
	writefile.close()

class ConfigClass(dict):
	def read(self,key):
		return self.get(key)

class ListClass(deque):
	def length(self):
		return len(self)
	def __str__(self):
		return super().__str__(self)

def do_sha1(s):
	debuglog('hashing...%s'%s)
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

def readFFprobedate(obj,Config):
	return readFFprobe(obj,Config,'creation_time')

def readdate(obj,Config):
	if obj_is_video(obj,Config):
		return readFFprobedate(obj,Config)
	else:
		return readEXIFdate(obj,Config)

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

def FFprobeCmd(f):
	c = 'ffprobe -v quiet -print_format json -show_format %s'%f
	r = os.popen(c)
	text = r.read()
	r.close()
	return text

def readFFprobe(obj,Config,tag):
	dst = obj2dst(obj,Config)
	jtext = json.loads(FFprobeCmd(dst))
	try:
		if tag in jtext['format']['tags']:
			return jtext['format']['tags'][tag]
		else:
			debuglog(u'FFprobe: \'%s\' not found in %s'%(tag,obj['fhash']))
			return False
	except KeyError:
		debuglog(u'FFprobe: KeyError and \'%s\' not found in %s'%(tag,obj['fhash']))
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

def face2path(h,i=''):
	return u'face/%s.%s.jpg' % (hash2path(h),i)

def obj2dst(obj,Config):
	return u'%s/%s' % (Config.read('data_root'),hash2path(obj['fhash']))

def obj2convert(obj,Config,cid,ctarget=u'{DST}'):
	return u'%s/%s' % (Config.read('data_root'),convert2path(obj['fhash'],cid,ctarget))

def obj2face(obj,Config,i=''):
	return u'%s/%s' % (Config.read('data_root'),face2path(obj['fhash'],i))

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
	os.chmod(dst, 0644)
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

class dbClass:
	"""mysqldatabase interface"""
	def __init__(self, Config):
		self.database_ready = False
		self.database_busy = False
		self.Config = Config
		self.init_db()

	def init_db(self):
		#connect the database
		try:
			mysql_host = self.Config.read('mysql_host')
			debuglog('Database %s connecting.'%mysql_host)
			self.db = MySQLdb.connect(host=mysql_host,user=self.Config.read('mysql_user'),passwd=self.Config.read('mysql_passwd'),db=self.Config.read('mysql_db'),charset='utf8')
			self.cur = self.db.cursor(cursorclass = MySQLdb.cursors.DictCursor) 	
			debuglog('Database %s ready.'%mysql_host)
			self.database_ready = True
			self.database_busy = False
		except MySQLdb.Error,e:
			try:
				debuglog("Database Error %d:%s" % (e.args[0], e.args[1]))
			except IndexError:
				debuglog("MySQL Error:%s" % str(e))
			self.database_ready = False
			self.database_busy = False
		
	def halt_db(self):
		if self.database_ready:
			self.db.close()
			self.database_ready = False
			self.database_busy = False

	def ready(self):
		try:
			if self.database_ready:
				self.db.ping()
		except MySQLdb.Error,e:
			self.database_ready = False
		return self.database_ready

	def execute(self,sql):
		while not self.ready():
			sleep(1)
			self.init_db()
		while self.database_busy:
			debuglog('Database busy. Wait 5 secs.')
			sleep(5)
		self.database_busy = True
		debuglog('Run SQL: %s'%sql)
		self.cur.execute(sql)
		self.db.commit()
		self.database_busy = False

	def fatchall(self,sql):
		while not self.ready():
			sleep(1)
			self.init_db()
		while self.database_busy:
			debuglog('Database busy. Wait 5 secs.')
			sleep(5)
		self.database_busy = True
		debuglog('Run SQL: %s'%sql)
		self.cur.execute(sql)
		r = self.cur.fatchall()
		self.database_busy = False
		return r

	def fatchone(self,sql):
		while not self.ready():
			sleep(1)
			self.init_db()
		while self.database_busy:
			debuglog('Database busy. Wait 5 secs.')
			sleep(5)
		self.database_busy = True
		debuglog('Run SQL: %s'%sql)
		self.cur.execute(sql)
		r = self.cur.fatchone()
		self.database_busy = False
		return r
