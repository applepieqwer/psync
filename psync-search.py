from multiprocessing.managers import BaseManager
from time import sleep
import os
from json import dumps as jsonEncode
from json import loads as jsonDecode
import urllib2

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

def load_jobs_from_url(Config):
	#load objs form database tablename
	#fatch fid and mission
	print 'psync-search: fatch jobs from database'
	try:
		headers = {'Content-Type': 'application/json'}
		request = urllib2.Request(url=Config.get('todo_jobs_url'), headers=headers, data=jsonEncode({'did':Config.get('did')}))
		response = urllib2.urlopen(request)
		r = jsonDecode(response.read())
		return r['jobs']
	except:
		return list()
	

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
				todo_jobs = load_jobs_from_url(Config)
				if len(todo_jobs) > 0:
					for job in todo_jobs:
						print 'psync-search: from todo_jobs/%s[%s].'%(job['fid'],job['mission'])
						MainList.append(dict(fid=int(job['fid']),mission=job['mission']))
						MainListLen = MainListLen + 1
				else:
					#print 'psync-search: Lazytag.....+2.'
					#MainList.append(dict(mission='lazytag'))
					#MainList.append(dict(mission='lazytag'))
					#MainListLen = MainListLen + 2
					print 'psync-search: Convert.....+2.'
					MainList.append(dict(mission='convert'))
					MainList.append(dict(mission='convert'))
					MainListLen = MainListLen + 2
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

	
	

	
