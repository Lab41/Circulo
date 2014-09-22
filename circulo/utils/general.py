from scipy.stats import describe
from scipy import median

def aggregate(array, axis=0):

    stats = describe(array, axis)
    stats = stats + (median(array, axis),)

    return dict(zip(['Size', '(min,max)', 'Arithmetic Mean', 'Unbiased Variance', 'Biased Skewness', 'Biased Kurtosis', 'Median'], stats))
