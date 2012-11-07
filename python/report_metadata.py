#!/usr/bin/python
# -*- coding: utf-8 -*-

""" producir un reporte de los metadatos de un catalago CSW
args:
"""

import csv, codecs, cStringIO
from owslib.csw import CatalogueServiceWeb
import dateutil.parser
import math
import datetime
import osgeo.osr
from osgeo import ogr
from unidecode import unidecode

def getcswrecords(csw):
    # Logica para recuperar todos los metadatos
    cswrecords=dict()
    startposition=0
    maxrecordsinit=5
    maxrecords=maxrecordsinit
    more=True
    iter=0
    matches = None
    factormult = 2
    while iter < 2 and more:
        iter = iter+1
        if matches and startposition + maxrecords > matches:
            maxrecords = matches - startposition

        print str(iter) + " - startposition: " + str(startposition) + " - maxrecords: " + str(maxrecords)
        try:
            csw.getrecords(outputschema='http://www.isotc211.org/2005/gmd',esn='full', startposition=startposition, maxrecords=maxrecords)
        except:
            print 'error'

        matches=csw.results['matches']

        if len(csw.records)==maxrecords:
            cswrecords=dict(cswrecords.items() + csw.records.items())
            startposition+=len(csw.records)
            maxrecords=maxrecords*factormult
            if startposition >= matches:
                more=False
        else:
            # There is an error in the list of records
            if maxrecords > 1:
                # We divide the list of records
                maxrecords=1
            else:
                # We only asked for one record and it failed -> we bypass it
                startposition=startposition+1
                maxrecords=maxrecords*factormult

    print str(len(cswrecords)) + ' metadata correctly fetched'
    print str(matches - len(cswrecords)) + ' metadata with error'
    return cswrecords

# Class for writing in CSV without encoding problems
# See: http://docs.python.org/2/library/csv.html#csv-examples
class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def prepareforcsv(cswrecords):
    matrix=[]
    matrix.insert(0,['id','Titulo',u'A\u00F1o','Contacto (organizacion)'])
    for rec in cswrecords:
        r=cswrecords[rec]
        # Selección de los campos interesantes
        id=r.identifier
        title=r.identification.title
        contactorg=r.identification.contact[0].organization
        date=r.identification.date[0].date
        year=str(dateutil.parser.parse(date).year) if date else ''

        # Put in output array
        matrix.append([
                id,
                title,
                year,
                contactorg
                ])
    # Transpose the matrix
    matrix=zip(*matrix)

    return matrix

# Export to a CSV file
def exporttocsv(cswrecords):
    matrix=prepareforcsv(cswrecords)
    filename = '/tmp/tmp.csv'
    item_length = len(matrix[0])
    with open(filename, mode='wb') as test_file:
        file_writer = UnicodeWriter(test_file)
        for i in range(item_length):
            file_writer.writerow([x[i] if x[i] else '' for x in matrix])

# Output results to a SHP
def exporttoshp(cswrecords):
    spatialReference = osgeo.osr.SpatialReference()
    spatialReference.ImportFromProj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    driver = osgeo.ogr.GetDriverByName('ESRI Shapefile')
    name='/tmp/tmp' + str(datetime.datetime.now()) + '.shp'
    #name='/tmp/catalogo_geobolivia.shp'
    shapeData = driver.CreateDataSource(name)

    layer = shapeData.CreateLayer('layer1', spatialReference, osgeo.ogr.wkbPolygon)
    layerDefinition = layer.GetLayerDefn()

    ### Shapefile fields
    # id
    fieldDefn = ogr.FieldDefn('id', ogr.OFTString)
    fieldDefn.SetWidth(64)
    layer.CreateField(fieldDefn)
    # anio
    fieldDefn = ogr.FieldDefn('anio', ogr.OFTInteger)
    fieldDefn.SetWidth(4)
    layer.CreateField(fieldDefn)
    # titulo
    fieldDefn = ogr.FieldDefn('titulo', ogr.OFTString)
    fieldDefn.SetWidth(128)
    layer.CreateField(fieldDefn)
    # organizacion
    fieldDefn = ogr.FieldDefn('contacto', ogr.OFTString)
    fieldDefn.SetWidth(128)
    layer.CreateField(fieldDefn)

    for rec in cswrecords:
        r=cswrecords[rec]
        # Create ring
        ring = osgeo.ogr.Geometry(osgeo.ogr.wkbLinearRing)
        # Prepare each field
        id=r.identifier
        title=r.identification.title
        contactorg=r.identification.contact[0].organization
        date=r.identification.date[0].date
        year=str(dateutil.parser.parse(date).year) if date else ''
        bb=r.identification.extent.boundingBox
        if hasattr(bb,'minx'):
            west=float(bb.minx)
            east=float(bb.maxx)
            south=float(bb.miny)
            north=float(bb.maxy)
            ring.AddPoint(west, south)
            ring.AddPoint(west, north)
            ring.AddPoint(east, north)
            ring.AddPoint(east, south)
            polygon = osgeo.ogr.Geometry(osgeo.ogr.wkbPolygon)
            polygon.AddGeometry(ring)

            featureIndex = 0
            feature = osgeo.ogr.Feature(layerDefinition)
            feature.SetGeometry(polygon)
            feature.SetFID(featureIndex)

            feature.SetField('id', id)
            feature.SetField('anio', year)
            if title:
                feature.SetField('titulo', unidecode(title))
            if contactorg:
                feature.SetField('contacto', unidecode(contactorg))

            layer.CreateFeature(feature)

    shapeData.Destroy()

# Connect to the catalog
csw = CatalogueServiceWeb('http://www.geo.gob.bo/geonetwork/srv/es/csw')

# Get the metadata
cswrecords = getcswrecords(csw)

# Export to Shapefile
exporttoshp(cswrecords)

# Export to CSV
exporttocsv(cswrecords)
