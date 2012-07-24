#!/usr/bin/python
# -*- coding: utf-8 -*-
# para el encoding, ver: http://www.python.org/dev/peps/pep-0263/
# para el encoding, ver: http://www.python.org/dev/peps/pep-0263/
# sin utf-8, no se pueden utilizar caracteres con tildes, etc (ni el código, ni 
# en los comentarios)

"""Objeto: Utilizando el módulo gsconfig, publicar un SLD / una carpeta de SLD
    en el GeoServer de dev.
    
    Usos:
        * subir un archivo SLD::
    
            subir_sld /path/to/archivo.sld
        
        * subir una carpeta de archivos SLD::
    
            subir_sld /path/to/carpeta/
        
"""


# Importación de los siguientes modulos
from geoserver.catalog import Catalog # para conectarse a GeoServer via la API 
# REST (gsconfig)
import os # para manejar los archivos del sistema operativo
import curses # para elaborar una pantalla interactiva con el usuario
import argparse # para hacer un parsing de los argumentos en linea de comando
import getpass # para pedir y recuperar la contraseña de manera segura

def crear_parser():
    """Creación del parser para los argumentos de la linea de comando.
    
    Utilizamos el módulo argparse (http://docs.python.org/howto/argparse.html).
    
    Returns:
        Un parser (objeto argparse.ArgumentParser).

    """
    # Creacion del parser
    parser = argparse.ArgumentParser()

    # Especificacion del argumento archivos - se llamara la funcion 
    # parse_archivos para crear la lista de archivos a procesar
    parser.add_argument(
        "archivos", 
        help="archivo SLD / carpeta de archivos SLD - para subir en el " + 
            "servidor GeoServer de dev de GeoBolivia",
        type=parse_archivos,
        )

    return parser

def test_and_open_sld_file(files,fileName):
    """Verificar y abrir un archivo SLD.
    
    Se verifica que el archivo fileName es de tipo estilo SLD (.sld) y que se 
    puede abrir.
    
    Args:
        * files: Lista de otros archivos SLD ya abiertos.
        * fileName: Nombre del archivo SLD a añadir.
    
    Returns:
        La lista de archivos "files", con un nuevo elemento si el archivo SLD
        fue validado: el archivo abierto en modo lectura texto.
    
    """

    # Recuperar la extension
    fileBase, fileExtension = os.path.splitext(fileName)
    # Parece un archivo SLD (extension .sld) ?
    if fileExtension == ".sld":
        # Parece un archivo SLD
        try:
            # Probamos de abrir el archivo
            f = open(fileName,'rt')
            # Lo pudimos abrir - anadimos el archivo abierto a la lista "files"
            files.append(f)
        except IOError as e:
            # No se puede abrir - no hacemos nada
            pass
    return files

def parse_archivos(path):
    """Verificar y abrir los archivos SLD a procesar.
    
    Si path es un archivo, probar de abrirlo. Si es una carpeta, buscar todos
    los archivos SLD que contiene (sin recursividad) y probar de abrirlos.
    
    Args:
        * path: Carpeta o archivo a procesar.
        
    Returns:
        Una lista de archivos SLD abiertos en modo lectura texto.
        
    """
    # Creamos la lista de archivos SLD abiertos
    files = []

    # Pruebas sobre el tipo de "path"
    if os.path.isfile(path):
        # Es un archivo - verificamos si es de tipo sld
        files = test_and_open_sld_file(files,path)
    elif os.path.isdir(path):
        # Es una carpeta, probamos de abrir sus archivos
        # Lista de archivos de la carpeta
        fileNames=os.listdir(path)
        # Para cada archivo
        for fileName in    fileNames:
            # probamos de abrirlo, verificando que es con extension .sld
            files = test_and_open_sld_file(files,os.path.join(path, fileName))

    # Devolvemos la lista de archivos SLD encontrados
    return files

def conectar_geoserver(stdscr,user,pw):
    """Probar la conexión a GeoServer (de dev) y crear el objeto Catalogo.
    
    Args:
        * stdscr: Objeto ventana del módulo curses.
        * user: Nombre de usuario para la conexión a GeoServer.
        * pw: Password para la conexión a GeoServer.
        
    Returns:
        Un objeto Catalogo del módulo gsconfig para manejar la conexión al
        GeoServer de dev de GeoBolivia.
        
    Raises:
        Cualquier excepción mandada por la función gsconfig.get_workspaces()
        esta transmitida.
    
    """
    
    # Datos para la conexion a GeoServer
    url_geoserver = "http://www-dev.geo.gob.bo/geoserver/rest"

    # Especificación de la conexion a GeoServer
    cat = Catalog(url_geoserver, user, pw)

    # Probar la conexion con una consulta simple
    try:
        # Recuperación de los workspaces
        all_workspaces = cat.get_workspaces()
    except Exception as e:
        # Salio una excepcion:
        # la mostramos
        stdscr.addstr("Error durante la conexion al GeoServer:\n%s\n" % e)
        # y la relanzamos
        raise

    # Devolvemos el objeto catalogo
    return cat

