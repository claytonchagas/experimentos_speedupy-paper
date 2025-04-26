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

# Define paths
ROOT_PATH="$(pwd)"
SOURCE_DIR="$ROOT_PATH/speedupy"
DESTINATIONS_0="$ROOT_PATH/speedupy_experiments/01pilots/01pilots_exp03_quicksort/quicksort.py" 
DESTINATIONS_1="$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp02_look_and_say/look_and_say.py" 
DESTINATIONS_2="$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp11_gauss_legendre_quadrature/gauss_legendre_quadrature.py"

DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1 $DESTINATIONS_2)

# Define arguments
ARGUMENTS_0=("1e1" "1e2" "1e3" "1e4" "1e5") # quicksort
ARGUMENTS_1=("25" "30" "35" "40" "43") # look_and_say
ARGUMENTS_2=("1000" "2000" "3000" "4000" "4500") # gauss_legendre_quadrature

# Copy speedupy to each destination
for i in "${!DESTINATIONS[@]}"; do
    DEST="${DESTINATIONS[i]}"
    DEST_DIR=$(dirname "$DEST")
    if [ ! -d "$DEST_DIR/speedupy" ]; then
        cp -r "$SOURCE_DIR" "$DEST_DIR"
        echo "Copied $SOURCE_DIR to $DEST_DIR"
    fi
done

# Define output files
declare -A OUTPUT_FILES
for i in "${!DESTINATIONS[@]}"; do
    PYTHON_FILE="${DESTINATIONS[i]}"
    BASE_NAME=$(basename $PYTHON_FILE | cut -d. -f1)
    OUTPUT_FILES["${i}_no_cache"]="$ROOT_PATH/outputs/${BASE_NAME}_output_no_cache.txt"
    OUTPUT_FILES["${i}_intra_args"]="$ROOT_PATH/outputs/${BASE_NAME}_output_spdpy_intra_args.txt"
    OUTPUT_FILES["${i}_intra_exec"]="$ROOT_PATH/outputs/${BASE_NAME}_output_spdpy_intra_exec.txt"
    OUTPUT_FILES["${i}_intra_exp"]="$ROOT_PATH/outputs/${BASE_NAME}_output_spdpy_intra_exp.txt"
done

########################################
# Modo 1: Execução sem cache (no-cache)
########################################
echo "========================================"
echo "Modo 1: Execução sem cache (no-cache)"
echo "========================================"

for round in {1..3}; do
    echo "Rodada $round - Modo no-cache"
    for arg_index in {0..4}; do
        echo "Argumento índice $arg_index - Modo no-cache"
        for exp_index in "${!DESTINATIONS[@]}"; do
            DEST="${DESTINATIONS[exp_index]}"
            DEST_DIR=$(dirname "$DEST")
            PYTHON_FILE="$DEST"
            
            ARGUMENTS_VAR="ARGUMENTS_${exp_index}[$arg_index]"
            ARG=${!ARGUMENTS_VAR}
            
            cd "$DEST_DIR"
            echo "Executando $PYTHON_FILE com argumento $ARG - Modo no-cache"
            python3.12 $PYTHON_FILE $(echo "$ARG") --exec-mode no-cache | tail -n 1 | cut -d':' -f2 >> ${OUTPUT_FILES["${exp_index}_no_cache"]}
            
            cd "$ROOT_PATH"
        done
    done
done

########################################
# Modo 2: Execução com cache intra-args
########################################
echo "========================================"
echo "Modo 2: Execução com cache intra-args"
echo "========================================"

