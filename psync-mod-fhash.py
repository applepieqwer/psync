from hashlib import sha1
from psync_func import obj2dst,debuglog
import os

#hash file
#find obj['src'], if obj['src'] not set, then break
# obj['fhash'] --------the sha1 hash of file

def do_sha1(s):
	read_size = 1024
	sha1Obj = sha1()
	with open(s,'rb') as f:
		data = f.read(read_size)
		while data:
			sha1Obj.update(data)
			data = f.read(read_size)
		return sha1Obj.hexdigest()

def new_fhash(obj,Config):
	if not obj.has_key('src'):
		raise UserWarning,'src not set'
		return obj
	else:
		src = obj['src']
	obj['fhash'] = do_sha1(src)
	return obj

def old_fhash(obj,Config):
	if not obj.has_key('fhash'):
		raise UserWarning,'fhash not set'
		return obj
	else:
		src = obj2dst(obj,Config)
		if not os.path.isfile(src):
			obj['fhashcheck'] = False
			return obj
	if obj['fhash'] == do_sha1(src):
		obj['fhashcheck'] = True
	else:
		obj['fhashcheck'] = False
	return obj

def do(obj,Config):
	mission = obj['mission']
	if mission == 'import':
		return new_fhash(obj,Config)
	if mission == 'lazycheck':
		return old_fhash(obj,Config)
	return obj