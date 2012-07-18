#!/usr/bin/python

# Objeto: jalar la lista de workspaces, con la libreria pycurl
#
# Parametros: ninguno

import pycurl
import sys

# Unos testeos de que las librerias estan cargadas
#print pycurl.__doc__
#print >>sys.stderr, 'Testing', pycurl.version

class Test:
	def __init__(self):
		self.contents = ''

	def body_callback(self, buf):
		self.contents = self.contents + buf

user = 'admin_geobolivia'
password = 'YGoL3lSJYCwjCLDC'
t = Test()
c = pycurl.Curl()
c.setopt(c.URL, 'http://' + user + ':' + password + '@www-dev.geo.gob.bo/geoserver/rest/workspaces.json')
c.setopt(c.WRITEFUNCTION, t.body_callback)
c.perform()
c.close()

print t.contents
