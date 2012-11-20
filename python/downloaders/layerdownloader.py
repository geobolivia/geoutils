from geoserver.catalog import Catalog

from re import compile
from re import split

class LayerDownloader:
	def __init__(self, restConnection=None, layerMetadata=None):
                self.layerMetadata = layerMetadata
                if layerMetadata is None:
                        self.workspace = None
                        self.layer = None
                else:
                        regexp = compile(":")
                        tmp = regexp.split(layerMetadata.id)
                        self.workspace = tmp[0]
                        self.layer = tmp[1]

                if restConnection is None:
                        self.restConnection = connectToRest()

	def connectToRest(restUrl=None, username=None, password=None):
                """
                Connect to the REST interface of GeoServer
                """
		return Catalog(restUrl, username=username, password=password)

        connectToRest = staticmethod(connectToRest)
