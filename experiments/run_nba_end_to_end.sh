#/usr/bin/env

python3 ./run_algos.py nba_schedule conga
python3 ./run_algos.py nba_schedule congo
python3 ./run_algos.py nba_schedule edge_betweenness
python3 ./run_algos.py nba_schedule fastgreedy
python3 ./run_algos.py nba_schedule groundtruth
python3 ./run_algos.py nba_schedule infomap
python3 ./run_algos.py nba_schedule label_propagation
python3 ./run_algos.py nba_schedule leading_eigenvector
python3 ./run_algos.py nba_schedule multilevel
python3 ./run_algos.py nba_schedule radicchi_strong
python3 ./run_algos.py nba_schedule radicchi_wak
python3 ./run_algos.py nba_schedule radicchi_weak
python3 ./run_algos.py nba_schedule spinglass
python3 ./run_algos.py nba_schedule walktrap

#Aggregate Stochastic Algorithms, [deterministic ones are left unchanged]
find . -name 'nba_schedule-*' -exec python3 ./run_dist_mat.py {} \;
find . -name 'nba_schedule-*' -exec python3 ./run_pick_reps.py {} \;

# Put all the representatives in one pickle file.
python3 ./run_aggregate.py nba_schedule

# Compute the overall distance matrix
python3 ./run_dist_mat.py nba_schedule.pickle 

# Pick final reps
python3 ./run_pick_reps.py nba_schedule.pickle 
python3 ./run_metrics.py nba_schedule.pickle 


