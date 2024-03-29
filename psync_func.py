
from collections import deque
from Queue import Queue
from os import getpid,remove,lstat
import os
import __builtin__
from hashlib import sha1
import json
from time import sleep,time
from copy import deepcopy
from datetime import date
from base64 import b64encode,b64decode
import requests
from ConfigParser import ConfigParser

try:
	import mysql.connector
except:
	print "import mysql.connector error"

try:
	import exifread as exifreader
except:
	print "import exifread error"

try:
	import geocoder
except:
	print "import geocoder error"

try:
	import cPickle as pickle
except:
	import pickle

#from shutil import copy2 as shutil_move
from shutil import move as shutil_move
from shutil import copy as shutil_copy

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
		
class StatusClass(dict):
	"""the status of server"""
	def __init__(self):
		super(dict, self).__init__()
		self['clients']={}
		self['clients_pid_list']=deque(maxlen=10)  #max 10 clients
		self['reporter']={}
	def read(self,key):
		return self.get(key)
	def read_all(self):
		r = {}
		r['reporter'] = deepcopy(self['reporter'])
		r['clients_pid_list']=list(self['clients_pid_list'])
		r['clients'] = {}
		for pid in self['clients'].keys():
			if pid in r['clients_pid_list']:
				r['clients'][pid] = list(self['clients'][pid])
			else:
				del self['clients'][pid]
		return r
	def client_status(self,pid,status):
		if pid in self['clients_pid_list']:
			self['clients'][pid].append({'time':time(),'status':status})
		else:
			self['clients_pid_list'].append(pid)
			self['clients'][pid] = deque(maxlen=5)  #max 5 msgs for 1 client
			self['clients'][pid].append({'time':time(),'status':status})
		return len(self['clients'][pid])
	def reporter_status(self,pid,status):
		self['reporter'].update({pid:status})

class ConfigClass(dict):
	def __init__(self):
		print 'ConfigClass init'
		super(ConfigClass, self).__init__()
		#read all config data
		self._cp = ConfigParser()
		self._cp.read('psync.conf')
		self['endswith'] = eval(self._cp.get('psync_config','endswith'))
		self['search_root'] = self._cp.get('psync_config','search_root')
		self['data_root'] = self._cp.get('psync_config','data_root')
		self['did'] = self._cp.getint('psync_config','did')
		self['distname'] = self._cp.get('psync_config','distname')
		self['disttype'] = self._cp.get('psync_config','disttype')
		self['diststate'] = self._cp.get('psync_config','diststate')
		self['distserver'] = self._cp.get('psync_config','distserver')
		self['todo_jobs_url'] = self._cp.get('psync_web_config','todo_jobs_url')
		self['wget_jobs_url'] = self._cp.get('psync_web_config','wget_jobs_url')
		self['mysql_host'] = self._cp.get('psync_config','mysql_host')
		self['mysql_user'] = self._cp.get('psync_config','mysql_user')
		self['mysql_passwd'] = self._cp.get('psync_config','mysql_passwd')
		self['mysql_db'] = self._cp.get('psync_config','mysql_db')
		self['baidu_key'] = self._cp.get('psync_gps','baidu_key')
		self['psync_api_host'] = self._cp.get('psync_api','psync_api_host')
		self['psync_api_url'] = self._cp.get('psync_api','psync_api_url')
		self['psync_api_token'] = self._cp.get('psync_api','psync_api_token')
		self['wget_target_url'] = self._cp.get('psync_local','wget_target_url')
	def read(self,key):
		return self.get(key)	

class ConfigRemoteClass(ConfigClass):
	"""docstring for ConfigClass"""
	def __init__(self):
		super(ConfigRemoteClass, self).__init__()
		self['remote_config']={}
	def read_remote_config(self):
		api = ApiClass(self)
		r = api.go_api('distribute.read',{})
		if api.is_ok():
			self['remote_config']['distribute'] = api.payload()['distribute']
		r = api.go_api('converter.read',{})
		if api.is_ok():
			self['remote_config']['converter'] = api.payload()['converter']
		r = api.go_api('ftype.read',{})
		if api.is_ok():
			self['remote_config']['ftype'] = api.payload()['ftype']

		

