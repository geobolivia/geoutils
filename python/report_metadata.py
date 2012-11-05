#!/usr/bin/python
# -*- coding: utf-8 -*-

""" producir un reporte de los metadatos de un catalago CSW
args:
"""

import sys
#sys.path.append("lib/OWSLib")
from owslib.csw import CatalogueServiceWeb
import dateutil.parser

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
data=[['id','Titulo','Fecha',u'A\u00F1o','Contacto (nombre)', 'Contacto (organizacion)', 'Contacto (email)', 'Contacto (telefono)']]

csw.getrecords(maxrecords=10,outputschema='http://www.isotc211.org/2005/gmd',esn='full',sortby='gco:CharacterString')
print str(len(csw.records)) + ' fichas de metadatos'

# Format data
for rec in csw.records:
    r=csw.records[rec]
    # Prepare each field
    id=r.identifier
    title=r.identification.title
    contactname=r.identification.contact[0].name
    contactorg=r.identification.contact[0].organization
    contactemail=r.identification.contact[0].email
    contacttel=r.identification.contact[0].phone
    date=r.identification.date[0].date
    year=str(dateutil.parser.parse(date).year) if date else ''
    # Put in output array
    data.append([
            id,
            title,
            date,
            year,
            contactname,
            contactorg,
            contactemail,
            contacttel
            ])

# Transpose the matrix
data=zip(*data)

# Output results to a CSV file
filename = '/tmp/tmp.csv'
item_length = len(data[0])
with open(filename, mode='wb') as test_file:
  file_writer = UnicodeWriter(test_file)
  for i in range(item_length):
      file_writer.writerow([x[i] if x[i] else '' for x in data])
