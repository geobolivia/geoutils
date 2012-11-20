from geoserver.catalog import Catalog

from re import compile
from re import split
import time
import os
from urlparse import urlparse
from urlparse import urlunparse
from urlparse import urljoin
from urllib import urlretrieve

class LayerDownloader:
	def __init__(self, restConnection=None, layerMetadata=None, replaceTime=None):
                self.layerMetadata = layerMetadata
                if layerMetadata is None:
                        self.workspace = None
                        self.layer = None
                else:
                        regexp = compile(":")
                        tmp = regexp.split(layerMetadata.id)
                        self.workspace = tmp[0]
                        self.layer = tmp[1]

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
