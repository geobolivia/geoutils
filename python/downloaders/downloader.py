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
                self.layerDownloaders = []
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

        def filterAndOrderLayersFromCsv(self, csvFilename, firstLayerFilter=None):
                #layersFilter = ['otros:mosaico_landsat', 'otros:Spot', 'inra:Predios2012']
                layersFilter = []
                with open(csvFilename, 'rb') as csvfile:
                        csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
                        for row in csvreader:
                                layersFilter.append(row[0] + ':' + row[1])

                if firstLayerFilter in layersFilter:
                        firstindex = layersFilter.index(firstLayerFilter)
                        layersFilter = layersFilter[firstindex:]

                # Convert the list in dictionary for manipulation comodity
                tmpLayerDownloaders = {ld.layerMetadata.id: ld for ld in self.layerDownloaders}
                lenDiff = len(self.layerDownloaders) - len(tmpLayerDownloaders)
                if lenDiff > 0 and self.warning:
                        print 'WARNING ' + str(lenDiff) + ' duplicated layers (same identifier as another) have been deleted'
                        # TODO - in DEBUG mode, list the duplicated layers that have been deleted

                # Filter existing layerDownloaders
                unwanted = set(tmpLayerDownloaders) - set(layersFilter)
                for unwanted_key in unwanted:
                        if self.debug:
                                print 'DEBUG the following layer will not be downloaded', unwanted_key
                        del tmpLayerDownloaders[unwanted_key]
                if self.warning:
                        print 'WARNING ' + str(len(unwanted)) + ' layers have been filtered and will not be downloaded'

                # Delete unknown layers in filter
                notfound = set(layersFilter) - set(tmpLayerDownloaders)
                layersFilter = [l for l in layersFilter if not l in notfound]
                if self.warning:
                        print 'WARNING ' + str(len(notfound)) + ' layers were not found', ', '.join(notfound)

                # Order the layerDownloaders, converting into list
                self.layerDownloaders = [tmpLayerDownloaders[key] for key in layersFilter]

        def addLayerDownloader(self, layerMetadata):
                """Create a new layer downloader and add to the list
                layerMetadata: metadata object (of owslib) of the new layer
                """
                ld = LayerDownloader(self.restConnection, layerMetadata, self.geoserverUrl, debug=self.debug)
                self.layerDownloaders.append(ld)
                return ld

        def getLayers(self, outputPath):
                for ld in self.layerDownloaders:
                        ld.getLayer(outputPath)
