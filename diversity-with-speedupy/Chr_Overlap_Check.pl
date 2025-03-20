#!/usr/bin/perl
#Input a blast output, script will run through and keep only entries beyond a threshold distance
use strict; use warnings;

die "usage:Chr_Overlap_Check.pl <BLASToutput> <SeqLocationoutput>" unless @ARGV==2;

my $blast_input = $ARGV[0];
my $filtered_output = $ARGV[1];
my $SV_CHR = 0;
my $SV_START = -100;
my $SV_END = 0;
my $SV_LENGTH = 0;
my $SV_PERCID = 0;
my $UPPER = 0;
my $LOWER = 0;
my $SV_REVCOMP = 0;
#my ($query_id, $subject_id, $percid, $length, $mismatch, $gap, $q_start, $q_end, $s_start, $s_end, $evalue, $bit) = 0;

open(BLAST, "<$blast_input");
open(OUT, ">$filtered_output");

while (<BLAST>) {
	chomp;
	if ($_ =~ m/^chr/) {
	 	my ($query_id, $subject_id, $percid, $length, $mismatch, $gap, $q_start, $q_end, $s_start, $s_end, $evalue, $bit) = split ("\t", $_);
	#	print "$length\nfailboat\n";
		if ($length > 140) {							#check if the length meets our threshold, 140
			$UPPER = $SV_START + 100;
			$LOWER = $SV_START - 100;
			if ($LOWER<=$q_start and $q_start<=$UPPER) {	#check if the start of current read is within 100 bases of saved read
				if ($SV_PERCID <= $percid) {				#if within range, check if it has a higher percid
					$SV_CHR = $query_id;	#set saved chr to the current query, to be altered if chr is not query
					$SV_START = $q_start;
					$SV_END = $q_end;
					$SV_LENGTH = $length;
					$SV_PERCID = $percid;
					$SV_REVCOMP = $s_start;
				}
			} else {
				if ($length >140) {
					print OUT "$SV_CHR\t$SV_START\t$SV_END\t$SV_LENGTH\t$SV_PERCID\t$SV_REVCOMP\n";
						$SV_CHR = $query_id;	#set saved chr to the current query, to be altered if chr is not query
						$SV_START = $q_start;
						$SV_END = $q_end;
						$SV_LENGTH = $length;
						$SV_PERCID = $percid;
						$SV_REVCOMP = $s_start;
				}
			}
		}
	}
}

print OUT "$SV_CHR\t$SV_START\t$SV_END\t$SV_LENGTH\t$SV_PERCID\t$SV_REVCOMP\n";
		
