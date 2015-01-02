#!/usr/bin/python
# -*- coding: UTF-8 -*-
#---------------------linux only-----------------------
#this is a picture sync tool

import os
from os.path import isfile
import time
import sys, select
import pickle
import MySQLdb
from MySQLdb import IntegrityError
from skylark import Database, Model, Field, PrimaryKey, ForeignKey, fn, distinct
from base64 import b64encode,b64decode
from ftplib import FTP
from copy import deepcopy
import pyexiv2

#define MySQL ORM	
class File(Model):
	table_name = 'file'
	fid = PrimaryKey()
	fhash = Field()
	type = Field()
	ctime = Field()
	filename = Field()
	filetime = Field()

class Tag(Model):
	table_name = 'tag'
	tid = PrimaryKey()
	tagname = Field()

class File_Tag(Model):
	table_name = 'file_tag'
	fid = PrimaryKey()
	tid = PrimaryKey()
	filetagvalue = Field()

class Distribute(Model):
	table_name = 'distribute'
	did = PrimaryKey()
	distname = Field()
	disttype = Field()
	distserver = Field()


class File_Distribute(Model):
	table_name = 'file_distribute'
	fid = PrimaryKey()
	did = PrimaryKey()
	dtime = Field()

class Converter(Model):
	table_name = 'converter'
	cid = PrimaryKey()
	ctype = Field()
	cvalue = Field()

class File_Converter(Model):
	table_name = 'file_converter'
	fid = PrimaryKey()
	cid = PrimaryKey()
	result = Field()
	convert_time = Field()

#joint MySQL ORM , work with mysql view
class File_Tag_View(Model):
	table_name = 'file_tag_view'
	fid = PrimaryKey()
	fhash = Field()
	type = Field()
	ctime = Field()
	filename = Field()
	filetime = Field()
	tid = PrimaryKey()
	tagname = Field()
	filetagvalue = Field()

class File_Distribute_View(Model):
	table_name = 'file_distribute_view'
	fid = PrimaryKey()
	fhash = Field()
	type = Field()
	ctime = Field()
	filename = Field()
	filetime = Field()
	did = PrimaryKey()
	distname = Field()
	disttype = Field()
	distserver = Field()
	dtime = Field()

class File_Converter_View(Model):
	table_name = 'file_converter_view'
	fid = PrimaryKey()
	fhash = Field()
	type = Field()
	ctime = Field()
	filename = Field()
	filetime = Field()
	cid = PrimaryKey()
	ctype = Field()
	cvalue = Field()
	result = Field()
	convert_time = Field()

class psyncFileTag():
	def __init__(self,fid):
		self.__tag = {}
		self.__fid = deepcopy(fid)
		self.recheck()
	def __getitem__(self, key):
		return self.__tag[key]['value']
	def __setitem__(self, key,value):
		#this is update not insert,use 'add' for new tag
		tid = self.__tag[key]['tid']
		self.__tag[key]['value'] = value
		File_Tag.where(fid=self.__fid,tid=tid).update(filetagvalue = value).execute()
	def __iter__(self):
		return iter(self.__tag)
	def __str__(self):
		if len(self.__tag) == 0:
			return 'no tags' 
		r = ''
		for k in self.__tag.keys():
			r = r + ('#%s): %s = %s\n' %(self.__tag[k]['tid'],k,self.__tag[k]['value']))
		r = r + 'total %d tags'%len(self.__tag)
		return r.encode('utf8')
	def xml(self):
		if len(self.__tag) == 0:
			return '<count>0</count>'
		r = '<count>%d</count>'%len(self.__tag)
		for k in self.__tag.keys():
			r = r + '<t><tid>%s</tid><name>%s</name><value>%s</value></t>'%(self.__tag[k]['tid'],k,self.__tag[k]['value'])
		return r.encode('utf8')
	def recheck(self):
		tagid = deepcopy(psyncFileLib.tag)
		for t in File_Tag.findall(fid = self.__fid):
			self.__tag[tagid[t.tid]['tagname']]={'tid':t.tid,'value':t.filetagvalue}
	def add(self,tid,value):
		File_Tag.create(fid=self.__fid,tid=tid,filetagvalue=value)
		#reload
		self.recheck()

