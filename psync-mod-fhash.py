from psync_func import obj2dst,debuglog,do_sha1
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
	obj['fhash'] = do_sha1(src)
	return obj

def old_fhash(obj,Config):
	if obj.has_key('fhashcheck'):
		return obj
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
	if obj.has_key('src'):
		src = obj['src']
	else:
		if obj.has_key('fhash'):
			src = obj2dst(obj,Config)
		else:
			raise UserWarning,'src or fhash not set'
			return obj
	if not os.path.isfile(src):
		obj['fhashcheck'] = False
		raise UserWarning,'file not found'
		return obj
	else:
		new_fhash = do_sha1(src)
		if obj.has_key('fhash') and obj['fhash'] != new_fhash:
			obj['fhashcheck'] = False
			raise UserWarning,'fhash check failed'
			return obj
		else:
			obj['fhash'] = new_fhash
			obj['fhashcheck'] = True
			return obj
