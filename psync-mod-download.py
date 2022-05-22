from psync_func import obj2dst,debuglog,do_sha1
import os

def do(obj,Config):
	if not obj.has_key('fhash'):
		raise UserWarning('fhash not found')
		return obj
	if not obj.has_key('hash2path'):
		raise UserWarning('hash2path not found')
		return obj
	if not obj.has_key('raw_url'):
		raise UserWarning('raw_url not found')
		return obj