class psyncFileConverter():
	def __init__(self,fid):
		self.__conv = {}
		self.__fid = deepcopy(fid)
		self.recheck()
	def __getitem__(self, key):
		return self.__conv[key]['result']
	def __setitem__(self, key,value):
		#this is update not insert,use 'add' for new converter
		cid = self.__conv[key]['cid']
		self.__conv[key]['result'] = value
		File_Converter.where(fid=self.__fid,cid=cid).update(result = value).execute()
	def __iter__(self):
		return iter(self.__conv)
	def __str__(self):
		if len(self.__conv) == 0:
			return 'no converters' 
		r = ''
		for k in self.__conv.keys():
			r = r + '#%s): %s %s @%s\n' %(self.__conv[k]['cid'],k,self.__conv[k]['result'],self.__conv[k]['convert_time'])
		r = r + 'total %d converters'%len(self.__conv)
		return r.encode('utf8')
	def xml(self):
		if len(self.__conv) == 0:
			return '<count>0</count>'
		r = '<count>%d</count>'%len(self.__conv)
		for k in self.__conv.keys():
			r = r + '<c><cid>%s</cid><cvalue>%s</cvalue><result>%s</result><convert_time>%s</convert_time></c>'%(self.__conv[k]['cid'],k,self.__conv[k]['result'],self.__conv[k]['convert_time'])
		return r.encode('utf8')
	def recheck(self):
		convid = deepcopy(psyncFileLib.converter)
		for t in File_Converter.findall(fid = self.__fid):
			self.__conv[convid[t.cid]['cvalue']]={'cid':t.cid,'result':t.result,'convert_time':t.convert_time}
	def add(self,cid,result):
		File_Converter.create(fid=self.__fid,cid=cid,result=result)
		#reload
		self.recheck()
	def is_converted(self,cvalue):
		return (cvalue in self.__conv.keys())
	def keys(self):
		return self.__conv.keys()

class psyncFileDistribute():
	def __init__(self,fid):
		self.__dist = {}
		self.__fid = deepcopy(fid)
		self.recheck()
	def __getitem__(self, key):
		return self.__dist[key]['dtime']
	def __iter__(self):
		return iter(self.__dist)
	def __str__(self):
		if len(self.__dist) == 0:
			return 'no distributes' 
		r = ''
		for k in self.__dist.keys():
			r = r + '#%s): %s @%s\n' %(self.__dist[k]['did'],k,self.__dist[k]['dtime'])
		r = r + 'total %d distributes'%len(self.__dist)
		return r.encode('utf8')
	def xml(self):
		if len(self.__dist) == 0:
			return '<count>0</count>'
		r = '<count>%d</count>'%len(self.__dist)
		for k in self.__dist.keys():
			r = r + '<d><did>%s</did><distname>%s</distname><dtime>%s</dtime></d>'%(self.__dist[k]['did'],k,self.__dist[k]['dtime'])
		return r.encode('utf8')
	def recheck(self):
		distid = deepcopy(psyncFileLib.distribute)
		for t in File_Distribute.findall(fid = self.__fid):
			self.__dist[distid[t.did]['distname']]={'did':t.did,'dtime':t.dtime}
	def add(self,did):
		File_Distribute.create(fid=self.__fid,did=did)
		#reload
		self.recheck()
	def remove(self,did):
		File_Distribute.where(fid=self.__fid,did=did).delete().execute()
		#reload
		self.recheck()

