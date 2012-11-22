#!/usr/bin/python
import getpass
from downloaders import Downloader

# Input parameters
import properties
geoserverUrl = properties.geoserverUrl
if properties.user is None:
	user = raw_input("User: ")
else:
	user = properties.user
if properties.pw is None:
	pw = getpass.getpass('Password: ')
else:
	pw = properties.pw
csvFilename = properties.csvFilename
outputPath = properties.outputPath
firstLayerFilter = properties.firstLayerFilter
cacheTimeout = properties.cacheTimeout
forceOverwrite = properties.forceOverwrite
onlyCheck = properties.onlyCheck

d = Downloader(geoserverUrl, user, pw, cacheTimeout, forceOverwrite)
d.addLayersFromWms()
d.filterAndOrderLayersFromCsv(csvFilename, firstLayerFilter)
if onlyCheck:
        d.checkLayers(outputPath)
else:
        d.getLayers(outputPath)
