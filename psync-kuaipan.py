#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import os
import kuaipan

def print_help():
	print 'Usage: python',sys.argv[0],'hash','file'
	print 'Return value: 0 success, 1 error'

if len(sys.argv)<3:
	print_help()
	exit(1)

filehash = sys.argv[1]
filename = sys.argv[2]
(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.lstat(filename)
bs = int(size / 100 / 1024 / 1024) + 1
cnt = int(size / (bs *1024 * 1024)) + 1
for i in range(cnt):
	cmd = 'dd if=\"' + filename + '\" of = .kuaipan_tmp bs=' + str(bs) + 'M skip=' + str(i) + ' count=1'
	print cmd
	kf_name = '/' + filehash[1] + '/' + filehash + '/' + os.path.basename(filename) + '.p' + str(i)
	print kf_name
