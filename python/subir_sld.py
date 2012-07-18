#!/usr/bin/python

# Objeto: utilizando la libreria gsconfig, publicar un SLD en el GeoServer
#
# Parametros: ninguno

from geoserver.catalog import Catalog
import sys
import os

# Datos para la conexion a GeoServer
user = 'admin_geobolivia'
password = 'YGoL3lSJYCwjCLDC'
url_geoserver = "http://www-dev.geo.gob.bo/geoserver/rest"

# Verificamos que se dio un argumento en la linea de comando
if len(sys.argv) < 2:
	print "Dar el archivo SLD como argumento: %s /path/to/archivo.sld" % sys.argv[0]
	quit()

# Verificamos que el archivo dado en la linea de comando existe
# (sacamos los eventuales ", ', espacio)
#archivo = sys.argv[1].strip(' \"\'')
archivo = sys.argv[1]
if not os.path.isfile(archivo):
	print "El archivo %s no existe" % archivo
	quit()
	
# Verificamos que la extension es SLD (.sld)
fileName, fileExtension = os.path.splitext(archivo)
baseArchivo = os.path.basename(fileName)
if fileExtension != ".sld":
	print "El archivo %s no tiene la extension SLD" % archivo
	quit()

# Salida grafica
print "Subimos el archivo %s de estilo en el servidor http://www-dev.geo.gob.bo/geoserver/\n" % archivo

# Conexion a GeoServer
cat = Catalog(url_geoserver, user, password)

# Verificamos que funciono la conexion
if not cat:
	print "La conexion con el GeoServer fallo"
	quit()

# Miramos si ya existe el estilo
estilo = cat.get_style(baseArchivo)
if estilo:
	print "Ya existe el estilo %s en el servidor" % estilo.name
	quit()

# No existe el estilo, lo subimos
# para el uso de "with", ver http://effbot.org/zone/python-with-statement.htm
# -> el archivo se cerrara automaticamente
with open(archivo) as f:
	cat.create_style(baseArchivo, f.read())
