import MySQLdb
from os import getpid

from shutil import copy2 as shutil_move
#from shutil import move as shutil_move

def hash2path(h):
	return '%s/%s' % (h[0], h)

def obj2dst(obj,Config):
	return '%s/%s' % (Config.read('data_root'),hash2path(obj['fhash']))

def dict2insert(table,d):
	placeholders = ', '.join(['\'%s\''] * len(d))
	columns = ', '.join(['`%s`'] * len(d)) % tuple(d.keys())
	return "INSERT INTO `%s` ( %s ) VALUES ( %s )" % (table, columns, placeholders)

def move_file(obj,Config):
	dst = obj2dst(obj,Config)
	debuglog('moving %s \n=====> %s'%(obj['src'],dst))
	shutil_move(obj['src'],dst)
	obj['dst']=dst
	return obj


client_id = 0
mod_name = ''
debug_switch = True

def debugset(mn,ds=True):
	global client_id,mod_name,debug_switch
	client_id = str(getpid())
	mod_name = str(mn)
	debug_switch = ds

def debuglog(msg):
	global client_id,mod_name,debug_switch
	if debug_switch:
		print 'debuglog[%s/%s]: %s'%(client_id,mod_name,msg)
	return msg
