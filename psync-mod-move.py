from urllib import pathname2url
from mimetypes import guess_type
from os import lstat

def typefile(filename):
	return guess_type(pathname2url(filename))[0]

#find the type of file
#find obj['src'] or die, if obj['fhash'] not set, then todo hash
# obj['ftype'] --------the mimetype of file
# obj['filetime'] -----------the file change time
# obj['todo'] = 'debug'  ---------next todo is 'debug'


def do(obj,Config):
	if not obj.has_key('src'):
		raise UserWarning,'src not set'
		return False
	if not obj.has_key('fhash'):
		obj['todo']='hash'
		return obj
	else:
		src = obj['src']
	obj['ftype'] = typefile(src)
	(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = lstat(src)
	obj['filetime'] = mtime
	obj['todo'] = 'debug'
	return obj
	
