#!/usr/bin/env python
#!/Library/Frameworks/Python.framework/Versions/Current/bin/python  
# ick hardcoded python path...
# make sure that the path has a scipy/numpy with netcdf4 in it
# on my mac, .profile should prepend the Enthought package:
# Setting PATH for EPD-6.0.4
# The orginal version is saved in .profile.pysave
#PATH="/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH}"
#export PATH

# read a selfe format file per
# http://www.ccalmr.ogi.edu/CORIE/modeling/selfe/input_mpi.html#Global%20output2
# 
# and write it in a netcdf format

# some hints on reading binaries from http://snippets.dzone.com/posts/show/740

# consider using structured reads as per http://stackoverflow.com/questions/7569563/efficient-way-to-create-numpy-arrays-from-binary-files
# e.g.:
#  record_dtype = np.dtype( [ ( 'timestamp' , '<i4' ) , ( 'samples' , '<i2' , ( sample_rate , 4 ) ) ] )
#  data = np.fromfile(openfile , dtype = record_dtype , count = number_of_records )

import time
from array import array
from struct import unpack
import sys, getopt, re
import numpy

try:
    opts,args = getopt.getopt(sys.argv[1:], "l:",["latlon="])
except getopt.GetoptError, err:
    print str(err) 
    sys.exit(2)

latlonFile = None
for o,a in opts:
    if o in ("-l","--latlon"):
        latlonFile = a
        print "handling option %s, %s\n" % (o,a)
    else:
        assert False, "unhandled option"


# #  Data format description (char*48): e.g., 'DataFormat v2'
# version (char*48): version of Elcirc;
# start_time (char*48): start time of the run;
# variable_nm (char*48): variable description;
# variable_dim (char*48): '2D(3D) scalar(vector)'
# # of output time steps (int), output time step (real), skip (int), ivs (=1 or 2 for scalar or vector), i23d (=2 or 3 for 2D or 3D), vpos (=0, 0.5, 1 meaning no vertical structure, at half level or whole level);

# Data format description (char*48): e.g., 'DataFormat v5.0'
# version (char*48): version of SELFE;
# start_time (char*48): start time of the run;
# variable_nm (char*48): variable description;
# variable_dim (char*48): '2D(3D) scalar(vector)'
# # of output time steps (int), output time step (real), skip (int), ivs (=1 or 2 for scalar or vector), i23d (=2 or 3 for 2D or 3D);

def readRealLE(file): 
    b4=file.read(4)
    n4=unpack('<f',b4) # little endian
    return n4[0]

def readDoubleLE(file): 
    b=file.read(8)
    n=unpack('<d',b8) # little endian
    return n[0]

def readIntLE(file): 
    b4=file.read(4)
    n4=unpack('<l',b4) # little endian
    return n4[0]

def parseline(line, *types): return [c(x) for (x, c) in zip(line.split(), types) if c] or [None]
# from http://code.activestate.com/recipes/502260-parseline-break-a-text-line-into-formatted-regions/

def readHgridForLonLat(file):   # get the hgrid locations from an ascii hgrid.gr3 file
    print "Reading %s as hgrid.ll" % (file)
    f=open(file,'r')
    desc = f.readline()
    junk = f.readline()
    nele,nnode = parseline(junk,int,int)
    print "..Has %d elements and %d nodes" % (nele,nnode)
    x=numpy.zeros(nnode)
    y=numpy.zeros(nnode)
    for n in range(nnode):
        junk = f.readline()
#        print "  ..read %s" % (junk) 
        i,j = parseline(junk,None,float,float,None)
        x[n]=i
        y[n]=j
    return x,y,desc

#fname=sys.argv[1]
fname=args[0]
(basename,sep,suffix)=fname.rpartition('.')
outname=basename+'.nc'
if re.match('^[0-9]',outname) :
    outname='nc_'+outname  # prepend some chars for valid netcdf names
print "Converting %s to %s\n" % (fname,outname)

f=open(fname,'rb')
# header per http://www.ccalmr.ogi.edu/CORIE/modeling/selfe/input_mpi.html#Global%20output2
dataformat=f.read(48)
print "dataformat=%s" % dataformat
codeVersion=f.read(48)
print "codeVersion=%s" % codeVersion
timeStart=f.read(48) # mm/dd/yyyy HH:MM:SS TZD
variableName=f.read(48)
variableDimensions=f.read(48)

print "Timestart=%s\nVariableName=%s\n variable Dimensions=%s\n" % (timeStart,variableName,variableDimensions)

m= re.search("(\d+)/(\d+)/(\d+) *(\d+):(\d+):(\d+) *(\S+)" ,timeStart)
if m:
        (mon,day,year,hour,minute,second,tz)=m.group(1,2,3,4,5,6,7)
        print "timeStart parsed into ", m.group(3,2,1,4,5,6,7)
else:
	print "couldn't parse '{}' into components".format(timeStart)
	year,mon,day,hour,minute,second,tz=(0000,1,1,0,0,0,0000)

