from psync_func import ApiClass

###render obj with fhash using api

def do(obj,Config):
	if not obj.has_key('fhash'):
		raise UserWarning('fhash not found')
		return obj
	api = ApiClass(Config)
	r = api.go_api('file.direct_render',{'fhash':obj['fhash']})
	if api.is_ok():
		obj.update(api.payload())
		return obj
	else:
		raise UserWarning('api error')
		return obj