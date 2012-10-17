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
os.chdir('/home/wilson/pythonDiana/DATA')
arch = 'TLayers.csv'
datos = open(arch, "rb")

# download metadata and pdf
for row in datos:
    linea = row.split(';')
    layername = linea [5]
   
    title = linea [6]
    cache = linea [4]
   
    tupla = cache.partition('file:')
    temp = tupla [2]
    temp2 = temp.partition("'")
    find = temp2 [0]
    metalink = linea [8]
    styles = linea [9]
    style_xml = styles + '.xml'
    style_sld = styles + '.sld'
    tupla = metalink.partition('id=')
    cad = tupla [2]
    num = cad.replace ("'","")
    num = num.replace (")","")
    num = num.replace ("]", "")
    dire = '/home/wilson/pythonDiana/DATA' + '/' + find     
    print num
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
    for root, dirnames, filenames in os.walk('/home/wilson/pythonDiana/DATA/styles'):
        for filename in fnmatch.filter(filenames, style_xml):
            # actual_xml is the xml file asociated to the style
            actual_xml = os.path.join(root, filename)
            print actual_xml
            if find == '':
				print 'no hay directorio'
            else:
				# Find the SLD file, from the XML content
				actual_sld = os.path.join(root, style_sld)
				# Copy the SLD file into the output directory
				final = dire + '/' + layername + '.sld'   
				shutil.copy2(actual_sld, final)

# check if you have the extension prj and if it creates
#    shapefile = dire + '/' + layername + '.shp'
#    driver = ogr.GetDriverByName('ESRI Shapefile')
#    inDS = driver.Open(shapefile, 0)
#    if inDS is None:
#        print 'Could not open file'
 #   referencia = dire + '/' + layername + '.prj'
#    inLayer = inDS.GetLayer()
#    spatialRef = inLayer.GetSpatialRef()
#    if spatialRef == None:
#		geod= 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",'
#		sphe='SPHEROID/["WGS_1984",6378137.0,298.257223563]],'
#		primen = 'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
#		ref = geod + sphe + primen
#		file = open(referencia, 'w')
#		file.write(ref)
#		file.close()
	   	  
