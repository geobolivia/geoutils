#!/usr/bin/python

# Objeto: contar los workspaces, con la libreria gsconfig
#
# Parametros: ninguno

from geoserver.catalog import Catalog
import sys
import csv
c = csv.writer(open("TLayers-03042014.csv", "wb"), delimiter=';', quotechar='|')


user = 'USER'
password = 'PASS'


cat = Catalog("http://geo.gob.bo/geoserver/rest", user, password)

# Recuperar los datos
all_layers = cat.get_layers()


# Recuperar estadisticas sobre las capas
sin_metadata = 0
nb_capas = len(all_layers)
print "Capas sin metadatos:"
print ""

#that_layer = cat.get_layer("PassifloraInsignis")
# that_layer.enabled = True

# print that_layer.resource.workspace,that_layer.name,that_layer.resource.metadata_links,that_layer.resource.native_bbox,that_layer.default_style

c.writerow([\
"nro",\
"enabled",\
"WS",\
"DS",\
"DS_ConnProperties",\
"layerName",\
"title",\
"abstract",\
"metadata_links",\
"default_style",\
"native_bbox",\
"latlon_bbox ",\
"projection",\
"projection_policy"\
])


#"default_style",\
#"attribution_object",\
#"keywords",\
#"native_bbox",\
#"projection",\
#"projection_policy",\
#"latlon_bbox ",\
#"enabled"\

print "hola"
for i,that_layer in enumerate(all_layers):
	try:	
		Li = i
	except:
		Li = "<Error>"
	try:
		enabled = that_layer.enabled
	except:
		enabled = "<Error>"
	try:
		WS = str(that_layer.resource.store.workspace.name)
	except:
		WS = "<Error>"
	try:
		DS = str(that_layer.resource.store.name)
	except:
		DS = "<Error>"
	try:
		DS_ConnProperties = str(that_layer.resource.store.connection_parameters)
	except:
		DS_ConnProperties = "<Error>"
	try:
		Layer = that_layer.name
	except:
		Layer = "<Error>"	
	try:
		Title = unicode(that_layer.resource.title,"utf-8")
	except:
		Title = "<Error>"	
	try:
		Abstract = unicode(that_layer.resource.abstract,"utf-8")
	except:
		Abstract = "<Error>"
	try:
		Metadata0 = str(that_layer.resource.metadata_links)
	except:
		Metadata0 = "<Error>"
	try:
		default_style = str(that_layer.default_style.name)
	except:
		default_style = "<Error>"
	try:
		native_bbox = str(that_layer.resource.native_bbox)
	except:
		native_bbox = "<Error>"
	try:
		latlon_bbox = str(that_layer.resource.latlon_bbox)
	except:
		latlon_bbox = "<Error>"
	try:
		projection = str(that_layer.resource.projection)
	except:
		projection = "<Error>"
	try:
		projection_policy = str(that_layer.resource.projection_policy)
	except:
		projection_policy = "<Error>"
	
	print WS, DS, Layer
	
	if WS != "":
		WS2 = WS.encode("utf-8")
	if DS != "":
		DS2 = DS.encode("utf-8")
	if DS_ConnProperties != "":
		DS_ConnProperties2 = DS_ConnProperties.encode("utf-8")
	if Layer != "":
		Layer2 = Layer.encode("utf-8")
	if Title != "":
		Title2 = Title.encode("utf-8")
	if Abstract != "":
		Abstract2 = Abstract.encode("utf-8")
	if Metadata0 != "":
		Metadata2 = Metadata0.encode("utf-8")
	if default_style != "":
		default_style2 = default_style.encode("utf-8")
	if native_bbox != "":
		native_bbox2 = native_bbox.encode("utf-8")
	if latlon_bbox != "":
		latlon_bbox2 = latlon_bbox.encode("utf-8")
	if projection != "":
		projection2 = projection.encode("utf-8")
	if projection_policy != "":
		projection_policy2 = projection_policy.encode("utf-8")
	c.writerow([Li,enabled,WS,DS,DS_ConnProperties2,Layer2,Title2,Abstract2,Metadata2,default_style2,native_bbox2,latlon_bbox2,projection2,projection_policy2])

#c.writerow([i,\W
#that_layer.enabled,\

#that_layer.resource.store.workspace.name,\
#that_layer.resource.store.name,\
#that_layer.name,\
#that_layer.default_style.name,\
#that_layer.resource.title,\
#that_layer.resource.abstract,\
#that_layer.resource.metadata_links\
#])
#that_layer.attribution_object,\
#that_layer.resource.keywords,\
#that_layer.resource.native_bbox,\
#that_layer.resource.projection,\
#that_layer.resource.projection_policy,\
#that_layer.resource.latlon_bbox,\
#that_layer.resource.enabled\
	
print "terminado"
print nb_capas
