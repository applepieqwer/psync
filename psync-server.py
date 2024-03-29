from multiprocessing.managers import BaseManager,Process
from psync_func import ConfigClass,ListClass,ApiClass,StatusClass,ConfigRemoteClass
from psync_func import debuglog,debugset
import os
from time import sleep
import sys

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
	reload(sys)
	sys.setdefaultencoding(defaultencoding)

class MyManager(BaseManager):
	pass

def manager_proc():
	try:
		debugset('psync-server/manager_proc')
		debuglog('setup Manager')
		debuglog('reading local config')
		Config = ConfigRemoteClass()
		debuglog('reading remote config')
		Config.read_remote_config()
		Status = StatusClass()
		L2S = ListClass() # list to search
		MainList = ListClass() # main jobs list
		DoneList = ListClass() # jobs done list
		L2S.put(Config['search_root'])

		MyManager.register('List2Search',callable=lambda:L2S)
		MyManager.register('MainList',callable=lambda:MainList)
		MyManager.register('DoneList',callable=lambda:DoneList)
		MyManager.register('Config',callable=lambda:Config)
		MyManager.register('Status',callable=lambda:Status)
		#MyManager.register('DB',callable=lambda:DB)

		manager = MyManager(address=('', 50000), authkey='1111')
		s = manager.get_server()
		debuglog('starting Manager')
		s.serve_forever()
	except Exception as e:
		debuglog('manager_proc Exception, exit.')
		debuglog(e.args)
		exit()

def reporter_proc():
	try:
		debugset('psync-server/reporter_proc')
		pid = os.getpid()
		debuglog('connecting Manager')
		MyManager.register('List2Search')
		MyManager.register('MainList')
		MyManager.register('DoneList')
		MyManager.register('Config')
		MyManager.register('Status')

		reporter = MyManager(address=('', 50000), authkey='1111')
		reporter.connect()
		L2S = reporter.List2Search()
		MainList = reporter.MainList()
		Config = reporter.Config()
		DoneList = reporter.DoneList()
		Status = reporter.Status()

		api = ApiClass(Config)
		while True:
			Status.reporter_status(pid,{
				'mainlist.length':MainList.length(),
				'searchlist.length':L2S.length(),
				'donelist.length':DoneList.length(),
				})
			r = Status.read_all()
			debuglog(r)
			api.go_api('distribute.update',{'did':Config.read('did'),'diststate':r})
			sleep(15)
	except Exception as e:
		debuglog('reporter_proc Exception, exit.')
		debuglog(e.args)
		exit()

if __name__ == '__main__':
	try:
		debugset('psync-server/main')
		debuglog('Main Process: %d'%os.getpid())
		m_proc = Process(target=manager_proc,name='manager_proc')
		r_proc = Process(target=reporter_proc,name='reporter_proc')
		debuglog('starting manager_proc')
		m_proc.start()
		debuglog('sleep 5, and starting reporter_proc')
		sleep(5)
		r_proc.start()
		r_proc.join()
		m_proc.join()
		debuglog('Main exit')
		exit()
	except KeyboardInterrupt:
		debuglog('KeyboardInterrupt')
		debuglog('terminating reporter_proc')
		r_proc.terminate()
		debuglog('terminating manager_proc')
		m_proc.terminate()
		exit()
