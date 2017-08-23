from multiprocessing.managers import BaseManager
from time import sleep
import os

class MyManager(BaseManager):
	pass

MyManager.register('List2Search')
MyManager.register('MainList')
MyManager.register('Config')

#search and create:
# obj['src'] ---------It is the source of file.
# obj['filename'] ----------the filename
# obj['mission'] ---------mission: import 

if __name__ == '__main__':
	manager = MyManager(address=('', 50000), authkey='1111')
	manager.connect()
	L2S = manager.List2Search()
	MainList = manager.MainList()
	Config = manager.Config()
	while True:
		if L2S.length():
			d = L2S.popleft()
			print d
			if os.path.isdir(d):
				for fname in os.listdir(d):
					f = os.path.join(d,fname)
					print f
					if os.path.islink(f):
						continue
					if os.path.isdir(f):
						L2S.append(f)
						continue
					if os.path.isfile(f):
						if f.endswith(Config.get('endswith')):
							MainList.append(dict(mission='import', src=f, filename=fname))
		else:
			MainListLen = MainList.length()
			print 'psync-search: Search(%d)/MainList(%d)'%(L2S.length(),MainListLen)
			if MainListLen < 10:
				MainList.append(dict(mission='lazycheck'))
			sl = 15 * MainListLen + 1
			print 'psync-search: Sleeping %d sec(s)'%(sl)
			sleep(sl)

	
	

	
