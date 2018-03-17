from multiprocessing.managers import BaseManager
from collections import deque
from ConfigParser import ConfigParser

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
	cp = ConfigParser()
	cp.read('psync.conf')
	
	L2S = ListClass() # list to search
	MainList = ListClass() # main list
	
	Config = ConfigClass()
	Config['endswith'] = eval(cp.get('psync_config','endswith'))
	Config['search_root'] = cp.get('psync_config','search_root')
	Config['data_root'] = cp.get('psync_config','data_root')
	Config['did'] = cp.getint('psync_config','did')
	Config['distname'] = cp.get('psync_config','distname')
	Config['disttype'] = cp.get('psync_config','disttype')
	Config['diststate'] = cp.get('psync_config','diststate')
	Config['distserver'] = cp.get('psync_config','distserver')

	Config['mysql_host'] = cp.get('psync_config','mysql_host')
	Config['mysql_user'] = cp.get('psync_config','mysql_user')
	Config['mysql_passwd'] = cp.get('psync_config','mysql_passwd')
	Config['mysql_db'] = cp.get('psync_config','mysql_db')

	L2S.append(Config['search_root'])

	MyManager.register('List2Search',callable=lambda:L2S)
	MyManager.register('MainList',callable=lambda:MainList)
	MyManager.register('Config',callable=lambda:Config)

	manager = MyManager(address=('', 50000), authkey='1111')
	s = manager.get_server()
	s.serve_forever()
