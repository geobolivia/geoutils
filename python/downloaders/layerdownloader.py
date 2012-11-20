from geoserver.catalog import Catalog

from osgeo import ogr
from osgeo import gdal

from re import compile
from re import split
import time
import os
from urlparse import urlparse
from urlparse import urlunparse
from urlparse import urljoin
from urllib import urlretrieve

class LayerDownloader:
	def __init__(self, restConnection=None, layerMetadata=None, geoserverUrl='http://www.geo.gob.bo/geoserver/', replaceTime=None):
                self.layerMetadata = layerMetadata
                if layerMetadata is None:
                        self.workspace = None
                        self.layer = None
                else:
                        regexp = compile(":")
                        tmp = regexp.split(layerMetadata.id)
                        self.workspace = tmp[0]
                        self.layer = tmp[1]

                self.geoserverUrl = geoserverUrl

                self.restConnection = restConnection
                if restConnection is None:
                        self.restConnection = connectToRest()

                self.replaceTime = replaceTime
                if replaceTime is None:
                        replaceTime = 60 * 60 * 24

	def connectToRest(restUrl=None, username=None, password=None):
                """
                Connect to the REST interface of GeoServer
                """
		return Catalog(restUrl, username=username, password=password)

        connectToRest = staticmethod(connectToRest)

        def forgeOwsUrl(self, ows='wms'):
                baseUrl = self.geoserverUrl
                if not self.workspace is None:
                        baseUrl += '/' + self.workspace
                        if not self.layer is None:
                                baseUrl += '/' + self.layer
                baseUrl += '/' + ows + '?'
                return baseUrl

        def writeMetadata(self, url, filebase, extension):
                filename = filebase + extension

                # Code specific to GeoBolivia way to fill the MetadataUrl fields in GeoServer
                try:
                        mdtuple=urlparse(url)
                        xmlpath=urljoin(mdtuple.path,'iso19139' + extension)
                        xmltuple=[mdtuple.scheme, mdtuple.netloc, xmlpath, mdtuple.params, mdtuple.query, mdtuple.fragment]
                        xmlurl=urlunparse(xmltuple)
                        urlretrieve(xmlurl, filename)
                except:
                        pass

        def writeStyle(self, style, filebase):
                # TODO: wrap SLD in human-readable style
                stylefile = filebase + '.sld'
                with open(stylefile, 'w') as f:
                        f.write(style.sld_body)

        def writeShpData(self, workspacebase,workspacename,layername):
#                if not test_update_file(os.path.join(workspacebase, layername + '.shp'), replaceTime):
#                        return

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

                layerwfsurl = self.forgeOwsUrl('wfs')
                wfs = wfsdriver.Open("WFS:"+layerwfsurl)
                wfsl = wfs.GetLayerByName(workspacename+':'+layername)
                try:
                        shpdatasource.CopyLayer(wfsl, layername)
                        shpdatasource.SyncToDisk()
                except:
                        raise

                def write_tiff_data(workspacebase,workspacename,layername):
                        gtifffilename = os.path.join(workspacebase, layername + '.tiff')
                        #if not test_update_file(gtifffilename, replaceTime):
                        #    return

                        # The WCS driver needs a temporary XML file
                        # http://www.gdal.org/frmt_wcs.html
                        serviceURL = self.forgeOwsUrl('wcs')
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
