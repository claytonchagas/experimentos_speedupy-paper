Input for plotting:
library(RCircos);
data <- read.csv("C:/cygwin/home/Kevin/data/Schnable_SG_assignments5.csv", header=T)
chr.exclude <- NULL;
tracks.inside <- 1;
tracks.outside <- 0;
cyto.info <- data;
RCircos.Set.Core.Components(cyto.info, chr.exclude,tracks.inside, tracks.outside);
RCircos.Set.Plot.Area();
RCircos.Chromosome.Ideogram.Plot()

- Core components must be set to create the graphs.

To modify/change parameters of graph:
http://cran.r-project.org/web/packages/RCircos/vignettes/Using_RCircos.pdf
page 10 goes over this
page 6-7 goes over what each param is

My Input:
library(RCircos)
params <- RCircos.Get.Plot.Parameters()
params$chrom.width <- .5
RCircos.Reset.Plot.Parameters(params)
data <- read.csv("C:/cygwin/home/Kevin/data/Schnable_SG_assignments5.csv", header=T)
chr.exclude <- NULL
tracks.inside <- 1
tracks.outside <- 0
cyto.info <- data
RCircos.Set.Core.Components(cyto.info, chr.exclude,tracks.inside, tracks.outside);
RCircos.Set.Plot.Area()
RCircos.Chromosome.Ideogram.Plot()

POS_chrAll.txt
Same idea as above instead read data as this file instead. Hopefully to get plots like A E F or G on this graph: http://www.nature.com/ncomms/2013/130827/ncomms3320/fig_tab/ncomms3320_F3.html