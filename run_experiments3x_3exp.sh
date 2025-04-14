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


# Define the common root path / Define o caminho raiz comum
ROOT_PATH="$(pwd)"

# Define the source directory
SOURCE_DIR="$ROOT_PATH/speedupy"

# Define the list of destination paths / Define a lista de caminhos de destino

DESTINATIONS_0="$ROOT_PATH/speedupy_experiments/01pilots/01pilots_exp03_quicksort/quicksort.py" 
DESTINATIONS_1="$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp02_look_and_say/look_and_say.py" 
DESTINATIONS_2="$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp11_gauss_legendre_quadrature/gauss_legendre_quadrature.py" 


DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1 $DESTINATIONS_2)

# Define the list of arguments for each destination path / Define a lista de argumentos para cada caminho de destino
ARGUMENTS_0=("1e1" "1e2" "1e3" "1e4" "1e5") # quicksort
ARGUMENTS_1=("25" "30" "35" "40" "45") # look_and_say
ARGUMENTS_2=("1000" "2000" "3000" "4000" "5000") # gauss_legendre_quadrature


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
        for j in {1..3}; do
            python3.12 $PYTHON_FILE $(echo "$ARG") --exec-mode no-cache | tail -n 1 | cut -d':' -f2 >> $OUTPUT_FILE_NO_CACHE
        done
        
        echo "-Execution mode: manual with $ARG"
        
        # Execute the Python script with the argument in 'manual' mode
        for j in {1..3}; do
            python3.12 $PYTHON_FILE $(echo "$ARG") --exec-mode manual | tail -n 1 | cut -d':' -f2 >> $OUTPUT_FILE_MANUAL
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
        echo "-Execution mode: manual with $ARG"
        
        # Execute the Python script with the argument in 'manual' mode
        for j in {1..3}; do
            python3.12 "speedupy/setup_exp/setup.py" "$PYTHON_FILE"        
            python3.12 $PYTHON_FILE $(echo "$ARG") --exec-mode manual | tail -n 1 | cut -d':' -f2 >> $OUTPUT_FILE_MANUAL
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
    echo "-Execution mode: manual with $ARG"

    # Run the script with each argument
    for ARG in "${ARGUMENTS[@]}"; do    
        # Execute the Python script with the argument in 'manual' mode
        for j in {1..3}; do
            python3.12 $PYTHON_FILE $(echo "$ARG") --exec-mode manual | tail -n 1 | cut -d':' -f2 >> $OUTPUT_FILE_MANUAL
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
