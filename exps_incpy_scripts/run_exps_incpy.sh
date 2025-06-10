#!/bin/bash

# Capture start time
START_TIME=$(date +%s)
echo "IncPy Experiment Run - Start time: $(date '+%H:%M:%S')"

# Define root path (assuming the script is run from workspace root)
# If this script is in exps_incpy_scripts, ROOT_PATH should be ..
ROOT_PATH="$(pwd)/.."

# Create or clear outputs directory
OUTPUT_DIR_REL="outputs_incpy"
OUTPUT_DIR_ABS="$ROOT_PATH/$OUTPUT_DIR_REL"
OUTPUT_DIR_HERE="outputs_incpy"
mkdir -p "$OUTPUT_DIR_HERE"
# rm -f "$OUTPUT_DIR_HERE"/*.txt
echo "Outputs will be saved in $OUTPUT_DIR_HERE"

PYTHON_CMD="python"

EXPERIMENTS_REL=(
    #"belief_propagation/belief_propagation_incpy.py"
    #"cvar/cvar_incpy.py"
    #"diversity_sims/diversity_sims_incpy.py"
    ###"epr/epr_incpy.py"
    ###"fft/fft_incpy.py"
    ###"gauss_legendre_quadrature/gauss_legendre_quadrature_incpy.py"
    #"heat_distribution_lu/heat_distribution_lu_incpy.py"
    #"look_and_say/look_and_say_incpy.py"
    ###"tiny_gshcgp/tiny_gshcgp_incpy.py"
    "dnacc/basic_spheres/basic_spheres_incpy.py"
    ###"dnacc/walking_colloid/walking_colloid_incpy.py"
)

# Define arguments for each experiment
# These are the 'n' values passed as sys.argv[1]
#ARGS_0=("1000" "5500" "10000" "14500" "19000") # belief_propagation (N for loop) - Matches run_exps.sh
#ARGS_1=("1e6" "5e6" "10e6" "50e6" "100e6") # cvar (number of rewards) - Changed to match run_exps.sh literal strings
#ARGS_0=("1000000" "2000000" "3000000" "4000000" "5000000") # diversity_sims (G value) - Changed to match run_exps.sh literal strings
#ARGS_0=("200" "400" "600" "800" "1000") # epr (n for setting_mode: 1=specific, 2=[:100], 3=[:200], etc.) - Specific to incpy script
#ARGS_0=("2000" "4000" "6000" "8000" "10000") # fft (n for matrix size) - Matches commented section in run_exps.sh
#ARGS_0=("5000" "7000" "9000" "11000" "13000") # gauss_legendre_quadrature (order n) - Matches commented section in run_exps.sh
#ARGS_0=("0.1" "0.05" "0.01" "0.005" "0.001") # heat_distribution_lu (n for dimensionality (n,n)) - Specific to incpy script needs, changed from decimals
#ARGS_1=("45" "46" "47" "48" "49") # look_and_say (N iterations) - Matches commented section in run_exps.sh
#ARGS_0=("12" "13" "14" "15" "16") # tiny_gshcgp (NUMVARS: 1, 3, 5, 7, 9) - Specific to incpy script needs
ARGS_0=("2000000" "5000000" "8000000" "11000000" "13000000") # dnacc_basic_spheres (n for linspace points)
#ARGS_0=("-20" "-50" "-80" "-110" "-140") # dnacc_walking_colloid
# Array of argument array names
#ARG_LIST_NAMES=("ARGS_0" "ARGS_1" "ARGS_2" "ARGS_3" "ARGS_4" "ARGS_5" "ARGS_6" "ARGS_7" "ARGS_8" "ARGS_9" "ARGS_10")
#ARG_LIST_NAMES=("ARGS_0" "ARGS_1")
ARG_LIST_NAMES=("ARGS_0")

NUM_ROUNDS=4
NUM_ARGS_PER_EXP=5 

echo "Starting $NUM_ROUNDS rounds of execution for each experiment and argument..."

SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR" || exit

for round in $(seq 1 $NUM_ROUNDS); do
    echo "--- Round $round ---"
    for exp_idx in "${!EXPERIMENTS_REL[@]}"; do
        PYTHON_SCRIPT_REL="${EXPERIMENTS_REL[exp_idx]}"
        BASE_NAME=$(basename "$PYTHON_SCRIPT_REL" .py) 
        OUTPUT_FILE="$OUTPUT_DIR_HERE/${BASE_NAME}_times.txt"

        CURRENT_ARGS_NAME="${ARG_LIST_NAMES[exp_idx]}"
        eval "CURRENT_ARGS_ARRAY=(\"\${${CURRENT_ARGS_NAME}[@]}\")" 

        echo "  Experiment: $PYTHON_SCRIPT_REL"

        for arg_idx in $(seq 0 $((NUM_ARGS_PER_EXP - 1))); do
            ARG="${CURRENT_ARGS_ARRAY[arg_idx]}"
            echo "    Arg: $ARG (Round $round)"

            if [ ! -f "$PYTHON_SCRIPT_REL" ]; then
                echo "ERROR: Script $PYTHON_SCRIPT_REL not found!"
                continue
            fi
            
            execution_time=$($PYTHON_CMD "$PYTHON_SCRIPT_REL" "$ARG" | tail -n 1)
            
            echo "$execution_time" >> "$OUTPUT_FILE"
            echo "      Execution time: $execution_time"
        done
        echo "  Finished $PYTHON_SCRIPT_REL for Round $round. Results in $OUTPUT_FILE"
    done
    echo "--- Finished Round $round ---"
done

cd "$ROOT_PATH" 

# Capture end time
END_TIME=$(date +%s)
echo "IncPy Experiment Run - End time: $(date '+%H:%M:%S')"

# Calculate execution time
ELAPSED_TIME=$((END_TIME - START_TIME))
HOURS=$(printf "%02d" $((ELAPSED_TIME / 3600)))
MINUTES=$(printf "%02d" $(((ELAPSED_TIME % 3600) / 60)))
SECONDS=$(printf "%02d" $((ELAPSED_TIME % 60)))

if [ $ELAPSED_TIME -lt 60 ]; then
    echo "Total execution time: ${SECONDS} seconds"
elif [ $ELAPSED_TIME -lt 3600 ]; then
    echo "Total execution time: ${MINUTES}:${SECONDS} minutes"
else
    echo "Total execution time: ${HOURS}:${MINUTES}:${SECONDS} hours"
fi

echo "IncPy execution completed. Outputs saved in '$SCRIPT_DIR/$OUTPUT_DIR_HERE' directory." 
