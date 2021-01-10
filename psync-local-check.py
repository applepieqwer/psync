####check fhash with local list
####input file is "psync-local-check.input"
####download all the fhash with:
####mysql --compress -upsync -p -hpsync.db.6677333.hostedresource.com psync -ss -e 'SELECT `fhash` FROM `file`;' | sed 's/\t/","/g;s/^//;s/$//;s/\n//g' > psync-local-check.input
####upload sql to mysql server:
####mysql -v --compress -upsync -p -hpsync.db.6677333.hostedresource.com psync < sql_log2020-10-18-4192.sql

import __builtin__
import os
from ConfigParser import ConfigParser
from psync_func import ConfigClass,CheckLocal_sql,CheckLocal_wget
from psync_func import debuglog,debugset,do_sha1,obj2dst
import getopt
import sys

def main(action,filter_fhash='',target_folder=''):
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

	if action == 'wget':
		CheckMan = CheckLocal_wget()
	if action == 'sql':
		CheckMan = CheckLocal_sql()
	if action == '7zip':
		CheckMan = CheckLocal_7zip(target_folder=target_folder)
	with open('psync-local-check.input', 'r') as f:
		lines = f.readlines()
		total = len(lines)
		for i in range(total):
			fhash = lines[i].strip()
			if fhash.find(filter_fhash) != 0:
				debuglog('%d/%d: skipped'%(i,total))
				continue
			debuglog('%d/%d: %s'%(i,total,fhash))
			CheckMan.check({'fhash':fhash},Config)

if __name__ == '__main__':
	debugset('psync-local-check')
	filter_fhash = ''
	target_folder = ''
	action = ''
	try:
	    options,args = getopt.getopt(sys.argv[1:],'hf:t:du:wsz', ['help','filter=','target=','download','upload=','wget','sql','7zip'])
	    for name,value in options:
	    	if name in ('-f','--filter'):
	    		filter_fhash = value
	    		debuglog('filter_fhash: %s'%value)
	    	if name in ('-t','--target'):
	    		target_folder = value
	    		debuglog('target_folder: %s'%value)
	    	if name in ('-w','--wget'):
	    		action = 'wget'
	    	if name in ('-s','--sql'):
	    		action = 'sql'
	    	if name in ('-z','--7zip'):
	    		action = '7zip'
	    	if name in ('-d','--download'):
	    		print "Download: mysql --compress -upsync -p -hpsync.db.6677333.hostedresource.com psync -ss -e 'SELECT `fhash` FROM `file`;' | sed 's/\\t/\",\"/g;s/^//;s/$//;s/\\n//g' > psync-local-check.input"
	    		sys.exit()
	    	if name in ('-u','--upload'):
	    		print "Upload: mysql -v --compress -upsync -p -hpsync.db.6677333.hostedresource.com psync < %s"%value
	    		sys.exit()
	    if action != '':
	    	main(action,filter_fhash,target_folder)
	    else:
	    	print "%s usage:"%sys.argv[0]
	    	print "-h --help       : Show this help"
	    	print "-f --filter     : Filter for fhash(example: aa will filter aabcde)"
	    	print "-d --download   : Download fhash list from mysql server"
	    	print "-u --upload sql : Upload sql script file to mysql server"
	    	print "-w --wget       : Check fhash and output wget script"
	    	print "-s --sql        : Check fhash and output sql script"
	    sys.exit()
	except getopt.GetoptError:
	    sys.exit()
	except KeyboardInterrupt:
		print 'KeyboardInterrupt'
		sys.exit()