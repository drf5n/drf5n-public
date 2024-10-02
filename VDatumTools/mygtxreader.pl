#!/usr/bin/perl
use strict;

my $usage = <<EOT;
For unpacking a vdatum GTX file per http://vdatum.noaa.gov/dev/gtx_info.html
drf@vims.edu
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


printf "(#%12.9f,%12.9f)\n# +d(%12.9f, %12.9f)\n#  *(%d,%d)\n",
             $llLat,$llLon,$dy,$dx,$nRows, $ncolumns;

for( my $ix=0 ; $ix <$ncolumns ; $ix++) {
  for (my $iy=0 ; $iy < $nRows ; $iy++){

	printf "%10.9f	%12.9f	%12.4f\n",
         $llLon+$dx*$ix,
	 $llLat+$dy*$iy,
	 0;
}
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


