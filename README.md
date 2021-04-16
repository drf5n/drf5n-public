drf5n-public
============

This is a public repository of some of my tools.  -- Dave  drf@vims.edu

VDatumTools: Decode vdatum files per http://vdatum.noaa.gov/dev/gtx_info.html into GIS-compatible files
(obsolescent -- GDAL now supports GTX <http://www.gdal.org/formats_list.html> as does ArcInfo <http://desktop.arcgis.com/en/arcmap/10.3/manage-data/raster-and-images/supported-raster-dataset-file-formats.htm> )

The VDATUM data is distributed as EPSG:4326, (which has latitude bounds of -180,180) but the data is in 0-360.  You can use GDAL to fix this and make it more compatible with other datasets:

    gdalwarp -t_srs WGS84 tss.gtx tss.tif  --config CENTER_LONG 0

or if you have a problem with crossing a meridian:

    gdalwarp -t_srs WGS84 tss.gtx tss.tif i -wo SOURCE_EXTRA=1000 --config CENTER_LONG 0
