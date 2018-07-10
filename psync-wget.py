from ConfigParser import ConfigParser
from json import dumps as jsonEncode
from json import loads as jsonDecode
import urllib2
import os
from psync_func import obj2dst,obj2convert,do_sha1,hash2path
from time import sleep

def makePost(fhash,Config):
	return jsonEncode({'did':Config['did'],'fhash':fhash})

def sendPost(data,Config):
	headers = {'Content-Type': 'application/json'}
	request = urllib2.Request(url=Config['jobs_url'], headers=headers, data=data)
	response = urllib2.urlopen(request)
	return jsonDecode(response.read())

def goJob(job,Config):
	cmd = 'wget -c -o \'%s/%s\' \'%s\''%(job['distserver'],hash2path(job['fhash']),obj2dst({'fhash':job['fhash']},Config))
	print cmd
	#os.system(cmd)

def goHash(job,Config):
	return do_sha1(obj2dst({'fhash':job['fhash']},Config))


def main():
	cp = ConfigParser()
	cp.read('psync.conf')
	Config = {}
	Config['data_root'] = cp.get('psync_config','data_root')
	Config['did'] = cp.getint('psync_config','did')
	Config['jobs_url'] = cp.get('psync_config','jobs_url')

	fhash_array = {}
	while True:
		r = makePost(fhash_array,Config)
		print r
		r = sendPost(r,Config)
		print r
		fhash_array = {}
		for job in r['jobs']:
			goJob(job,Config)
			if job['fhash'] != goHash(job,Config):
				pass
				#os.remove(obj2dst({'fhash':job['fhash']},Config))
		sleep(1)


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print 'KeyboardInterrupt'
		exit()