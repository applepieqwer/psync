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
	LastLen = 0
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
			d = LastLen - MainListLen
			while MainListLen * 2 - LastLen < 10:
				print 'psync-search: Lazytag.....+1.'
				MainList.append(dict(mission='lazytag'))
				MainListLen = MainListLen + 1
				print 'psync-search: Convert.....+1.'
				MainList.append(dict(mission='convert'))
				MainListLen = MainListLen + 1
			sl = 30
			if d > 0:
				eta = sl * MainListLen / d
			else:
				eta = -1.0
			LastLen = MainListLen
			if eta >= 0:
				day = eta / 60 / 60 / 24
				h = eta % (60*60*24) / 60 / 60
				m = eta % (60*60) / 60
				print 'psync-search: ETA: %d day(s) %d hour(s) %d min(s) later'%(day,h,m)
			print 'psync-search: Sleeping %d sec(s)'%(sl)
			sleep(sl)

	
	

	
