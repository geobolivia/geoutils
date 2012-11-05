#!/usr/bin/python
# -*- coding: utf-8 -*-

""" producir un reporte de los metadatos de un catalago CSW
args:
"""

from owslib.csw import CatalogueServiceWeb
import dateutil.parser
import math

# Class for writing in CSV without encoding problems
# See: http://docs.python.org/2/library/csv.html#csv-examples
import csv, codecs, cStringIO
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

# Connect to the catalog
csw = CatalogueServiceWeb('http://www.geo.gob.bo/geonetwork/srv/es/csw')

# Get all metadata

def getrecords(csw, startposition=0, maxrecords=10):
    datapart=[]
    try:
        csw.getrecords(outputschema='http://www.isotc211.org/2005/gmd',esn='full', startposition=startposition, maxrecords=maxrecords)

        # Format data
        for rec in csw.records:
            r=csw.records[rec]
            # Prepare each field
            id=r.identifier
            title=r.identification.title
            contactorg=r.identification.contact[0].organization
            date=r.identification.date[0].date
            year=str(dateutil.parser.parse(date).year) if date else ''
            # Put in output array
            datapart.append([
                    id,
                    title,
                    year,
                    contactorg
                    ])
    except:
        return []

    return datapart

# Logica para recuperar todos los metadatos
data=[['id','Titulo','Fecha',u'A\u00F1o','Contacto (nombre)', 'Contacto (organizacion)', 'Contacto (email)', 'Contacto (telefono)']]

startposition=0
maxrecordsinit=50
maxrecords=maxrecordsinit
more=True
iter=0
matches = None
factormult = 2
while iter < 500 and more:
    iter = iter+1
    if matches and startposition + maxrecords > matches:
        maxrecords = matches - startposition

    #print str(iter) + " - startposition: " + str(startposition) + " - maxrecords: " + str(maxrecords)
    datapart=getrecords(csw=csw, startposition=startposition, maxrecords=maxrecords)
    matches=csw.results['matches']
    returned=len(datapart)
    #print returned

    if returned==maxrecords:
        data.extend(datapart)
        startposition+=returned
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

print str(len(data)) + ' metadata correctly fetched'
print str(matches - len(data)) + ' metadata with error'

# Transpose the matrix
data=zip(*data)

# Output results to a CSV file
filename = '/tmp/tmp.csv'
item_length = len(data[0])
with open(filename, mode='wb') as test_file:
  file_writer = UnicodeWriter(test_file)
  for i in range(item_length):
      file_writer.writerow([x[i] if x[i] else '' for x in data])
