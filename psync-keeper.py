from multiprocessing.managers import BaseManager
from time import sleep
import __builtin__
import sys
import os
from json import dumps as jsonEncode
from json import loads as jsonDecode
import urllib2

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
		response = urllib2.urlopen(request)
		r = jsonDecode(response.read())
		return r['jobs']
	except:
		return list()

class MyManager(BaseManager):
	pass

def main():
	#make connect to python server
	MyManager.register('MainList')
	MyManager.register('Config')
	MyManager.register('DB')

	manager = MyManager(address=('', 50000), authkey='1111')
	manager.connect()
	MainList = manager.MainList()
	Config = manager.Config()
	__builtin__.db = manager.DB()

	#loop
	LastLen = 0
	db_busy_count = 0
	while True:
		MainListLen = MainList.length()
		db_ready = db.ready()
		db_busy = db.busy()
		if db_busy:
			db_busy_count = db_busy_count + 1
		else:
			db_busy_count = 0
		if db_busy_count > 5:
			db_busy_count = 0
			print("psync-keeper: db.busy count to max, restart database")
			db.halt_db()
			db.init_db()
		print("psync-keeper: MainList.length = %d, db.ready = %s, db.busy = %s."%(MainListLen,db_ready,db_busy))
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
				sleep(30)
				#print 'psync-keeper: Lazytag.....+2.'
				#MainList.append(dict(mission='lazytag'))
				#MainList.append(dict(mission='lazytag'))
				#MainListLen = MainListLen + 2
				#print 'psync-keeper: Convert.....+2.'
				#MainList.append(dict(mission='convert'))
				#MainList.append(dict(mission='convert'))
				#MainListLen = MainListLen + 2
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
