#!/usr/bin/python
# -*- coding: UTF-8 -*-
from psync import psyncFileLib

p = psyncFileLib()
print u'选择本地文件所在的主机标志，系统将以这个标志在数据库中查找文件并校验。'
for d in p.distribute.values():
	print '[ID: %d] %s/%s'%(d['did'],d['distname'],d['distserver'])
selected_distribute = int(raw_input('Select Distribute: '))
for f in p.listFileByDistribute(selected_distribute,file_only=True):
	print 'checking %d'%f['fid']
	try:
		r = f.disk_hash_check()
		if not r:
			print '%d file check failed'%f['fid']
			f.load_all()
			f.distributes.remove(selected_distribute)
	except KeyboardInterrupt:
		print 'KeyboardInterrupt'
		break
		
