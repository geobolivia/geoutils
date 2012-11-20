from geoserver.catalog import Catalog

class LayerDownloader:
	def __init__(self, workspace=None, layer=None, restConnection=None):
		self.workspace = workspace
		self.layer = layer
                if restConnection is None:
                        self.restConnection = connectToRest()

	def connectToRest(restUrl=None, username=None, password=None):
                """
                Connect to the REST interface of GeoServer
                """
		return Catalog(restUrl, username=username, password=password)

        connectToRest = staticmethod(connectToRest)
