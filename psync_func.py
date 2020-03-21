import mysql.connector
from collections import deque
from os import getpid,remove,lstat
import os
import exifread as exifreader
import __builtin__
from hashlib import sha1
import json
from time import sleep
from copy import deepcopy
from datetime import date
from base64 import b64encode,b64decode
import geocoder

try:
	import cPickle as pickle
except:
	import pickle

#from shutil import copy2 as shutil_move
from shutil import move as shutil_move

def geo_osm_raw(lat,lng):
	r = geocoder.osm([lat,lng], method='reverse')
	if r.ok:
		return r.json['raw']
	else:
		return ""

def geo_baidu_raw(lat,lng,key):
	r = geocoder.baidu([lat,lng], method='reverse',key=key)
	if r.ok:
		return r.json['raw']
	else:
		return ""

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

def parse_gps(titude):
	return float(titude.values[0].num + (titude.values[1].num+(float(titude.values[2].num)/float(titude.values[2].den))/60)/60)

def parse_alt(alt):
	return float(alt.values[0].num) / float(alt.values[0].den)

def readGPS(obj,Config):
	if obj_is_video(obj,Config):
		debuglog(u'readGPS: %s has no GPS data'%obj['fhash'])
		return False
	if hasattr(readGPS, 'fhash') and hasattr(readGPS, 'gps_data') and readGPS.fhash == obj['fhash']:
		debuglog(u'readGPS: read GPS data from cache %s'%obj['fhash'])
		return deepcopy(readGPS.gps_data)
	else:
		readGPS.fhash = obj['fhash']
		readGPS.gps_data = {}
		dst = obj2dst(obj,Config)
		debuglog(u'readGPS: read GPS data from file %s'%obj['fhash'])
		f = open(dst,'rb')
		tags = exifreader.process_file(f, details=False)
		f.close()
		for i in tags.keys():
			if i[:3] == 'GPS':
				readGPS.gps_data[i] = tags[i]
		if len(readGPS.gps_data) < 1 :
			debuglog(u'readGPS: %s has no GPS data'%obj['fhash'])
			return False
		readGPS.gps_data['fhash'] = obj['fhash']
		return deepcopy(readGPS.gps_data)

def readGPSlong(obj,Config):
	gps_data = readGPS(obj,Config)
	if gps_data == False:
		return False
	if gps_data['fhash'] != obj['fhash']:
		debuglog(u'readGPSlong: GPS data fhash mismatch')
		return False
	if str(gps_data['GPS GPSLongitudeRef']) == 'W':
		return 0 - parse_gps(gps_data['GPS GPSLongitude'])
	else:
		return parse_gps(gps_data['GPS GPSLongitude'])

def readGPSlat(obj,Config):
	gps_data = readGPS(obj,Config)
	if gps_data == False:
		return False
	if gps_data['fhash'] != obj['fhash']:
		debuglog(u'readGPSlat: GPS data fhash mismatch')
		return False
	if str(gps_data['GPS GPSLatitudeRef']) == 'S':
		return 0 - parse_gps(gps_data['GPS GPSLatitude'])
	else:
		return parse_gps(gps_data['GPS GPSLatitude'])

def readGPSalt(obj,Config):
	gps_data = readGPS(obj,Config)
	if gps_data == False:
		return False
	if gps_data['fhash'] != obj['fhash']:
		debuglog(u'readGPSalt: GPS data fhash mismatch')
		return False
	try:
		if int(gps_data['GPS GPSAltitudeRef'].values[0]) == 1:
			return 0 - parse_alt(gps_data['GPS GPSAltitude'])
		else:
			return parse_alt(gps_data['GPS GPSAltitude'])
	except AttributeError:
		debuglog(u'readGPSalt: GPS GPSAltitudeRef AttributeError')
		return False
	

def readGPSdatetime(obj,Config):
	gps_data = readGPS(obj,Config)
	if gps_data == False:
		return False
	if gps_data['fhash'] != obj['fhash']:
		debuglog(u'readGPSalt: GPS data fhash mismatch')
		return False
	return u'%s %02d:%02d:%02d'%(gps_data['GPS GPSDate'].values,gps_data['GPS GPSTimeStamp'].values[0].num,gps_data['GPS GPSTimeStamp'].values[1].num,gps_data['GPS GPSTimeStamp'].values[2].num)

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
	tags = exifreader.process_file(f, stop_tag=tag, details=False)
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
		self.Config = Config
		self.init_db()

	def init_db(self):
		#connect the database
		try:
			mysql_host = self.Config.read('mysql_host')
			debuglog('Database %s connecting.'%mysql_host)
			self.db = mysql.connector.connect(host=mysql_host,user=self.Config.read('mysql_user'),password=self.Config.read('mysql_passwd'),database=self.Config.read('mysql_db'),autocommit=True,compress=True,buffered=True)
			self.cur = self.db.cursor(dictionary=True) 	
			debuglog('Database %s ready.'%mysql_host)
		except mysql.connector.Error as e:
			debuglog("MySQL Error:%s" % str(e))
		return True
		
	def halt_db(self):
		if self.db.is_connected():
			self.cur.close()
			self.db.close()
		return True

	def ready(self):
		try:
			#debuglog('Ping Database.')
			self.db.ping(reconnect=True, attempts=5, delay=1)
		except mysql.connector.InterfaceError:
			debuglog('Database InterfaceError.')
			self.init_db()
		return self.db.is_connected()

	def execute(self,sql):
		success = False
		while not success:
			try:
				while not self.ready():
					debuglog('Database not ready. Wait 5 secs.')
					sleep(5)
				debuglog('Execute SQL: %s'%sql)
				result = self.cur.execute(sql)
				self.db.commit()
				debuglog('Execute Done.')
				success = True
			except mysql.connector.InterfaceError:
				success = False
				debuglog('Execute SQL InterfaceError, Retry')
			except mysql.connector.OperationalError:
				success = False
				debuglog('Execute SQL OperationalError, Retry')
		return True

	def execute2file(self,sql):
		filename = 'sql_log%s-%s.sql' % (date.today(),os.getpid())
		debuglog('Save SQL to file: %s'%filename)
		with open(filename, 'a') as f:
			f.write('%s;\n'%sql)
		debuglog(sql)
		return True

	def lastrowid(self):
		return deepcopy(self.cur.lastrowid)

	def fetchall(self,sql):
		success = False
		while not success:
			try:
				while not self.ready():
					debuglog('Database not ready. Wait 5 secs.')
					sleep(5)
				debuglog('Fetchall SQL: %s'%sql)
				result = self.cur.execute(sql)
				r = self.cur.fetchall()
				debuglog('Fatchall Done.')
				success = True
			except mysql.connector.InterfaceError:
				success = False
				debuglog('Execute SQL InterfaceError, Retry')
			except mysql.connector.OperationalError:
				success = False
				debuglog('Execute SQL OperationalError, Retry')
		return deepcopy(r)

	def fetchone(self,sql):
		success = False
		while not success:
			try:
				while not self.ready():
					debuglog('Database not ready. Wait 5 secs.')
					sleep(5)
				debuglog('Fetchone SQL: %s'%sql)
				result = self.cur.execute(sql)
				r = self.cur.fetchone()
				debuglog('Fatchone Done.')
				success = True
			except mysql.connector.InterfaceError:
				success = False
				debuglog('Execute SQL InterfaceError, Retry')
			except mysql.connector.OperationalError:
				success = False
				debuglog('Execute SQL OperationalError, Retry')
		return deepcopy(r)
