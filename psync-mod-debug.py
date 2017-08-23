
#print the obj

def do(obj,Config):
	for k in obj.keys():
		print '%10.10s: %s'%(k,obj[k])
	print '='*30
	return obj
	