def crear_nombre_estilo(archivo):
    """Crear el nombre del estilo a partir del archivo abierto en lectura.
    
    Recuperar el nombre del archivo abierto y sacar la extensión .sld.
    
    Args:
        * archivo: Archivo SLD abierto en modo lectura texto.
        
    Returns:
        El nombre del estilo correspondiente (destinado a ser el nombre del 
        estilo en GeoServer).
        
    """
    # Recuperamos el nombre de archivo sin la extension
    fileName, fileExtension = os.path.splitext(archivo.name)

    # Creamos el nombre del estilo (base del archivo, sin extension)
    nombreEstilo = os.path.basename(fileName)

    # Retornamos el nombre del estilo
    return nombreEstilo

def subir_sld(stdscr, cat, archivo):
    """Probar de subir el archivo SLD al servidor GeoServer.
    
    A partir del archivo, recuperar el nombre de estilo correspondiente, y 
    probar de subirlo a GeoServer. Si ya existe un estilo con el mismo nombre
    en el GeoServer, preguntar al usuario lo que quiere hacer.
    
    Hay varias posibilidades de respuesta para el usuario:
        * 'r': remplazar el estilo de GeoServer con el archivo SLD,
        * 'd': dejar el estilo existente en GeoServer,
        * 'b': borrar el estilo existente, sin tampoco subir el archivo SLD,
        * 'q': salir de la función, pidiendo que se pare el programa (mismo
            efecto que 'd', pidiendo la misma respuesta para todos los otros
            archivos SLD eventuales).
    
    Args:
        * stdscr: Objeto ventana del módulo curses.
        * cat: Objeto Catalogo del módulo gsconfig (para manejar el acceso a
            GeoServer).
        * archivo: Archivo SLD abierto en modo lectura texto.
    
    Returns:
        True para indicar que el usuario quiere parar el programa (corresponde a
        la respuesta "q" del usuario). En cualquier otro caso, None.
        
    """
    # Recuperar el nombre del archivo
    nombreEstilo = crear_nombre_estilo(archivo)

    # Mostrar el nombre del estilo
    stdscr.addstr("\n* %s\n" % nombreEstilo)

    # Miramos si ya existe el estilo
    try:
        # Pedimos el estilo a GeoServer
        estilo = cat.get_style(nombreEstilo)
    except Exception as e:
        # Hubo un error durante la conexion a GeoServer
        stdscr.addstr("No se pudo recuperar el estilo %s\n" % nombreEstilo)
        # Salimos sin mayor problema
        return None

    # Existe el estilo en GeoServer ?        
    if estilo:
        # El estilo existe en GeoServer - el usuario decide que hacer
        # Preguntaremos hasta tres veces al usuario
        i = 3
        # Indicamos que el estilo ya existe en el servidor
        stdscr.addstr("\nEl estilo '%s' ya existe en el servidor.\n" % 
           estilo.name)
        # Empezamos a pedir una respuesta al usuario
        while i > 0:
            # Bajamos el numero de preguntas restantes
            i -=1
            # Preguntamos al usuario que hacer
            stdscr.addstr("[r]emplazar, [d]ejar sin cambio, solo [b]orrar el " +
                "estilo del servidor, o [q]uit ?\n")
            # Esperamos su respuesta (un caracter)
            c = stdscr.getch()
            # Miramos que caracter tecló
            if c == ord('r'):
                # El usuario quiere subir el archivo y remplazar el estilo
                # existante
                try:
                    # Probamos de remplazar el estilo por el archivo
                    cat.create_style(nombreEstilo, archivo.read(), 
                        overwrite=True)
                    # Funcionó: indicamos que el estilo fue remplazado
                    stdscr.addstr("Estilo remplazado en el servidor\n")
                except Exception as e:
                    # Salió una excepción: indicamos que no se pudó remplazar el
                    # estilo
                    stdscr.addstr("Salio un error al remplazar el " +
                        "archivo:\n%s\n" % e)
                    # Salimos
                    return None
                # Salimos del bucle de preguntas
                break
            elif c == ord('b'):
                # El usuario quiere borrar el estilo existante, sin subir el 
                # archivo
                try:
                    # Probamos de borrar el estilo (archivos .sld y .xml en el 
                    # servidor)
                    # * para el parametro purge, ver 
                    #   http://jira.codehaus.org/browse/GEOS-3621
                    cat.delete(estilo,purge=True)
                    # Funcionó: indicamos que el estilo fue borrado
                    stdscr.addstr("Estilo borrado en el servidor\n")
                except Exception as e:
                    # Salió una excepción: indicamos que no se pudó borrar
                    # estilo
                    stdscr.addstr("Salio un error al borrar el estilo en el " +
                        "servidor:\n%s\n" % e)
                    # Salimos
                    return None
                # Salimos del bucle de preguntas
                break
            elif c == ord('d'):
                # El usuario quiere dejar el estilo actual en el servidor
                # Indicamos que entendimos la decision y que no se hizó nada
                stdscr.addstr("Dejamos la version anterior del estilo en el " +
                    "servidor\n")
                # Salimos del bucle de preguntas
                break
            elif c == ord('q'):
                # El usuario quiere para el programa
                # Indicamos que salimos del programa
                stdscr.addstr("Salimos del programa\n")
                # Salimos de la funcion, indicando que queremos parar el
                # programa (stop = True)
                return True
        # Test sobre el numero de preguntas restantes
        if i == 0:
            # Ya no hay preguntas restantes - no entendimos las respuestas del 
            # usuario
            # Indicamos que no se hizó nada (equivalente a la opción "[d]ejar")
            stdscr.addstr("No se entiende - dejamos la version anterior del " +
                "estilo en el servidor\n")
    else:
        # El estilo no existe en el servidor - subimos el archivo sin preguntar
        # nada al usuario
        try:
            # Probamos de subir el archivo
            cat.create_style(nombreEstilo, archivo.read())
            # Funcionó: indicamos que el estilo fue creado
            stdscr.addstr("Estilo subido en el servidor\n")
        except Exception as e:
            # Salió una excepción: indicamos que no se pudó subir el archivo
            stdscr.addstr("Salio un error al subir el archivo:\n%s\n" % e)
            # Salimos
            return None
    # Salimos del programa, sin indicar que queremos parar (sería "return True")
    return None

