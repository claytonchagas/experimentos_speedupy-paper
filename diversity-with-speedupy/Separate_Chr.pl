#!/usr/bin/perl
#Input a blast output, script will run through and keep only entries beyond a threshold distance
use strict; use warnings;

die "usage:Separate_Chr.pl <BLASToutput> <CHRoutput> <target chromosome>" unless @ARGV==3;

my $blast_input = $ARGV[0];
my $separated_out =$ARGV[1];
my $chromosome = $ARGV[2];
#my ($query_id, $subject_id, $percid, $length, $mismatch, $gap, $q_start, $q_end, $s_start, $s_end, $evalue, $bit) = 0;

open(BLAST, "<$blast_input");
open(OUT, ">$separated_out");

while (<BLAST>) {
	chomp;
	if ($_ =~ m/^$chromosome/) {
	 	my ($query_id, $subject_id, $percid, $length, $mismatch, $gap, $q_start, $q_end, $s_start, $s_end, $evalue, $bit) = split ("\t", $_);
		if ($length > 140) {							#check if the length meets our threshold, 140
			print OUT "$query_id\t$subject_id\t$percid\t$length\t$mismatch\t$gap\t$q_start\t$q_end\t$s_start\t$s_end\t$evalue\t$bit\n"
		}
	}
}		
