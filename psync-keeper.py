from multiprocessing.managers import BaseManager
from time import sleep
import __builtin__
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
	reload(sys)
	sys.setdefaultencoding(defaultencoding)

class MyManager(BaseManager):
	pass

def main():
	debugset('Keeper')
	#make connect to python server
	MyManager.register('MainList')
	MyManager.register('Config')
	MyManager.register('DB')

	manager = MyManager(address=('', 50000), authkey='1111')
	manager.connect()
	MainList = manager.MainList()
	Config = manager.Config()
	__builtin__.db = manager.DB()

	#loop
	while True:
		mainlist_length = MainList.length():
		db_ready = db.ready()
		print("\rMainList.length = %d, db.ready = %s"%(mainlist_length,db_ready))
		sleep(10)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print 'KeyboardInterrupt'
		exit()
