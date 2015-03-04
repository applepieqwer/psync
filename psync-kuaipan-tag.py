#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from psync import psyncFileLib

p = psyncFileLib()
#find tag = 6, tag for 快盘
for f in p.listFIDByMissingTag(6):
	print '[ID: %d]'%f
	pf = p.readFileByID(f)
	cmd = 'python psync-kuaipan-upload.py %s %s'%(pf['fhash'],pf.disk_location())
	r = os.system(cmd)
	if r == 0:
		pf.tags.add(6,'yes')