class ListClass(Queue):
	def length(self):
		return self.qsize()
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
		#read gps long
		if readGPS.gps_data.has_key('GPS GPSLongitudeRef') and readGPS.gps_data.has_key('GPS GPSLongitude'):
			if str(readGPS.gps_data['GPS GPSLongitudeRef']) == 'W':
				readGPS.gps_data['long'] = 0 - parse_gps(readGPS.gps_data['GPS GPSLongitude'])
			else:
				readGPS.gps_data['long'] = parse_gps(readGPS.gps_data['GPS GPSLongitude'])
		
		#read gps lat
		if readGPS.gps_data.has_key('GPS GPSLatitudeRef') and readGPS.gps_data.has_key('GPS GPSLatitude'):
			if str(readGPS.gps_data['GPS GPSLatitudeRef']) == 'S':
				readGPS.gps_data['lat'] = 0 - parse_gps(readGPS.gps_data['GPS GPSLatitude'])
			else:
				readGPS.gps_data['lat'] = parse_gps(readGPS.gps_data['GPS GPSLatitude'])
		#read gps alt
		if readGPS.gps_data.has_key('GPS GPSAltitudeRef') and readGPS.gps_data.has_key('GPS GPSAltitude'):
			if int(readGPS.gps_data['GPS GPSAltitudeRef'].values[0]) == 1:
				readGPS.gps_data['alt'] = 0 - parse_alt(readGPS.gps_data['GPS GPSAltitude'])
			else:
				readGPS.gps_data['alt'] = parse_alt(readGPS.gps_data['GPS GPSAltitude'])

		if readGPS.gps_data.has_key('long') and readGPS.gps_data.has_key('lat'):
			#read geo from baidu
			debuglog(u'readGPS: read geo from baidu')
			readGPS.gps_data['baidu_raw'] = geo_baidu_raw(readGPS.gps_data['lat'],readGPS.gps_data['long'],Config.read('baidu_key'))
			#read geo from osm
			debuglog(u'readGPS: read geo from osm')
			readGPS.gps_data['osm_raw'] = geo_osm_raw(readGPS.gps_data['lat'],readGPS.gps_data['long'])
		return deepcopy(readGPS.gps_data)

def readGPSjson(obj,Config):
	gps_data = readGPS(obj,Config)
	if gps_data == False:
		return False
	if gps_data['fhash'] != obj['fhash']:
		debuglog(u'readGPSraw: GPS data fhash mismatch')
		return False
	gps_json = {'fid':obj['fid'],
				'lat':gps_data['lat'],
				'long':gps_data['long'],
				'baidu_raw':gps_data['baidu_raw'],
				'osm_raw':gps_data['osm_raw']}
	return b64encode(json.dumps(gps_json))

def readGPSlong(obj,Config):
	gps_data = readGPS(obj,Config)
	if gps_data == False:
		return False
	if gps_data['fhash'] != obj['fhash']:
		debuglog(u'readGPSlong: GPS data fhash mismatch')
		return False
	if gps_data.has_key('long'):
		return gps_data['long']
	else:
		return False
	

def readGPSlat(obj,Config):
	gps_data = readGPS(obj,Config)
	if gps_data == False:
		return False
	if gps_data['fhash'] != obj['fhash']:
		debuglog(u'readGPSlat: GPS data fhash mismatch')
		return False
	if gps_data.has_key('lat'):
		return gps_data['lat']
	else:
		return False

def readGPSalt(obj,Config):
	gps_data = readGPS(obj,Config)
	if gps_data == False:
		return False
	if gps_data['fhash'] != obj['fhash']:
		debuglog(u'readGPSalt: GPS data fhash mismatch')
		return False
	if gps_data.has_key('alt'):
		return gps_data['alt']
	else:
		return False
	

