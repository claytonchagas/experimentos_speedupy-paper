#!/usr/bin/perl
#Script to read in the position of a blast hit and print out the sequence associated with that postion/length
use strict; use warnings;

die "usage: Extract_Seq.pl <CHR FASTA> <FILTERED OUTPUT> <CHR> <OUTPUT>" unless @ARGV==4;

my $chr_fasta = $ARGV[0];
my $filtered_centc = $ARGV[1];
my $chromosome = $ARGV[2];
my $output = $ARGV[3];

open(REFCHR, "<$chr_fasta");
open(OVL, "<$filtered_centc");
open(OUT, ">$output");

my $chr_pos;
my $count=1;

while(<REFCHR>){
	if ($_ =~ m/^[N|A|T|G|C]/) {
		$chr_pos = $_;
	}
}

close REFCHR;

while (<OVL>) {
	chomp;
	if ($_ =~ m/$chromosome/) {
		my ($chr, $start, $stop, $length, $percid, $RC) = split ("\t", $_);
		my $sequence = substr ($chr_pos, $start, $length);
		if ($RC > 100) {
			my $rev_comp = reverse($sequence);
			$rev_comp =~ tr/ATGC/TACG/;
			print OUT "$chr.$count\t$start\t$count\n";
			$count++;
		} else {
			print OUT "$chr.$count\t$start\t$count\n";
			$count++;
		}
	}
}

print "\n";	
