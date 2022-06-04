from multiprocessing.managers import BaseManager
from time import sleep
from psync_func import debuglog,debugset,dbClass
import __builtin__
import sys
import os

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
	reload(sys)
	sys.setdefaultencoding(defaultencoding)

class MyManager(BaseManager):
	pass

def main():
	pid = os.getpid()
	debugset('main')
	#make connect to python server
	MyManager.register('MainList')
	MyManager.register('DoneList')
	MyManager.register('Status')
	MyManager.register('Config')
	#MyManager.register('DB')

	manager = MyManager(address=('', 50000), authkey='1111')
	manager.connect()
	MainList = manager.MainList()
	Config = manager.Config()
	DoneList = manager.DoneList()
	Status = manager.Status()
	__builtin__.db = dbClass(Config)
	
	#define Mission roadmap
	Mission = { 
	'remote_convert':['readobj','download','debug'] ,
	'import' :   ['fhash' , 'ftype' , 'fid' , 'distribute' , 'debug'] , 
	'lazycheck': ['fid' , 'distribute' , 'fhash' , 'distribute' , 'debug'] ,
	'lazytag' :  ['fid' , 'distribute' , 'fhash' , 'distribute' , 'savetag' , 'debug'] ,
	'convert' :  ['fid' , 'distribute' , 'fhash' , 'distribute' , 'convert' , 'debug'] ,
	'lazygps' :  ['fid' , 'distribute' , 'fhash' , 'distribute' , 'savegps' , 'debug']}

	#loop
	while True:
		if MainList.length():
			obj = MainList.get()
			if obj is None:
				continue
			if obj['mission'] == '':
				continue
			if obj['mission'] == 'done':
				Status.client_status(pid,'Obj Done')
				DoneList.put(obj)
				continue
			else:
				debuglog('mission: %s'%obj['mission'])
				Status.client_status(pid,'mission: %s'%obj['mission'])
				for todo in Mission[obj['mission']]:
					try:
						debugset(todo)
						obj['doing'] = todo
						Status.client_status(pid,'mission: %s, doing: %s'%(obj['mission'],todo))
						auto_module = __import__('psync-mod-%s'%todo)
						obj = auto_module.do(obj,Config)
						#the result obj "r" is reload to MainList
					except ImportError:
						debuglog('ERROR: %s module not found'%todo)
						Status.client_status(pid,'ERROR: %s module not found'%todo)
						break
					except UserWarning,e:
						debuglog('MOD %s WARNING:%s'%(todo,e))
						Status.client_status(pid,'MOD %s WARNING:%s'%(todo,e))
						break
					except TypeError,e:
						debuglog('ERROR: %s TypeError %s'%(todo,e))
						Status.client_status(pid,'ERROR: %s TypeError %s'%(todo,e))
						break
					#except:
					#	debuglog('ERROR: %s Unknown Error'%todo)
					#	print obj
					#	print 'DUMP DONE'
					#	MainList.put(obj)
					#	break
		else:
			print "psync-client: nothing to do....exit"
			####sleep(10)
			exit()

	


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print 'KeyboardInterrupt'
		db.halt_db()
		exit()