for round in {1..3}; do
    echo "Rodada $round - Modo intra-args"
    
    for arg_index in {0..4}; do
        echo "Processando argumento índice $arg_index - Modo intra-args"
        
        # Inicializa/reinicia o cache para este argumento
        for exp_index in "${!DESTINATIONS[@]}"; do
            DEST="${DESTINATIONS[exp_index]}"
            DEST_DIR=$(dirname "$DEST")
            PYTHON_FILE="$DEST"
            CACHE_STORAGE_DIR="$DEST_DIR/.speedupy_cache_${exp_index}_${arg_index}"
            
            cd "$DEST_DIR"
            echo "Preparando cache para $PYTHON_FILE argumento $arg_index - Rodada $round"
            
            if [ $round -eq 1 ]; then
                rm -rf "$DEST_DIR/.speedupy" 2>/dev/null
                rm -rf "$CACHE_STORAGE_DIR" 2>/dev/null
                mkdir -p "$CACHE_STORAGE_DIR"
                python3.12 "speedupy/setup_exp/setup.py" "$PYTHON_FILE"
            else
                if [ -d "$CACHE_STORAGE_DIR/.speedupy" ]; then
                    rm -rf "$DEST_DIR/.speedupy" 2>/dev/null
                    cp -r "$CACHE_STORAGE_DIR/.speedupy" "$DEST_DIR/"
                fi
            fi
            
            cd "$ROOT_PATH"
        done
        
        # Executa todos os experimentos para este argumento
        for exp_index in "${!DESTINATIONS[@]}"; do
            DEST="${DESTINATIONS[exp_index]}"
            DEST_DIR=$(dirname "$DEST")
            PYTHON_FILE="$DEST"
            OUTPUT_FILE="$ROOT_PATH/outputs/$(basename $PYTHON_FILE | cut -d. -f1)_output_spdpy_intra_args.txt"
            
            ARGUMENTS_VAR="ARGUMENTS_${exp_index}[$arg_index]"
            ARG=${!ARGUMENTS_VAR}
            
            cd "$DEST_DIR"
            echo "Executando $PYTHON_FILE com argumento $ARG - Rodada $round"
            python3.12 $PYTHON_FILE $(echo "$ARG") --exec-mode manual | tail -n 1 | cut -d':' -f2 >> "$OUTPUT_FILE"
            
            # Armazena o cache após a execução
            CACHE_STORAGE_DIR="$DEST_DIR/.speedupy_cache_${exp_index}_${arg_index}"
            mkdir -p "$CACHE_STORAGE_DIR"
            rm -rf "$CACHE_STORAGE_DIR/.speedupy" 2>/dev/null
            if [ -d ".speedupy" ]; then
                cp -r ".speedupy" "$CACHE_STORAGE_DIR/"
            fi
            
            cd "$ROOT_PATH"
        done
    done
done

# Limpeza final do Modo 2
for exp_index in "${!DESTINATIONS[@]}"; do
    DEST="${DESTINATIONS[exp_index]}"
    DEST_DIR=$(dirname "$DEST")
    for arg_index in {0..4}; do
        CACHE_STORAGE_DIR="$DEST_DIR/.speedupy_cache_${exp_index}_${arg_index}"
        rm -rf "$CACHE_STORAGE_DIR"
    done
done

########################################
# Modo 3: Execução com cache intra-exec
########################################
echo "========================================"
echo "Modo 3: Execução com cache intra-exec"
echo "========================================"

for round in {1..3}; do
    echo "Rodada $round - Modo intra-exec"
    for arg_index in {0..4}; do
        echo "Argumento índice $arg_index - Modo intra-exec"
        for exp_index in "${!DESTINATIONS[@]}"; do
            DEST="${DESTINATIONS[exp_index]}"
            DEST_DIR=$(dirname "$DEST")
            PYTHON_FILE="$DEST"
            
            ARGUMENTS_VAR="ARGUMENTS_${exp_index}[$arg_index]"
            ARG=${!ARGUMENTS_VAR}
            
            cd "$DEST_DIR"
            echo "Executando $PYTHON_FILE com argumento $ARG - Modo intra-exec"
            
            # Setup para o modo intra-exec
            python3.12 "speedupy/setup_exp/setup.py" "$PYTHON_FILE"
            
            # Executa o script
            python3.12 $PYTHON_FILE $(echo "$ARG") --exec-mode manual | tail -n 1 | cut -d':' -f2 >> ${OUTPUT_FILES["${exp_index}_intra_exec"]}
            
            # Apaga o cache após cada execução
            rm -rf "$DEST_DIR/.speedupy/"
            
            cd "$ROOT_PATH"
        done
    done
