from downloaders.layerdownloader import LayerDownloader

from owslib.wms import WebMapService

import csv
import os

class Downloader:
	"""
	Class for downloading and managing a repository of GeoBolivia data.
	"""
	def __init__(self, geoserverUrl='http://www.geo.gob.bo/geoserver/', username=None, password=None, debug=None):
                """
                Constructor.
                layerDownloaders: a dictionary of LayerDownloader objects (key: layerId)
                baseUrl: URL of geoserver, eg. 'http://www.geo.gob.bo/geoserver/'
                """
                self.layerDownloaders = {}
                self.geoserverUrl = geoserverUrl
                self.restConnection = LayerDownloader.connectToRest(geoserverUrl + '/rest/', username=username, password=password)
                self.debug = debug
                if debug is None:
                        debug = False
                self.warning = True

        def forgeOwsUrl(self, ows='wms'):
                baseUrl = self.geoserverUrl
                baseUrl += '/' + ows + '?'
                return baseUrl

        def addLayersFromWms(self):
                """Add new LayerDownloaders from the result of a WMS GetCapabilities
                """
                wmsUrl = self.forgeOwsUrl('wms')
                wms = WebMapService(wmsUrl, version='1.1.1')
                layers = wms.items()
                for l in layers:
                        self.addLayerDownloader(l[1])
                return self.layerDownloaders

        def filterLayersFromCsv(self, csvFilename, firstLayerFilter=None):
                #layersFilter = ['otros:mosaico_landsat', 'otros:Spot', 'inra:Predios2012']
                layersFilter = []
                with open(csvFilename, 'rb') as csvfile:
                        csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
                        for row in csvreader:
                                layersFilter.append(row[0] + ':' + row[1])

                if firstLayerFilter in layersFilter:
                        firstindex = layersFilter.index(firstLayerFilter)
                        layersFilter = layersFilter[firstindex:]

                unwanted = set(self.layerDownloaders) - set(layersFilter)
                for unwanted_key in unwanted:
                        if self.debug:
                                print 'DEBUG the following layer will not be downloaded', unwanted_key
                        del self.layerDownloaders[unwanted_key]
                if self.warning:
                        print 'WARNING ' + str(len(unwanted)) + ' layers have been filtered and will not be downloaded'

                notfound = set(layersFilter) - set(self.layerDownloaders)
                layersFilter = [l for l in layersFilter if not l in notfound]
                if self.warning:
                        print 'WARNING ' + str(len(notfound)) + ' layers were not found', ', '.join(notfound)

        def addLayerDownloader(self, layerMetadata):
                """Create a new layer downloader and add to the list
                layerMetadata: metadata object (of owslib) of the new layer
                """
                ld = LayerDownloader(self.restConnection, layerMetadata, self.geoserverUrl, debug=self.debug)
                if layerMetadata.id in self.layerDownloaders:
                        print 'WARNING new metadata definition for the layer', layerMetadata.id
                self.layerDownloaders[layerMetadata.id] = ld
                return ld

        def getLayers(self, outputpath):
                for layerId in self.layerDownloaders:
                        ld = self.layerDownloaders[layerId]
                        if not ld.workspace is None:
                                workspacepath = os.path.join(outputpath,ld.workspace)
                        else:
                                workspacepath = outputpath
                        if not os.access(workspacepath, os.W_OK):
                                os.mkdir(workspacepath)
                        filebase = os.path.join(workspacepath,ld.layer)

                        if self.debug:
                                print '--Get layer ' + ld.layerMetadata.id
                        ld.getLayer(filebase, workspacepath)
