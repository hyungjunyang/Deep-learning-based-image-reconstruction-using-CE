#!/bin/bash
#SBATCH --job-name case1_true
#SBATCH --partition=suprib
#SBATCH --mem-per-cpu=1GB
#SBATCH --time=50:00:00
#SBATCH --error=/data/cees/hjyang3/PnP/test.err
#SBATCH --output=/data/cees/hjyang3/PnP/test.out
#
# Job steps:
cd $SLURM_SUBMIT_DIR
#
/data/cees/hjyang3/anaconda3/envs/fenicsproject/bin/python True_Case1.py
# end script