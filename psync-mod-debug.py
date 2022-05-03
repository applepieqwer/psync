
#print the obj

def do(obj,Config):
	for k in obj.keys():
		print '%20.20s: %s'%(k,obj[k])
	print '='*30
	return obj
	
