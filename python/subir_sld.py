#!/usr/bin/python
# -*- coding: utf-8 -*-

# Objeto: utilizando la libreria gsconfig, publicar un SLD en el GeoServer
#
# Uso:
#   subir_sld /path/to/archivos
#
# Parametros: 
# * archivos: el archivo sld a subir / o la carpeta con archivos sld

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
import getpass

# Primero: los argumentos
# utilizamos argparse (http://docs.python.org/howto/argparse.html)
# * creacion del parser
parser = argparse.ArgumentParser()
# * funcion para abrir un archivo, verificando que es de tipo SLD
def test_and_open_sld_file(files,fileName):
	# parece un archivo SLD (extension .sld) ?
	fileBase, fileExtension = os.path.splitext(fileName)
	if fileExtension == ".sld":
		# Parece un archivo SLD - probamos de abrirlo
		try:
			f = open(fileName,'rt')
			# Lo pudimos abrir - anadimos el archivo abierto
			files.append(f)
		except IOError as e:
			# No se puede abrir
			pass
	return files
# * funcion para abrir el archivo SLD, o los archivos SLD si el argumento es una carpeta
# * devuelve una lista de los archivos SLD abiertos para lectura en modo texto
def parse_archivos(path):
	# Creamos la lista de archivos SLD abiertos
	files = []

	if os.path.isfile(path):
		# parece un archivo
		files = test_and_open_sld_file(files,path)
	elif os.path.isdir(path):
		# parece una carpeta, probamos de abrir sus archivos
		fileNames=os.listdir(path)
		for fileName in	fileNames:
			files = test_and_open_sld_file(files,os.path.join(path, fileName))

	return files

# * especificacion del argumento archivo, de tipo "argparse.FileType('r')", es decir que es un archivo abierto.
parser.add_argument("archivos", 
	help="archivo SLD / carpeta de archivos SLD - para subir en el servidor GeoServer de dev de GeoBolivia",
	type=parse_archivos,
	)

# * hacemos un parsing, con verificacion, de los argumentos
args = parser.parse_args()

# Funcion de conexion a GeoServer
def connectar_geoserver(stdscr,user,pw):
	# Datos para la conexion a GeoServer
	url_geoserver = "http://www-dev.geo.gob.bo/geoserver/rest"

	# Conexion a GeoServer
	cat = Catalog(url_geoserver, user, pw)

	# Probar la conexion con una consulta simple
	try:
		all_workspaces = cat.get_workspaces()
	except Exception as e:
		# Salio una excepcion: la mostramos y relanzamos la excepcion
		stdscr.addstr("Error durante la conexion al GeoServer:\n%s\n" % e)
		raise

	return cat

# Crear el nombre del estilo
def crear_nombre_estilo(archivo):
	# Recuperamos el nombre de archivo sin la extension
	fileName, fileExtension = os.path.splitext(archivo.name)

	# Base del archivo (nombre del estilo)
	nombreEstilo = os.path.basename(fileName)

	# Retornamos el nombre del estilo
	return nombreEstilo

# Funcion llamada justo antes de salir
def salir(stdscr,mensaje=""):
	if mensaje:
		stdscr.addstr(mensaje)

	stdscr.addstr("Cualquier tecla para salir.\n")
	c = stdscr.getch()

	return None

def subir_sld(stdscr, cat, archivo):
	# Recuperar el nombre del archivo
	nombreEstilo = crear_nombre_estilo(archivo)

	# Salida grafica
	stdscr.addstr("\n* %s\n" % nombreEstilo)

	# Miramos si ya existe el estilo - preguntar que hacer
	try:
		estilo = cat.get_style(nombreEstilo)
	except Exception as e:
		stdscr.addstr("No se pudo recuperar el estilo %s\n" % nombreEstilo)
		return None
		
	if estilo:
		i = 3
		stdscr.addstr("\nEl estilo '%s' ya existe en el servidor.\n" % estilo.name)
		while i > 0:
			i -=1
			stdscr.addstr("[r]emplazar, [d]ejar sin cambio, solo [b]orrar el estilo del servidor, o [q]uit ?\n")
			c = stdscr.getch()
			if c == ord('r'):
				# Existe el estilo, subimos una nueva version (remplazamos)
				try:
					cat.create_style(nombreEstilo, archivo.read(), overwrite=True)
					stdscr.addstr("Estilo remplazado en el servidor\n")
				except Exception as e:
					stdscr.addstr("Salio un error al remplazar el archivo:\n%s\n" % e)
					return None
				break # Exit the while()
			elif c == ord('b'):
				# Existe el estilo, lo borramos
				# http://jira.codehaus.org/browse/GEOS-3621
				try:
					cat.delete(estilo,purge=True)
					stdscr.addstr("Estilo borrado en el servidor\n")
				except Exception as e:
					stdscr.addstr("Salio un error al borrar el estilo en el servidor:\n%s\n" % e)
					return None
				break # Exit the while()
			elif c == ord('d'):
				# No hacemos nada
				stdscr.addstr("Dejamos la version anterior del estilo en el servidor\n")
				break # Exit the while()
			elif c == ord('q'):
				# Salimos de la funcion, indicando que queremos parar (stop = True)
				stdscr.addstr("Salimos del programa\n")
				return True # Exit the while()
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


def main(stdscr,args,user,pw):
	# Avisamos si no hay archivos
	if not len(args.archivos):
		return salir(stdscr, "Ningun archivo SLD para procesar\n")

	# Probamos la conexion a GeoServer
	try:
		cat =  connectar_geoserver(stdscr,user,pw)
	except Exception as e:
		return salir(stdscr,"La conexion con el GeoServer fallo\n")

	# Subir los archivos SLD
	stdscr.addstr("Subimos los siguientes archivos de estilo al servidor http://www-dev.geo.gob.bo/geoserver/\n\n")
	stop = False
	for archivo in args.archivos:
		# subimos el archivo SLD
		if not stop: stop = subir_sld(stdscr, cat, archivo)
		# cerrar el archivo (fue abierto al momento del parsing)
		archivo.close()

	# Todo salio bien - mensaje para terminar la funcion
	return salir(stdscr)


# preguntamos el usuario / password - son las credenciales LDAP
user = raw_input("Usuario: ")
pw = getpass.getpass('Contraseña: ')

# Creacion de la pantalla con curses
# ver http://docs.python.org/howto/curses.html#curses-howto para un tutorial sobre curses
curses.wrapper(main,args,user,pw)

# Fin
quit()
