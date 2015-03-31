#!/usr/bin/python
# -*- coding: UTF-8 -*-
from psync import psyncFileLib

p = psyncFileLib()
p.selectLocal()
for f in p.listFileByDistribute(p.selected_local,file_only=True):
	print 'checking %d'%f['fid']
	try:
		r = f.disk_hash_check()
		if not r:
			print '%d file check failed'%f['fid']
			f.load_all()
			f.distributes.remove(p.selected_local)
	except KeyboardInterrupt:
		print 'KeyboardInterrupt'
		break
		
