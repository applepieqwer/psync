from multiprocessing.managers import BaseManager
from time import sleep
from psync_func import debuglog,debugset,dbClass
import __builtin__
import sys

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
	reload(sys)
	sys.setdefaultencoding(defaultencoding)

class MyManager(BaseManager):
	pass

def main():
	debugset('main')
	#make connect to python server
	MyManager.register('MainList')
	MyManager.register('Config')
	#MyManager.register('DB')

	manager = MyManager(address=('', 50000), authkey='1111')
	manager.connect()
	MainList = manager.MainList()
	Config = manager.Config()
	__builtin__.db = dbClass(Config)
	
	#define Mission roadmap
	Mission = { 
	'import' :   ['fhash' , 'ftype' , 'fid' , 'distribute' , 'debug'] , 
	'lazycheck': ['fid' , 'distribute' , 'fhash' , 'distribute' , 'debug'] ,
	'lazytag' :  ['fid' , 'distribute' , 'fhash' , 'distribute' , 'savetag' , 'debug'] ,
	'convert' :  ['fid' , 'distribute' , 'fhash' , 'distribute' , 'convert' , 'debug'] ,
	'lazygps' :  ['fid' , 'distribute' , 'fhash' , 'distribute' , 'savegps' , 'debug']}

	#loop
	while True:
		if MainList.length():
			obj = MainList.popleft()
			if obj is None:
				continue
			if obj['mission'] == '' or obj['mission'] == 'done':
				debuglog('this obj is dump')
				continue
			else:
				debuglog('mission: %s'%obj['mission'])
				for todo in Mission[obj['mission']]:
					if obj is None:
						break
					try:
						debugset(todo)
						obj['doing'] = todo
						auto_module = __import__('psync-mod-%s'%todo)
						obj = auto_module.do(obj,Config)
						#the result obj "r" is reload to MainList
					except ImportError:
						debuglog('ERROR: %s module not found'%todo)
						print obj
						print 'DUMP DONE'
					except UserWarning,e:
						debuglog('MOD %s WARNING:%s'%(todo,e))
						print obj
						print 'DUMP DONE'
					except TypeError,e:
						debuglog('ERROR: %s TypeError %s'%(todo,e))
						print obj
						print 'DUMP DONE'
						MainList.append(obj)
						break
					#except:
					#	debuglog('ERROR: %s Unknown Error'%todo)
					#	print obj
					#	print 'DUMP DONE'
					#	MainList.append(obj)
					#	break
		else:
			print "psync-client: nothing to do....sleeping"
			sleep(10)

	


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print 'KeyboardInterrupt'
		db.halt_db()
		exit()
