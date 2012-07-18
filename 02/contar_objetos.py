#!/usr/bin/python

# Objeto: contar los workspaces, con la libreria gsconfig
#
# Parametros: ninguno

from geoserver.catalog import Catalog
import sys

user = 'admin_geobolivia'
password = 'YGoL3lSJYCwjCLDC'
cat = Catalog("http://www.geo.gob.bo/geoserver/rest", user, password)

# Recuperar los datos
all_workspaces = cat.get_workspaces()
all_stores = cat.get_stores()
all_layers = cat.get_layers()

# Recuperar estadisticas sobre las capas
sin_metadata = 0
sin_recurso = []
nb_capas = len(all_layers)
print str(nb_capas) + " capas"
for i,layer in enumerate(all_layers):
	print "\r%d/%d - %s" % (i,nb_capas,str(layer)),
	sys.stdout.flush()
	if layer.resource:
		sin_metadata += (not layer.resource.metadata_links)
	else:
		sin_recurso.append(layer)

# Salida grafica
print "ESTADISTICAS DE GEOBOLIVIA (http://www.geo.gob.bo)\n"

# Mostrar el numero de workspaces
print "* " + str(len(all_workspaces)) + " workspaces"

# Mostrar el numero de almacenes
print "* " + str(len(all_stores)) + " almacenes"

# Mostrar el numero de capas
print "* " + str(len(all_layers)) + " capas"
# Mostrar el numero de capas con un metadato
print "  * " + str(sin_metadata) + " capas sin metadata"
print "  * " + str(len(sin_recurso)) + " capas sin recurso"
for i,layer in enumerate(sin_recurso):
	print "    * capa " + layer.name
	
