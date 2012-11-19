#!/usr/bin/python
""" get the metadata xml file from wms capabilities
args:
""" 
from osgeo import ogr
from osgeo import gdal
from owslib.wms import WebMapService
from urlparse import urlparse
from urlparse import urlunparse
from urlparse import urljoin
from urllib import urlretrieve
import os
from re import compile
from re import split
from geoserver.catalog import Catalog
import getpass
from xml.etree.ElementTree import Element, SubElement, tostring

# Libraries
# ogr: WFS, SHP
#  http://www.gdal.org/ogr/drv_wfs.html
#  http://www.paolocorti.net/2011/03/23/a-quick-look-at-the-wfs-gdal-driver/
# owslib: WMS (CSW)
#  http://geopython.github.com/OWSLib/
# gsconfig: SLD
#  http://dwins.github.com/gsconfig.py/

def write_xml_metadata(url,filebase):
	# TODO download the PDF too

	# Code specific to GeoBolivia way to fill the MetadataUrl fields in GeoServer
	try:
		mdtuple=urlparse(url)
		xmlpath=urljoin(mdtuple.path,'iso19139.xml')
		xmltuple=[mdtuple.scheme, mdtuple.netloc, xmlpath, mdtuple.params, mdtuple.query, mdtuple.fragment]
		xmlurl=urlunparse(xmltuple)
		urlretrieve(xmlurl, filebase+'.xml')
	except:
		pass

def write_sld_style(style,filebase):
	# TODO: wrap SLD in human-readable style
	stylefile=filebase+'.sld'
	with open(stylefile, 'w') as f:
		f.write(style.sld_body)

def write_shp_data(baseurl,workspacebase,workspacename,layername):
	wfsdriver = ogr.GetDriverByName('WFS')
	shpdriver = ogr.GetDriverByName("ESRI Shapefile")
	shpdatasource = shpdriver.CreateDataSource(workspacebase)

	replaceshp=True
	if replaceshp:
		itodelete=None
		for i in range(0, shpdatasource.GetLayerCount()):
			shpl = shpdatasource.GetLayerByIndex(i)
			if shpl.GetName() == layername:
				itodelete=i
		if itodelete is not None:
			shpdatasource.DeleteLayer(itodelete)
			shpdatasource.SyncToDisk()

	layerwfsurl=baseurl+'/'+workspacename+'/'+layername+'/wfs'
	wfs = wfsdriver.Open("WFS:"+layerwfsurl)
	wfsl = wfs.GetLayerByName(workspacename+':'+layername)
	try:
		shpdatasource.CopyLayer(wfsl, layername)
		shpdatasource.SyncToDisk()
	except:
		raise

def write_tiff_data(baseurl,workspacebase,workspacename,layername):
	# The WCS driver needs a temporary XML file
	serviceURL = baseurl+'/'+workspacename+'/'+layername+'/wcs?'
	coverageName = workspacename+':'+layername
	tmpxmlfile = '/tmp/gdalwcsdataset.xml'
	top = Element('WCS_GDAL')
	child = SubElement(top, 'ServiceURL')
	child.text = serviceURL
	child = SubElement(top, 'CoverageName')
	child.text = coverageName
	with open(tmpxmlfile, "w") as f:
		f.write(tostring(top))

	wcsds=gdal.Open(tmpxmlfile)	
	gtiffdriver = gdal.GetDriverByName("GTiff")

	try:
		# TODO use a function for showing copy progress
		gtiffds = gtiffdriver.CreateCopy(workspacebase+'/'+layername+'.tiff', wcsds, 0)
		gtiffds = None
		wcsds = None
	except:
		gtiffds = None
		wcsds = None
		raise

# Input arguments
baseurl='http://www.geo.gob.bo/geoserver/'
#wmsurl=baseurl+'/otros/wms'
#wmsurl=baseurl+'/otros/mosaico_landsat/wms'
wmsurl=baseurl+'/mapashistoricos/mapahistorico1834/wms'
outputpath='/tmp/'
re_layerid=compile(":")

# Connect to REST GeoServer
resturl=baseurl+'rest'
stylesurl=resturl+'/styles/'
user = raw_input("User: ")
pw = getpass.getpass('Password: ')
cat = Catalog(resturl, username=user, password=pw)

# Get capabilities for this layer
wms = WebMapService(wmsurl, version='1.1.1')

layers=wms.items()

for l in layers:
	layerid=l[0]
	layermd=l[1]
	tmp=re_layerid.split(layermd.id)
	layername=tmp[-1:][0]
	workspacename=tmp[-2:-1][0]
	workspacepath=os.path.join(outputpath,workspacename)
	if not os.access(workspacepath, os.W_OK):
		os.mkdir(workspacepath)
	filebase=os.path.join(outputpath,workspacename,layername)
	print workspacename + '/' + layername
	
	# Metadata
	# TODO - manage various Metadata Urls
	for m in layermd.metadataUrls:
		write_xml_metadata(m['url'],filebase)

	# Style
	# TODO - manage various Metadata styles
	for s in layermd.styles.keys():
		reststyle=cat.get_style(s)
		write_sld_style(reststyle,filebase)

	# Data
	# TODO: download raster layers
	# Try WFS
	try:
		write_shp_data(baseurl,workspacepath,workspacename,layername)
	except:
		# Try WCS
		try:
			print 'Download via WCS'
			write_tiff_data(baseurl,workspacepath,workspacename,layername)
		except Exception as e:
			print "Unexpected error:", e
			pass
		pass	