timezones = {'PST': -8, 'UTC': 0, 'EST': -5 ,'GMT': 0}

if tz in timezones:
        print "timezones[tz=={0}]= {1}".format(tz,timezones[tz])
	tz=timezones[tz]
else :
    print "tz of '{0}' was not found in the {1}".format(tz,timezones)
    print "timezones['GMT']={0}".format(timezones['GMT'])

print "{0} -> {1}-{2}-{3}T{4}:{5}:{6}{7:+05d}".format(timeStart,year,mon,day,hour,minute,second,tz*100)
timeUnitsString="days since {0}-{1}-{2} {3}:{4}:{5} {6:+02d}:00".format(year,mon,day,hour,minute,second,tz) ;
print timeUnitsString

ntime=readIntLE(f)
step=readRealLE(f)
skip=readIntLE(f)
ivs=readIntLE(f)
i23d=readIntLE(f)
#vpos=readRealLE(f)
print "ntime=%d step=%f skip=%d ivs=%d i23d=%d" % (ntime, step, skip, ivs, i23d)

# Vertical Grid Part
nvrt=readIntLE(f)  # verticals
kz=readIntLE(f)  # number of Z levels
h0=readRealLE(f)
h_s=readRealLE(f)
hc=readRealLE(f)
theta_b=readRealLE(f)
theta_f=readRealLE(f)
print "S-Z constants: h0=%f h_s=%f hc=%f theta_b=%f theta_f=%f" % (h0,h_s,hc,theta_b,theta_f)
# vertical grid

print "%d levels below %f as MSL" %  (nvrt, h0)
vrts=numpy.zeros(nvrt)
for i in range(nvrt):    #  off by one error in elcirc doc???
    vrts[i]=(readRealLE(f))

print vrts

# horizontal grid

np=readIntLE(f)
ne=readIntLE(f)

print "Horiz grid: %d nodes and  %d elements " % (np, ne)

x=numpy.zeros(np)
y=numpy.zeros(np)
h=numpy.zeros(np)
kbp00=numpy.zeros(np)
for m in range(np):
    x[m]=readRealLE(f)
    y[m]=readRealLE(f)
    h[m]=readRealLE(f)
    kbp00[m]=readIntLE(f)  #### XXXX  ragged bottom
    if m % 100000 == 0: print "node %d: (%f,%f,%f),%f" % (m,x[m],y[m],h[m],kbp00[m])
    if m == np-1: print "node %d: (%f,%f,%f),%f" % (m,x[m],y[m],h[m],kbp00[m])

nm=numpy.zeros([ne,4])
i34=numpy.zeros(ne,dtype=int)
for m in range(ne):
    i34[m]=readIntLE(f)
    for mm in range(i34[m]):
        nm[m,mm]=readIntLE(f)
    if m % 100000 == 0: print "element %d: (%d,%d,%d,%d)" % (m,nm[m,0],nm[m,1],nm[m,2],nm[m,3])
    if m == ne-1: print "element %d: (%d,%d,%d,%d)" % (m,nm[m,0],nm[m,1],nm[m,2],nm[m,3])

if (max(i34) == 3) :
    nm=nm[:,0:3]
    


# do the netcdf writing
from netCDF4 import *

ncf=Dataset(outname,'w',format='NETCDF3_64BIT')

ncf.createDimension('time',None)
ncf.createDimension('nele',ne)
ncf.createDimension('node',np)
ncf.createDimension('nface',max(i34))
ncf.createDimension('nbi',4)
ncf.createDimension('sigma',1)
ncf.createDimension('nfacepp',max(i34)+1)

times=ncf.createVariable('time','f4',('time',))
lats=ncf.createVariable('lat','f4',('node',))
lons=ncf.createVariable('lon','f4',('node',))
depth=ncf.createVariable('depth','f4',('node',))
sigma=ncf.createVariable('sigma','f4',('sigma'))
ele=ncf.createVariable('ele','i4',('nele','nface'))
elemixed=ncf.createVariable('elemixed','i4',('nele','nfacepp'))

gridComment = "no hgrid.ll comment"
if (latlonFile != None ) :
    x,y,gridComment = readHgridForLonLat(latlonFile)

lats[:]=y
lons[:]=x
depth[:]=h

ele[:,:]=nm
elemixed[:,0]=i34
elemixed[:,1:(max(i34)+1)]=nm

#for m in range(ne):
#    ele[m,0:(i34[m])]=nm[m]
#    elemixed[m,0]=i34[m]
#    elemixed[m,1:(i34[m]+1)]=nm[m]

ncf.description = 'SELFE elevation file from selfe2nc.py by drf@vims.edu 2010-12-07'
ncf.file_type = 'FEM' 
ncf.Conventions = 'CF-1.0' 

if (max(i34) != min(i34)) :
   ncf.grid_type = 'Mixed <= %dsided grid' % (max(i34)) 
elif max(i34) == 3 :
   ncf.grid_type = 'Triangular'
elif max(i34) == 4 :
   ncf.grid_type = 'Quadrilateral'
