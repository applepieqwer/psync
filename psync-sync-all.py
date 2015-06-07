#!/usr/bin/python
# -*- coding: UTF-8 -*-
from psync import psyncFileLib

p = psyncFileLib()
p.selectDistribute()
print "将\"%s\"的文件同步到\"%s\"？"%(p.distribute[p.selected_local]['distname'].encode('utf8'),p.distribute[p.selected_distribute['did']]['distname'].encode('utf8'))
if raw_input('Select Y or n: ') == 'Y':
	print "开始同步"
	local_did = p.selected_local
	dist_did = p.selected_distribute['did']
	local_fid_list = p.listFIDByDistribute(local_did)
	dist_fid_list = p.listFIDByDistribute(dist_did)
	for i in [x for x in local_fid_list if x not in dist_fid_list]:
		print "正在同步[ID:%d]"%i
		r = p.syncFile(dist_did,i)
		if r:
			print "同步成功"
		else:
			print "同步失败"
else:
	print "退出"
