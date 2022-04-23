from multiprocessing.managers import BaseManager
from psync_func import ConfigClass,ListClass
from psync_func import debuglog,debugset

class MyManager(BaseManager):
	pass

if __name__ == '__main__':
	try:
		debugset('psync-server')
		Config = ConfigClass()
		L2S = ListClass() # list to search
		MainList = ListClass() # main jobs list
		DoneList = ListClass() # jobs done list
		L2S.put(Config['search_root'])

		MyManager.register('List2Search',callable=lambda:L2S)
		MyManager.register('MainList',callable=lambda:MainList)
		MyManager.register('DoneList',callable=lambda:DoneList)
		MyManager.register('Config',callable=lambda:Config)
		#MyManager.register('DB',callable=lambda:DB)

		manager = MyManager(address=('', 50000), authkey='1111')
		s = manager.get_server()
		s.serve_forever()

	except KeyboardInterrupt:
		print 'KeyboardInterrupt'
		#DB.halt_db()
		exit()
