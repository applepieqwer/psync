####check fhash with local list
####input file is "psync-local-check.input"
####download all the fhash with:
####mysql --compress -upsync -p -hpsync.db.6677333.hostedresource.com psync -ss -e 'SELECT `fhash` FROM `file`;' | sed 's/\t/","/g;s/^//;s/$//;s/\n//g' > psync-local-check.input
####mysql --compress -upsync -p -hpsync.db.6677333.hostedresource.com psync < sql_log2020-10-18-4192.sql

import __builtin__
import os
from ConfigParser import ConfigParser
from psync_func import ConfigClass
from psync_func import debuglog,debugset,dbClassLocal,do_sha1,obj2dst

def sql_delete_did(fhash,did):
	sql = "DELETE FROM `file_distribute` WHERE `file_distribute`.`fid` IN (SELECT `fid`  FROM `file` WHERE `fhash` = '%s') AND `file_distribute`.`did` = %s LIMIT 1"%(fhash,did)
	db.execute(sql)

def check_fail(fhash,Config):
	sql_delete_did(fhash,Config.read('did'))
	debuglog('Error: %s <==============Check Fail'%fhash)

def check_pass(fhash,Config):
	pass

def main():
	debugset('psync-local-check')
	__builtin__.db = dbClassLocal()
	cp = ConfigParser()
	cp.read('psync.conf')
	Config = ConfigClass()
	Config['data_root'] = cp.get('psync_config','data_root')
	Config['did'] = cp.getint('psync_config','did')
	Config['distname'] = cp.get('psync_config','distname')
	Config['disttype'] = cp.get('psync_config','disttype')
	Config['diststate'] = cp.get('psync_config','diststate')
	Config['distserver'] = cp.get('psync_config','distserver')

	with open('psync-local-check.input', 'r') as f:
		lines = f.readlines()
		total = len(lines)
		for i in range(total):
			fhash = lines[i].strip()
			debuglog('%d/%d: %s'%(i,total,fhash))
			src = obj2dst({'fhash':fhash},Config)
			if not os.path.isfile(src):
				check_fail(fhash,Config)
			else:
				if fhash == do_sha1(src):
					check_pass(fhash,Config)
				else:
					check_fail(fhash,Config)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print 'KeyboardInterrupt'
		exit()