def readGPSdatetime(obj,Config):
	gps_data = readGPS(obj,Config)
	if gps_data == False:
		return False
	if gps_data['fhash'] != obj['fhash']:
		debuglog(u'readGPSalt: GPS data fhash mismatch')
		return False
	return u'%s %02d:%02d:%02d'%(gps_data['GPS GPSDate'].values,gps_data['GPS GPSTimeStamp'].values[0].num,gps_data['GPS GPSTimeStamp'].values[1].num,gps_data['GPS GPSTimeStamp'].values[2].num)

def readGPSBaiduOSM(obj,Config,i):
	gps_data = readGPS(obj,Config)
	if gps_data == False:
		return False
	if gps_data['fhash'] != obj['fhash']:
		debuglog(u'readGPSBaiduOSM: GPS data fhash mismatch')
		return False
	try:
		if i == 'BaiduPlace':
			return gps_data['baidu_raw']['formatted_address']
		elif i == 'BaiduCountry':
			return gps_data['baidu_raw']['addressComponent']['country']
		elif i == 'BaiduCity':
			return gps_data['baidu_raw']['addressComponent']['city']
		elif i == 'OSMPlace':
			return gps_data['osm_raw']['display_name']
		elif i == 'OSMCountry':
			return gps_data['osm_raw']['address']['country']
		elif i == 'OSMCity':
			return gps_data['osm_raw']['address']['city']
		else:
			raise KeyError
	except KeyError as e:
		debuglog(u'readGPSBaiduOSM: %s not found'%i)
		return False

def readGPSBaiduPlace(obj,Config):
	return readGPSBaiduOSM(obj,Config,'BaiduPlace')
def readGPSBaiduCountry(obj,Config):
	return readGPSBaiduOSM(obj,Config,'BaiduCountry')
def readGPSBaiduCity(obj,Config):
	return readGPSBaiduOSM(obj,Config,'BaiduCity')
def readGPSOSMPlace(obj,Config):
	return readGPSBaiduOSM(obj,Config,'OSMPlace')
def readGPSOSMCountry(obj,Config):
	return readGPSBaiduOSM(obj,Config,'OSMCountry')
def readGPSOSMCity(obj,Config):
	return readGPSBaiduOSM(obj,Config,'OSMCity')


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
	try:
		shutil_move(obj['src'],dst)
	except OSError as e:
		debuglog(u'OSError: Maybe ReadOnly, try Copy.')
		shutil_copy(obj['src'],dst)
	os.chmod(dst, 0644)
	obj['dst']=dst
	return obj

def rm_file(obj,Config):
	debuglog(u'RM! %s'%obj['src'])
	try:
		remove(obj['src'])
	except OSError as e:
		debuglog(u'OSError: Maybe ReadOnly, Ignore.')
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

def wget(fhash,Config):
	return 'wget -c -O \'%s\' \'%s/%s\''%(obj2dst({'fhash':fhash},Config),Config.read('wget_target_url'),hash2path(fhash))

class CheckLocal:
	def __init__(self):
		pass
	def check(self,obj,Config):
		src = obj2dst(obj,Config)
		if not os.path.isfile(src):
			self.check_fail(obj,Config)
			return False
		else:
			if obj['fhash'] == do_sha1(src):
				self.check_pass(obj,Config)
				return True
			else:
				self.check_fail(obj,Config)
				return False
	def check_pass(self,obj,Config):
		debuglog('CheckLocal Pass')
	def check_fail(self,obj,Config):
		debuglog('CheckLocal Fail')

class CheckLocal_sql(CheckLocal):
	def __init__(self):
		CheckLocal.__init__(self)
		__builtin__.db = dbClassLocal()
	def check_pass(self,obj,Config):
		sql = "REPLACE INTO `file_distribute` (`fid`,`did`) VALUES SELECT `fid`,'%s'  FROM `file` WHERE `fhash` = '%s'"%(Config.read('did'),obj['fhash'])
		db.execute(sql)
		debuglog('CheckLocal_sql Pass')
	def check_fail(self,obj,Config):
		sql = "DELETE FROM `file_distribute` WHERE `file_distribute`.`fid` IN (SELECT `fid`  FROM `file` WHERE `fhash` = '%s') AND `file_distribute`.`did` = %s LIMIT 1"%(obj['fhash'],Config.read('did'))
		db.execute(sql)
		debuglog('CheckLocal_sql Fail: %s <==============Check Fail'%obj['fhash'])

