#!/usr/bin/env python 
#!/Library/Frameworks/EPD64.framework/Versions/Current/bin/python
# -*- encoding: utf-8 -*-
#//: selfe2Shape.py -- extracts cell information to shapefiles drf@vims.edu 2011-10-04
#//: $Id: selfe2Shape.py 12 2011-10-06 13:58:07Z drf $ from $URL: file:///Users/drf/SVN/tsunami/trunk/selfe2Shape.py $
# svn file:///Users/drf/SVN/tsunami on drf's macbook
from __future__ import print_function

import getopt

import sys,math,subprocess
from scipy import *
import numpy as np
import matplotlib

#import shapefile  # dependent on shapefile.py from http://code.google.com/p/pyshp/ on path

global x,y,ele,elev,depth


def getPRJwkt(epsg):
   """
   Grab an WKT version of an EPSG code
   usage getPRJwkt(4326)

   This makes use of links like http://spatialreference.org/ref/epsg/4326/prettywkt/
   """
   
   import urllib
   f=urllib.urlopen("http://spatialreference.org/ref/epsg/{0}/prettywkt/".format(epsg))
   return (f.read())


def parseline(line, *types): return [c(x) for (x, c) in zip(line.split(), types) if c] or [None]

def readHgridForLonLat(file):   # get the hgrid locations from an ascii hgrid.gr3 file
#    print "Reading %s as hgrid.ll" % (file)
    f=open(file,'r')
    desc = f.readline()
    junk = f.readline()
    nele,nnode = parseline(junk,int,int)
#    print "..Has %d elements and %d nodes" % (nele,nnode)
    x=np.zeros(nnode)
    y=np.zeros(nnode)
    d=np.zeros(nnode)
    ele=np.zeros((nele,3),dtype='int')
    for n in range(nnode):
        junk = f.readline()
#        print "  ..read %s" % (junk) 
        nodenum,xx,yy,dd = parseline(junk,int,float,float,float)
        x[nodenum-1]=xx
        y[nodenum-1]=yy
        d[nodenum-1]=dd
    for n in range(nele):
        junk=f.readline();
        elenum,nside,n1,n2,n3 = parseline(junk,int,int,int,int,int)
        ele[elenum-1,:]=(n1,n2,n3) # note starting index=1
    bounds=f.readlines()
    return x,y,d,ele,desc,bounds


def main():
    filename = sys.argv[1]
    ps = sys.argv[2]
    pd = sys.argv[3]
  #  print "{f} as {ps} projcted to {pd}".format(f=filename,ps=ps,pd=pd) 
    global x,y,ele,elev,depth
    x,y,depth,ele,desc,bound=readHgridForLonLat(filename)
    import pyproj
    p1=pyproj.Proj(init=ps)
    p2=pyproj.Proj(init=pd)
    xp,yp = pyproj.transform(p1,p2,x,y)
    print ("{desc} as {pd}".format(desc=desc.rstrip(),pd=pd))
    print (len(ele), len(x))
    for  ii in range(len(x)):
        print (ii+1,xp[ii], yp[ii],depth[ii])
    for ii in range(len(ele)):
        print ("{enum} 3 {nodes}".format(enum=ii+1,nodes=" ".join(map(str,ele[ii]))))
    print ("".join(bound))

if __name__ == "__main__":
   if len (sys.argv) == 4:
      main ()
   else:
      print ("How to use: %s data_file epsg:4326 epsg:32618" % sys.argv[0])



      
