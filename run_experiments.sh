#!/bin/bash

# Capture start time / Captura a hora de início
START_TIME=$(date +%s)
echo "Start time: $(date '+%H:%M:%S')"

# Apaga os outputs antigos, se existirem
rm outputs/*
#source speedupy_experiments_venv/bin/activate

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

DESTINATIONS=("$ROOT_PATH/speedupy_experiments/01pilots/01pilots_exp03_quicksort/quicksort.py" "$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp02_look_and_say/look_and_say.py" "$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp11_gauss_legendre_quadrature/test_gauss_legendre_quadrature.py" "$ROOT_PATH/speedupy_experiments/01pilots/01pilots_exp04_heat_distribution_lu/__main__.py" "$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp08_fft/test_compute_FFT_speedupy.py" "$ROOT_PATH/speedupy_experiments/05msrgithubexps/05msrgithubexps_exp04_curves/curves_speedupy.py" "$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp14_pernicious_numbers/test_pernicious_numbers.py" "$ROOT_PATH/speedupy_experiments/05msrgithubexps/05msrgithubexps_exp02_cvar/cvar_speedupy.py" "$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp06_belief_propagation/test_belief_propagation_speedupy.py" "$ROOT_PATH/DNACC-with-speedupy/adapted_for_speedupy/examples/basic/basic_spheres.py" "$ROOT_PATH/DNACC-with-speedupy/adapted_for_speedupy/examples/walking_colloid/walking_colloid.py" "$ROOT_PATH/diversity-with-speedupy/Diversity_sims/vince_sim_speedupy.py" "$ROOT_PATH/Tiny-GSGP-with-speedupy/adapted_for_speedupy/TINY_GSHCGP.py" "$ROOT_PATH/epr-with-speedupy/analyse_speedupy.py" "$ROOT_PATH/qho-with-speedupy/qho2_speedupy.py")

# Define the list of arguments for each destination path / Define a lista de argumentos para cada caminho de destino
# ARGUMENTS_0=("1e1")
ARGUMENTS_0=("1e1" "1e2" "1e3" "1e4" "1e5") # quicksort
ARGUMENTS_1=("25" "30" "35" "40" "45") # look_and_say
ARGUMENTS_2=("1000" "2000" "3000" "4000" "5000") # gauss_legendre_quadrature
ARGUMENTS_3=("0.1" "0.05" "0.01" "0.005" "0.001") # heat
ARGUMENTS_4=("1000" "2000" "3000" "4000" "5000")
ARGUMENTS_5=("1576862 -8567453 1648423 542312 512 -20135 1455678 52349" "4341212 -12312419 123123 5423672 107 20135 145678 52349" "-11124 -11124 62412 1412 107501 201635 15678 57849" "43441212 -22523123 6219 5143228 107501 20135 1455678 5234567849" "-111243412 -124122123 62192412 5281412 107501 201422635 123455678 5234567849")
ARGUMENTS_6=("20000" "25000" "30000" "35000" "39000")
ARGUMENTS_7=("1e6" "5e6" "10e6" "50e6" "100e6")
ARGUMENTS_8=("1000" "2000" "3000" "4000" "5000")
ARGUMENTS_9=("40" "1000" "10000" "100000" "1000000")
ARGUMENTS_10=("-10" "-20" "-30" "-40" "-50")
ARGUMENTS_11=("1000000" "2000000" "3000000" "4000000" "5000000")
ARGUMENTS_12=("1" "3" "5" "7" "9")
ARGUMENTS_13=("100" "200" "300" "400" "500")
ARGUMENTS_14=("100" "500" "1000" "5000" "10000")

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
    OUTPUT_FILE_NO_CACHE="$ROOT_PATH/$(basename "${PYTHON_FILE}_output_no_cache.txt")"
    OUTPUT_FILE_MANUAL="$ROOT_PATH/intra_args_$(basename "${PYTHON_FILE}_output_manual.txt")"

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
        for j in {1..10}; do
            python3.12 $PYTHON_FILE $ARG --exec-mode no-cache | tail -n 1 | cut -d':' -f2 >> $OUTPUT_FILE_NO_CACHE
        done
        
        echo "-Execution mode: manual with $ARG"
        
        # Execute the Python script with the argument in 'manual' mode
        for j in {1..10}; do
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
    OUTPUT_FILE_MANUAL="$ROOT_PATH/intra_exec_only_$(basename "${PYTHON_FILE}_output_manual.txt")"

    cd "$DEST_DIR"
    echo "Running $PYTHON_FILE with different arguments..."

    # Run the script with each argument
    for ARG in "${ARGUMENTS[@]}"; do
    
        #Run setup.py before executing the Python script
        echo "Running setup.py for $PYTHON_FILE..."
        # python3.12 "$ROOT_PATH/speedupy/setup_exp/setup.py" "$PYTHON_FILE"
        echo "-Execution mode: manual"
        
        # Execute the Python script with the argument in 'manual' mode
        for j in {1..10}; do
            python3.12 "speedupy/setup_exp/setup.py" "$PYTHON_FILE"        
            python3.12 $PYTHON_FILE $ARG --exec-mode manual | tail -n 1 | cut -d':' -f2 >> $OUTPUT_FILE_MANUAL
            rm -rf "$DEST_DIR/.speedupy/"
        done        
       # Delete the .speedupy folder after each argument / Deleta a pasta .speedupy após cada argumento		
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
    OUTPUT_FILE_MANUAL="$ROOT_PATH/$(basename "intra_experiment_${PYTHON_FILE}_output_manual.txt")"

    cd "$DEST_DIR"
    echo "Running $PYTHON_FILE with different arguments..."

    # Run the script with each argument
    for ARG in "${ARGUMENTS[@]}"; do
    
        #Run setup.py before executing the Python script
        echo "Running setup.py for $PYTHON_FILE..."
        # python3.12 "$ROOT_PATH/speedupy/setup_exp/setup.py" "$PYTHON_FILE"
        python3.12 "speedupy/setup_exp/setup.py" "$PYTHON_FILE"
        echo "-Execution mode: manual"
        
        # Execute the Python script with the argument in 'manual' mode
        for j in {1..10}; do
            python3.12 $PYTHON_FILE $ARG --exec-mode manual | tail -n 1 | cut -d':' -f2 >> $OUTPUT_FILE_MANUAL
        done        
       # Delete the .speedupy folder after each argument / Deleta a pasta .speedupy após cada argumento
    done
    rm -rf "$DEST_DIR/.speedupy/"
done

# Movendo saida para um diretório
cd $ROOT_PATH
mkdir outputs
mv *.txt outputs/

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