class psyncFile():
	def __init__(self,f,file_only=False):
		self.__f = None
		self.tags = None
		self.converters = None
		self.distributes = None
		if f == None:
			raise ValueError('File ORM Object is None')
		self.__f = deepcopy(f)
		if not file_only:
			self.load_all()

	#重新加载所有附加内容
	def load_all(self):
		self.tags = psyncFileTag(f.fid)
		self.converters = psyncFileConverter(f.fid)
		self.distributes = psyncFileDistribute(f.fid)
		
	def __getitem__(self, i):
		return self.__f.__getattribute__(i)

	def __str__(self):
		r = 'file hash:%s\n'%self.__f.fhash
		r = r + 'file location:%s\n'%self.disk_location()
		r = r + 'file type:%s\n'%self.__f.type
		r = r + '==tags:\n'
		r = r + str(self.tags).decode('utf8') + '\n'
		r = r + '==distributes:\n'
		r = r + str(self.distributes).decode('utf8') + '\n'
		r = r + '==converters:\n'
		r = r + str(self.converters).decode('utf8')
		return r.encode('utf8')

	#根据文件类型确定后缀名
	def mime2extension(self,t):
		if t == 'image/gif':
			return '.gif'
		elif t == 'image/jpeg':
			return '.jpg'
		elif t == 'video/mp4':
			return '.mp4'
		elif t == 'video/mpeg':
			return '.mpeg'
		elif t == 'video/quicktime':
			return '.mov'
		elif t == 'video/mp2t':
			return '.mts'
		elif t == 'video/3gpp':
			return '.3gp'
		elif t == 'video/x-msvideo':
			return '.avi'
		else:
			print '!!!!!unknow type:',t
			return '.unknown'

	def xml(self,default_image_cvalue='1024',default_video_cvalue='1280x720'):
		r = '<psync_file>'
		r = r + '<fid>%d</fid>'%self.__f.fid
		r = r + '<fhash>%s</fhash>'%self.__f.fhash
		r = r + '<type>%s</type>'%self.__f.type
		r = r + '<ctime>%s</ctime>'%self.__f.ctime
		r = r + '<disk_filename>%s</disk_filename>'%self.disk_filename()
		r = r + '<disk_location>%s</disk_location>'%self.disk_location()
		r = r + '<url_location>%s</url_location>'%self.url_location()
		if self.__f.type[:5] == 'video':
			# for video
			#url_gif_location is the default preview
			r = r + '<url_gif_location>%s</url_gif_location>'%self.url_video_converter_gif_location()
			r = r + '<url_flv_location>%s</url_flv_location>'%self.url_video_converter_flv_location(default_video_cvalue)
			if self.converters != None:
				for k in self.converters.keys():
					r = r + '<video>'
					r = r + '<cvalue>%s</cvalue>'%k
					#url_flv_location is the default video format
					r = r + '<url_video_converter_flv_location>%s</url_video_converter_flv_location>'%self.url_video_converter_flv_location(k)
					#url_flv_image_location is 4 images preview
					for i in range(4):
						r = r + '<url_video_converter_images_location>%s</url_video_converter_images_location>'%self.url_video_converter_images_location(k,i)
					r = r + '</video>'
		if self.__f.type[:5] == 'image':
			# for image
			r = r + '<url_img_location>%s</url_img_location>'%self.url_converter_location(default_image_cvalue)
			if self.converters != None:
				for k in self.converters.keys():
					r = r + '<image>'
					r = r + '<cvalue>%s</cvalue>'%k
					r = r + '<url_converter_location>%s</url_converter_location>'%self.url_converter_location(k)
					r = r + '</image>'
			
		if self.tags != None:
				r = r + '<tags>%s</tags>'%self.tags.xml().decode('utf8')
		if self.converters != None:
				r = r + '<converters>%s</converters>'%self.converters.xml().decode('utf8')
		if self.distributes != None:
				r = r + '<distributes>%s</distributes>'%self.distributes.xml().decode('utf8')
		r = r + '</psync_file>'
		return r.encode('utf8')

	def disk_filename(self):
		return u'%s%s' % (self.__f.fhash, self.mime2extension(self.__f.type))
	def disk_location(self):
		return u'/home/applepie/Data/psync/%s/%s' % (self.__f.fhash[0], self.disk_filename())
	def url_location(self):
		return u'/psync/%s/%s' %(self.__f.fhash[0], self.disk_filename())
	def disk_converter_location(self,cvalue):
		return u'/home/applepie/Data/psync/%s/converter/%s.%s%s' % (self.__f.fhash[0], self.__f.fhash, cvalue, switch_type(self.__f.type))
	def url_converter_location(self,cvalue):
		return u'/psync/%s/converter/%s.%s%s' % (self.__f.fhash[0], self.__f.fhash, cvalue, switch_type(self.__f.type))
	def disk_video_converter_dir(self):
		return u'/home/applepie/Data/psync/%s/converter/%s/' % (self.__f.fhash[0], self.__f.fhash)
	def disk_video_converter_flv_location(self,cvalue):
		return u'%s%s.%s.flv' % (self.disk_video_converter_dir(),self.__f.fhash,cvalue)
	def url_video_converter_flv_location(self,cvalue):
		return u'/psync/%s/converter/%s/%s.%s.flv' % (self.__f.fhash[0], self.__f.fhash,self.__f.fhash,cvalue)
	def disk_video_converter_images_list(self,cvalue):
		return u'%s%s.%s-%%d.jpg' % (self.disk_video_converter_dir(),self.__f.fhash,cvalue)
	def disk_video_converter_images_location(self,cvalue,i):
		return u'%s%s.%s-%d.jpg' % (self.disk_video_converter_dir(),self.__f.fhash,cvalue,i)
	def url_video_converter_images_location(self,cvalue,i):
		return u'/psync/%s/converter/%s/%s.%s-%d.jpg' % (self.__f.fhash[0],self.__f.fhash,self.__f.fhash,cvalue,i)
	def disk_video_converter_gif_location(self):
		return u'%s%s.gif' % (self.disk_video_converter_dir(),self.__f.fhash)
	def url_video_converter_gif_location(self):
		return u'/psync/%s/converter/%s/%s.gif' % (self.__f.fhash[0],self.__f.fhash,self.__f.fhash)

	def url_small_preview(self):
		if self.__f.type[:5] == 'image':
			return self.url_converter_location('150')
		if self.__f.type[:5] == 'video':
			return self.url_video_converter_gif_location()
		return 'about:blank'
	
	def url_big_preview(self):
		if self.__f.type[:5] == 'image':
			return self.url_converter_location('1024')
		if self.__f.type[:5] == 'video':
			return 'about:blank'
		return 'about:blank'
	

	def disk_hash_check(self):
		f = os.popen('sha1sum -b \'' + self.disk_location() + '\'')
		fhash = f.readline()[:40]
		return (fhash == self.__f.fhash)

	def __gif_convert(self,cid,ctype,cvalue):
		#mkdir
		cmd = 'mkdir -p \'%s\''%self.disk_video_converter_dir()
		os.system(cmd)
		#get Duration
		cmd = 'ffmpeg -i \'%s\' 2>&1|grep \'Duration\' |cut -d \' \' -f 4 |sed s/,//|cut -d \'.\' -f 1'%self.disk_location()
		duration = os.popen(cmd).read().split(':')
		duration_total = int(duration[0])*60*60 + int(duration[1])*60 + int(duration[2])
		#we need 4 pics		
		pic_intv = duration_total / 4.0
		for i in range(4):
			cmd = 'ffmpeg -loglevel panic -i \'%s\' -s %s -f image2 -ss %.2f -vframes 1 \'%s\'' % (self.disk_location(),cvalue,pic_intv*i,self.disk_video_converter_images_location(cvalue,i))
			print cmd
			os.system(cmd)
		#convert jpg to gif
		cmd = 'convert -resize 320x160 -delay 100 \'%s\'[0-3] -loop 0 \'%s\''%(self.disk_video_converter_images_list(cvalue),self.disk_video_converter_gif_location())
		print cmd
		os.system(cmd)

	def __video_convert(self,cid,ctype,cvalue):
		#mkdir
		cmd = 'mkdir -p \'%s\''%self.disk_video_converter_dir()
		os.system(cmd)
		#convert now,convert to flv
		cmd = 'ffmpeg -loglevel panic -i \'%s\' -y -ab 96k -ar 22050 -ac 1 -s %s -r 25 -qscale 5 -pix_fmt yuv420p -f flv \'%s\''%(self.disk_location(),cvalue,self.disk_video_converter_flv_location(cvalue))
		print cmd 
		os.system(cmd)#run convert cmd
		
	def __convert(self,cid,ctype,cvalue,force=False):
		if ctype=='image/jpeg':
			cmd = 'convert \'%s\' -resize %sx%s \'%s\'' % (self.disk_location(),cvalue,cvalue,self.disk_converter_location(cvalue))
			print 'converting %s to %s.'%(self.__f.fhash,cvalue)
			os.system(cmd)
			self.converters[cvalue]=u'converted'
			return
		elif ctype in ('video/mp2t','video/quicktime','video/mp4','video/x-msvideo'):
			if (not isfile(self.disk_video_converter_gif_location())) or force:
				self.__gif_convert(cid,ctype,cvalue)
			if (not isfile(self.disk_video_converter_flv_location(cvalue))) or force:
				self.__video_convert(cid,ctype,cvalue)
			self.converters[cvalue]=u'converted'
			return

	def convert(self,cvalue,force=False):
		new_cid = None
		for c in psyncFileLib.converter.values():
			if c['ctype'] == self.__f.type and c['cvalue'] == cvalue:
				new_cid = c['cid']
				new_ctype = c['ctype']
				new_cvalue = c['cvalue']
		if new_cid == None:
			raise ValueError('cvalue not found')
			return
		isc = self.converters.is_converted(cvalue)
		if isc:
			if force:
				self.converters[cvalue]=u'converting'
				self.__convert(new_cid,new_ctype,new_cvalue,force)
			else:
				print 'cvalue = %s is converted ,plz use force'%cvalue
				return
		else:
			self.converters.add(new_cid,u'converting')
			self.__convert(new_cid,new_ctype,new_cvalue,force)
		

