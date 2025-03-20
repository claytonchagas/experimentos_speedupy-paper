setwd("~/Documents/Projects/Centc/Github_CentC")

data <- read.csv("Supl_TWtable.csv",header=TRUE)

subgenome <- data$Chr
subgenome[which(subgenome %in% c(1,2,5,7,9,10))] = "green3"
subgenome[which(subgenome %in% c(3,4,6,8))] = "peru"

plot(data$Chr ~ data$Group, cex=logb(data$Value, base=60), pch=16, col=subgenome, xlab="Group", ylab="Chromosome",yaxt='n')
axis(2, at=c(1,2,3,4,5,6,7,8,9,10))
#text(data$Chr, data$Group, label=as.character(data$Value), font=5)
?plot