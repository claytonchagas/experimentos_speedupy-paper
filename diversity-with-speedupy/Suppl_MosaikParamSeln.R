setwd("~/Documents/Projects/Centc/Github_CentC")
data <- read.csv("Supplemental_MosaikParamSeln.csv")

plot(data$ACT, data$Percent_Mapping, xlab="Alignment Candidate Threshhold", ylab="Percent of Reads Mapping", main="Alignment Candidate Threshold Parameter Selection")