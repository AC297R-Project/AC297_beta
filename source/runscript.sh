#!/bin/bash
#SBATCH -n 1                    # Number of cores
#SBATCH -N 1                    # Ensure that all cores are on one machine
#SBATCH -t 1-00:00              # Runtime in D-HH:MM
#SBATCH -p serial_requeue       # Partition to submit to
#SBATCH --mem=400               # Memory pool for all cores (see also --mem-per-cpu) MAYBE CHANGE THIS
#SBATCH -o std_%j.out      # File to which STDOUT will be written
#SBATCH -e std_%j.err      # File to which STDERR will be written
#SBATCH --mail-type=ALL        # Type of email notification- BEGIN,END,FAIL,ALL
#SBATCH --mail-user=jonathanfriedman@g.harvard.edu # Email to which notifications will be sent
 
python experiment.py in.txt out.txt bestmarket.txt outstates.txt