class psyncFileLib():
	psync_host = '192.168.1.1'
	psync_user = 'psync'
	psync_pass = '123456'
	psync_db = 'psync'
	selected_distribute = {'did':1,'username':'applepie','password':''}
	
	#///////////////初始化////////////////////////
	tag = {}
	distribute = {}
	converter = {}
	def __init__(self):
		Database.set_dbapi(MySQLdb)
		Database.config(host=self.psync_host,db=self.psync_db,user=self.psync_user,passwd=self.psync_pass,charset='utf8')
		self.__readTag()
		self.__readDistribute()
		self.__readConverter()

	#tag初始化和新建
	def __readTag(self):
		for t in Tag.select():
			self.tag[t.tid] = {'tid':t.tid,'tagname':t.tagname}
		return self.tag
	def newTag(self,tag):
		Tag.create(tagname=tag)
		return self.__readTag()

	#Dist初始化和新建
	def __readDistribute(self):
		for t in Distribute.select():
			self.distribute[t.did] = {'did':t.did,'distname':t.distname,'distserver':t.distserver}
		return self.distribute
	def newDistribute(self,distname,disttype,distserver):
		Distribute.create(distname=distname,disttype=disttype,distserver=distserver)
		return self.__readDistribute()

	#选择操作所使用的目标，并保存用户名和密码
	def selectDistribute(self):
		print u'选择需要上传的主机，文件将以FTP的形式上传到主机上，并在数据库中记录。'
		for d in self.distribute.values():
			print d['did'],d['distname'].encode('utf8'),d['distserver'].encode('utf8')
		self.selected_distribute['did'] = int(raw_input('Select Distribute: '))
		self.selected_distribute['username']	= raw_input('Username: ')
		self.selected_distribute['password']	= raw_input('Password: ')
	
	#测试链接是否可用
	def testDistribute(self):
		d = self.distribute[self.selected_distribute['did']]
		print 'Test selected distribute: %s@%s'%(self.selected_distribute['username'],d['distserver'])
		try:
			ftp = FTP(d['distserver'],self.selected_distribute['username'],self.selected_distribute['password'])
			print ftp.getwelcome()
			ftp.quit()
			print 'Test OK '
			return True
		except:
			print 'Test error '
			ftp.quit()
			return False

	#Convert初始化和新建
	def __readConverter(self):
		for t in Converter.select():
			self.converter[t.cid] = {'cid':t.cid,'ctype':t.ctype,'cvalue':t.cvalue}
		return self.converter
	def newConverter(self,ctype,cvalue):
		Converter.create(ctype=ctype,cvalue=cvalue)
		return self.__readConverter()
	
	
	#==========================导入====================
	#调用wput
	def wput(self,src,filename):
		#默认ftp存放路径为 ~/Data/psync
		default_path = 'Data/psync/%s'%filename[0]
		d = self.distribute[self.selected_distribute['did']]
		cmd = 'wput -t 3 \"%s\" ftp://%s:%s@%s/%s/%s'%(src.decode('utf8'),self.selected_distribute['username'],self.selected_distribute['password'],d['distserver'],default_path,filename)
		return os.system(cmd.encode('utf8'))
	
	#调用sha1sum
	def sha1sum(self,filepath):
		f = os.popen('sha1sum -b \'' + filepath + '\'')
		return f.readline()[:40]

	#自定义文件类型
	def file_type_override(self,filepath,filetype):
		if filetype == 'application/octet-stream' and (filepath[-3:].upper() == 'MTS' or filepath[-3:].upper() == 'MP4'):
			return 'video/mp2t'
		return filetype
  
	#调用file确定文件类型
	def extension2mime(self,filepath):
		f = os.popen('file --mime-type \'' + filepath + '\'')
		t = f.readline()
		return self.file_type_override(filepath,t[len(filepath)+2:].strip())
	
	#根据文件类型确定后缀名
	def mime2extension(self,t):
		if t == 'image/gif':
			return '.gif'
		elif t == 'image/jpeg':
			return '.jpg'
		elif t == 'video/mp4':
			return '.mp4'
		elif t == 'video/mpeg':
			return '.mpeg'
		elif t == 'video/quicktime':
			return '.mov'
		elif t == 'video/mp2t':
			return '.mts'
		elif t == 'video/3gpp':
			return '.3gp'
		elif t == 'video/x-msvideo':
			return '.avi'
		else:
			print '!!!!!unknow type:',t
			return '.unknown'
	
	#导入一个文件，src为文件位置，导入完成后，原文件将会被删除
	#只有当文件已经存在了，才会删除。importFile必须返回same
	#所以只有当文件被扫描两次时才会被删除
	#如果文件被删除，返回True，否则返回False
	def import_and_delete_same(self,src):
		(r,e) = self.importFile(src)
		if r == 2:
			os.unlink(src)
			return True
		else:
			return False
			
	#导入一个文件，src为文件位置，导入完成后，原文件将会被链接回原先位置
	#这个函数只对selectDistribute选择为本机起作用，因为它默认文件是通过FTP保存在本机硬盘上的
	def import_and_link(self,src):
		(r,new_hash) = self.importFile(src)
		if r == 2 or r == 0:
			#默认ftp存放路径为 /home/applepie/Data/psync
			filename = os.path.basename(src)
			new_mime = self.extension2mime(src)
			new_filename = new_hash+self.mime2extension(new_mime)
			default_path = '/home/applepie/Data/psync/%s/%s'%(new_filename[0],new_filename)
			timeout = 5
			while not os.path.lexists(default_path):
				print default_path,'not found,wait 1 sec, timeout=',timeout
				timeout = timeout  - 1
				time.sleep(1)
				if timeout <1:
					return False
			os.unlink(src)
			print 'link: %s -> %s'%(default_path,src)
			return os.link(default_path,src)
		else:
			return False

	#导入一个文件，src为文件位置
	#正常返回0，如果FTP失败返回512，如果硬链接返回1和hardlink，如果文件重复返回2和它的hash值
	def importFile(self,src):
		#get file information
		(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.lstat(src)
		if nlink > 1:
			print '%s is hardlink, skipped'%src
			return (1,'hardlink')
		new_hash = self.sha1sum(src)
		new_file = File.findone(fhash=new_hash)
		if new_file == None:
			#file not find in db
			#get filename
			filename = os.path.basename(src)
			#get mime type
			new_mime = self.extension2mime(src)
			#make new file name = hash + extension
			new_filename = new_hash+self.mime2extension(new_mime)
			#make ftp upload
			r = self.wput(src,new_filename)
			if r == 0:
				new_file = File(fhash=new_hash,type=new_mime,filename=b64encode(filename),filetime=mtime)
				new_file.save()
				return (0,new_hash)
			else:
				print 'wput error returned'
				return (512,'ftp error')
		else:
			print 'file hash found in db, upload skipped'
			return (2,new_hash)

	#搜索文件，返回一个文件列表
	def searchFile(self,d = '/home/applepie/Data/psync/PicToImport/'):
		t = ['jpg','jpeg','mp4','mov','3gp','mts','avi']
		cmd = ''
		for i in t:
			cmd = cmd + '-o -name \'*.' + i +'\' '
			cmd = cmd + '-o -name \'*.' + i.upper() +'\' '
		cmd = 'find ' + d + cmd[2:]
		f = os.popen(cmd)
		filelist = f.readlines()
		f.close()
		return [i[:-1] for i in filelist]

	#以HASH和ID方式获得一个File
	def readFileByHash(self,hashvalue,file_only = False):
		return psyncFile(File.findone(fhash=hashvalue),file_only)
	def readFileByID(self,fid,file_only = False):
		return psyncFile(File.findone(fid=fid),file_only)
	#获得FID列表
	def listFID(self):
		return [f.fid for f in File.select(File.fid).execute().all()]
	#获得所有File对象
	def listFile(self,file_only = False):
		return [psyncFile(f,file_only) for f in File.getall()]
	#根据不同类型获得所有File对象
	def listFileByType(self,t,file_only = False):
		return [psyncFile(f,file_only) for f in File.where(type=t).getall()]
	#根据所选的主机ID获得所有File对象
	def listFileByDistribute(self,d,file_only = False):
		return [psyncFile(f,file_only) for f in File_Distribute_View.where(did=d).getall()]
	#列出所有缺少tag号的文件
	def listFIDByMissingTag(self,t):
		result = Database.execute("SELECT `file`.`fid` FROM `file` left join `file_tag` on `file`.`fid`=`file_tag`.`fid` and `file_tag`.`tid`=" + str(t) + " where `file_tag`.`tid` is null")
		return [f[0] for f in result.fetchall()]

	#all date
	def listItem(self,v):
		#list all date in db
		# tid = 1 is date
		q = File_Tag_View.groupby(File_Tag_View.filetagvalue).where(tid=v).orderby(File_Tag_View.filetagvalue,True).select(distinct(File_Tag_View.filetagvalue),fn.count(File_Tag_View.filetagvalue).alias('count'))
		return [{'item':t.filetagvalue,'count':func.count,'select':False} for t,func in q]
	def listItemXml(self,v):
		r=''
		for t in self.listItem(v):
			r = r + '<item count=\"%d\">%s</item>'%(t['count'],t['item'])
		return r.encode('utf8')
	def listSelect(self):
		return [{'tid':t.tid,'tagname':t.tagname,'item':self.listItem(t.tid)} for t in Tag.getall()]
	def listSelectXml(self):
		tid_list = [{'tid':t.tid,'tagname':t.tagname} for t in Tag.getall()]
		r = ''
		for t in tid_list:
			r = r + '<tag tid=\"%d\" tagname=\"%s\">%s</tag>'%(t['tid'],t['tagname'],self.listItemXml(t['tid']).decode('utf8'))
		return r.encode('utf8')
	def newSelectHandle(self):
		return SelectHandle([{'tid':t.tid,'label':t.tagname,'tagname':t.tagname,'item':self.listItem(t.tid),'select':False} for t in Tag.getall()])

class SelectHandle():
	#select handle
	def __init__(self, h=None):
		self.__h = h
		self.__fids = [f.fid for f in File.orderby(File.fid, desc=True).select(File.fid).execute().all()]
		self.__select = {}
		self.limit = 0
		self.offset = 100
	def rebuild(self,limit=0,offset=100): 
		if len(self.__select)==0:
			return 'limit=%d&amp;offset=%d'%(int(limit),int(offset))
		r = '&amp;'.join(['tags=%s&amp;select=%s'%(k,v) for (k,v) in self.__select.iteritems()])
		r = r + '&amp;limit=%d&amp;offset=%d'%(int(limit),int(offset))
		return r
	def nav(self):
		total = len(self.__fids)
		total_page = total/100
		if total_page < 2:
			return ''
		else:
			r = '<nav>'
			for c in range(total_page):
				if int(self.limit) == c*100:
					select = 'True'
				else:
					select = 'False'
				r = r + '<item url=\"?task=find&amp;%s\" select=\"%s\">Page %d - Total %d</item>'%(self.rebuild(c*100,100),select,c+1,total_page)
			r = r + '</nav>'
			return r.encode('utf8')
 
	def listViewXml(self):
		r = ('<psync_file_list><current_select>?task=iframe_ajax&amp;iframe=%s</current_select>'%b64encode('?task=select&amp;'+self.rebuild(self.limit,self.offset)))+self.nav().decode('utf8')
		for fid in self.fids():
			r = r + '<fid>%d</fid>'%fid
		r = r + '</psync_file_list>'
		return r.encode('utf8')

	def select(self,t,v):
		self.__select[t]=v
		if len(self.__fids) == 0:
			return self.__fids
		if v == 'None':
			return self.__fids
		if t == 'date_from':
			t = '1'
			new_fids = [f.fid for f in File_Tag_View.where((File_Tag_View.tid==t) & (File_Tag_View.filetagvalue>=v)).select(distinct(File_Tag_View.fid)).execute().all()]
		elif t == 'date_till':
			t = '1'
			new_fids = [f.fid for f in File_Tag_View.where((File_Tag_View.tid==t) & (File_Tag_View.filetagvalue<=v)).select(distinct(File_Tag_View.fid)).execute().all()]
		if t != '1':
			new_fids = [f.fid for f in File_Tag_View.where((File_Tag_View.tid==t) & (File_Tag_View.filetagvalue==v)).select(distinct(File_Tag_View.fid)).execute().all()]
		if len(new_fids) == 0:
			self.__fids = []
		else:
			self.__fids = list(set(self.__fids).intersection(set(new_fids)))
		return self.__fids 
	def fids(self):
		return self.__fids[int(self.limit):(int(self.limit)+int(self.offset))]
	def select_xml(self,tags,select):
		for c in range(len(tags)):
			self.__select[tags[c]]=select[c]
		r = '<select>'
		for t in self.__h:
			if t['tid'] in self.__select.keys():
				t['select'] = True
			if t['tid'] == 1:
				if 'date_from' in self.__select.keys():
					t['select'] = True
				else:
					t['select'] = False
				r = r + '<tag tid=\"%s\" label=\"%s\" tagname=\"%s\" select=\"%s\">'%('date_from',u'开始时间',t['tagname'],t['select'])
				c = 0
				for i in t['item']:
					if t['select'] == True:
						if self.__select['date_from'] == i['item']:
							i['select'] = True
					r = r + '<item iid=\"%s_%d\" count=\"%d\" select=\"%s\">%s</item>'%('date_from',c,i['count'],i['select'],i['item'])
					if i['select'] == True:
						#clear select for next round: date_till
						i['select'] = False
					c = c + 1
				r = r + '</tag>'
				
				if 'date_till' in self.__select.keys():
					t['select'] = True
				else:
					t['select'] = False
				r = r + '<tag tid=\"%s\" label=\"%s\" tagname=\"%s\" select=\"%s\">'%('date_till',u'结束时间',t['tagname'],t['select'])
				c = 0
				for i in t['item']:
					if t['select'] == True:
						if self.__select['date_till'] == i['item']:
							i['select']=True
					r = r + '<item iid=\"%s_%d\" count=\"%d\" select=\"%s\">%s</item>'%('date_till',c,i['count'],i['select'],i['item'])
					c = c + 1
				r = r + '</tag>'
			else:
				r = r + '<tag tid=\"%s\" label=\"%s\" tagname=\"%s\" select=\"%s\">'%(t['tid'],t['label'],t['tagname'],t['select'])
				c = 0
				for i in t['item']:
					if t['select'] == True:
						if self.__select[t['tid']] == i['item']:
							i['select']='True'
					r = r + '<item iid=\"%s_%d\" count=\"%d\" select=\"%s\">%s</item>'%(t['tid'],c,i['count'],i['select'],i['item'])
					c = c + 1
				r = r + '</tag>'
		r = r + '</select>'
		return r.encode('utf8')
	def __str__(self):
		return pickle.dumps(self.__h)
	def loads(self,s):
		self.__h = pickle.loads(s)
	def dumps(self):
		return pickle.dumps(self.__h)
	


