#!/bin/sh

# Super usuario para el GeoServer de dev
USER=admin_geobolivia
PW=YGoL3lSJYCwjCLDC

# URL de GeoServer y la API REST
URL_GS=http://www-dev.geo.gob.bo/geoserver
URL_REST=$URL_GS/rest

# Recuperar la lista de workspaces en formato json
echo "*** LISTA DE WORKSPACES ***"
echo "* en JSON"
curl -u $USER:$PW -XGET $URL_REST/workspaces.json
echo "\n"

# Otra manera, para XML, por ejemplo
echo "* en XML"
curl -u $USER:$PW -H 'Accept: text/xml' -XGET $URL_REST/workspaces
echo "\n"

