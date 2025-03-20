#!/usr/bin/perl
#Convert the square matrix format from the phylip file into a matrix ready for spadegi as a tab delimited matrix
use strict; use warnings;

die "usage:ConvertPhylipMatrixtoCSV.pl <input matrix> <output matrix>" unless @ARGV==2;

open(INPUT, "<$ARGV[0]");
open(OUTPUT, ">$ARGV[1]");

my $storeline;

while(<INPUT>){
	chomp;
	$_ =~ tr/ /,/;
	if ($_ =~ m/^chr/){
		print OUTPUT "$storeline\n";
		$storeline=$_;
	} else {
		$storeline = $storeline . $_;
	}
}

print OUTPUT "$storeline";
