#!/usr/bin/python

# Objeto: jalar la lista de workspaces, con la libreria gsconfig
#
# Parametros: ninguno

from geoserver.catalog import Catalog

user = 'admin_geobolivia'
password = 'YGoL3lSJYCwjCLDC'
cat = Catalog("http://www-dev.geo.gob.bo/geoserver/rest", user, password)
all_workspaces = cat.get_workspaces()

print all_workspaces
print all_workspaces
