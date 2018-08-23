from ConfigParser import ConfigParser
from json import dumps as jsonEncode
from json import loads as jsonDecode
import urllib2
from psync_func import obj2dst,obj2face,do_sha1,hash2path,face2path,saveEncoding
from psync_func import ConfigClass
import face_recognition
from PIL import Image
from time import sleep

def makePost(face_array,Config):
	return jsonEncode({'did':Config['did'],'face_array':face_array})

def sendPost(data,Config):
	headers = {'Content-Type': 'application/json'}
	request = urllib2.Request(url=Config['face_url'], headers=headers, data=data)
	#request.set_proxy('172.31.1.246:8080','http')
	response = urllib2.urlopen(request)
	return jsonDecode(response.read())

def goFace(job,Config):
	size = 200,200
	face_data = {}
	src = obj2dst({'fhash':job['fhash']},Config)
	print job['fhash']
	image = face_recognition.load_image_file(src)
	face_locations = face_recognition.face_locations(image)
	face_encodings = face_recognition.face_encodings(image,face_locations)
	c = len(face_locations)
	if c < 1:
		face_data['%s.0-0-0-0'%job['fhash']]={
			'fhash':job['fhash'],
			'face_top':0,
			'face_right':0,
			'face_bottom':0,
			'face_left':0,
			'face_location':None,
			'face_encoding':None}
		return face_data
	for i in range(c):
		top, right, bottom, left = face_locations[i]
		print 'found face at Top: {}, Left: {}, Bottom: {}, Right: {}'.format(top, left, bottom, right)
		
		face_icon = Image.fromarray(image[top:bottom, left:right])
		face_icon.thumbnail(size, Image.ANTIALIAS)
		
		#save to disk
		dst = obj2face({'fhash':job['fhash']},Config,'%d-%d-%d-%d'%(top, left, bottom, right))
		face_icon.save(dst,'JPEG')
		print 'face saved to %s'%(dst)
		
		#save to str
		#buffer = cStringIO.StringIO()
		#face_icon.save(buffer, format="JPEG")

		face_data['%s.%d-%d-%d-%d'%(job['fhash'], top, left, bottom, right)]={
			'fhash':job['fhash'],
			'face_top':top,
			'face_right':right,
			'face_bottom':bottom,
			'face_left':left,
			'face_location':face_locations[i],
			'face_encoding':face_encodings[i]}
	return face_data

def goHash(job,Config):
	return do_sha1(obj2dst({'fhash':job['fhash']},Config))

def main():
	cp = ConfigParser()
	cp.read('psync.conf')
	Config = ConfigClass()
	Config['data_root'] = cp.get('psync_config','data_root')
	Config['did'] = cp.getint('psync_config','did')
	Config['face_url'] = cp.get('psync_web_config','face_jobs_url')

	face_array = list()
	while True:
		r = makePost(face_array,Config)
		print r
		r = sendPost(r,Config)
		print r
		face_array = list()
		for job in r['jobs']:
			if job['fhash'] == goHash(job,Config):
				face_data = goFace(job,Config)
				saveEncoding(face_data,Config)
				for f in face_data.values():
					del f['face_location']
					del f['face_encoding']
					face_array.append(f)
	sleep(1)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print 'KeyboardInterrupt'
		exit()