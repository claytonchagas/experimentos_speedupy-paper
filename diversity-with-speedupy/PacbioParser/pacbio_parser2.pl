#!/usr/bin/perl
#PacbioParser2

use strict;
use warnings;

# perl pacbio_parser2.pl DB_centc_Q_B73PB600  

my $infile = $ARGV[0];
my $outfile = $ARGV[1];

open (INFILE, "<$infile") or die 'File cannot be opened\n\n';
open (TEMP1, ">temp1.txt") or die 'File cannot be opened\n\n';

my $count = 0;
my @array1;
#Read in pacbio data
while (<INFILE>) {
	chomp $_;
	#If hits line is less than 4 hits found, go to next line
	if ($_=~m/\#\s{1}(\d+)\D{4}\D{5}/) {
	next if ($1<4);
	}
	#Read in a block of hits from a read
	if (/^#\s{1}\d+/../^#\s{1}\D{5}/) {
		next if /^#\s{1}\D{5}/;
		my @linedata = split('\t',$_);
		my $align_value = $linedata[3];
		#Push hits to an array if align value is greater than 100
		if (defined $align_value && $align_value ne '') {
			if ($align_value<100) {
				next;
			}
		}
		push (@array1,"$_");
	}
			#Print array to temporary parsed file
			if (defined $array1[0] && $array1[0] ne '') {
				print TEMP1 "$array1[0]\n";
			}
	undef (@array1);
}
close (TEMP1);

open (TEMP1, "<temp1.txt") or die 'File cannot be opened\n\n';

my @array2;
my @temp_array;
my @temp_sorted;
my $centc_count=0;
my $total_count=0;

while (<TEMP1>) {
	chomp;
	#Read in block of Pacbio data reads
	if ($_=~m/^m/) {
	my @array2 = split('\t',$_);
	my $q_start = $array2[6];
	#Push start values to an array
	push (@temp_array,"$q_start");
	}
	#If it's the start of the next block process the block that was read in
	else {
			#Sort the start values and set centc counts in the block.
			@temp_sorted = sort { $a <=> $b } @temp_array;
			#Compare each start value of the array with the next number. If the difference is less than 50 add to count.
			for (my $i = 0; $i <= $#temp_sorted; ++$i) {
				local $_ = $temp_sorted[$i];
				my $next_qstart = $temp_sorted[++$i];
				if (defined $next_qstart && $next_qstart ne '') {
					if ($_-$next_qstart<50) {
						$centc_count++;
					}
				next;
				}
			#Once every start is compared, check if the the total count for the block is 4 or more. If it is add one to the reads that have more than 4 CentCs in tandem.
			}
			if (defined $centc_count && $centc_count ne '') {
				if($centc_count>3) {
					$total_count++;
				}
			}
			#Once block is done processing, reset everything.
			$centc_count=0;
			undef (@temp_array);
			undef (@temp_sorted);
		}
}

print "$infile\n$total_count\n";

