#!/bin/bash

# Capture start time / Captura a hora de início
START_TIME=$(date +%s)
echo "Start time: $(date '+%H:%M:%S')"

# Delete the old outputs / Deleta as saídas antigas
rm *.txt
if [ -d outputs ]; then
    rm outputs/*
else
    mkdir outputs
fi

# Pre-configurations to run the Framework | Configurações prévias para executar o Framework
pip install -r speedupy/requirements.txt

chmod +x dnacc_prepare.sh
./dnacc_prepare.sh

chmod +x epr_prepare.sh
./epr_prepare.sh

chmod +x qho2_prepare.sh
./qho2_prepare.sh

chmod +x heat_prepare.sh
./heat_prepare.sh

# Define the common root path / Define o caminho raiz comum
ROOT_PATH="$(pwd)"

# Define the source directory
SOURCE_DIR="$ROOT_PATH/speedupy"

# Define the list of destination paths / Define a lista de caminhos de destino

DESTINATIONS_0="$ROOT_PATH/speedupy_experiments/01pilots/01pilots_exp03_quicksort/quicksort.py" 
DESTINATIONS_1="$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp02_look_and_say/look_and_say.py" 
DESTINATIONS_2="$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp11_gauss_legendre_quadrature/gauss_legendre_quadrature.py" 
DESTINATIONS_3="$ROOT_PATH/speedupy_experiments/01pilots/01pilots_exp04_heat_distribution_lu/heat_distribution_lu.py" 
DESTINATIONS_4="$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp08_fft/fft_speedupy.py" 
DESTINATIONS_5="$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp14_pernicious_numbers/pernicious_numbers.py" 
DESTINATIONS_6="$ROOT_PATH/speedupy_experiments/05msrgithubexps/05msrgithubexps_exp02_cvar/cvar_speedupy.py" 
DESTINATIONS_7="$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp06_belief_propagation/belief_propagation_speedupy.py" 
DESTINATIONS_8="$ROOT_PATH/DNACC-with-speedupy/adapted_for_speedupy/examples/basic/basic_spheres.py" 
DESTINATIONS_9="$ROOT_PATH/DNACC-with-speedupy/adapted_for_speedupy/examples/walking_colloid/walking_colloid.py" 
DESTINATIONS_10="$ROOT_PATH/diversity-with-speedupy/Diversity_sims/vince_sim_speedupy.py" 
DESTINATIONS_11="$ROOT_PATH/Tiny-GSGP-with-speedupy/adapted_for_speedupy/TINY_GSHCGP.py" 
DESTINATIONS_12="$ROOT_PATH/epr-with-speedupy/analyse_speedupy.py"
# DESTINATIONS_13="$ROOT_PATH/speedupy_experiments/05msrgithubexps/05msrgithubexps_exp04_curves/curves_speedupy.py"
# DESTINATIONS_14="$ROOT_PATH/qho-with-speedupy/qho2_speedupy.py"

DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1 $DESTINATIONS_2 $DESTINATIONS_3 $DESTINATIONS_4 $DESTINATIONS_5 $DESTINATIONS_6 $DESTINATIONS_7 $DESTINATIONS_8 $DESTINATIONS_9 $DESTINATIONS_10 $DESTINATIONS_11 $DESTINATIONS_12)

# Define the list of arguments for each destination path / Define a lista de argumentos para cada caminho de destino
ARGUMENTS_0=("1e1") # "1e2" "1e3" "1e4" "1e5") # quicksort
ARGUMENTS_1=("25") # "30" "35" "40" "45") # look_and_say
ARGUMENTS_2=("1000") # "2000" "3000" "4000" "5000") # gauss_legendre_quadrature
ARGUMENTS_3=("0.1") # "0.05" "0.01" "0.005" "0.001") # heat_distribution_lu
ARGUMENTS_4=("1000") # "2000" "3000" "4000" "5000") # fft
ARGUMENTS_5=("20000") # "25000" "30000" "35000" "39000") # pernicious_numbers
ARGUMENTS_6=("1e6") # "5e6" "10e6" "50e6" "100e6") # cvar
ARGUMENTS_7=("1000") # "2000" "3000" "4000" "5000") # belief_propagation
ARGUMENTS_8=("40") # "1000" "10000" "100000" "1000000") # dnacc_basic_spheres
ARGUMENTS_9=("-10") # "-20" "-30" "-40" "-50") # dnacc_walking_colloid
ARGUMENTS_10=("1000000") # "2000000" "3000000" "4000000" "5000000") # vince_sim
ARGUMENTS_11=("1") # "3" "5" "7" "9") # TINY_GSHCGP
ARGUMENTS_12=("100") # "200" "300" "400" "500") # analyse_epr
# ARGUMENTS_13=("1576862 -8567453 1648423 542312 512 -20135 1455678 52349" "4341212 -12312419 123123 5423672 107 20135 145678 52349" "-11124 -11124 62412 1412 107501 201635 15678 57849" "43441212 -22523123 6219 5143228 107501 20135 1455678 5234567849" "-111243412 -124122123 62192412 5281412 107501 201422635 123455678 5234567849")
# curves
# ARGUMENTS_14=("100" "500" "1000" "5000" "10000") # qho2

# Copy the source directory to each destination directory / Copia o diretório de origem para cada diretório de destino
for i in "${!DESTINATIONS[@]}"; do
    DEST="${DESTINATIONS[i]}"
    DEST_DIR=$(dirname "$DEST")  # Extract the directory path from the destination path
    if [ ! -d "$DEST_DIR/speedupy" ]; then # speedupy não está no diretório
        cp -r "$SOURCE_DIR" "$DEST_DIR"
        echo "Copied $SOURCE_DIR to $DEST_DIR"
    fi
done

# Modo 1 - apaga o .speedupy entre cada argumento e executa sem cache
for i in "${!DESTINATIONS[@]}"; do
    DEST="${DESTINATIONS[i]}"
    DEST_DIR=$(dirname "$DEST")
    
    # Define the Python file to be executed
    PYTHON_FILE="$DEST"
    
    # Define the arguments for the current destination
    ARGUMENTS_VAR="ARGUMENTS_$i[@]"
    ARGUMENTS=("${!ARGUMENTS_VAR}")
    
    # Define the output file name based on the Python file name
    OUTPUT_FILE_NO_CACHE=$ROOT_PATH/outputs/$(basename $PYTHON_FILE | cut -d. -f1)_output_no_cache.txt
    # OUTPUT_FILE_MANUAL="$ROOT_PATH/intra_args_$(basename "${PYTHON_FILE}_output_manual.txt")"
    OUTPUT_FILE_MANUAL="$ROOT_PATH/outputs/$(basename $PYTHON_FILE | cut -d. -f1)_output_spdpy_intra_args.txt"

    cd "$DEST_DIR"
    echo "Running $PYTHON_FILE with different arguments..."

    # Run the script with each argument
    for ARG in "${ARGUMENTS[@]}"; do
    
        #Run setup.py before executing the Python script
        echo "Running setup.py for $PYTHON_FILE..."
        # python3.12 "$ROOT_PATH/speedupy/setup_exp/setup.py" "$PYTHON_FILE"
        python3.12 "speedupy/setup_exp/setup.py" "$PYTHON_FILE"
        echo "-Execution mode: no-cache with $ARG"

        # Execute the Python script with the argument in 'no-cache' mode
        for j in {1..2}; do
            python3.12 $PYTHON_FILE $ARG --exec-mode no-cache | tail -n 1 | cut -d':' -f2 >> $OUTPUT_FILE_NO_CACHE
        done
        
        echo "-Execution mode: manual with $ARG"
        
        # Execute the Python script with the argument in 'manual' mode
        for j in {1..2}; do
            python3.12 $PYTHON_FILE $ARG --exec-mode manual | tail -n 1 | cut -d':' -f2 >> $OUTPUT_FILE_MANUAL
        done        
       # Delete the .speedupy folder after each argument / Deleta a pasta .speedupy após cada argumento
		rm -rf "$DEST_DIR/.speedupy/"
    done    
done

cd $ROOT_PATH

# Modo 2 - apaga o .speedupy entre cada execução
for i in "${!DESTINATIONS[@]}"; do
    DEST="${DESTINATIONS[i]}"
    DEST_DIR=$(dirname "$DEST")
    
    # Define the Python file to be executed
    PYTHON_FILE="$DEST"

    # Define the arguments for the current destination
    ARGUMENTS_VAR="ARGUMENTS_$i[@]"
    ARGUMENTS=("${!ARGUMENTS_VAR}")
    
    # Define the output file name based on the Python file name    
    # OUTPUT_FILE_MANUAL="$ROOT_PATH/intra_exec_only_$(basename "${PYTHON_FILE}_output_manual.txt")"
    OUTPUT_FILE_MANUAL="$ROOT_PATH/outputs/$(basename $PYTHON_FILE | cut -d. -f1)_output_spdpy_intra_exec.txt"

    cd "$DEST_DIR"
    echo "Running $PYTHON_FILE with different arguments..."

    # Run the script with each argument
    for ARG in "${ARGUMENTS[@]}"; do
    
        #Run setup.py before executing the Python script
        echo "Running setup.py for $PYTHON_FILE..."
        # python3.12 "$ROOT_PATH/speedupy/setup_exp/setup.py" "$PYTHON_FILE"
        echo "-Execution mode: manual"
        
        # Execute the Python script with the argument in 'manual' mode
        for j in {1..2}; do
            python3.12 "speedupy/setup_exp/setup.py" "$PYTHON_FILE"        
            python3.12 $PYTHON_FILE $ARG --exec-mode manual | tail -n 1 | cut -d':' -f2 >> $OUTPUT_FILE_MANUAL
            # Delete the .speedupy folder after each execution / Deleta a pasta .speedupy após cada execução
            rm -rf "$DEST_DIR/.speedupy/"
        done        
       		
    done    
done

cd $ROOT_PATH

# Modo 3 - apaga o .speedupy ao final de todos os argumentos
for i in "${!DESTINATIONS[@]}"; do
    DEST="${DESTINATIONS[i]}"
    DEST_DIR=$(dirname "$DEST")
    
    # Define the Python file to be executed
    PYTHON_FILE="$DEST"

    # Define the arguments for the current destination
    ARGUMENTS_VAR="ARGUMENTS_$i[@]"
    ARGUMENTS=("${!ARGUMENTS_VAR}")
    
    # Define the output file name based on the Python file name    
    # OUTPUT_FILE_MANUAL="$ROOT_PATH/$(basename "intra_experiment_${PYTHON_FILE}_output_manual.txt")"
    OUTPUT_FILE_MANUAL="$ROOT_PATH/outputs/$(basename $PYTHON_FILE | cut -d. -f1)_output_spdpy_intra_exp.txt"

    cd "$DEST_DIR"
    echo "Running $PYTHON_FILE with different arguments..."
    
    #Run setup.py before executing the Python script
    echo "Running setup.py for $PYTHON_FILE..."
    # python3.12 "$ROOT_PATH/speedupy/setup_exp/setup.py" "$PYTHON_FILE"
    python3.12 "speedupy/setup_exp/setup.py" "$PYTHON_FILE"
    echo "-Execution mode: manual"

    # Run the script with each argument
    for ARG in "${ARGUMENTS[@]}"; do    
        # Execute the Python script with the argument in 'manual' mode
        for j in {1..2}; do
            python3.12 $PYTHON_FILE $ARG --exec-mode manual | tail -n 1 | cut -d':' -f2 >> $OUTPUT_FILE_MANUAL
        done        
    done
    # Deleta os diretórios do speedupy copiados previamente
    rm -rf "$DEST_DIR/.speedupy/" "$DEST_DIR/speedupy/"
done

# Capture end time / Captura a hora de término
END_TIME=$(date +%s)
echo "End time: $(date '+%H:%M:%S')"

# Calculate and format execution time / Calcula e formata o tempo de execução
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

echo "Execution completed. Outputs saved."
