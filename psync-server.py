from multiprocessing.managers import BaseManager
from ConfigParser import ConfigParser
from psync_func import ConfigClass,ListClass
from psync_func import debuglog,debugset

class MyManager(BaseManager):
	pass

if __name__ == '__main__':
	try:
		debugset('psync-server')

		cp = ConfigParser()
		cp.read('psync.conf')
		
		Config = ConfigClass()
		Config['endswith'] = eval(cp.get('psync_config','endswith'))
		Config['search_root'] = cp.get('psync_config','search_root')
		Config['data_root'] = cp.get('psync_config','data_root')
		Config['did'] = cp.getint('psync_config','did')
		Config['distname'] = cp.get('psync_config','distname')
		Config['disttype'] = cp.get('psync_config','disttype')
		Config['diststate'] = cp.get('psync_config','diststate')
		Config['distserver'] = cp.get('psync_config','distserver')

		Config['todo_jobs_url'] = cp.get('psync_web_config','todo_jobs_url')
		Config['wget_jobs_url'] = cp.get('psync_web_config','wget_jobs_url')

		Config['mysql_host'] = cp.get('psync_config','mysql_host')
		Config['mysql_user'] = cp.get('psync_config','mysql_user')
		Config['mysql_passwd'] = cp.get('psync_config','mysql_passwd')
		Config['mysql_db'] = cp.get('psync_config','mysql_db')

		Config['baidu_key'] = cp.get('psync_gps','baidu_key')
		#DB = dbClass(Config) # go for mysql

		Config['psync_api_url'] = cp.get('psync_api','psync_api_url')
		Config['psync_api_token'] = cp.get('psync_api','psync_api_token')

		L2S = ListClass() # list to search
		MainList = ListClass() # main list

		L2S.append(Config['search_root'])

		MyManager.register('List2Search',callable=lambda:L2S)
		MyManager.register('MainList',callable=lambda:MainList)
		MyManager.register('Config',callable=lambda:Config)
		#MyManager.register('DB',callable=lambda:DB)

		manager = MyManager(address=('', 50000), authkey='1111')
		s = manager.get_server()
		s.serve_forever()

	except KeyboardInterrupt:
		print 'KeyboardInterrupt'
		#DB.halt_db()
		exit()
