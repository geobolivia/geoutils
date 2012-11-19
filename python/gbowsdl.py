#!/usr/bin/python
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
import time

# Libraries
# ogr: WFS, SHP
#  http://www.gdal.org/ogr/drv_wfs.html
#  http://www.paolocorti.net/2011/03/23/a-quick-look-at-the-wfs-gdal-driver/
# owslib: WMS (CSW)
#  http://geopython.github.com/OWSLib/
# gsconfig: SLD
#  http://dwins.github.com/gsconfig.py/

def test_update_file(filename, replaceTime):
	now = time.time()
	too_old = now - replaceTime
	try:
		modification_time = os.path.getctime(filename)
	except OSError:
		pass
		return True

	if debug:
		print '    the file exists and is new - download aborted'

	if modification_time < too_old:
		return True


	return False

def write_metadata(url,filebase,extension):
	filename = filebase + extension

	if not test_update_file(filename, replaceTime):
		return

	# Code specific to GeoBolivia way to fill the MetadataUrl fields in GeoServer
	try:
		mdtuple=urlparse(url)
		xmlpath=urljoin(mdtuple.path,'iso19139' + extension)
		xmltuple=[mdtuple.scheme, mdtuple.netloc, xmlpath, mdtuple.params, mdtuple.query, mdtuple.fragment]
		xmlurl=urlunparse(xmltuple)
		urlretrieve(xmlurl, filename)
	except:
		pass

def write_sld_style(style,filebase):
	# TODO: wrap SLD in human-readable style
	stylefile=filebase+'.sld'

	if not test_update_file(stylefile, replaceTime):
		return

	with open(stylefile, 'w') as f:
		f.write(style.sld_body)

def write_shp_data(baseurl,workspacebase,workspacename,layername):
	if not test_update_file(os.path.join(workspacebase, layername + '.shp'), replaceTime):
		return

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

	layerwfsurl = forge_ows_url(baseurl, 'wfs', workspacename, layername)
	wfs = wfsdriver.Open("WFS:"+layerwfsurl)
	wfsl = wfs.GetLayerByName(workspacename+':'+layername)
	try:
		shpdatasource.CopyLayer(wfsl, layername)
		shpdatasource.SyncToDisk()
	except:
		raise

def write_tiff_data(baseurl,workspacebase,workspacename,layername):
	gtifffilename = os.path.join(workspacebase, layername + '.tiff')
	if not test_update_file(gtifffilename, replaceTime):
		return

	# The WCS driver needs a temporary XML file
	# http://www.gdal.org/frmt_wcs.html
	serviceURL = forge_ows_url(baseurl, 'wcs', workspacename, layername)
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
	# http://www.gdal.org/frmt_gtiff.html
	gtiffdriver = gdal.GetDriverByName("GTiff")

	try:
		# TODO use a function for showing copy progress
		gtiffds = gtiffdriver.CreateCopy(gtifffilename, wcsds, 0)
		gtiffds = None
		wcsds = None
	except:
		gtiffds = None
		wcsds = None
		raise

def forge_ows_url(baseurl, ows='wms', workspacename=None, layername=None):
	#if not workspacename is None:
	#	baseurl += '/' + workspacename
	#	if not layername is None:
	#		baseurl += '/' + layername
	baseurl += '/' + ows + '?'
	return baseurl

def get_layer(baseurl, layermd, filebase, cat, workspacename, layername, workspacepath):
	# Metadata
	# TODO - manage various Metadata Urls
	for m in layermd.metadataUrls:
		if debug:
			print '  xml and pdf metadata'
		write_metadata(m['url'],filebase,'.xml')
		write_metadata(m['url'],filebase,'.pdf')

	# Style
	# TODO - manage various Metadata styles
	for s in layermd.styles.keys():
		if debug:
			print '  sld style'
		reststyle = cat.get_style(s)
		write_sld_style(reststyle,filebase)

	# Data
	# TODO: download raster layers
	# Try WFS
	try:
		if debug:
			print '  vectorial data via wfs'
		write_shp_data(baseurl,workspacepath,workspacename,layername)
	except:
		# Try WCS
		try:
			if debug:
				print '  error in downloading vector data'
				print '  try raster data via wcs'
			write_tiff_data(baseurl,workspacepath,workspacename,layername)
		except Exception as e:
			print "    ERROR in downloading raster file:", e
			pass
		pass	

	print '--Layer downloaded'

def get_workspace(baseurl, outputpath, workspacename = None, layername = None, user = None, pw = None, cat = None):

	# Connect to REST GeoServer
	if cat is None:
		resturl=baseurl+'rest'
		stylesurl=resturl+'/styles/'
		if user is None:
			user = raw_input("User: ")
		if pw is None:
			pw = getpass.getpass('Password: ')
		cat = Catalog(resturl, username=user, password=pw)

	# Get capabilities for this layer
	wmsurl = forge_ows_url(baseurl, 'wms', workspacename, layername)
	wms = WebMapService(wmsurl, version='1.1.1')
	layers=wms.items()

	if len(layers) == 0:
		print '  ERROR: layer not found on WMS server'

	for l in layers:
		layerid = l[0]
		layermd = l[1]

		re_layerid = compile(":")
		tmp = re_layerid.split(layermd.id)
		layername = tmp[-1:][0]
		workspacename = tmp[-2:-1][0]
		workspacepath = os.path.join(outputpath,workspacename)
		if not os.access(workspacepath, os.W_OK):
			os.mkdir(workspacepath)
		filebase = os.path.join(outputpath,workspacename,layername)

		if debug:
			print '--Get layer ' + workspacename + ':' + layername
		get_layer(baseurl, layermd, filebase, cat, workspacename, layername, workspacepath)
		
version = '0.1'
debug = True
replaceTime = 24000