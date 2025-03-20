**************************************
*      BLAST Annotation of CentC     *
**************************************
By: Paul Bilinski, UC Davis, 2012

These instructions will take a reference library, turn it into a database, and blast the maize genome against that library.  In this case the library is CentC, reverse complemented and aligned from its various sources.  This allows for the easy identification of inverted repeats within the sequence.  The sequence of the reads will then be extracted from the reference and can be analyzed.

Step 1: Database and Query Preparation 

In gathering the reads for the library, ensure that all reads are in the same direction and in the same frame.  This will allow you to build an NJ tree with the reads that is accurate as far as genetic distance.  NJ trees need aligned sequence.  The reads can then be transferred to the cluster and made into a blast database with:

	makeblastdb -in CentC_Seq_RC.fasta -dbtype 'nucl' -parse_seqids
	
To make the maize reference genome a suitable query, we must have a unique identifier for each of the chromosomes.  This is done for you in the file v2B73_ref.fasta where each of the chromosomes are named with 2 digits, such as chr00 for chromosome 0.

Step 2: Submit BLAST Query

On the cluster with all of the data prepared, submit a BLAST job with Submit_Flipped.sh, or

	blastn -query ~/centc/blasting_wgs/Flipped/v2B73_ref.fasta -evalue 1E-1 -outfmt 7 -db CentC_Seq_RC.fasta -num_threads 4 -out DB_CENTC_Q_v2B73

Pay attention as to how many CPU you ask to reserve, because this job does not need a ton.

Step 3: Separate/Sort/Delete Overlap BLAST output

To extract all sequences that are from each of the chromosome, use the perl script Separate_Chr.pl with the following template.

	 perl Separate_Chr.pl DB_CENTC_Q_v2B73 CHR00.blastout chr00

This will take the blast hits and separate based on each of the chromosomes. Each of these chr00.blastout needs to be sorted based on position on chr with

	cat chr00.blastout | sort -k7n > chr00.sorted
	
These sequences now need to be checked for overlapping centc hits with the perl script Chr_Overlap_Check.pl

	perl Chr_Overlap_Check.pl <BLASTsorted> <Hits without overlap output>
	
Step 4: Extract Sequence from the Reference Genome

#NOT NECESSARY FOR JUST PULLING OUT NUMBER OF SEQUENCES

Next, you will have to take the reference sequence and parse it so that each of the chromosomes end up in their own file in a single line.  This is necessary for the substr function to work.  I accomplished this with the script Replace_Line_End.pl and 

	sed '2q;d' FILEFROM 
	Where the 2 indicates the line i want to grab.
	
With the chromosome reference, ovl checked BLAST, a specific chromosome, and a filename for the output, we can extract all sequences.

	perl Extract_Seq.pl REFERENCE_FILE OVL_CHECKED CHRNAME OUTPUT
#THIS STEP GIVES YOU THE FINAL
#example: 

	
Step 5: Making the NJ tree


Step 6: Making SpaGeDi

	This will be the steps that you have to take to generate a Spagedi Permutation.  First, you have get the distances from the BLAST hits.  Use Extract_forSpagedi.pl on each of the chromosomes.
	The output will print a file of the given alleles.  Follow the naming convention for a proper SPAGEDI header (see the spagedi manual or one of my SPAGEDI files.
	Next, we have to add the distance matrix.  This comes from an alignment of the CentC sequences.  Grep out the chromosomes of interest from the full alignmented (B73centcseq) and calculate the distance.
	The matrix can be generated from DNADIST in phylip on the cluster.  I used JC distance, brought it back to my computer, and converted the matrix to a csv with
		ConvertPhylipMatrixtoCSV.pl
	and opened it as a CSV. Now you notice that the CentC's are no longer listed in order of where they occur...
	Easiest way to sort them is to
	Have to change the centc names from the chr02.___ to the number, 1 2 3 4 etc.  This identifies them as alleles, and also name the locus (Ugh in this case).
	Add this matrix along with an END command, and run in spagedi (execute spagedi in the application directory from the directory with my finished Spagedi formatted file)
	Once in Spagedi, Select Nij, (3) Make Permutation tests, (1) Test of genetic structuring, NOTHING so all is reported, (2) for all stat of regression analyses
	Use Obs value and the conf intervals to generate my graph!
