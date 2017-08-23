import MySQLdb
from multiprocessing.managers import BaseManager
from time import sleep
from psync_func import debuglog,debugset
import __builtin__

class MyManager(BaseManager):
	pass

def init_db(Config):
	#connect the database
	try:
		if not 'db' in dir(__builtin__) or not __builtin__.db.open:
			mysql_host = Config.read('mysql_host')
			debuglog('Database %s connecting.'%mysql_host)
			__builtin__.db = MySQLdb.connect(host=mysql_host,user=Config.read('mysql_user'),passwd=Config.read('mysql_passwd'),db=Config.read('mysql_db'),charset='utf8')
			__builtin__.cur = db.cursor(cursorclass = MySQLdb.cursors.DictCursor) 	
		debuglog('Database %s ready.'%mysql_host)
		#update server stat here
	except Exception as e:
		debuglog("Mysql Error %d: %s" % (e.args[0], e.args[1]))
		raise e

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
	'import' : [ 'fhash' , 'ftype' , 'fid' , 'distribute' , 'debug'] , 
	'lazycheck' : ['fid' , 'distribute' , 'fhash' , 'distribute' , 'debug']}

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
							#connection lost ,re-connect
							debuglog("Re-Connect to database")
							init_db(Config)
							#send obj back to MainList
							MainList.append(obj)
						else:
							debuglog("Mysql Error %d: %s" % (e.args[0], e.args[1]))
							print obj
							print 'DUMP DONE'
		else:
			sleep(3)

	


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print 'KeyboardInterrupt'
		db.commit()
		db.close()
