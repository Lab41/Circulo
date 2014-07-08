#!/usr/local/bin/python

import csv
import re
import sys
import os
import glob
import networkx as nx

def main(argv):

    team_dict = {}
    
    out = open("test.txt", "w")
    
    for filename in glob.glob('*.csv'):

        data = open(filename,"rb")
        reader = csv.reader(data)
    
        parse = re.sub('.csv',"",filename)
        parse = re.sub('_',"-",parse)
        
        next(reader,None)

        for row in reader:
            if( ((parse,convert(row[2])) or (convert(row[2]),parse)) in team_dict):
                team_dict[parse,convert(row[2])] += 1
            else:    
                team_dict[parse,convert(row[2])] = 1
    
        data.close()

    for key,value in team_dict.iteritems():
        out.write(str(key[0]) + ' ' + str(key[1]) + ' ' + str(value) + '\n')
    
    out.close()
    data.close()

def convert(string):
    string = string.lower()
    string = re.sub('_',"-", string)
    string = re.sub(' ',"-", string)
    return string

if __name__ == "__main__":
    main(sys.argv[1:])
