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
from xml.etree.ElementTree import Element, SubElement, tostring

# Libraries
# ogr: WFS, SHP
#  http://www.gdal.org/ogr/drv_wfs.html
#  http://www.paolocorti.net/2011/03/23/a-quick-look-at-the-wfs-gdal-driver/
# owslib: WMS (CSW)
#  http://geopython.github.com/OWSLib/
# gsconfig: SLD
#  http://dwins.github.com/gsconfig.py/

class LayerDownloader:
	def __init__(self, restConnection=None, layerMetadata=None, geoserverUrl='http://www.geo.gob.bo/geoserver/', replaceTime=None, debug=None):
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
                self.debug = debug
                if debug is None:
                        self.debug = True

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

        def writeShpData(self, workspacebase):
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
                                if shpl.GetName() == self.layer:
                                        itodelete=i
                        if itodelete is not None:
                                shpdatasource.DeleteLayer(itodelete)
                                shpdatasource.SyncToDisk()

                layerwfsurl = self.forgeOwsUrl('wfs')
                wfs = wfsdriver.Open("WFS:"+layerwfsurl)
                wfsl = wfs.GetLayerByName(self.layerMetadata.id)
                try:
                        shpdatasource.CopyLayer(wfsl, self.layer)
                        shpdatasource.SyncToDisk()
                except:
                        raise

        def writeTiffData(self, workspacebase):
                gtifffilename = os.path.join(workspacebase, self.layer + '.tiff')
                #if not test_update_file(gtifffilename, replaceTime):
                #    return

                # The WCS driver needs a temporary XML file
                # http://www.gdal.org/frmt_wcs.html
                serviceURL = self.forgeOwsUrl('wcs')
                coverageName = self.layerMetadata.id
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

        def getLayer(self, filebase, workspacepath):
                # Metadata
                # TODO - manage various Metadata Urls
                for m in self.layerMetadata.metadataUrls:
                        if self.debug:
                                print '  xml and pdf metadata'
                        self.writeMetadata(m['url'],filebase,'.xml')
                        self.writeMetadata(m['url'],filebase,'.pdf')

                # Style
                # TODO - manage various Metadata styles
                for s in self.layerMetadata.styles.keys():
                        if self.debug:
                                print '  sld style'
                        reststyle = self.restConnection.get_style(s)
                        self.writeStyle(reststyle,filebase)

                # Data
                # TODO: download raster layers
                # Try WFS
                try:
                        if self.debug:
                                print '  vectorial data via wfs'
                        self.writeShpData(workspacepath)
                except:
                        # Try WCS
                        try:
                                if self.debug:
                                        print '  error in downloading vector data'
                                        print '  try raster data via wcs'
                                self.writeTiffData(workspacepath)
                        except Exception as e:
                                print "    ERROR in downloading raster file:", e
                                pass
                        pass
                print '--Layer downloaded'

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
