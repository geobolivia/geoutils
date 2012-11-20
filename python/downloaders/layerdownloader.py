from geoserver.catalog import Catalog

from osgeo import ogr
from osgeo import gdal

from re import compile
from re import split
import datetime
import os
from urlparse import urlparse
from urlparse import urlunparse
from urlparse import urljoin
from urllib import urlretrieve
from xml.etree.ElementTree import Element, SubElement, tostring

import logging

logging.basicConfig(format='%(asctime)s %(levelname)s\t%(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)

# Libraries
# ogr: WFS, SHP
#  http://www.gdal.org/ogr/drv_wfs.html
#  http://www.paolocorti.net/2011/03/23/a-quick-look-at-the-wfs-gdal-driver/
# owslib: WMS (CSW)
#  http://geopython.github.com/OWSLib/
# gsconfig: SLD
#  http://dwins.github.com/gsconfig.py/

class LayerDownloader:
	def __init__(self, restConnection=None, layerMetadata=None, geoserverUrl='http://www.geo.gob.bo/geoserver/', replaceTime=None):
                self.layerMetadata = layerMetadata
                if layerMetadata is None:
                        self.workspace = None
                        self.layer = None
                else:
                        regexp = compile(":")
                        tmp = regexp.split(layerMetadata.id)
                        if len(tmp) == 2:
                                self.workspace = tmp[0]
                                self.layer = tmp[1]
                        elif len(tmp) == 1:
                                self.workspace = None
                                self.layer = tmp[0]
                        else:
                                logging.error('the layerId is incorrect (more than one ":" characters): ' + layerMetadata.id)
                                # TODO raise an exception

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
                timeout = '120'
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
                child = SubElement(top, 'Timeout')
                child.text = str(timeout)
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

        def getLayer(self, outputPath):
                logging.info('layer "' + self.layerMetadata.id + '" - start downloading')
                t1 = datetime.datetime.now()

                if not self.workspace is None:
                        workspacepath = os.path.join(outputPath, self.workspace)
                else:
                        workspacepath = outputPath
                if not os.access(workspacepath, os.W_OK):
                        os.mkdir(workspacepath)
                filebase = os.path.join(workspacepath, self.layer)

                # Metadata
                # TODO - manage various Metadata Urls
                for m in self.layerMetadata.metadataUrls:
                        logging.debug('layer "' + self.layerMetadata.id + '" - download metadata in xml and pdf formats')
                        self.writeMetadata(m['url'],filebase,'.xml')
                        self.writeMetadata(m['url'],filebase,'.pdf')

                # Style
                # TODO - manage various Metadata styles
                for s in self.layerMetadata.styles.keys():
                        logging.debug('layer "' + self.layerMetadata.id + '" - download style in SLD format')
                        reststyle = self.restConnection.get_style(s)
                        self.writeStyle(reststyle,filebase)

                # Data
                # Try WFS
                try:
                        logging.debug('layer "' + self.layerMetadata.id + '" - download vectorial data from WMS in SHP format')
                        self.writeShpData(workspacepath)
                except ValueError:
                        # There was no WFS layer with this identifier - try WCS
                        try:
                                logging.debug('layer "' + self.layerMetadata.id + '" - download raster data from WCS in GeoTIFF format')
                                self.writeTiffData(workspacepath)
                        except Exception as e:
                                logging.error("error in downloading raster file: " + e)
                                pass
                        # Todo - test the raster really was downloaded because some error are not raised as exceptions:
                        # ERROR 1: Operation timed out after 30001 milliseconds with 0 bytes received
                        pass
                except Exception as e:
                        logging.warning('error in downloading vector data: ' + e)
                        pass

                delta = datetime.datetime.now() - t1
                logging.info('layer "' + self.layerMetadata.id + '" - succesfully downloaded in ' + str(delta) )

        def test_update_file(filename, replaceTime):
                now = time.time()
                too_old = now - replaceTime
                try:
                        modification_time = os.path.getctime(filename)
                except OSError:
                        pass
                        return True

                logging.info('    the file exists and is new - download aborted')

                if modification_time < too_old:
                        return True

                return False