else :
   ncf.grid_type = '%d-sided grid (Error?)' % (max(i34))
   


ncf.z_type = 'Z' 
ncf.model = 'SELFE' 
ncf.title = 'SELFE Title' 
ncf.comment = 'SELFE Comment'  
ncf.comment_elcirc_param = 'NA'  
ncf.comment_elcirc_hgrid = gridComment  
ncf.source = 'source code version not known' 
ncf.institution = 'VIMS - http://www.vims.edu/' 
ncf.history = 'original' 
ncf.references = 'drf@vims.edu' 
ncf.creation_date = '2011-12-07T12:00' 

ele.long_name = 'Horizontal Element Incidence List'
ele.units = 'index_start_1'
ele.index_start = "1"
ele.cell_type = "mixed_ccw"
ele.standard_name = "connectivity_array"
ele.coordinates_node = "lat lon"
ele.drfnote = 'mixed grid--x[3] is 0 if the element is a triangle'

elemixed.long_name = 'Horizontal Element Incidence List'
elemixed.units = 'index_start_1'
elemixed.index_start = "1"
elemixed.cell_type = "mixed_ccw"
elemixed.standard_name = "connectivity_array"
elemixed.coordinates_node = "lat lon"
elemixed.drfnote = 'mixed grid--x[0] has length of mixed polygon, x[1:x[0]] has nodes'
elemixed.drfcomment = gridComment

times.long_name = 'Time' ;
times.units = timeUnitsString
times.base_date = (int(year), int(mon), int(day), int(hour)) ;
times.standard_name = 'time' ;

lats.units = 'degrees_north'
lats.long_name = 'Latitude'
lats.standard_name = 'latitude'

lons.units = 'degrees_east'
lons.long_name = 'Longitude'
lons.standard_name = 'longitude'
depth.units = 'meters'
depth.long_name = 'Bathymetry'
depth.standard_name = 'depth'
depth.positive = 'down'

if i23d == 2:
    myVarDims=('time','node')
else: # 3d
    myVarDims=('time','sigma','node')

if ivs == 1:
    z=ncf.createVariable('z','f4',myVarDims)
    z.units = "meters"
    z.long_name = "Water Surface Elevation"
    z.standard_name = "sea_surface_elevation"
    z.positive = "up"
    z.grid = "elemixed"
    z.grid_location = "node"
    z.type = "data"
    z.coordinates ="lat lon"
else:  # vector    
    zu=ncf.createVariable('zu','f4',myVarDims)
    zv=ncf.createVariable('zv','f4',myVarDims)


# Now we read the actual data
# time iteration part

# 2011-07-04 look into numpy.fromfile and numpy.core.records.fromfile
#from http://www.scipy.org/Numpy_Example_List_With_Doc

nZsRead=0
myFloats=array('f')
for it in range(ntime):
    t=readRealLE(f)
    times[it]=t/3600/24 # assign a slice to extend the unlimited dimension
    itval=readIntLE(f)
    print "iteration %d at time %fs (or %fd) with itval=%d\n" % (it,t,times[it],itval)
#    kfp=numpy.zeros(np) # This seems wrong.  http://www.ccalmr.ogi.edu/CORIE/modeling/selfe/input_mpi.html#Global%20output2 says surf elev, then.... whatever  
#    for i in range(np):
#        kfp[i]=readRealLE(f)
    kfp=numpy.fromfile(f,dtype='<f4',count=np)
    if i23d == 2:
        print " {0}-dimensional output".format(i23d)
        if ivs == 1:
            print " scalar data--ivs={0}".format(ivs)
            # slow iterative method
            #for i in range(np):
            #   tmp1=readRealLE(f)
            #   z[it,i]=tmp1
            #   nZsRead += 1
            #
            # fast numpy.fromfile method per http://stackoverflow.com/questions/1632673/python-file-slurp-w-endian-conversion 
            # and http://docs.scipy.org/doc/numpy/reference/generated/numpy.fromfile.html
            z[it,:]=numpy.fromfile(f,dtype='<f4',count=np)
            nZsRead += np

        else:   # vector
            tmp1=readRealLE(f)
            tmp2=readRealLE(f)
            zu[it,i]=tmp1
            zv[it,i]=tmp2
            nZsRead += 2
    else:   # 3d
        print " {0}-dimensional output".format(i23d)
        print "Using slow 3d code.  Untested as of 2011-07-06"
        for i in range(np):
            for k in range(kbp00(i)-1,nvrt):  # allow for a ragged bottom at each node
                if ivs == 1 :  # scalar
                    tmp1=readRealLE(f)
                    z[it,k,i]=tmp1
                    nZsRead += 1
                else:  #  vector
                    tmp1=readRealLE(f)
                    tmp2=readRealLE(f)
                    zu[it,k,i]=tmp1
                    zv[it,k,i]=tmp2
                    nZsRead += 2
    ncf.sync()
# print "extra int was %d" %  readIntLE(f)  # test to see if there was more to read...

f.close()
ncf.close()
print "I read %d z values\n" % (nZsRead)
