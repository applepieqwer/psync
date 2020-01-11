#!/usr/bin/python
# -*- coding: UTF-8 -*-
from psync import psyncFileLib
import os

p = psyncFileLib()
#find tag = 5, tag for Size
for f in p.listFIDByMissingTag(5):
	pf = p.readFileByID(f)
	(mode, ino, dev, nlink, uid, gid, fsize, atime, mtime, ctime) = os.lstat(pf.disk_location())
	if fsize > 0:
		#add new tag
		print '[ID: %d]'%f
		pf.tags.add(5,str(fsize))
