#!/bin/bash

# Capture start time / Captura a hora de início
START_TIME=$(date +%s)
echo "Start time: $(date '+%H:%M:%S')"

# Delete the old outputs / Deleta as saídas antigas
rm -f *.txt
if [ -d outputs ]; then
    rm -f outputs/*
else
    mkdir -p outputs
fi

# Pre-configurations to run the Framework | Configurações prévias para executar o Framework
pip install -r speedupy/requirements.txt

# Define the common root path / Define o caminho raiz comum
ROOT_PATH="$(pwd)"

# Define the source directory
SOURCE_DIR="$ROOT_PATH/speedupy"

# Define the list of destination paths / Define a lista de caminhos de destino
# DESTINATIONS_0="$ROOT_PATH/speedupy_experiments/01pilots/01pilots_exp03_quicksort/quicksort.py" 
DESTINATIONS_0="$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp02_look_and_say/look_and_say.py" 
DESTINATIONS_1="$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp11_gauss_legendre_quadrature/gauss_legendre_quadrature.py" 

# DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1 $DESTINATIONS_2)
DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1)

# Define the list of arguments for each destination path / Define a lista de argumentos para cada caminho de destino
# ARGUMENTS_0=("1e1" "1e2" "1e3" "1e4" "1e5") # quicksort
ARGUMENTS_0=("45" "46" "47" "48" "49") # look_and_say
ARGUMENTS_1=("5000" "7000" "9000" "11000" "13000") # gauss_legendre_quadrature

# Copy the source directory to each destination directory / Copia o diretório de origem para cada diretório de destino
for i in "${!DESTINATIONS[@]}"; do
    DEST="${DESTINATIONS[i]}"
    DEST_DIR=$(dirname "$DEST")  # Extract the directory path from the destination path
    if [ ! -d "$DEST_DIR/speedupy" ]; then # speedupy não está no diretório
        cp -r "$SOURCE_DIR" "$DEST_DIR"
        echo "Copied $SOURCE_DIR to $DEST_DIR"
    fi
done

# Definir arquivos de saída para cada experimento e modo
declare -A OUTPUT_FILES
for i in "${!DESTINATIONS[@]}"; do
    PYTHON_FILE="${DESTINATIONS[i]}"
    BASE_NAME=$(basename $PYTHON_FILE | cut -d. -f1)
    OUTPUT_FILES["${i}_no_cache"]="$ROOT_PATH/outputs/${BASE_NAME}_output_no_cache.txt"
    OUTPUT_FILES["${i}_intra_args"]="$ROOT_PATH/outputs/${BASE_NAME}_output_spdpy_intra_args.txt"
    OUTPUT_FILES["${i}_intra_exec"]="$ROOT_PATH/outputs/${BASE_NAME}_output_spdpy_intra_exec.txt"
    OUTPUT_FILES["${i}_intra_exp"]="$ROOT_PATH/outputs/${BASE_NAME}_output_spdpy_intra_exp.txt"
done

echo "========================================"
echo "Modo 1: Execução sem cache (no-cache)"
echo "========================================"
# Para cada uma das 3 rodadas
for round in {1..3}; do
    echo "Rodada $round - Modo no-cache"
    # Para cada um dos 5 argumentos
    for arg_index in {0..4}; do
        echo "Argumento índice $arg_index - Modo no-cache"
        # Para cada um dos 3 experimentos
        for exp_index in "${!DESTINATIONS[@]}"; do
            DEST="${DESTINATIONS[exp_index]}"
            DEST_DIR=$(dirname "$DEST")
            PYTHON_FILE="$DEST"
            
            # Obtém o argumento correto para este experimento
            ARGUMENTS_VAR="ARGUMENTS_${exp_index}[$arg_index]"
            ARG=${!ARGUMENTS_VAR}
            
            cd "$DEST_DIR"
            echo "Executando $PYTHON_FILE com argumento $ARG - Modo no-cache"
            
            # Executa o script Python com o argumento no modo 'no-cache'
            python3.12 $PYTHON_FILE $(echo "$ARG") --exec-mode no-cache | tail -n 1 | cut -d':' -f2 >> ${OUTPUT_FILES["${exp_index}_no_cache"]}
            
            cd "$ROOT_PATH"
        done
    done
done

echo "========================================"
echo "Modo 2: Execução com cache intra-args (VERSÃO CORRIGIDA)"
echo "========================================"

# Para cada uma das 3 rodadas
for round in {1..3}; do
    echo "Rodada $round - Modo intra-args"
    
    # Para cada um dos 5 argumentos
    for arg_index in {0..4}; do
        echo "Processando argumento índice $arg_index - Modo intra-args"
        
        # Inicializa/reinicia o cache para este argumento em cada experimento
        for exp_index in "${!DESTINATIONS[@]}"; do
            DEST="${DESTINATIONS[exp_index]}"
            DEST_DIR=$(dirname "$DEST")
            PYTHON_FILE="$DEST"
            CACHE_STORAGE_DIR="$DEST_DIR/.speedupy_cache_${exp_index}_${arg_index}"
            
            cd "$DEST_DIR"
            echo "Preparando cache para $PYTHON_FILE argumento $arg_index - Rodada $round"
            
            # Se for a primeira rodada para este argumento, cria novo cache
            if [ $round -eq 1 ]; then
                rm -rf "$DEST_DIR/.speedupy" 2>/dev/null
                rm -rf "$CACHE_STORAGE_DIR" 2>/dev/null
                mkdir -p "$CACHE_STORAGE_DIR"
                # Executa o setup para inicializar o cache
                python3.12 "speedupy/setup_exp/setup.py" "$PYTHON_FILE"
            else
                # Restaura o cache da rodada anterior para este argumento
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
            
            # Obtém o argumento correto para este experimento
            ARGUMENTS_VAR="ARGUMENTS_${exp_index}[$arg_index]"
            ARG=${!ARGUMENTS_VAR}
            
            cd "$DEST_DIR"
            echo "Executando $PYTHON_FILE com argumento $ARG - Rodada $round"
            
            # Executa e grava o resultado
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

# Limpeza final
for exp_index in "${!DESTINATIONS[@]}"; do
    DEST="${DESTINATIONS[exp_index]}"
    DEST_DIR=$(dirname "$DEST")
    for arg_index in {0..4}; do
        CACHE_STORAGE_DIR="$DEST_DIR/.speedupy_cache_${exp_index}_${arg_index}"
        rm -rf "$CACHE_STORAGE_DIR"
    done
done

echo "========================================"
echo "Modo 3: Execução com cache intra-exec"
echo "========================================"
# Para cada uma das 3 rodadas
for round in {1..3}; do
    echo "Rodada $round - Modo intra-exec"
    # Para cada um dos 5 argumentos
    for arg_index in {0..4}; do
        echo "Argumento índice $arg_index - Modo intra-exec"
        # Para cada um dos 3 experimentos
        for exp_index in "${!DESTINATIONS[@]}"; do
            DEST="${DESTINATIONS[exp_index]}"
            DEST_DIR=$(dirname "$DEST")
            PYTHON_FILE="$DEST"
            
            # Obtém o argumento correto para este experimento
            ARGUMENTS_VAR="ARGUMENTS_${exp_index}[$arg_index]"
            ARG=${!ARGUMENTS_VAR}
            
            cd "$DEST_DIR"
            echo "Executando $PYTHON_FILE com argumento $ARG - Modo intra-exec"
            
            # Setup para o modo intra-exec (cache é criado e destruído a cada execução)
            python3.12 "speedupy/setup_exp/setup.py" "$PYTHON_FILE"
            
            # Executa o script Python com o argumento no modo 'manual'
            python3.12 $PYTHON_FILE $(echo "$ARG") --exec-mode manual | tail -n 1 | cut -d':' -f2 >> ${OUTPUT_FILES["${exp_index}_intra_exec"]}
            
            # Apaga o cache após cada execução
            rm -rf "$DEST_DIR/.speedupy/"
            
            cd "$ROOT_PATH"
        done
    done
done

echo "========================================"
echo "Modo 4: Execução com cache intra-exp"
echo "========================================"
# Para cada uma das 3 rodadas
for round in {1..3}; do
    echo "Rodada $round - Modo intra-exp"
    
    # Setup inicial para cada experimento no início da rodada
    for exp_index in "${!DESTINATIONS[@]}"; do
        DEST="${DESTINATIONS[exp_index]}"
        DEST_DIR=$(dirname "$DEST")
        PYTHON_FILE="$DEST"
        
        cd "$DEST_DIR"
        echo "Inicializando cache para $PYTHON_FILE - Modo intra-exp"
        
        # Apaga qualquer cache anterior
        rm -rf "$DEST_DIR/.speedupy/"
        
        # Setup para o modo intra-exp (cache permanece para todas as entradas do experimento)
        python3.12 "speedupy/setup_exp/setup.py" "$PYTHON_FILE"
        
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
            
            # Obtém o argumento correto para este experimento
            ARGUMENTS_VAR="ARGUMENTS_${exp_index}[$arg_index]"
            ARG=${!ARGUMENTS_VAR}
            
            cd "$DEST_DIR"
            echo "Executando $PYTHON_FILE com argumento $ARG - Modo intra-exp"
            
            # Executa o script Python com o argumento no modo 'manual'
            python3.12 $PYTHON_FILE $(echo "$ARG") --exec-mode manual | tail -n 1 | cut -d':' -f2 >> ${OUTPUT_FILES["${exp_index}_intra_exp"]}
            
            cd "$ROOT_PATH"
        done
    done
    
    # Limpa o cache de todos os experimentos no final da rodada
    for exp_index in "${!DESTINATIONS[@]}"; do
        DEST="${DESTINATIONS[exp_index]}"
        DEST_DIR=$(dirname "$DEST")
        echo "Limpando cache para $DEST após todos os argumentos - Modo intra-exp"
        rm -rf "$DEST_DIR/.speedupy/"
    done
done

# Limpa os diretórios do speedupy copiados previamente
for i in "${!DESTINATIONS[@]}"; do
    DEST="${DESTINATIONS[i]}"
    DEST_DIR=$(dirname "$DEST")
    rm -rf "$DEST_DIR/speedupy/"
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
