import json
import circulo
import circulo.metrics
import numpy
import argparse
import os
import scipy
import csv

def omega_loop(path, output_filename):
    i = 0 
    j = 0
    k = 0
    df_dimension = 0
    total_omega_fs = 0
    omega_fs = 0

    files = sorted(os.listdir(path[0]))
    
    for filename in files:
        df_dimension = df_dimension + 1
    omega_df = numpy.ones(shape = [df_dimension, df_dimension])*-1
    #omega_list = numpy.empty(shape = [df_dimension*df_dimension+df_dimension, 3], dtype='S100')
    omega_list = []
    
    
    for f in files:
        print(f)
        json_data_f = open(path[0]+'/'+f)
        data_f = json.load(json_data_f)
        for s in files:
           json_data_s = open(path[0]+'/'+s)
           data_s = json.load(json_data_s)
           omega_fs = circulo.metrics.omega.omega_index(data_f['membership'], data_s['membership'])
           omega_list.append([f, s, omega_fs])
           omega_df[i, j] = omega_fs
           if f != s:
               total_omega_fs = total_omega_fs + omega_fs
           j = j + 1
        omega_list.append([f, 'Adjusted_Average', total_omega_fs/(df_dimension-1)])
        total_omega_fs = 0
        i = i + 1
        j = 0
    print(omega_df)
    numpy.save(output_filename[0], omega_df)
    
    with open(output_filename[0],'w') as myfile:
        csvwriter = csv.writer(myfile,delimiter='\t')
        csvwriter.writerow(['Graph1','Graph2','omega'])
        for x in omega_list:
            csvwriter.writerow(x)

    if omega_df.min() == 1:
        print('All files give identical results')
    else:
        print('Differences exist among the files')

def main():
    # Parse user input
    parser = argparse.ArgumentParser(description='Run metrics across several algorithms or across iterations of a stochastic algorithm.')
    parser.add_argument('path', nargs=1,help='Filepath location')
    parser.add_argument('output_filename', nargs=1, help='Output filename')
    args = parser.parse_args()
    omega_loop(args.path, args.output_filename)

if __name__ == '__main__':
    main()
