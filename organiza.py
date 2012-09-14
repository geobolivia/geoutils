
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

# leee un archivo csv
os.chdir('/home/diana/geoutils/python/DATA')
arch = 'TLayers.csv'
#sin archivo csv
for i,layer in enumerate(all_layers):
	b = layer.name
	a = layer.resource.metadata_links
	that_layer = cat.get_layer(b)
	that_style = that_layer.default_style
	print that_style.name
# descarga el metadato
for row in datos:
    layername = row [5]
    title = row [6]
    cache = row [4]
    tupla = cache.partition('file:')
    temp = tupla [2]
    temp2 = temp.partition("'")
    find = temp2 [0]
   
    #para la direccion del metadato
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
        #descarga el metadato
        a=title.find ('Error' or "")
        if a == -1:
           
           urlpdf= 'http://www.geo.gob.bo/geonetwork/srv/es/iso19139.pdf?id='
           urlpdf = urlpdf + num
       
           pdf = dire + '/' + layername + '.pdf'
           urllib.urlretrieve(urlpdf, filename=pdf)
           #print dire
           metadata = dire + '/' + layername + '.xml'
           url= 'http://www.geo.gob.bo/geonetwork/srv/es/iso19139.xml?id='    
           url = url + num
           urllib.urlretrieve(url, filename=metadata)
    #copia el SLD asociado
 
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
            
