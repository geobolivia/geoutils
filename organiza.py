#!/usr/bin/python
""" organiza los datos del geoserver 
args: las carpetas de shp, stylos y un archivo csv de los datos del geoserver
""" 
from osgeo import ogr
from osgeo import gdal
import urllib
import os
import csv
import fnmatch
import shutil

# read file csv
os.chdir('/home/diana/geoutils/python/DATA')
arch = 'TLayers.csv'
for i,layer in enumerate(all_layers):
	b = layer.name
	a = layer.resource.metadata_links
	that_layer = cat.get_layer(b)
	that_style = that_layer.default_style
	print that_style.name
# download metadata and pdf
for row in datos:
    layername = row [5]
    title = row [6]
    cache = row [4]
    tupla = cache.partition('file:')
    temp = tupla [2]
    temp2 = temp.partition("'")
    find = temp2 [0]
    metalink = row [8]
    styles = row [9]
    styles = styles + '.sld'
    tupla = metalink.partition('id=')
    cad = tupla [2]
    num = cad.replace ("'","")
    num = num.replace (")","")
    num = num.replace ("]", "")
    dire = '/home/diana/geoutils/python/DATA' + '/' + find     
    if num == '':
		print 'no tiene metadato' 
    else: 
        
        a=title.find ('Error' or "")
        if a == -1:
           
           urlpdf= 'http://www.geo.gob.bo/geonetwork/srv/es/iso19139.pdf?id='
           urlpdf = urlpdf + num
       
           pdf = dire + '/' + layername + '.pdf'
           urllib.urlretrieve(urlpdf, filename=pdf)
           metadata = dire + '/' + layername + '.xml'
           url= 'http://www.geo.gob.bo/geonetwork/srv/es/iso19139.xml?id='    
           url = url + num
           urllib.urlretrieve(url, filename=metadata)
    #copy the associated SLD
    matches = []
    for root, dirnames, filenames in os.walk('/home/diana/geoutils/python/DATA/styles'):
        for filename in fnmatch.filter(filenames, styles):  
            matches.append(os.path.join(root, filename))
           
            actual = root + '/'+ filename
            print actual 
            if find == '':
				print 'no hay directorio'
            else:
				final = dire + '/' + layername + '.sld'   
				shutil.copy2(actual, final)

# check if you have the extension prj and if it creates
    shapefile = dire + '/' + layername + '.shp'
    # creates an object (ESRI Shapefile)
    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDS = driver.Open(shapefile, 0)
    if inDS is None:
        print 'Could not open file'
    referencia = dire + '/' + layername + '.prj'
    inLayer = inDS.GetLayer()
    spatialRef = inLayer.GetSpatialRef()
    if spatialRef == None:
		geod= 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",'
		sphe='SPHEROID/["WGS_1984",6378137.0,298.257223563]],'
		primen = 'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
		ref = geod + sphe + primen
		file = open(referencia, 'w')
		file.write(ref)
		file.close()
	   	  
	   
