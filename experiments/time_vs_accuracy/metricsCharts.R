#For Lab 41 Circulo metrics json files
#Patrick Wheatley NGA + others :)
#29Aug2014. Modified 22 Sep 2014
#reads json files from directory and plots pdf bubble chart of computation time and omega accuracy

# Sample Usage:
#   metrics <- getMetrics(datapath)
#   plotMetrics(metrics)
#   plotHist(metrics,'omega')
#   plotHist(metrics,'time')

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
    metrics <-data.frame(metrics[ind,],stringsAsFactors=FALSE)
    metrics <- data.frame(lapply(metrics, unlist),stringsAsFactors=FALSE)
    metrics$ComputationTime <- as.numeric(metrics$ComputationTime)
    metrics$OmegaAccuracy <- as.numeric(metrics$OmegaAccuracy)

    
   return(metrics)
}

# Plot Metrics
plotMetrics <- function(metrics,toPDF=FALSE) {
    # Group metrics by Dataset and Algorithm, then summarize
    data <- aggregate(metrics[,c('ComputationTime','OmegaAccuracy')],list(metrics$Datasets,metrics$Algorithms),mean)
    colnames(data)[1:2] <- c("Datasets","Algorithms")
    
    keep <- which(data$Algorithms != 'groundtruth')
    data <- data[keep,]
    
    bubbleplot <- ggplot(data, aes(x=Datasets, y=Algorithms))+
          geom_point(aes(size=OmegaAccuracy, colour=ComputationTime), alpha=0.75)+
          scale_size_continuous(limits=c(0,1),range =c(5, 25))+
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

# Plots histogram of specified metric (omega or computation time right now)
plotHist <- function(metrics,col='ComputationTime',toPDF=FALSE) {

    data <- metrics[c('Algorithms','Datasets',col)]
    colnames(data)[3] <- "value"

    p <- ggplot(data,aes(x=value,fill=Algorithms)) +
    facet_grid(. ~ Datasets) +
    geom_density(alpha=0.5) +
    #geom_histogram(alpha=0.5,position='identity')
    xlab(col) + 
    ylab('Probability Density') + 
    theme_bw() +
    ggtitle(Sys.time())
  

    if (toPDF) {
        pdffile <- paste(Sys.time(),"metricsGraph.pdf", sep='')
        pdf(pdffile,height=10,width=12)
        print(p)
        dev.off()
        cat(sprintf('printed to %s \n', pdffile))
    } else {
        print(p)
    }
}
