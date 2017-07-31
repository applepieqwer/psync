from hashlib import sha1

#hash file
#find obj['src'], if obj['src'] not set, then break
# obj['fhash'] --------the sha1 hash of file


def do(obj,Config):
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
	
