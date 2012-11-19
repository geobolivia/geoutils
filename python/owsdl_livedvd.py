#!/usr/bin/python
import gbowsdl
import getpass
import csv
from geoserver.catalog import Catalog

# Input arguments
baseurl='http://www.geo.gob.bo/geoserver/'
outputpath='/tmp/'
user = raw_input("User: ")
pw = getpass.getpass('Password: ')
csvfilename = 'prioridad_test.csv'

resturl=baseurl+'rest'
stylesurl=resturl+'/styles/'
if user is None:
	user = raw_input("User: ")
if pw is None:
	pw = getpass.getpass('Password: ')
cat = Catalog(resturl, username=user, password=pw)

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

# Loop on the layers
for d in datalist:
	workspacename = d[0]
	layername = d[1]
	print 'Download layer ' + workspacename + ':' + layername
	layerbaseurl = baseurl + workspacename + '/' + layername + '/'
	try:
		gbowsdl.get_workspace(layerbaseurl, outputpath, workspacename, layername, cat=cat)
	except Exception as e:
		print "Unexpected error:", e
		pass
