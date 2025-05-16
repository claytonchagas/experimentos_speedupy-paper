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

# # Install requirements
# pip install -r speedupy/requirements.txt
chmod +x run_before/dnacc_prepare.sh
./run_before/dnacc_prepare.sh

# chmod +x run_before/epr_prepare.sh
# ./run_before/epr_prepare.sh

chmod +x run_before/heat_prepare.sh
./run_before/heat_prepare.sh

# Define paths
ROOT_PATH="$(pwd)"

# Define the source directory
SOURCE_DIR="$ROOT_PATH/speedupy"


# Define the list of destination paths / Define a lista de caminhos de destino
# DESTINATIONS_0="$ROOT_PATH/exps/belief_propagation/belief_propagation.py"
# DESTINATIONS_1="$ROOT_PATH/exps/cvar/cvar.py"
# DESTINATIONS_2="$ROOT_PATH/exps/diversity_sims/vince_sim.py"

# DESTINATIONS_3="$ROOT_PATH/exps/dnacc/basic_spheres/basic_spheres.py" 
# DESTINATIONS_4="$ROOT_PATH/exps/dnacc/walking_colloid/walking_colloid.py"
# DESTINATIONS_5="$ROOT_PATH/exps/epr/epr_analyse.py"
 
DESTINATIONS_6="$ROOT_PATH/exps/fft/fft.py"  
DESTINATIONS_7="$ROOT_PATH/exps/gauss_legendre_quadrature/gauss_legendre_quadrature.py" 
# DESTINATIONS_8="$ROOT_PATH/exps/heat_distribution_lu/heat_distribution_lu.py"
 
# DESTINATIONS_9="$ROOT_PATH/exps/look_and_say/look_and_say.py"
# DESTINATIONS_10="$ROOT_PATH/exps/tiny/TINY_GSHCGP.py" 


# DESTINATIONS=($DESTINATIONS_0)
#DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1)
# DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1 $DESTINATIONS_2)
#DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1 $DESTINATIONS_2 $DESTINATIONS_3)

DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1 $DESTINATIONS_2 $DESTINATIONS_3 $DESTINATIONS_4 $DESTINATIONS_5 $DESTINATIONS_6 $DESTINATIONS_7 $DESTINATIONS_8 $DESTINATIONS_9 $DESTINATIONS_10)


# Define arguments
# ARGUMENTS_0=("5500" "14500") # belief_propagation
# ARGUMENTS_1=("5e6" "50e6") # cvar
# ARGUMENTS_2=("2000000" "4000000") # diversity_sim

# ARGUMENTS_3=("5000000" "11000000") # dnacc_basic_spheres
# ARGUMENTS_4=("-50" "-110") # dnacc_walking_colloid
# ARGUMENTS_5=("400" "800") # epr_analyse

ARGUMENTS_0=("4000" "6000") # fft
ARGUMENTS_1=("7000" "11000") # gauss_legendre_quadrature
# ARGUMENTS_1=("0.05" "0.005") # heat_distribution_lu

# ARGUMENTS_9=("46" "48") # look_and_say
# ARGUMENTS_10=("13" "15") # TINY_GSHCGP


# Copy speedupy to each destination
for i in "${!DESTINATIONS[@]}"; do
    DEST="${DESTINATIONS[i]}"
    DEST_DIR=$(dirname "$DEST")  # Extract the directory path from the destination path
    if [ ! -d "$DEST_DIR/speedupy" ]; then # speedupy não está no diretório
        cp -r "$SOURCE_DIR" "$DEST_DIR"
        echo "Copied $SOURCE_DIR to $DEST_DIR"
    fi
done

# Execution
for exp_index in "${!DESTINATIONS[@]}"; do
    
    for arg_index in {0..1}; do    
        # Para cada um dos experimentos
        DEST="${DESTINATIONS[exp_index]}"
        DEST_DIR=$(dirname "$DEST")
        PYTHON_FILE="$DEST"
        
        # Obtém o argumento correto para este experimento
        ARGUMENTS_VAR="ARGUMENTS_${exp_index}[$arg_index]"
        ARG=${!ARGUMENTS_VAR}
        
        cd "$DEST_DIR"
        python3.12 speedupy/setup_exp/setup.py $PYTHON_FILE
        echo "Executando $(basename $PYTHON_FILE) com argumento $ARG"
        
        # Executa o script Python com o argumento no modo 'no-cache'
        echo "Modo no-cache"
        python3.12 $(basename $PYTHON_FILE) $(echo "$ARG") --exec-mode no-cache| tail -n 1 | cut -d':' -f2 >> "$ROOT_PATH/outputs/$(basename $PYTHON_FILE | sed 's/\.[^.]*$//')_no_cache.txt"
        echo "Modo manual"
        python3.12 $(basename $PYTHON_FILE) $(echo "$ARG") --exec-mode manual -s file
        python3.12 $(basename $PYTHON_FILE) $(echo "$ARG") --exec-mode manual -s file | tail -n 1 | cut -d':' -f2 >> "$ROOT_PATH/outputs/$(basename $PYTHON_FILE | sed 's/\.[^.]*$//')_cache.txt"
        echo "Modo multiprocess"
        python3.12 $(basename $PYTHON_FILE) $(echo "$ARG") --exec-mode multiprocess -s file| tail -n 3 >> "$ROOT_PATH/outputs/$(basename $PYTHON_FILE | sed 's/\.[^.]*$//')_multiprocess.txt"
        echo "Fim da rodada"        
        cd "$ROOT_PATH"
        
    done
done

# Remove speedupy copies
for i in "${!DESTINATIONS[@]}"; do
    DEST="${DESTINATIONS[i]}"
    DEST_DIR=$(dirname "$DEST")
    rm -rf "$DEST_DIR/speedupy/" rm -rf "$DEST_DIR/.speedupy/"
done

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
python3.12 gen_graphs/gen_graphs_multiprocess.py
echo "Tabela salva"


echo "Execution completed. Outputs saved in 'outputs' directory."
