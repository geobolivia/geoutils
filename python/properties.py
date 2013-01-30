# Input arguments
geoserverUrl='http://www.geo.gob.bo/geoserver/'
outputPath='/var/www/geobolivia_data/'
user = None
pw = None
csvFilename = '/opt/prio_final.csv'
csvFilename = '/opt/prioridad_ultimos.csv'
#csvFilename = '/opt/prioridad.csv.tmp'
#firstLayerFilter = 'universidades:AreasAccesoComunidades-porcentaje_15_35'
firstLayerFilter = None
cacheTimeout = 7 * 24 * 60 * 60
forceOverwrite = False
onlyCheck = True