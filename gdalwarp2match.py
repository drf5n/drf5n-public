#!/usr/bin/env python
# https://github.com/drf5n/drf5n-public/blob/master/gdalwarp2match.py


from osgeo import gdal, gdalconst
import argparse

# some mappings per https://gdal.org/programs/gdalwarp.html and https://gdal.org/python/osgeo.gdalconst-module.html
resampling = { 'near': gdalconst.GRA_NearestNeighbour,
                   'bilinear': gdalconst.GRA_Bilinear,
                   'cubic': gdalconst.GRA_Cubic,}


parser = argparse.ArgumentParser(description='Use GDAL to reproject a raster to match the extents and res of a template')
parser.add_argument("source", help="Source file")
parser.add_argument("template", help = "template with extents and resolution to match")
parser.add_argument("destination", help = "destination file (geoTIFF)")
parser.add_argument("--resample", choices=resampling.keys(),
                    help="""Resampling/interpolation method """, default="near")

args = parser.parse_args()
print(args)



# Source
src_filename = args.source
src = gdal.Open(src_filename, gdalconst.GA_ReadOnly)
src_proj = src.GetProjection()
src_geotrans = src.GetGeoTransform()

# We want a section of source that matches this:
match_filename = args.template
match_ds = gdal.Open(match_filename, gdalconst.GA_ReadOnly)
match_proj = match_ds.GetProjection()
match_geotrans = match_ds.GetGeoTransform()
wide = match_ds.RasterXSize
high = match_ds.RasterYSize

# Output / destination
dst_filename = args.destination
dst = gdal.GetDriverByName('GTiff').Create(dst_filename, wide, high, 1, gdalconst.GDT_Float32)
dst.SetGeoTransform( match_geotrans )
dst.SetProjection( match_proj)

# Do the work
gdal.ReprojectImage(src, dst, src_proj, match_proj, resampling[args.resample])

del dst # Flush
