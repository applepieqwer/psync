### show msg at awtrix
from time import sleep
from psync_func import debuglog,debugset
import os
import getopt
import sys

def main(i,n,s,m):
	print "awtrix server: %s"%s
	cmd = "curl -X POST --header 'Content-Type: application/json' -d '{\"force\":true, \"text\": \"%s\", \"color\":[0,255,0], \"repeat\":1, \"duration\":%d}' 'http://%s:7000/api/v3/notify'"%(m,i,s)
	while n!=0:
		print "Loop #%d"%n
		os.system(cmd)
		if n < 0:
			n = -1
		else:
			n = n - 1
		print "Sleep %d sec(s),Ctrl-c to Interrupt"%i
		sleep(i)
			
if __name__ == '__main__':
	debugset('psync-awtrix')
	
	loop = 1  #default one loop
	interval = 60  #default interval 60 secs
	awtrix_server = "192.168.1.250"  ###default server
	msg = "" ###default msg
	try:
	    options,args = getopt.getopt(sys.argv[1:],'i:n:sm:h', ['interval=','loop=','server=','msg=','help'])
	    for name,value in options:
	    	if name in ('-i','--interval'):
	    		interval = int(value)
	    		##debuglog('interval: %s'%value)
	    	if name in ('-n','--loop'):
	    		loop = int(value)
	    		##debuglog('loop: %s'%value)
	    	if name in ('-s','--server'):
	    		awtrix_server = value
	    		##debuglog('awtrix server: %s'%value)
	    	if name in ('-m','--msg'):
	    		msg = value.strip()
	    if msg != '':
	    	main(interval,loop,awtrix_server,msg)
	    else:
	    	print "%s usage:"%sys.argv[0]
	    	print "-i --interval   : loop interval, default: 60 secs"
	    	print "-n --loop       : loop times, -1 = loop forever, default: 1 loop"
	    	print "-s --server     : awtrix server, default: 192.168.1.250"
	    	print "-m --msg        : message"
	    	print "-h --help       : Show this help"
	    sys.exit()
	except getopt.GetoptError:
	    sys.exit()
	except KeyboardInterrupt:
		print 'KeyboardInterrupt'
		sys.exit()