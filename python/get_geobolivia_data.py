#!/usr/bin/python
""" get the metadata xml file from wms capabilities
args:
""" 
from osgeo import ogr
from osgeo import gdal
from owslib.csw import CatalogueServiceWeb
from owslib.wms import WebMapService
from urlparse import urlparse
from urlparse import urlunparse
from urlparse import urljoin
from urllib import urlretrieve
import os
from re import compile
from re import split
# Libraries
# ogr: WFS, SHP
# http://www.gdal.org/ogr/drv_wfs.html
# http://www.paolocorti.net/2011/03/23/a-quick-look-at-the-wfs-gdal-driver/
# owslib: WMS, CSW, SLD
# http://geopython.github.com/OWSLib/

def write_xml_metadata(url,filebase):
	# Code specific to GeoBolivia way to fill the MetadataUrl fields in GeoServer
	try:
		mdtuple=urlparse(url)
		xmlpath=urljoin(mdtuple.path,'iso19139.xml')
		xmltuple=[mdtuple.scheme, mdtuple.netloc, xmlpath, mdtuple.params, mdtuple.query, mdtuple.fragment]
		xmlurl=urlunparse(xmltuple)
		urlretrieve(xmlurl, filebase+'.xml')
	except:
		pass

# Input arguments
baseurl='http://www.geo.gob.bo/geoserver/'
workspacename='otros'
layername='Ecoregiones_WWF'
#wmsurl=baseurl+'/'+workspacename+'/wms'
wmsurl=baseurl+'/'+workspacename+'/'+layername+'/wms'
outputpath='/tmp/'
re_layerid=compile(":")

# Get capabilities for this layer
wms = WebMapService(wmsurl, version='1.1.1')

layers=wms.items()

for l in layers:
	layerid=l[0]
	layermd=l[1]
	tmp=re_layerid.split(layermd.id)
	layername=tmp[-1:][0]
	print layername
	workspacename=tmp[-2:-1][0]
	print workspacename
	workspacepath=os.path.join(outputpath,workspacename)
	if not os.access(workspacepath, os.W_OK):
		os.mkdir(workspacepath)
	filebase=os.path.join(outputpath,workspacename,layername)
	
	# Metadata
	# TODO - manage various Metadata Urls
	for m in layermd.metadataUrls:
		write_xml_metadata(m['url'],filebase)

