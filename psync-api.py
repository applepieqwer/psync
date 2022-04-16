from psync_func import go_api
import getopt
import sys
import json

if __name__ == '__main__':
	action = ''
	payload = 'null'
	try:
		options,args = getopt.getopt(sys.argv[1:],'a:p:Jh', ['action=','payload='])
		for name,value in options:
			if name in ('-h','--help'):
				action = ''
			if name in ('-a','--action'):
				action = value
			if name in ('-p','--payload'):
				payload = json.loads(value)
			if name in ('-J'):
				action = 'wxpusher.push'
				payload = {"content":"Job Done."}
		if action != '':
			r = go_api(action,payload)
			print r
			sys.exit()
		else:
			print "%s usage:"%sys.argv[0]
			print "    -a --action      : API action, default:echo"
			print "    -p --payload     : API payload, default:{\"msg\":\"hello world\"}"
			print "    -J               : Send \"Job Done\" with wxpusher"
			print "example:"
			print "    python psync-api.py -J"
			print "    python psync-api.py -a \'wxpusher.push\' -p \'{\"content\":\"hello world\"}\'"
			print "note:"
			print "    setup url and token in psync.conf first"
			sys.exit()
	except getopt.GetoptError:
		print "%s: getopt.GetoptError"%sys.argv[0]
		sys.exit()
