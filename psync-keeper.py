from multiprocessing.managers import BaseManager
from time import sleep
import __builtin__
import sys
import os
from json import dumps as jsonEncode
from json import loads as jsonDecode
import urllib2
import socket

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
	reload(sys)
	sys.setdefaultencoding(defaultencoding)


def load_jobs_from_url(Config):
	#load objs form database tablename
	#fatch fid and mission
	print 'psync-keeper: fatch jobs from database'
	try:
		headers = {'Content-Type': 'application/json'}
		request = urllib2.Request(url=Config.get('todo_jobs_url'), headers=headers, data=jsonEncode({'did':Config.get('did')}))
		response = urllib2.urlopen(request,timeout=200)
		d = response.read()
		print d
		r = jsonDecode(d)
		return r['jobs']
	except urllib2.URLError, e:
		print 'psync-keeper: URLError'
		return list()
	except socket.timeout, e:
		print 'psync-keeper: timeout'
		return list()

class MyManager(BaseManager):
	pass

def main():
	#make connect to python server
	MyManager.register('MainList')
	MyManager.register('Config')
	#MyManager.register('DB')

	manager = MyManager(address=('', 50000), authkey='1111')
	manager.connect()
	MainList = manager.MainList()
	Config = manager.Config()
	#__builtin__.db = manager.DB()

	#loop
	LastLen = 0
	while True:
		MainListLen = MainList.length()
		print("psync-keeper: MainList.length = %d."%MainListLen)
		d = LastLen - MainListLen
		if MainListLen * 2 - LastLen < 10:
			todo_jobs = load_jobs_from_url(Config)
			if len(todo_jobs) > 0:
				for job in todo_jobs:
					print 'psync-keeper: from todo_jobs/%s[%s].'%(job['fid'],job['mission'])
					MainList.append(dict(fid=int(job['fid']),mission=job['mission']))
					MainListLen = MainListLen + 1
			else:
				print 'psync-keeper: No jobs from database,Sleeping 30 sec(s)'
				print 'psync-keeper: Lazytag.....+2.'
				MainList.append(dict(mission='lazytag'))
				MainList.append(dict(mission='lazytag'))
				MainListLen = MainListLen + 2
				print 'psync-keeper: Convert.....+2.'
				MainList.append(dict(mission='convert'))
				MainList.append(dict(mission='convert'))
				MainListLen = MainListLen + 2
				sleep(30)
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
			print 'psync-keeper: ETA: %d day(s) %d hour(s) %d min(s) later'%(day,h,m)
		print 'psync-keeper: Sleeping %d sec(s)'%(sl)
		sleep(sl)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('KeyboardInterrupt')
		exit()
