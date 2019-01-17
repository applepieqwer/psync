from psync_func import debuglog,obj_is_here,size_file,readdate,readEXIFmodel,readEXIFdate,readEXIForientation,readEXIFwidth,readEXIFheight

def sql_replace_filetagvalue(fid,tid,value):
	sql = "REPLACE INTO `file_tag` (`fid`,`tid`,`filetagvalue`) VALUES (%s,%s,'%s')"%(fid,tid,value)
	debuglog(sql)
	cur.execute(sql)
	db.commit()

def save_tag(obj,Config):
	if not obj_is_here(obj,Config):
		raise UserWarning,'obj is not here'
		return obj
	tags_dict = [{'tid':1,'func':readdate},
				{'tid':2,'func':readEXIFmodel},
				{'tid':5,'func':size_file},
				{'tid':6,'func':readEXIForientation},
				{'tid':7,'func':readEXIFwidth},
				{'tid':8,'func':readEXIFheight}]

	for tag in tags_dict:
		v = tag['func'](obj,Config)
		if v is not False:
			sql_replace_filetagvalue(obj['fid'],tag['tid'],v)
	return obj


def do(obj,Config):
	mission = obj['mission']
	if mission in ['import','lazytag']:
		return save_tag(obj,Config)
	return obj