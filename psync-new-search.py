from multiprocessing.managers import BaseManager
import readline

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
	L2S.append(Config.read('search_root'))


	
	

	
