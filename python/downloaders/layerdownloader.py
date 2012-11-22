from geoserver.catalog import Catalog

from osgeo import ogr
ogr.UseExceptions()
from osgeo import gdal
gdal.UseExceptions()

from re import compile
from re import split
import datetime
import time
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
	def __init__(self, restConnection=None, layerMetadata=None, geoserverUrl='http://www.geo.gob.bo/geoserver/', cacheTimeout=60*60*24*7, forceOverwrite=False):
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

                self.cacheTimeout = cacheTimeout
                self.forceOverwrite = forceOverwrite

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
                if not self.testIfOverwriteFile(filename):
                       return

                # Code specific to GeoBolivia way to fill the MetadataUrl fields in GeoServer
                try:
                        mdtuple=urlparse(url)
                        xmlpath=urljoin(mdtuple.path,'iso19139' + extension)
                        xmltuple=[mdtuple.scheme, mdtuple.netloc, xmlpath, mdtuple.params, mdtuple.query, mdtuple.fragment]
                        xmlurl=urlunparse(xmltuple)
                        urlretrieve(xmlurl, filename)
                except:
                        logging.error('The metadata file "' + filename + '" could not be downloaded. URL: ' + xmlpath)
                        raise

        def writeStyle(self, style, filebase):
                # TODO: wrap SLD in human-readable style
                filename = filebase + '.sld'
                if not self.testIfOverwriteFile(filename):
                       return

                with open(filename, 'w') as f:
                        f.write(style.sld_body)

        def writeShpData(self, workspacebase):
                # TODO verify all the files, not only the SHP
                filename = os.path.join(workspacebase, self.layer + '.shp')
                if not self.testIfOverwriteFile(filename):
                        return

                wfsdriver = ogr.GetDriverByName('WFS')
                shpdriver = ogr.GetDriverByName("ESRI Shapefile")
                shpdatasource = shpdriver.CreateDataSource(workspacebase)

                iToDelete=None
                for i in range(0, shpdatasource.GetLayerCount()):
                        shpl = shpdatasource.GetLayerByIndex(i)
                        if shpl.GetName() == self.layer:
                                iToDelete=i
                if iToDelete is not None:
                        shpdatasource.DeleteLayer(iToDelete)
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
                # Default timeout for WCS GDAL driver is 30s
                timeout = '120'
                gtifffilename = os.path.join(workspacebase, self.layer + '.tiff')
                if not self.testIfOverwriteFile(gtifffilename):
                        return

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
                        try:
                                gtiffds = gtiffdriver.CreateCopy(gtifffilename, wcsds, 0, ['TILED=YES', 'COMPRESS=JPEG'])
                        except:
                                gtiffds = gtiffdriver.CreateCopy(gtifffilename, wcsds, 0, ['TILED=YES', 'COMPRESS=DEFLATE'])
                        gtiffds = None
                        wcsds = None
                except:
                        gtiffds = None
                        wcsds = None
                        raise

        def getLayer(self, outputPath):
                logging.info('layer "' + self.layerMetadata.id + '" - starting')
                t1 = datetime.datetime.now()

                someError = False

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
                        try:
                                self.writeMetadata(m['url'],filebase,'.xml')
                        except Exception as e:
                                logging.error("error while downloading XML metadata file: " + str(e))
                                someError = True
                                pass
                        try:
                                self.writeMetadata(m['url'],filebase,'.pdf')
                        except Exception as e:
                                logging.error("error while downloading PDF metadata file: " + str(e))
                                someError = True
                                pass

                # Style
                # TODO - manage various Metadata styles
                for s in self.layerMetadata.styles.keys():
                        logging.debug('layer "' + self.layerMetadata.id + '" - download style in SLD format')
                        try:
                                reststyle = self.restConnection.get_style(s)
                                self.writeStyle(reststyle,filebase)
                        except Exception as e:
                                logging.error("error while downloading SLD style file: " + str(e))
                                someError = True
                                pass
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
                                logging.error("error while downloading raster file: " + str(e))
                                someError = True
                                pass
                        # Todo - test the raster really was downloaded because some error are not raised as exceptions:
                        # ERROR 1: Operation timed out after 30001 milliseconds with 0 bytes received
                        pass
                except Exception as e:
                        logging.warning('error while downloading vector data: ' + str(e))
                        someError = True
                        pass

                delta = datetime.datetime.now() - t1
                logging.info('layer "' + self.layerMetadata.id + '" - processed in ' + str(delta) )

                return someError

        def testIfFileExists(self, filename):
                return os.path.isfile(filename)

        def testIfFileIsValid(self, filename):
                # Check if the size is superior to 100 Bytes
                statinfo = os.stat(filename)
                if statinfo.st_size <= 100:
                        return False

                return True

        def testIfFileCacheIsStillValid(self, filename):
                try:
                        modificationTime = os.path.getctime(filename)
                        expirationTime = modificationTime + self.cacheTimeout
                        now = time.time()
                        if expirationTime < now:
                                logging.debug('Expiration of file cache was ' + str(expirationTime))
                                return False
                        else:
                                logging.debug('Expiration of file cache is ' + str(expirationTime))
                                return True
                except OSError:
                        logging.warning('Unable to find "' + filename + '" file')
                        pass
                return False

        def testIfOverwriteFile(self, filename):
                # Check if file exists
                try:
                        if not self.testIfFileExists(filename):
                                logging.debug('File "' + filename + '" does not exist. Overwrite file.')
                                return True
                except:
                        logging.warning('Error while checking file existence. Overwrite file.')
                        return True

                # File exists - check if it is valid
                try:
                        if not self.testIfFileIsValid(filename):
                                logging.debug('File "' + filename + '" is no valid. Overwrite file.')
                                return True
                except:
                        logging.warning('Error while validating file. Overwrite file')
                        return True

                # File is valid - check if its cache is still valid
                try:
                        if not self.testIfFileCacheIsStillValid(filename):
                                logging.debug('File "' + filename + '" is too old. Overwrite file.')
                                return True
                except:
                        logging.warning('Error while checking cache expiration time. Overwrite file')
                        return True

                # File cache is still valid - force overwriting ?
                if self.forceOverwrite:
                        logging.debug('Force overwrite file.')
                        return True
                else:
                        logging.debug('The file exists and will not be updated. ' + filename)
                        return False
