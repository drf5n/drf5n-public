#!/usr/bin/perl
use strict;

my $usage = <<EOT;
For unpacking a vdatum GTX file per http://vdatum.noaa.gov/dev/gtx_info.html

EOT

my $file = $ARGV[0];
open FILE, $file or die "Couldn't open file $file: $!\n";

binmode FILE;

my $record =1;
my $buffer ='';



#read(FILE,$buffer,4*8+2*4) or die "Trouble reading header\n";

my ($llLat,$llLon,$dy,$dx,$nRows, $ncolumns) = 
( 
 readIEEErev(),
 readIEEErev()-360,
 readIEEErev(),
 readIEEErev(),
 readINTrev(),
 readINTrev(),
);

die "Non-square cellsi: $dx != $dy -- Arcinfo ASCII grid impossible\n" if ($dy != $dx ); 

# non-square might work in some software (gdal?) with DX and DY

my $nodata=-9999;

print <<EOT;
ncols $ncolumns
nrows $nRows
xllcorner $llLon
yllcorner $llLat
cellsize $dx
nodata_value $nodata
EOT

# gtx starts LL, AIG start UL, so reverse iy index:

for (my $iy=$nRows-1 ; $iy >=0  ; $iy--){
  seek FILE,40+$iy*8*$ncolumns,0;  
  for( my $ix=0 ; $ix <$ncolumns ; $ix++) {
    my $val=readIEEErev();
    $val = $nodata if (abs($val - -88.8888) <1e-9 );
    print  $val, ' ';;
	}
	print "\n";
}


sub readIEEErev {
#my $fn = shift;
my $buf ='';
read (FILE, $buf,8);

return unpack 'd', pack 'C8', reverse unpack 'C8', $buf;

}


sub readINTrev {
#my $fn = shift;
my $buf ='';
read (FILE, $buf,4);

return unpack 'i', pack 'C4', reverse unpack 'C4', $buf;

}


