from multiprocessing.managers import BaseManager
from time import sleep
import os
import sys

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
	reload(sys)
	sys.setdefaultencoding(defaultencoding)

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
			d = L2S.get()
			print d
			if os.path.isdir(d):
				for fname in os.listdir(d):
					f = os.path.join(d,fname)
					print f
					if os.path.islink(f):
						continue
					if os.path.isdir(f):
						L2S.put(f)
						continue
					if os.path.isfile(f):
						if f.endswith(Config.get('endswith')):
							MainList.put(dict(mission='import', src=f, filename=fname))
		else:
			print "psync-search: nothing to do....sleeping"
			sleep(60) #sleep 1 min
	

	
