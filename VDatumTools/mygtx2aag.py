#!/usr/bin/python
""" Read a VDatum .gtx binary file from http://vdatum.noaa.gov/dev/gtx_info.html and write an ArcIinfoAsciiGrid File
    for use with GIS systems
"""
import numpy
import sys
import os
from struct import unpack

file=sys.argv[1]

outbase=os.path.splitext(file)[0]


# Bigendian doubles and ints, per http://vdatum.noaa.gov/dev/gtx_info.html

f=open(file,'rb')

data=f.read(4*8+2*4)

llLat,llLon, dLat,dLon, nRow,nCol=unpack(">ddddii",data)
llLon=llLon-360.0
nodata= -9999

aagfile=open("{f}.asc".format(f=outbase),'w')

aagfile.write("""ncols {nCol}
nrows {nRow}
xllcorner {llLon}
yllcorner {llLat}
cellsize {dx}
nodata_value {nodata}
""".format(nCol=nCol,nRow=nRow,llLon=llLon,llLat=llLat,dx=dLat,nodata=nodata))

npoints=nRow*nCol
data=numpy.fromfile(f,dtype='>d',count=nRow*nCol*8).reshape((nRow,nCol))[::-1]
data[data==-88.8888]=nodata

for row in numpy.arange(nRow):
    aagfile.write( " ".join('{z}'.format(z=z) for z in data[row,:]))
    aagfile.write("\n")

aagfile.close()

prjfile=open("{f}.prj".format(f=outbase),'w')

prjfile.write("""GEOGCS["WGS 84",
    DATUM["WGS_1984",
        SPHEROID["WGS 84",6378137,298.257223563,
            AUTHORITY["EPSG","7030"]],
        AUTHORITY["EPSG","6326"]],
    PRIMEM["Greenwich",0,
        AUTHORITY["EPSG","8901"]],
    UNIT["degree",0.01745329251994328,
        AUTHORITY["EPSG","9122"]],
    AUTHORITY["EPSG","4326"]]
""")
prjfile.close()







