#!/usr/bin/python
""" Read a VDatum .gtx binary file from http://vdatum.noaa.gov/dev/gtx_info.html and write an ArcIinfoAsciiGrid File
    for use with GIS systems.

    Usage:
    mygtx2aag.py file.gtx  

    Outputs in working directory:
    file.asc  # an ArcInfo ASCII Grid file with the contents of file.gtx
    file.prj  # a projection file for EPSG:4269 (NAD83) from http://spatialreference.org/ref/epsg/4269/ 

"""
import numpy
import sys
import os
from struct import unpack

file=sys.argv[1]

outbase=os.path.splitext(os.path.basename(file))[0]  # filename, stripped of path and extension

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

prjfile.write("""GEOGCS["NAD83",
    DATUM["North_American_Datum_1983",
        SPHEROID["GRS 1980",6378137,298.257222101,
            AUTHORITY["EPSG","7019"]],
        AUTHORITY["EPSG","6269"]],
    PRIMEM["Greenwich",0,
        AUTHORITY["EPSG","8901"]],
    UNIT["degree",0.01745329251994328,
        AUTHORITY["EPSG","9122"]],
    AUTHORITY["EPSG","4269"]]
""")
prjfile.close()







