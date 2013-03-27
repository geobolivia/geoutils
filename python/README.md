Para poder descargar el archivo SLD, es necesario tener una cuenta de usuario en geoserver
Si no se cuenta con una cuenta de usuario, la respuesta http es: [401 No autorizado]

Existe un error en la libreria de geoserver, para poder descargar el SLD
la solucion por el momento es adicionar las siguientes lineas, en la funcion "get_xml"
del archivo **/usr/local/lib/python2.7/dist-packages/geoserver/catalog.py**

se encuentra aprox en la linea "116"

```
	def get_xml(self, rest_url):
		logger.warning("GET %s", rest_url)
		response, content = self.http.request(rest_url)
		if response.status == 200:**
			self._cache[rest_url] = (datetime.now(), content)**
```
 
INSTALAR
--------
<pre>
sudo apt-get install python-httplib2
sudo apt-get install gdal-bin
sudo aptitude install python-pip
sudo easy_install owslib
sudo pip install gsconfig
</pre>

EJECUTAR
--------
<pre>
sudo ./owsdl_livedvd.py
</pre>

