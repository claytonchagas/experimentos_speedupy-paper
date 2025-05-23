#!/bin/bash

# Capture start time
START_TIME=$(date +%s)
echo "Start time: $(date '+%H:%M:%S')"

# Delete old outputs
rm -f *.txt
if [ -d outputs ]; then
    rm -f outputs/*
else
    mkdir -p outputs
fi

# Install requirements
pip install -r speedupy/requirements.txt

#chmod +x dnacc_prepare.sh
#./run_before/dnacc_prepare.sh

chmod +x ./run_before/epr_prepare_functools.sh
./run_before/epr_prepare_functools.sh

#chmod +x heat_prepare.sh
#./run_before/heat_prepare.sh

# Define paths
ROOT_PATH="$(pwd)"

# Define the source directory
#SOURCE_DIR="$ROOT_PATH/speedupy"

# Define the list of destination paths / Define a lista de caminhos de destino
DESTINATIONS_0="$ROOT_PATH/exps_functools/belief_propagation/belief_propagation_functools.py"
DESTINATIONS_1="$ROOT_PATH/exps_functools/cvar/cvar_functools.py"
DESTINATIONS_2="$ROOT_PATH/exps_functools/diversity_sims/vince_sim_functools.py"
#DESTINATIONS_3="$ROOT_PATH/exps_functools/dnacc/basic_spheres/basic_spheres_functools.py" 
#DESTINATIONS_4="$ROOT_PATH/exps_functools/dnacc/walking_colloid/walking_colloid_functools.py"
DESTINATIONS_3="$ROOT_PATH/exps_functools/epr/epr_analyse_functools.py"
DESTINATIONS_4="$ROOT_PATH/exps_functools/fft/fft_functools.py"  
DESTINATIONS_5="$ROOT_PATH/exps_functools/gauss_legendre_quadrature/gauss_legendre_quadrature_functools.py" 
#DESTINATIONS_8="$ROOT_PATH/exps_functools/heat_distribution_lu/heat_distribution_lu_functools.py"
DESTINATIONS_6="$ROOT_PATH/exps_functools/look_and_say/look_and_say_functools.py"
DESTINATIONS_7="$ROOT_PATH/exps_functools/tiny/TINY_GSHCGP_functools.py" 


#DESTINATIONS=($DESTINATIONS_0)
#DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1)
#DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1 $DESTINATIONS_2)
DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1 $DESTINATIONS_2 $DESTINATIONS_3 $DESTINATIONS_4 $DESTINATIONS_5 $DESTINATIONS_6 $DESTINATIONS_7)

#DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1 $DESTINATIONS_2 $DESTINATIONS_3 $DESTINATIONS_4 $DESTINATIONS_5 $DESTINATIONS_6 $DESTINATIONS_7 $DESTINATIONS_8 $DESTINATIONS_9 $DESTINATIONS_10)


# Define arguments
ARGUMENTS_0=("1000" "5500" "10000" "14500" "19000") # belief_propagation
ARGUMENTS_1=("1e6" "5e6" "10e6" "50e6" "100e6") # cvar
ARGUMENTS_2=("1000000" "2000000" "3000000" "4000000" "5000000") # diversity_sim

#ARGUMENTS_0=("2000000" "5000000" "8000000" "11000000" "13000000") # dnacc_basic_spheres
#ARGUMENTS_1=("-20" "-50" "-80" "-110" "-140") # dnacc_walking_colloid
ARGUMENTS_3=("200" "400" "600" "800" "1000") # epr_analyse

ARGUMENTS_4=("2000" "4000" "6000" "8000" "10000") # fft
ARGUMENTS_5=("5000" "7000" "9000" "11000" "13000") # gauss_legendre_quadrature
#ARGUMENTS_2=("0.1" "0.05" "0.01" "0.005" "0.001") # heat_distribution_lu

ARGUMENTS_6=("45" "46" "47" "48" "49") # look_and_say
ARGUMENTS_7=("12" "13" "14" "15" "16") # TINY_GSHCGP


# Copy speedupy to each destination
#for i in "${!DESTINATIONS[@]}"; do
#    DEST="${DESTINATIONS[i]}"
#    DEST_DIR=$(dirname "$DEST")  # Extract the directory path from the destination path
#    if [ ! -d "$DEST_DIR/speedupy" ]; then # speedupy não está no diretório
#        cp -r "$SOURCE_DIR" "$DEST_DIR"
#        echo "Copied $SOURCE_DIR to $DEST_DIR"
#    fi
#done

# Define output files
declare -A OUTPUT_FILES
for i in "${!DESTINATIONS[@]}"; do
    PYTHON_FILE="${DESTINATIONS[i]}"
    BASE_NAME=$(basename $PYTHON_FILE | cut -d. -f1)
    OUTPUT_FILES["${i}_cache_functools"]="$ROOT_PATH/outputs/${BASE_NAME}_output_cache_functools.txt"
done

################################
# Execução com cache functools #
################################
echo "============================"
echo "Execução com cache functools"
echo "============================"
    
# Para cada um dos 5 argumentos
for arg_index in {0..4}; do
    echo "Argumento índice $arg_index"
        
    # Para cada um dos experimentos
    for exp_index in "${!DESTINATIONS[@]}"; do
        DEST="${DESTINATIONS[exp_index]}"
        DEST_DIR=$(dirname "$DEST")
        PYTHON_FILE="$DEST"
            
        # Obtém o argumento correto para este experimento
        ARGUMENTS_VAR="ARGUMENTS_${exp_index}[$arg_index]"
        ARG=${!ARGUMENTS_VAR}
            
        cd "$DEST_DIR"
        echo "Executando $PYTHON_FILE com argumento $ARG"
            
        # Executa o script Python com o argumento no modo 'manual'
        python3.12 $PYTHON_FILE $(echo "$ARG") 4 >> ${OUTPUT_FILES["${exp_index}_cache_functools"]}
            
        cd "$ROOT_PATH"
    done
done

###############
# Finalização #
###############

# Capture end time
END_TIME=$(date +%s)
echo "End time: $(date '+%H:%M:%S')"

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

echo "Execution completed. Outputs saved in 'outputs' directory."