class CheckLocal_wget(CheckLocal):
	def __init__(self):
		CheckLocal.__init__(self)
		pass
	def check_pass(self,obj,Config):
		debuglog('CheckLocal_wget Pass')
	def check_fail(self,obj,Config):
		filename = 'wget_log%s-%s.sh' % (date.today(),os.getpid())
		debuglog('Save Wget to file: %s'%filename)
		with open(filename, 'a') as f:
			f.write('%s;\n'%wget(obj['fhash'],Config))
		debuglog('CheckLocal_wget Fail: %s <==============Check Fail'%obj['fhash'])

class CheckLocal_7zip(CheckLocal):
	def __init__(self,target_folder):
		CheckLocal.__init__(self)
		self.target_folder = target_folder
		pass
	def check_pass(self,obj,Config):
		debuglog('CheckLocal_7zip Pass')
		filename = '7zip_log%s-%s.sh' % (date.today(),os.getpid())
		debuglog('Save 7zip to file: %s'%filename)
		with open(filename, 'a') as f:
			f.write('./psync-7z.sh \"%s\" %s;\n'%(self.target_folder,hash2path(obj['fhash'])))
	def check_fail(self,obj,Config):
		debuglog('CheckLocal_7zip Fail: %s <==============Check Fail'%obj['fhash'])

class dbClassLocal:
	def __init__(self):
		pass
	def init_db(self):
		return True
	def halt_db(self):
		return True
	def escape_string(self,s):
		return s
	def ready(self):
		return True
	def execute(self,sql):
		return self.execute2file(sql)
	def execute2file(self,sql):
		filename = 'sql_log%s-%s.sql' % (date.today(),os.getpid())
		debuglog('Save SQL to file: %s'%filename)
		with open(filename, 'a') as f:
			f.write('%s;\n'%sql)
		debuglog(sql)
		return True

class dbClass(dbClassLocal):
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

	def escape_string(self,s):
		return self.db._cmysql.escape_string(s)

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


#///////////www.fly19.net API/////////
class ApiClass(dict):
	STATUS_OK = 0
	STATUS_ERR = -1
	STATUS_FATAL_ARR = -2

	def __init__(self, Config):
		super(dict, self).__init__()
		self.Config = Config
	def go_api(self,action,payload):
		url = self.Config.read('psync_api_url')
		token = self.Config.read('psync_api_token')
		d = {"action":action,"token":token,"payload":payload}
		try:
			cmd = 'curl --silent -H \"Accept: application/json\" -H \"Content-type: application/json\" -X POST -d \'%s\' %s'%(json.dumps(d),url)
			#print cmd
			result = os.popen(cmd).read()
			self.update(json.loads(result))
		except Exception as e:
			self.update({'status':self.STATUS_FATAL_ARR,'payload':{}})
	def status(self):
		return self['status']
	def is_ok(self):
		return (self['status'] == self.STATUS_OK)
	def payload(self):
		if self.has_key('payload'):
			return self['payload']
		else:
			return {}


def go_api(action,payload={}):
	#direct api, direct output
	cp = ConfigParser()
	cp.read('psync.conf')
	url = cp.get('psync_api','psync_api_url')
	token = cp.get('psync_api','psync_api_token')
	d = {"action":action,"token":token,"payload":payload}
	try:
		cmd = 'curl --silent -H \"Accept: application/json\" -H \"Content-type: application/json\" -X POST -d \'%s\' %s'%(json.dumps(d),url)
		f = open('.api.dump', 'w')
		f.write(cmd)
		f.close()
		result = os.popen(cmd).read()
		return json.loads(result)
	except ValueError as e:
		debugset('api')
		debuglog('go_api error:%s, curl result:%s'%(e,result))
		raise e
	except Exception as e:
		debugset('api')
		debuglog('go_api error:%s, curl result:%s'%(e,result))
		raise e
