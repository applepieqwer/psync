from multiprocessing.managers import BaseManager
from collections import deque

class ListClass(deque):
	def length(self):
		return len(self)
	def __str__(self):
		return super().__str__(self)

class ConfigClass(dict):
	def read(self,key):
		return self.get(key)

class MyManager(BaseManager):
	pass

if __name__ == '__main__':
	L2S = ListClass() # list to search
	MainList = ListClass() # main list
	
	Config = ConfigClass()
	Config['endswith'] = ('.jpg','.JPG','.jpeg','.JPEG')
	Config['search_root'] = '/home/applepie/Data/psync/_test_'
	Config['data_root'] = '/home/applepie/Data/psync'
	Config['did'] = 4
	Config['distname'] = 'mainServer'
	Config['disttype'] = 'full'
	Config['diststate'] = 'ready'
	Config['distserver'] = 'http://applepie-daan.f3322.net/'

	Config['mysql_host'] = 'psync.db.6677333.hostedresource.com'
	Config['mysql_user'] = 'psync'
	Config['mysql_passwd'] = 'V79762psync!'
	Config['mysql_db'] = 'psync'

	L2S.append(Config['search_root'])

	MyManager.register('List2Search',callable=lambda:L2S)
	MyManager.register('MainList',callable=lambda:MainList)
	MyManager.register('Config',callable=lambda:Config)

	manager = MyManager(address=('', 50000), authkey='1111')
	s = manager.get_server()
	s.serve_forever()
