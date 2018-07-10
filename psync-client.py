import MySQLdb
from multiprocessing.managers import BaseManager
from time import sleep
from psync_func import debuglog,debugset,halt_db,init_db
import __builtin__

class MyManager(BaseManager):
	pass

def main():
	debugset('main')
	#make connect to python server
	MyManager.register('MainList')
	MyManager.register('Config')

	manager = MyManager(address=('', 50000), authkey='1111')
	manager.connect()
	MainList = manager.MainList()
	Config = manager.Config()

	init_db(Config)
	
	#define Mission roadmap
	Mission = { 
	'import' :    [ 'fhash' , 'ftype' , 'fid' , 'distribute' , 'debug'] , 
	'lazycheck' : ['fid' , 'distribute' , 'fhash' , 'distribute' , 'debug'] ,
	'lazytag' :   ['fid' , 'distribute' , 'savetag' , 'debug'] ,
	'convert' : ['fid' , 'debug' , 'distribute' , 'fhash' , 'distribute' , 'convert' , 'debug']}

	#loop
	while True:
		if MainList.length():
			obj = MainList.popleft()
			if obj['mission'] == '' or obj['mission'] == 'done':
				debuglog('this obj is dump')
				continue
			else:
				for todo in Mission[obj['mission']]:
					try:
						debugset(todo)
						obj['doing'] = todo
						auto_module = __import__('psync-mod-%s'%todo)
						obj = auto_module.do(obj,Config)
						__builtin__.db.ping()
						__builtin__.db.commit()
						#the result obj "r" is reload to MainList
					except ImportError:
						debuglog('ERROR: %s module not found'%todo)
						print obj
						print 'DUMP DONE'
					except UserWarning,e:
						debuglog('MOD %s WARNING:%s'%(todo,e))
						print obj
						print 'DUMP DONE'
					except MySQLdb.Error,e:
						if e.args[0] == 2006:
							#send obj back to list
							MainList.append(obj)
							#connection lost ,re-connect
							debuglog("Re-Connect to database")
							init_db(Config)
						else:
							debuglog("Mysql Error %d: %s" % (e.args[0], e.args[1]))
							print obj
							print 'DUMP DONE'
					#else:
						#debuglog("Oops! Error!")
						#print obj
						#print 'DUMP DONE'
		else:
			sleep(3)

	


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print 'KeyboardInterrupt'
		__builtin__.db.close()
