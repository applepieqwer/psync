from psync import psyncFileLib

p = psyncFileLib()
print "选择本地文件所在的主机标志，系统将以这个标志在数据库中查找文件并校验。"
for d in p.distribute.values():
	print "[ID: %d] %s/%s"%(d['did'],d['distname'],d['distserver'])
selected_distribute = int(raw_input('Select Distribute: '))
