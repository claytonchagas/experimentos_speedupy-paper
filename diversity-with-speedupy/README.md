CentC_Analyses
==============
**************************************
*      CentC Project Workflow        *
**************************************
By: Paul Bilinski, UC Davis, 2013

Original, large data files can be found on:
http://figshare.com/account/projects/124


1. Extract all CentC's from the maize reference genome (version 2)
-The original CentC sequences (Genbank + Nagaki et al 2003 Study) are in 

CentC_Seq_Originals.fasta

-Use the reverse complimented sequences for BLASTing.

-Follow instructions in the README_blast_anno.txt

-The DNA distance matrices can be generated using PHYLIP software package, DNADIST
function.  This project was run using PHYLIP 3.69.  To regenerate my dna distance 
matrices, I first performed 7 muscle alignments of the sequences I wanted to have in the
distance matrix (for example, all CentC from chromosome 2 or 5).  This was performed in
Geneious's muscle.  Then the alignment was fed to the dnadist.

-Execute the Spagedi analyses given the distance matrices and text files in the spagedi
manual.  These analyses were run with SPAGeDi 1.3a.

-Use these distances to generate the figure in the text

-The scripts you will need are:
Making_Chr_Dist_Figures.R
ExtractforSpagedi.pl
Extract_Seq_Pos.pl
Extract_Seq.pl

2. Circos

-Follow Kevin's Circos code in the Readme generated from his email.  The necessary files
are POS_chrAll.txt and the subgenome assignments from Schnable.

3. PacBio Tandem CentC Parsing in long reads

-Filtered data for long reads with CentC blast hits in is the PacBio folder

-Follow the Readme to calculate tandem counts seen in supplementary table

4. CentC abundance simulations with Mosaik

-Code available on Kevin Distor's Github https://github.com/kddistor/dnasims

5. Mapping Abundance with Mosaik

-Mosaik itself is zipped into this repo.  Open and install.

-Following manual and our parameters, you can map against the reference of all of the
CentC's in the maize genome.  Results are on this repo.

6. Diversity simulations (to show homoplasy is possible)

-Simple code in the diversity sims, execute and observe how many total shared mutations of
frequency occur

7. Tracy Widom Analyses

-In the PCoA_Analyses directory you will find the following files:

ConvertPhylipMatrixtoCSV.pl: perl script to make phylip files into csv matrix
Original_centc_DNADIST.csv: test matrix of 218 original CentC
twtable.txt: Joosts table

-Use these and the twcentc.rmd to recalculate the values

-A test matrix with the original 218 sequences is provided as well.

8. Gaby's CHIP results

-Performed in with Bowtie, mapped against CHIP reads from paper cited in text.

9. Cluster Distance Adjusting

-Using the AdjustCluster.pl and ClusterNeighbors_forscript.csv, you can calculate various
cluster distances

-The Code to do so is at the start of the perl script, or here
#for i in {1..20}; do BP=$(( $i*1000 )); perl AdjustCluster.pl $BP 10000;  done
#code to execute it for a lot of diff distances

If I have forgotten any analysis, please contact me at my UCDAVIS email and I will be sure
to upload it!