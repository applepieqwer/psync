from multiprocessing.managers import BaseManager
import readline
from psync_func import debuglog,debugset,dbClass
import __builtin__

class MyManager(BaseManager):
	pass

MyManager.register('List2Search')
MyManager.register('MainList')
MyManager.register('Config')


if __name__ == '__main__':
	manager = MyManager(address=('', 50000), authkey='1111')
	manager.connect()
	L2S = manager.List2Search()
	MainList = manager.MainList()
	Config = manager.Config()
	__builtin__.db = dbClass(Config)
	while True:
		print input('?>')


	
	

	
