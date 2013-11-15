#!/usr/bin/python
""" Read a VDatum .gtx binary file from http://vdatum.noaa.gov/dev/gtx_info.html and write an ArcIinfoAsciiGrid File
    for use with GIS systems
"""
import numpy
import sys
from struct import unpack

file=sys.argv[1]

# Bigendian doubles and ints, per http://vdatum.noaa.gov/dev/gtx_info.html

f=open(file,'rb')

data=f.read(4*8+2*4)

llLat,llLon, dLat,dLon, nRow,nCol=unpack(">ddddii",data)
llLon=llLon-360.0
nodata= -9999

print """ncols {nCol}
nrows {nRow}
xllcorner {llLon}
yllcorner {llLat}
cellsize {dx}
nodata_value {nodata}""".format(nCol=nCol,nRow=nRow,llLon=llLon,llLat=llLat,dx=dLat,nodata=nodata)

npoints=nRow*nCol
data=numpy.fromfile(f,dtype='>d',count=nRow*nCol*8).reshape((nRow,nCol))[::-1]
data[data==-88.8888]=nodata

for row in numpy.arange(nRow):
    print " ".join('{z}'.format(z=z) for z in data[row,:])







