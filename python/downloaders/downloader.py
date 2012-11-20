from downloaders.layerdownloader import LayerDownloader

from owslib.wms import WebMapService

import os

class Downloader:
	"""
	Class for downloading and managing a repository of GeoBolivia data.
	"""
	def __init__(self, geoserverUrl='http://www.geo.gob.bo/geoserver/', username=None, password=None, workspace=None, layer=None, debug=None):
                """
                Constructor.
                ldList: a list of LayerDownloader objects
                baseUrl: URL of geoserver, eg. 'http://www.geo.gob.bo/geoserver/'
                """
                self.ldList = []
                self.geoserverUrl = geoserverUrl
                self.restConnection = LayerDownloader.connectToRest(geoserverUrl + '/rest/', username=username, password=password)
                self.workspace = workspace
                self.layer = layer
                self.debug = debug
                if debug is None:
                        debug = True

        def forgeOwsUrl(self, ows='wms'):
                baseUrl = self.geoserverUrl
                if not self.workspace is None:
                        baseUrl += '/' + self.workspace
                        if not self.layer is None:
                                baseUrl += '/' + self.layer
                baseUrl += '/' + ows + '?'
                return baseUrl

        def addLayersFromWms(self):
                """Add new LayerDownloaders from the result of a WMS GetCapabilities
                """
                wmsUrl = self.forgeOwsUrl('wms')
                wms = WebMapService(wmsUrl, version='1.1.1')
                layers = wms.items()
                for l in layers:
                        layerMetadata = l[1]
                        self.addLayerDownloader(layerMetadata)
                return self.ldList

        def addLayerDownloader(self, layerMetadata):
                """Create a new layer downloader and add to the list
                layerMetadata: metadata object (of owslib) of the new layer
                """
                ld = LayerDownloader(self.restConnection, layerMetadata, self.geoserverUrl)
                self.ldList.append(ld)
                return ld

        def getLayers(self, outputpath):
                layers = self.addLayersFromWms()

                if len(layers) == 0:
                        print '  ERROR: layer not found on WMS server ' + self.workspace + ':' + self.layer

                for ld in layers:
                        workspacepath = os.path.join(outputpath,ld.workspace)
                        if not os.access(workspacepath, os.W_OK):
                                os.mkdir(workspacepath)
                        filebase = os.path.join(workspacepath,ld.layer)

                        if self.debug:
                                print '--Get layer ' + ld.layerMetadata.id
                        ld.getLayer(filebase, workspacepath)
