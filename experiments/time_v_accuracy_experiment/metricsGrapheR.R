#For Lab 41 Circulo metrics json files
#Patrick Wheatley NGA + others :)
#29Aug2014. Modified 22 Sep 2014
#reads json files from directory and plots pdf bubble chart of computation time and omega accuracy

# Sample Usage:
#   metrics <- getMetrics(datapath)
#   plotMetrics(metrics)

library(ggplot2)
library(jsonlite)

# Read metrics from json
getMetrics <- function(datapath='/home/lab41/workspace/circulo_output/metrics') {

    #Get file names and load the json files
    filenames <- list.files(datapath, pattern="*.json", full.names=TRUE)
    N <- length(filenames)
    results <- lapply(filenames, fromJSON)

    #parse filenames to get algorithm names and dataset names
    names <- basename(filenames)
    names2 <- sapply(1:N, function(x) strsplit(names, "\\.")[[x]][1])
    Datasets <- sapply(1:N, function(x) strsplit(names2, "--")[[x]][1])
    Algorithms <-sapply(1:N, function(x) strsplit(names2, "--")[[x]][2])

    #Pull computation time and omega from the json files
    ComputationTime <- sapply(1:N, function (x) results[[x]]$elapsed)
    OmegaAccuracy <-sapply(1:N, function (x) results[[x]]$metrics$omega)

    #fussy R data type formatting
    metrics <- cbind(Algorithms,Datasets,ComputationTime,OmegaAccuracy)
    ind <- which(metrics[,"OmegaAccuracy"] != "NULL")
    metrics <-data.frame(metrics[ind,])
    metrics <- data.frame(lapply(metrics, unlist))

   return(metrics)
}

# Plot Metrics
plotMetrics <- function(metrics,toPDF=FALSE) {
    bubbleplot <- ggplot(metrics, aes(x=Datasets, y=Algorithms))+
          geom_point(aes(size=OmegaAccuracy, colour=ComputationTime), alpha=0.75)+
          scale_size_continuous( range =c(5, 25))+
          scale_colour_gradient2(low="dark green",mid="yellow", high="red", trans='log')+
          theme_bw()+
          ggtitle(Sys.time())

    if (toPDF) {
        pdffile <- paste(Sys.time(),"metricsGraph.pdf", sep='')
        pdf(pdffile,height=10,width=12)
        print(bubbleplot)
        dev.off()
        cat(sprintf('printed to %s \n', pdffile))
    } else {
        print(bubbleplot)
    }
}
