#!/usr/bin/python

# Objeto: utilizando la libreria gsconfig, publicar un SLD en el GeoServer
#
# Uso:
#   subir_sld /path/to/archivo
#
# Parametros: 
# * archivo: el archivo sld a subir

# Excepciones manejadas por gsconfig

# UploadError
# ConflictingDataError
# AmbiguousRequestError
# FailedRequestError
# NotImplementedError

# Excepcion
# ExpatError
# SyntazError

from geoserver.catalog import Catalog
import sys
import os
import curses
import time
import argparse

# Primero: los argumentos
# utilizamos argparse (http://docs.python.org/howto/argparse.html)
# * creacion del parser
parser = argparse.ArgumentParser()
# * especificacion del argumento archivo, de tipo "argparse.FileType('r')", es decir que es un archivo abierto.
parser.add_argument("archivo", 
	help="Archivo SLD a subir en el servidor GeoServer de dev de GeoBolivia",
	type=argparse.FileType('r')
	)
# * hacemos un parsing, con verificacion, de los argumentos
args = parser.parse_args()

# Funcion de conexion a GeoServer
def connectar_geoserver(stdscr):
	# Datos para la conexion a GeoServer
	user = 'admin_geobolivia'
	password = 'YGoL3lSJYCwjCLDC'
	url_geoserver = "http://www-dev.geo.gob.bo/geoserver/rest"

	# Conexion a GeoServer
	cat = Catalog(url_geoserver, user, password)

	# Probar la conexion con una consulta simple
	try:
		all_workspaces = cat.get_workspaces()
	except Exception as e:
		# Salio una excepcion: la mostramos y relanzamos la excepcion
		stdscr.addstr("Error durante la conexion al GeoServer:\n%s\n" % e)
		raise

	return cat

# Funcion de recuperacion de los argumentos
def recuperar_archivo(stdscr, archivo):
	# Verificamos que la extension es SLD (.sld)
	fileName, fileExtension = os.path.splitext(archivo.name)
	if fileExtension != ".sld":
		stdscr.addstr("El archivo %s no tiene la extension SLD\n" % archivo.name)
		return None,None

	# Base del archivo (nombre del estilo)
	nombreEstilo = os.path.basename(fileName)

	# Todo esta OK - retornamos el archivo
	return archivo.name,nombreEstilo

# Funcion llamada justo antes de salir
def salir(stdscr,mensaje=""):
	if mensaje:
		stdscr.addstr(mensaje)

	stdscr.addstr("Cualquier tecla para salir.\n")
	c = stdscr.getch()

	return None

def subir_sld(stdscr, cat, archivo):
	# Recuperar el nombre del archivo
	nombreArchivo,nombreEstilo = recuperar_archivo(stdscr,archivo)
	if not nombreArchivo:
		return None

	# Salida grafica
	stdscr.addstr("Subimos el archivo %s de estilo en el servidor http://www-dev.geo.gob.bo/geoserver/\n" % nombreArchivo)
	# Miramos si ya existe el estilo - preguntar que hacer
	try:
		estilo = cat.get_style(nombreEstilo)
	except Exception as e:
		stdscr.addstr("No se pudo recuperar el estilo %s\n" % nombreEstilo)
		return None
		
	if estilo:
		i = 3
		while i > 0:
			i -=1
			stdscr.addstr("\nEl estilo '%s' ya existe en el servidor. [R]emplazar, [D]ejar la version anterior o [B]orrarla sin subir la nueva ?\n" % estilo.name)
			c = stdscr.getch()
			if c == ord('R'):
				# Existe el estilo, subimos una nueva version (remplazamos)
				try:
					cat.create_style(nombreEstilo, archivo.read(), overwrite=True)
					stdscr.addstr("Estilo remplazado en el servidor\n")
				except Exception as e:
					stdscr.addstr("Salio un error al remplazar el archivo:\n%s\n" % e)
					return None
				break # Exit the while()
			elif c == ord('B'):
				# Existe el estilo, lo borramos
				# http://jira.codehaus.org/browse/GEOS-3621
				try:
					cat.delete(estilo,purge=True)
					stdscr.addstr("Estilo borrado en el servidor\n")
				except Exception as e:
					stdscr.addstr("Salio un error al borrar el estilo en el servidor:\n%s\n" % e)
					return None
				break # Exit the while()
			elif c == ord('D'):
				# No hacemos nada
				stdscr.addstr("Dejamos la version anterior del estilo en el servidor\n")
				break # Exit the while()
		if i == 0:
			stdscr.addstr("No se entiende - dejamos la version anterior del estilo en el servidor\n")
	else:
		# No existe el estilo, lo subimos
		# para el uso de "with", ver http://effbot.org/zone/python-with-statement.htm
		# -> el archivo se cerrara automaticamente
		try:
			cat.create_style(nombreEstilo, archivo.read())
			stdscr.addstr("Estilo subido en el servidor\n")
		except Exception as e:
			stdscr.addstr("Salio un error al subir el archivo:\n%s\n" % e)
			return None
	return None


def main(stdscr,args):
	# Verificamos que funciono la conexion
	try:
		cat =  connectar_geoserver(stdscr)
	except Exception as e:
		return salir(stdscr,"La conexion con el GeoServer fallo\n")

	# Subir el archivo SLD
	subir_sld(stdscr, cat, args.archivo)

	# Todo salio bien - mensaje para terminar la funcion
	return salir(stdscr)

# Creacion de la pantalla con curses
# ver http://docs.python.org/howto/curses.html#curses-howto para un tutorial sobre curses
curses.wrapper(main,args)

# Fin
# cerrar el archivo (argparser lo abre al momento del parsing)
args.archivo.close()
# salir
quit()