done

########################################
# Modo 4: Execução com cache intra-exp (VERSÃO CORRIGIDA)
########################################
echo "========================================"
echo "Modo 4: Execução com cache intra-exp"
echo "========================================"

# Cria diretório para armazenar o cache entre rodadas
CACHE_STORAGE_DIR="$ROOT_PATH/.speedupy_cache_intra_exp"
mkdir -p "$CACHE_STORAGE_DIR"

for round in {1..3}; do
    echo "Rodada $round - Modo intra-exp"
    
    # Restaura/Inicializa o cache para cada experimento
    for exp_index in "${!DESTINATIONS[@]}"; do
        DEST="${DESTINATIONS[exp_index]}"
        DEST_DIR=$(dirname "$DEST")
        PYTHON_FILE="$DEST"
        
        cd "$DEST_DIR"
        echo "Preparando cache para $PYTHON_FILE - Rodada $round"
        
        if [ $round -eq 1 ]; then
            rm -rf "$DEST_DIR/.speedupy" 2>/dev/null
            python3.12 "speedupy/setup_exp/setup.py" "$PYTHON_FILE"
        else
            if [ -d "$CACHE_STORAGE_DIR/.speedupy_${exp_index}" ]; then
                rm -rf "$DEST_DIR/.speedupy" 2>/dev/null
                cp -r "$CACHE_STORAGE_DIR/.speedupy_${exp_index}" "$DEST_DIR/.speedupy"
            fi
        fi
        
        cd "$ROOT_PATH"
    done
    
    # Para cada um dos 5 argumentos
    for arg_index in {0..4}; do
        echo "Argumento índice $arg_index - Modo intra-exp"
        
        # Para cada um dos 3 experimentos
        for exp_index in "${!DESTINATIONS[@]}"; do
            DEST="${DESTINATIONS[exp_index]}"
            DEST_DIR=$(dirname "$DEST")
            PYTHON_FILE="$DEST"
            
            ARGUMENTS_VAR="ARGUMENTS_${exp_index}[$arg_index]"
            ARG=${!ARGUMENTS_VAR}
            
            cd "$DEST_DIR"
            echo "Executando $PYTHON_FILE com argumento $ARG - Rodada $round"
            python3.12 $PYTHON_FILE $(echo "$ARG") --exec-mode manual | tail -n 1 | cut -d':' -f2 >> ${OUTPUT_FILES["${exp_index}_intra_exp"]}
            
            cd "$ROOT_PATH"
        done
    done
    
    # Armazena o cache após cada rodada
    for exp_index in "${!DESTINATIONS[@]}"; do
        DEST="${DESTINATIONS[exp_index]}"
        DEST_DIR=$(dirname "$DEST")
        
        cd "$DEST_DIR"
        if [ -d ".speedupy" ]; then
            rm -rf "$CACHE_STORAGE_DIR/.speedupy_${exp_index}" 2>/dev/null
            cp -r ".speedupy" "$CACHE_STORAGE_DIR/.speedupy_${exp_index}"
        fi
        cd "$ROOT_PATH"
    done
done

# Limpeza final do Modo 4
rm -rf "$CACHE_STORAGE_DIR"

########################################
# Finalização
########################################

# Remove speedupy copies
for i in "${!DESTINATIONS[@]}"; do
    DEST="${DESTINATIONS[i]}"
    DEST_DIR=$(dirname "$DEST")
    rm -rf "$DEST_DIR/speedupy/"
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

echo "Execution completed. Outputs saved in 'outputs' directory."
