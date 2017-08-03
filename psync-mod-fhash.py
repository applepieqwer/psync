from hashlib import sha1
from psync_func import obj2dst,debuglog
import os

#hash file
#find obj['src'], if obj['src'] not set, then break
# obj['fhash'] --------the sha1 hash of file

def new_fhash(obj,Config):
	if not obj.has_key('src'):
		raise UserWarning,'src not set'
		return obj
	else:
		src = obj['src']
	sha1Obj = sha1()
	with open(src, 'rb') as f:
		sha1Obj.update(f.read())
	obj['fhash'] = sha1Obj.hexdigest()
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
	sha1Obj = sha1()
	with open(src, 'rb') as f:
		sha1Obj.update(f.read())
	if obj['fhash'] == sha1Obj.hexdigest():
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