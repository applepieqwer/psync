from psync import psyncFileLib
import pyexiv2

#read tag from jpg exif
def guess_jpeg_date(src):
  try:
    metadata = pyexiv2.ImageMetadata(src)
    metadata.read()
    if 'Exif.Photo.DateTimeOriginal' in metadata.keys():
      jpegtag = metadata['Exif.Photo.DateTimeOriginal']
    elif 'Exif.Image.DateTime' in metadata.keys():
      jpegtag = metadata['Exif.Image.DateTime']
    else:
      return None
    filedate = jpegtag.value.strftime('%Y-%m-%d')
  except:
    return None
  else:
    return filedate

p = psyncFileLib()
#find tag = 1, tag for Date
for f in p.listFIDByMissingTag(1):
	pf = p.readFileByID(f)
	if pf['type'] == 'image/jpeg':
		filedate = guess_jpeg_date(pf.disk_location())
		if filedate != None:
			#add new tag
			pf.tags.add(1,filedate)
		else:
			#read tag fail
			print pf.disk_location(), ' date tag not found.'
