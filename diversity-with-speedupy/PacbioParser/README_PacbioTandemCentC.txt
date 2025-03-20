**************************************
* BLAST ID of Tandem CentC in Pacbio *
**************************************
By: Paul Bilinski, UC Davis, 2013

Written to be able to redo the the pacbio tandem repeat detection portion of the CentC paper.

Start by concatenating all of the fastq reads from the pacbio sequences as a FASTA sequence.  Then make the fasta into a format i like with:

perl FASTA_linebreaks.pl FASTA_FILE CONCATENATED_FASTA

Then use the sequence length filter to get only 600bp + reads.

perl lengthfilter.pl 600 CONCAT_FASTA 600MINFASTA

Then run a blastn with:

blastn -query ~/centc/Pacbio_tandemevidence/mexicana_pacbio_600min.fasta -evalue 1E-1 -outfmt 7 -task blastn -db Random_centc.fasta -out DB_centc_Q_mexPB600

Using the randomcentc as the database.

The blast outputs are located copied into the GITHUB folder so that the analyses can be redone.

From the DB_OUTPUTS, run the pacbioparser2.pl
The number output will be the number of reads that contain 4+ tandem centc's.