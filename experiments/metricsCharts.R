#For Lab 41 Circulo metrics json files
#Patrick Wheatley NGA + others :)
#29Aug2014. Modified 22 Sep 2014
#reads json files from directory and plots pdf bubble chart of computation time and omega accuracy

# Sample Usage:
#   metrics <- getMetrics(datapath, "dataset name")
#   plotMetrics(metrics)
#   plotHist(metrics,'omega')
#   plotHist(metrics,'time')
#   plotRunOmega(metrics)

library(ggplot2)
#Switched from jsonlite to RJSIONIO for speed reasons
library(RJSONIO)

# Read metrics from json
getMetrics <- function(datapath='/Users/paulm/Desktop/metrics', dataset="football") {

    #Get file names and load the json files
    filenames <- list.files(datapath, pattern=paste(".*",dataset,".*.json", sep=""), full.names=TRUE)
    N <- length(filenames)
    results <- lapply(filenames, fromJSON)

    #parse filenames to get algorithm names and dataset names
    names <- basename(filenames)
    names2 <- sapply(1:N, function(x) strsplit(names, "\\.")[[x]][1])
    Datasets <- sapply(1:N, function(x) strsplit(names2, "--")[[x]][1])
    Algorithms <-sapply(1:N, function(x) strsplit(names2, "--")[[x]][2])

    #Pull computation time and omega from the json files
    ComputationTime <- sapply(1:N, function (x) results[[x]]$elapsed)
    OmegaAccuracy <-sapply(1:N, function (x) results[[x]]$omega)

    #fussy R data type formatting
    metrics <- cbind(Algorithms,Datasets,ComputationTime,OmegaAccuracy)
    ind <- which(metrics[,"OmegaAccuracy"] != "NULL")
    metrics <-data.frame(metrics[ind,],stringsAsFactors=FALSE)
    metrics <- data.frame(lapply(metrics, unlist),stringsAsFactors=FALSE)
    metrics$ComputationTime <- as.numeric(metrics$ComputationTime)
    # Normalize computation time by dataset
    metrics$ComputationTime <- ave(metrics$ComputationTime, list(metrics$Datasets), FUN=function(L) L/min(L))
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
          geom_point(aes(size=ComputationTime, colour=OmegaAccuracy), alpha=0.75)+
          scale_size_continuous(range =c(8, 25), trans='log')+
          scale_colour_gradient2(midpoint=0.4, low="red",mid="yellow", high="dark green")+
          theme_bw() + 
          theme(text = element_text(size=20))+
          ggtitle('Accuracy and Computation Time across Datasets and Algorithms')

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

# Plot chart comparing runtime to accuracy
plotRunOmega <- function(metrics, toPDF=FALSE) {
	runtimeplot <- ggplot(metrics, aes(x=log10(ComputationTime), y=OmegaAccuracy)) + 
		geom_point(size=0) +
		theme_bw()+
		geom_text(aes(x=log10(ComputationTime), y=OmegaAccuracy, label=Algorithms, color=Datasets), size=4, angle=45) 
	
	
	if (toPDF) {
        pdffile <- paste(Sys.time(),"runtimeVsOmegaAccuracy.png", sep='')
        png(pdffile, height=10, width=12, units='in', res=300)
        print(runtimeplot)
        dev.off()
        cat(sprintf('printed to %s \n', pdffile))
    } else {
        print(runtimeplot)
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

