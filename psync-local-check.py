####check fhash with local list
####input file is "psync-local-check.input"
####download all the fhash with:
####mysql --compress -upsync -p -hpsync.db.6677333.hostedresource.com psync -ss -e 'SELECT `fhash` FROM `file`;' | sed 's/\t/","/g;s/^//;s/$//;s/\n//g' > psync-local-check.input
####mysql --compress -upsync -p -hpsync.db.6677333.hostedresource.com psync < sql_log2020-10-18-4192.sql

import __builtin__
import os
from ConfigParser import ConfigParser
from psync_func import ConfigClass,CheckLocal_sql,CheckLocal_wget
from psync_func import debuglog,debugset,do_sha1,obj2dst

def main():
	debugset('psync-local-check')
	cp = ConfigParser()
	cp.read('psync.conf')
	Config = ConfigClass()
	Config['data_root'] = cp.get('psync_config','data_root')
	Config['did'] = cp.getint('psync_config','did')
	Config['distname'] = cp.get('psync_config','distname')
	Config['disttype'] = cp.get('psync_config','disttype')
	Config['diststate'] = cp.get('psync_config','diststate')
	Config['distserver'] = cp.get('psync_config','distserver')
	Config['wget_target_url'] = cp.get('psync_local','wget_target_url')

	CheckMan = CheckLocal_wget()
	with open('psync-local-check.input', 'r') as f:
		lines = f.readlines()
		total = len(lines)
		for i in range(total):
			fhash = lines[i].strip()
			debuglog('%d/%d: %s'%(i,total,fhash))
			CheckMan.check({'fhash':fhash},Config)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print 'KeyboardInterrupt'
		exit()