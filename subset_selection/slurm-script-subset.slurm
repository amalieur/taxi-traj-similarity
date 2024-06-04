#!/bin/sh
#SBATCH --account=ie-idi
#SBATCH --job-name=subset-selection-1000
#SBATCH --time=0-5:00:00

#SBATCH --partition=CPUQ
#SBATCH --mem=128G
#SBATCH --nodes=32
#SBATCH --output=output1.txt
#SBATCH --error=output1.err

#SBATCH --mail-user=amalieur@stud.ntnu.no
#SBATCH --mail-type=ALL

WORKDIR=${SLURM_SUBMIT_DIR}
cd ${WORKDIR}
echo "Running from this directory: $SLURM_SUBMIT_DIR"
echo "Name of job: $SLURM_JOB_NAME"
echo "ID of job: $SLURM_JOB_ID"
echo "The job was run on these nodes: $SLURM_JOB_NODELIST"

module purge

module load Anaconda/2020.07
jupyter nbconvert --to script subset_selection/dataset_subset.ipynb --output dataset_subset.py
python dataset_subset.py