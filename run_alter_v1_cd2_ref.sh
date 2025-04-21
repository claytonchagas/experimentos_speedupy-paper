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
#./dnacc_prepare.sh

#chmod +x epr_prepare.sh
#./epr_prepare.sh

#chmod +x qho2_prepare.sh
#./qho2_prepare.sh

#chmod +x heat_prepare.sh
#./heat_prepare.sh

# Define paths
ROOT_PATH="$(pwd)"

# Define the source directory
SOURCE_DIR="$ROOT_PATH/speedupy"

# Define the list of destination paths / Define a lista de caminhos de destino
###DESTINATIONS_0="$ROOT_PATH/speedupy_experiments/01pilots/01pilots_exp03_quicksort/quicksort.py" 
###DESTINATIONS_0="$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp02_look_and_say/look_and_say.py" 
###DESTINATIONS_0="$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp11_gauss_legendre_quadrature/gauss_legendre_quadrature.py" 
###DESTINATIONS_0="$ROOT_PATH/speedupy_experiments/01pilots/01pilots_exp04_heat_distribution_lu/heat_distribution_lu.py" 
###DESTINATIONS_0="$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp08_fft/fft_speedupy.py" 
###DESTINATIONS_0="$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp14_pernicious_numbers/pernicious_numbers.py" 
###DESTINATIONS_0="$ROOT_PATH/speedupy_experiments/05msrgithubexps/05msrgithubexps_exp02_cvar/cvar_speedupy.py" 
###DESTINATIONS_0="$ROOT_PATH/speedupy_experiments/04benchproglangs/04benchpl_exp06_belief_propagation/belief_propagation_speedupy.py" 
###DESTINATIONS_0="$ROOT_PATH/DNACC-with-speedupy/adapted_for_speedupy/examples/basic/basic_spheres.py" 
###DESTINATIONS_0="$ROOT_PATH/DNACC-with-speedupy/adapted_for_speedupy/examples/walking_colloid/walking_colloid.py" 
###DESTINATIONS_0="$ROOT_PATH/diversity-with-speedupy/Diversity_sims/vince_sim_speedupy.py" 
###DESTINATIONS_0="$ROOT_PATH/Tiny-GSGP-with-speedupy/adapted_for_speedupy/TINY_GSHCGP.py" 
###DESTINATIONS_0="$ROOT_PATH/epr-with-speedupy/analyse_speedupy.py"
###DESTINATIONS_0="$ROOT_PATH/qho-with-speedupy/qho2_speedupy.py"
###DESTINATIONS_0="$ROOT_PATH/speedupy_experiments/05msrgithubexps/05msrgithubexps_exp04_curves/curves_speedupy.py"

#DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1)
#DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1 $DESTINATIONS_2 $DESTINATIONS_3)
#DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1)
#DESTINATIONS=($DESTINATIONS_0 $DESTINATIONS_1 $DESTINATIONS_2 $DESTINATIONS_3 $DESTINATIONS_4 $DESTINATIONS_5 $DESTINATIONS_6 $DESTINATIONS_7 $DESTINATIONS_8 $DESTINATIONS_9 $DESTINATIONS_10 $DESTINATIONS_11 $DESTINATIONS_12 $DESTINATIONS_13 $DESTINATIONS_14)

# Define arguments
#ARGUMENTS_0=("1e1" "1e2" "1e3" "1e4" "1e5") # quicksort
#ARGUMENTS_0=("45" "46" "47" "48" "49") # look_and_say
#ARGUMENTS_0=("5000" "7000" "9000" "11000" "13000") # gauss_legendre_quadrature
#ARGUMENTS_0=("0.1" "0.05" "0.01" "0.005" "0.001") # heat_distribution_lu
#ARGUMENTS_0=("5000" "5500" "6000" "6500" "7000") # fft
#ARGUMENTS_1=("20000" "25000" "30000" "35000" "39000") # pernicious_numbers
#ARGUMENTS_2=("1e6" "5e6" "10e6" "50e6" "100e6") # cvar
#ARGUMENTS_0=("1000" "5500" "10000" "14500" "19000") # belief_propagation
#ARGUMENTS_1=("2000000" "5000000" "8000000" "11000000" "13000000") # dnacc_basic_spheres
#ARGUMENTS_0=("-20" "-50" "-80" "-110" "-140") # dnacc_walking_colloid
#ARGUMENTS_0=("1000000" "2000000" "3000000" "4000000" "5000000") # vince_sim
#ARGUMENTS_0=("12" "13" "14" "15" "16") # TINY_GSHCGP
#ARGUMENTS_1=("100" "250" "500" "750" "1000") # analyse_epr
#ARGUMENTS_0=("4000" "4500" "5000" "5500" "6000") # qho2

#ARG_CURVES_1=("-11124 -11124 62412 1412 107501 201635 15678 57849")
#ARG_CURVES_2=("1576862 -8567453 1648423 542312 512 -20135 1455678 52349")
#ARG_CURVES_3=("4341212 -12312419 123123 5423672 107 20135 145678 52349")
#ARG_CURVES_4=("4341241 -1231219 1231423 5423672 10547 20135 145678 52349")
#ARG_CURVES_5=("-1112434 -1241223 6212412 5281412 107501 20142265 3455678 5467849")

#ARGUMENTS_1=("${ARG_CURVES_1}" "${ARG_CURVES_2}" "${ARG_CURVES_3}" "${ARG_CURVES_4}" "${ARG_CURVES_5}") # curves

# Copy speedupy to each destination
for i in "${!DESTINATIONS[@]}"; do
    DEST="${DESTINATIONS[i]}"
    DEST_DIR=$(dirname "$DEST")  # Extract the directory path from the destination path
    if [ ! -d "$DEST_DIR/speedupy" ]; then # speedupy não está no diretório
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

########################################
# Modo 2: Execução com cache intra-args
########################################
echo "========================================"
echo "Modo 2: Execução com cache intra-args"
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

########################################
# Modo 3: Execução com cache intra-exec
########################################
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
