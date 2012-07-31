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
all_layers = cat.get_layers()

# Recuperar estadisticas sobre las capas
sin_metadata = 0
nb_capas = len(all_layers)
print "Capas sin metadatos:"
print ""
sys.stdout.flush()

for i,layer in enumerate(all_layers):
	try:
		if (not layer.resource.metadata_links):
			sin_metadata += (not layer.resource.metadata_links)
			print "%d/%d - %s - %s\n" % (i,nb_capas,layer.resource.workspace,layer.name),
			sys.stdout.flush()
	except:
		pass

# Mostrar el numero de capas
print "* " + str(len(all_layers)) + " capas"
# Mostrar el numero de capas con un metadato
print "  * " + str(sin_metadata) + " capas sin metadata"