def salir(stdscr,archivos=[],mensaje=""):
    """Limpiar el entorno antes de salir.

    Mostrar un eventual mensaje de salida, cerrar los archivos SLD abiertos
    en modo lectura texto, y esperar que el usuario tecle algo para salir

    Args:
        * stdscr: Objeto ventana del módulo curses.
        * archivos: Lista de archivos SLD abiertos en modo lectura texto.
        * mensaje: Eventual mensaje de salida.

    """

    # Si existe, mostramos el mensaje
    if mensaje: stdscr.addstr(mensaje)

    # Cerramos los archivos abiertos
    for archivo in archivos:
        # Cerrar el archivo (fue abierto al momento del parsing)
        archivo.close()

    # Esperamos que el usuario tecle algo
    stdscr.addstr("Cualquier tecla para salir.\n")
    c = stdscr.getch()

    # Salimos de la funcion
    return None

def main(stdscr,archivos,user,pw):
    """Subir una lista de archivos SLD a GeoServer.
    
    Se usan las credenciales user/pw para conectarse al servidor GeoServer de
    dev y subir los archivos SLD de la lista.
    
    Args:
        * stdscr: Objeto ventana del módulo curses.
        * archivos: Lista de archivos SLD abiertos en modo lectura texto.
        * user: Nombre de usuario para la conexión a GeoServer.
        * pw: Password para la conexión a GeoServer.
        
    """
    
    # Probar si se encontraron archivos SLD validos
    if not len(archivos):
        # No se encontró archivos validos - salimos de la función
        return salir(stdscr, archivos, "Ningún archivo SLD para procesar\n")

    # Configurar la conexión a GeoServer
    try:
        # Probamos la conexion a GeoServer
        cat =  conectar_geoserver(stdscr,user,pw)
    except Exception as e:
        # Salió una excepción, salimos del función indicando que no se pudó
        # conectar
        return salir(stdscr, archivos, "La conexion con el GeoServer fallo\n")

    # Indicamos que se van a subir los archivos SLD
    stdscr.addstr("Subimos los siguientes archivos de estilo al servidor " + 
        "http://www-dev.geo.gob.bo/geoserver/\n\n")
    # El parametro para parar el bucle esta desactivado
    stop = False
    # Procesamos cada archivo
    for archivo in archivos:
        # Si el parametro "stop" sigue falso
        if not stop:
            # probamos de subir el archivo SLD al servidor
            stop = subir_sld(stdscr, cat, archivo)

    # Salimos de la función, esperando que el usuario tecle algo
    salir(stdscr, archivos)
    
    return None


if __name__ == "__main__":
    # Parsing de los argumentos de la linea de comando
    # creación del objeto parser
    parser = crear_parser()
    # parsing de los argumentos
    args = parser.parse_args()

    # Preguntamos el usuario / password - son las credenciales LDAP
    # * usuario
    user = raw_input("Usuario: ")
    # * password (funcion getpass para no mostrar el password en la terminal)
    pw = getpass.getpass('Contraseña: ')

    # Creacion de la pantalla interactiva con curses, llamando la función "main"
    # * ver http://docs.python.org/howto/curses.html#curses-howto para un 
    # tutorial sobre curses
    curses.wrapper(main,args.archivos,user,pw)

    # Salimos del programa
    quit()

# Algunos datos de desarrollo - a poner en otro lugar

# para el uso de "with", ver http://effbot.org/zone/python-with-statement.htm
# -> el archivo se cerrara automaticamente

# import time # para hacer pausas, por ej: time.sleep(2)

# Excepciones manejadas por gsconfig:
# UploadError
# ConflictingDataError
# AmbiguousRequestError
# FailedRequestError
# NotImplementedError
# Excepcion
# ExpatError
# SyntaxError
