from downloaders.layerdownloader import LayerDownloader

from re import compile
from re import split

class Downloader:
	"""
	Class for downloading and managing a repository of GeoBolivia data.
	"""
	def __init__(self, geoserverUrl='http://www.geo.gob.bo/geoserver/', username=None, password=None):
                """
                Constructor.
                ldList: a list of LayerDownloader objects
                baseUrl: URL of geoserver, eg. 'http://www.geo.gob.bo/geoserver/'
                """
                self.ldList = []
                self.geoserverUrl = geoserverUrl
                self.restConnection = LayerDownloader.connectToRest(geoserverUrl + '/rest/', username=username, password=password)

        def addLayerDownloader(self, layerId):
                """Create a new layer downloader and add to the list
                layerId: identifier of the new layer (for GeoServer: workspace:layername)
                """
		regexp = compile(":")
		tmp = regexp.split(layerId)
		workspace = tmp[0]
		layer = tmp[1]
                ld = LayerDownloader(workspace, layer, self.restConnection)
                self.ldList.append(ld)
                return ld
