#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import os
import json
import kuaipan

def print_help():
	print 'Usage: python',sys.argv[0],'hash','file'
	print 'Return value: 0 success, 1 error'

def sha1sum(filepath):
	f = os.popen('sha1sum -b \'' + filepath + '\'')
	return f.readline()[:40]

if len(sys.argv)<3:
	print_help()
	exit(1)

KUAIPAN_TMP = '/tmp/.kuaipan_tmp'
filehash = sys.argv[1]
filename = sys.argv[2]
(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.lstat(filename)
bs = int(size / 100 / 1024 / 1024) + 1
cnt = int(size / (bs *1024 * 1024)) + 1
tasks = []
for i in range(cnt):
	cmd = 'dd if=\"' + filename + '\" of=' + KUAIPAN_TMP + ' bs=' + str(bs) + 'M skip=' + str(i) + ' count=1'
	kf_name = '/' + filehash[0] + '/' + filehash + '/' + os.path.basename(filename) + '.p' + str(i)
	tasks.append({'cmd':str(cmd),'kf_name':str(kf_name),'hash':None})
tasks_dir = '/' + filehash[0] + '/' + filehash

###ready to check and upload
CACHED_KEYFILE = '.cached_kuaipan_key.json'
try:
	kf = kuaipan.load(CACHED_KEYFILE)
except:
	kf = kuaipan.auth_me(CACHED_KEYFILE)

#ai = kf.account_info()
#print 'Account name:',ai['user_name']
#print 'Quota used pct: %d%%'%(ai['quota_used']/ ai['quota_total']*100)
hash_list=[]
kf_info = 503
while (kf_info == 503):
	kf_info = kf.metadata(tasks_dir)
	if type(kf_info) is int:
		if kf_info == 404:
			kf.fileops_create_folder(tasks_dir)
			break
		else:
			kf_info = 503
			continue
	if 'files' in kf_info.keys():
		for i in kf_info['files']:
			if  i['is_deleted'] == False and i['type']=='file':
				hash_list.append(str(i['sha1']))
print 'hash_list',hash_list

for i in range(cnt):
	os.system(tasks[i]['cmd'])
	target_hash = sha1sum(KUAIPAN_TMP)
	print '%d/%d hash = %s'%(i+1,cnt,target_hash)
	if target_hash not in hash_list:
		while (target_hash != tasks[i]['hash']):
			kf_info = 503
			while (kf_info == 503):
				kf_info = kf.metadata(tasks[i]['kf_name'])
				if type(kf_info) is int:
					if kf_info == 404:
						#upload it
						print 'upload it'
						kf.upload_file(KUAIPAN_TMP, kuaipan_path=tasks[i]['kf_name'], ForceOverwrite=True)
					kf_info = 503
				else:
					if 'sha1' in kf_info.keys():
						tasks[i]['hash'] = str(kf_info['sha1'])
exit(0)
