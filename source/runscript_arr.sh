#!/bin/bash
#SBATCH -J sa_arr               # A single job name for the array
#SBATCH -n 1                    # Number of cores
#SBATCH -N 1                    # Ensure that all cores are on one machine
#SBATCH -t 1-00:00              # Runtime in D-HH:MM
#SBATCH -p general              # Partition to submit to
#SBATCH --mem=1000               # Memory pool for all cores (see also --mem-per-cpu) MAYBE CHANGE THIS
#SBATCH -o std_%A_%a.out        # File to which STDOUT will be written
#SBATCH -e std_%A_%a.err        # File to which STDERR will be written
#SBATCH --mail-type=ALL         # Type of email notification- BEGIN,END,FAIL,ALL
#SBATCH --mail-user=christianjunge@g.harvard.edu
python experiment_arr.py files/in_"${SLURM_ARRAY_TASK_ID}".txt \
results/out_"${SLURM_ARRAY_TASK_ID}".txt \
results/bestmarket_"${SLURM_ARRAY_TASK_ID}".txt \
results/outstates_"${SLURM_ARRAY_TASK_ID}".txt \
results/error_"${SLURM_ARRAY_TASK_ID}".txt
