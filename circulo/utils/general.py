from scipy.stats import describe
from scipy import median

def aggregate(array, prefix="",axis=0):

    stats = describe(array, axis)

    return  {
        prefix+' Size':int(stats[0]),
        prefix+' Min':float(stats[1][0]),
        prefix+' Max':float(stats[1][1]),
        prefix+' Mean':float(stats[2]),
        prefix+' Unbiased Variance':float(stats[3]),
        prefix+' Biased Skewness':float(stats[4]),
        prefix+' Biased Kurtosis':float(stats[5]),
        prefix+' Median':float(median(array,axis))
            }
