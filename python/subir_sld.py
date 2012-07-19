#!/usr/bin/python

# Objeto: utilizando la libreria gsconfig, publicar un SLD en el GeoServer
#
# Parametros: 
# * archivo: el archivo sld a subir

from geoserver.catalog import Catalog
import sys
import os
import curses
import time

# Excepciones manejadas por gsconfig

# UploadError
# ConflictingDataError
# AmbiguousRequestError
# FailedRequestError
# NotImplementedError

# Excepcion
# ExpatError
# SyntazError

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
def recuperar_archivo(stdscr):
	# Verificamos que se dio un argumento en la linea de comando
	if len(sys.argv) < 2:
		stdscr.addstr("Dar el archivo SLD como argumento: %s /path/to/archivo.sld\n" % sys.argv[0])
		return None,None

	# Verificamos que el archivo dado en la linea de comando existe
	# (sacamos los eventuales ", ', espacio)
	#archivo = sys.argv[1].strip(' \"\'')
	archivo = sys.argv[1]
	if not os.path.isfile(archivo):
		stdscr.addstr("El archivo %s no existe\n" % archivo)
		return None,None
	
	# Verificamos que la extension es SLD (.sld)
	fileName, fileExtension = os.path.splitext(archivo)
	if fileExtension != ".sld":
		stdscr.addstr("El archivo %s no tiene la extension SLD\n" % archivo)
		return None,None

	# Base del archivo (nombre del estilo)
	nombreEstilo = os.path.basename(fileName)

	# Todo esta OK - retornamos el archivo
	return archivo,nombreEstilo

# Funcion llamada justo antes de salir
def salir(stdscr,mensaje=""):
	if mensaje:
		stdscr.addstr(mensaje)

	stdscr.addstr("Cualquier tecla para salir.\n")
	c = stdscr.getch()

	return None

def main(stdscr):
	# Recuperar el nombre del archivo
	archivo,nombreEstilo = recuperar_archivo(stdscr)
	if not archivo:
		return salir(stdscr,"La recuperacion del archivo SLD fallo\n")

	# Verificamos que funciono la conexion
	try:
		cat =  connectar_geoserver(stdscr)
	except Exception as e:
		return salir(stdscr,"La conexion con el GeoServer fallo\n")

	# Salida grafica
	stdscr.addstr("Subimos el archivo %s de estilo en el servidor http://www-dev.geo.gob.bo/geoserver/\n" % archivo)

	# Miramos si ya existe el estilo - preguntar que hacer
	try:
		estilo = cat.get_style(nombreEstilo)
	except Exception as e:
		return salir(stdscr,"No se pudo recuperar el estilo %s\n", nombreEstilo)
		
	if estilo:
		i = 3
		while i > 0:
			i -=1
			stdscr.addstr("\nEl estilo '%s' ya existe en el servidor. [R]emplazar, [D]ejar la version anterior o [B]orrarla sin subir la nueva ?\n" % estilo.name)
			c = stdscr.getch()
			if c == ord('R'):
				# Existe el estilo, subimos una nueva version (remplazamos)
				with open(archivo) as f:
					try:
						cat.create_style(nombreEstilo, f.read(), overwrite=True)
						stdscr.addstr("Estilo remplazado en el servidor\n")
					except Exception as e:
						return salir(stdscr,"Salio un error al remplazar el archivo:\n%s\n" % e)
				break # Exit the while()
			elif c == ord('B'):
				# Existe el estilo, lo borramos
				try:
					cat.delete(estilo,purge=True)
					stdscr.addstr("Estilo borrado en el servidor\n")
				except Exception as e:
					return salir(stdscr,"Salio un error al borrar el estilo en el servidor:\n%s\n" % e)
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
		with open(archivo) as f:
			try:
				cat.create_style(nombreEstilo, f.read())
				stdscr.addstr("Estilo subido en el servidor\n")
			except Exception as e:
				return salir(stdscr,"Salio un error al subir el archivo:\n%s\n" % e)
# http://jira.codehaus.org/browse/GEOS-3621

	# Todo salio bien - mensaje para terminar la funcion
	return salir(stdscr)

# Creacion de la pantalla con curses
# ver http://docs.python.org/howto/curses.html#curses-howto para un tutorial sobre curses
curses.wrapper(main)

# Esperamos un segundo antes de terminar
time.sleep(0.2)

# Fin
quit()
