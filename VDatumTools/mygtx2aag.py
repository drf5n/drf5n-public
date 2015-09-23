#!/usr/bin/python
import numpy
import sys
import os
import argparse
from struct import unpack

parser = argparse.ArgumentParser(description=
""" Read a VDatum .gtx binary file from http://vdatum.noaa.gov/docs/gtx_info.html and write an ArcIinfoAsciiGrid File
    for use with GIS systems.

    Outputs in working directory:
    file.asc  # an ArcInfo ASCII Grid file with the contents of file.gtx
    file.prj  # a projection file for EPSG:4269 (NAD83) from http://spatialreference.org/ref/epsg/4269/ 


    Note that the double format would have a filesize of 40+8*nRows*nCols  
    while the float and integer formats would have file sizes of 40+4*nRows*nCols.

"""

)
parser.add_argument("file", help="VDatum gtx format file per http://vdatum.noaa.gov/docs/gtx_info.html")
parser.add_argument("-i", "--integer", help="Parse data as integers instead of floats.  Units in mm.", action="store_true")
parser.add_argument("-f", "--float", help="Parse data as floats instead of doubles", action="store_true")
parser.add_argument("-d", "--double", help="Parse data as double instead of floats", action="store_true")
args = parser.parse_args()

file=args.file

data_type='>f'          # big-endian float default since 2009
if args.double:
	data_type='>d'  # big-endian double
if args.float:
	data_type='>i'  # big-endian integer
if args.integer:
	data_type='>f'  # big-endian float

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
data=numpy.fromfile(f,dtype=data_type,count=nRow*nCol)
print "Data size= {s} vs {n} from ({r} x {c})".format(s=data.size, n=npoints,r=nRow,c=nCol)
data=data.reshape((nRow,nCol))[::-1]
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







