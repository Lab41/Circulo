# Sample Usage:
#   metrics <- getMetrics(datapath)
#   plotMetrics(metrics)
#   plotHist(metrics,'omega')
#   plotHist(metrics,'time')

library(ggplot2)
library(jsonlite)

# Read metrics from json
getMetrics <- function(datapath) {

    #Get file names and load the json files
    filenames <- list.files(datapath, pattern="*.json", full.names=TRUE)
    N <- length(filenames)
    results <- lapply(filenames, fromJSON)

    #parse filenames to get algorithm names and dataset names
    names <- basename(filenames)
    names2 <- sapply(1:N, function(x) strsplit(names, "\\.")[[x]][1])
    Datasets <- sapply(1:N, function(x) strsplit(names2, "--")[[x]][1])
    Algorithms <-sapply(1:N, function(x) strsplit(names2, "--")[[x]][2])

    #fussy R data type formatting
    metrics <- data.frame(Algorithms,Datasets)
    
    metric.names <- names(results[[1]]$metrics)
    df <- data.frame(sapply(metric.names,function(l){
        sapply(1:N,function(i) {results[[i]]$metrics[[l]]['results']        }) }))
   
    metrics <- cbind(metrics,df)
    
   return(metrics)
}

# Plot one metric across a collection of datasets/algorithms
plotMetric<- function(metrics,column='Conductance',datasets=NULL,algos=NULL,logx=FALSE,logy=FALSE,toPDF=FALSE) {
    # Keep only data that matches datasets/algos criteria
    data <- metrics
    if (is.null(datasets)) {datasets <- unique(metrics$Datasets)}
    if (is.null(algos)) {algos <- unique(metrics$Algorithms)}

    keep <- (data$Datasets %in% datasets) & (data$Algorithms %in% algos)
    data <- data[keep,]

    # Reformat data columns into "long" format
    Algorithms <- rep(data$Algorithms,sapply(data$Conductance,length))
    Datasets <- rep(data$Datasets,sapply(data$Conductance,length))
    value <- unlist(data[column])
    data <- data.frame(Algorithms,Datasets,value)

    # Create density plot 
    densityplot<- ggplot(data, aes(x=value,colour=Algorithms,fill=Algorithms))+
                        facet_grid(. ~ Datasets) +
                        geom_density(alpha=0.5) + 
                        #geom_histogram(alpha=0.5,position='identity') + 
                        xlab(column) + 
                        ylab('Counts') + 
                        theme_bw()+
                        ggtitle(Sys.time())

    if (logx) {densityplot <- densityplot + scale_x_log10()}
    if (logy) {densityplot <- densityplot + scale_y_log10()}

    # Print plot to PDF or screen
    if (toPDF) {
        pdffile <- paste(Sys.time(),"metricsGraph.pdf", sep='')
        pdf(pdffile,height=10,width=12)
        print(densityplot)
        dev.off()
        cat(sprintf('printed to %s \n', pdffile))
    } else {
        print(densityplot)
    }
}

# Plot specified metrics for one run (dataset/algorithm)
## NEEDS TO BE FINISHED.
plotRun <- function(metrics,dataset='karate',algo='fastgreedy',columns=c('Conductance','Expansion'),logx=FALSE,logy=FALSE,toPDF=FALSE) {
    # Keep only data that matches datasets/algos criteria
    data <- metrics
    keep <- (data$Datasets == dataset) & (data$Algorithms == algo)
    data <- data[keep,]

    # Reformat data columns into "long" format
    df <- sapply(data[,columns],unlist)
    df <- data.frame(df,row.names=NULL)
    # not done yet..
}
