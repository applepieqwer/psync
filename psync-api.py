from ConfigParser import ConfigParser
import os
import getopt
import sys
def main(url,action='echo',payload=''):
	d = '{\"action\":\"%s\",\"payload\":{%s}}'%(action,payload)
	cmd = 'curl -H \"Accept: application/json\" -H \"Content-type: application/json\" -X POST -d \'%s\' %s'%(d,url)
	os.system(cmd) 

if __name__ == '__main__':
	cp = ConfigParser()
	cp.read('psync.conf')
	url = cp.get('psync_api','psync_api_url')
	action = ''
	payload = 'null'
	try:
		options,args = getopt.getopt(sys.argv[1:],'a:p:', ['action=','payload='])
		for name,value in options:
			if name in ('-a','--action'):
				action = value
			if name in ('-p','--payload'):
				payload = value
		if action != '':
			main(url,action,payload)
		else:
			print "%s usage:"%sys.argv[0]
			print "-a --action      : API action, default:echo"
			print "-p --payload     : API payload, default:\"msg\":\"hello world\""
			sys.exit()
	except getopt.GetoptError:
		sys.exit()
