#!/usr/bin/python
import gbowsdl
import getpass
import csv
from geoserver.catalog import Catalog

# Input parameters
import properties
geoserverurl = properties.baseurl
if properties.user is None:
	user = raw_input("User: ")
else:
	user = properties.user
if properties.pw is None:
	pw = getpass.getpass('Password: ')
else:
	pw = properties.pw
csvfilename = properties.csvfilename
outputpath = properties.outputpath
firstdata = properties.firstdata

# Read CSV file
def read_csv(csvfilename):
	datalist = []
	with open(csvfilename, 'rb') as csvfile:
		csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
		for row in csvreader:
			datalist.append([row[0], row[1]])
	return datalist

#datalist = [('otros', 'mosaico_landsat'), ('otros', 'Spot'), ('inra', 'Predios2012')]
datalist = read_csv(csvfilename)
if firstdata in datalist:
	firstindex = datalist.index(firstdata)
	datalist = datalist[firstindex:]

# Loop on the layers
for d in datalist:
	workspacename = d[0]
	layername = d[1]
	print 'Download layer ' + workspacename + ':' + layername
	#layerbaseurl = baseurl + workspacename + '/' + layername + '/'
#	try:
	gbowsdl.get_workspace(geoserverurl, outputpath, workspacename, layername, user=user, pw=pw)
#	except Exception as e:
#		print "  ERROR downloading data for layer " + workspacename + ':' + layername + ": ", e
#		pass
