from psync import psyncFileLib
p = psyncFileLib()
p.selectDistribute()
if p.testDistribute():
	f = p.searchFile()
	cur = 1
	total = len(f)
	for i in f:
		print '[%d/%d] %s'%(cur,total,i)
		p.import_and_link(i)
		cur = cur + 1
