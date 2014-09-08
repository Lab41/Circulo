#For Lab 41 Circulo metrics json files
#Patrick Wheatley NGA
#29Aug2014
#reads json files from directory and plots pdf bubble chart of computation time and omega accuracy


#first time this script is run on a machine you should uncomment the install.packages function lines
# Only required the first time

#install.packages ("jsonlite")
#install.packages("ggplot2")
library(ggplot2)
library(jsonlite)


#Point this to the directory containing metrics output json files
setwd("/home/lab41/Desktop/R stuff/outputs")

WD <- getwd()

#Get file names and load the json files
filenames <- list.files(WD, pattern="*json", full.names=TRUE)
results <- lapply(filenames, fromJSON)

#parse filenames to get algorithm names and dataset names
names <- basename(filenames)
names2 <- sapply(1:length(names), function(x) strsplit(names, "\\.")[[x]][1])
Algorithms <-sapply(1:length(names), function(x) strsplit(names2, "--")[[x]][1])
Datasets <- sapply(1:length(names), function(x) strsplit(names2, "--")[[x]][2])

#Pull computation time and omega from the json files
ComputationTime <- sapply(1:length(filenames), function (x) results[[x]]$elapsed)
OmegaAccuracy <- sapply(1:length(filenames), function (x) results[[x]]$metrics$omega)

#fussy R data type formatting
metrics <- (cbind(Algorithms, Datasets, ComputationTime, OmegaAccuracy))
ind <- which(metrics[,"OmegaAccuracy"] != "NULL")
metrics<-as.data.frame(metrics[ind,])
names(metrics) <- c('Algorithms', 'Datasets', 'ComputationTime', 'OmegaAccuracy')
metrics <- as.data.frame(lapply(metrics, unlist))

#if you want a csv file of the table of omega and comptime as a function of dataset and algorithm
#write.csv(metrics, "circuloMetrics.csv")

#####ggplot2 time######
#plot this data
bubbleplot<- ggplot(metrics, aes(x=Algorithms, y=Datasets))+
          geom_point(aes(size=OmegaAccuracy, colour=ComputationTime), alpha=0.75)+
          scale_size_continuous( range =c(5, 25))+
          scale_colour_gradient2(low="dark green",mid="yellow", high="red", trans='log')+
          theme_bw()+
          ggtitle(Sys.time() )

pdf(paste(Sys.time(),"metricsGraph.pdf", sep=''))
bubbleplot
dev.off()


#experimental plot with color as omega and size as comptime
#ggplot(metrics, aes(x=Algorithms, y=Datasets))+
              #geom_point(aes(size=ComputationTime, alpha=OmegaAccuracy, colour=OmegaAccuracy))+
              #scale_size_continuous( range =c(3, 25))+
              #scale_colour_gradient2(low="red",mid="yellow", high="dark green")+
              #theme_bw()

