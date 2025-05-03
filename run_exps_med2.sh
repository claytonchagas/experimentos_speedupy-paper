#!/bin/bash

# Script de execução para FASE 3 – Análise do Cache Instrumentado com SpeeduPy
# Executa os 11 experimentos com cache ativado, nos modos 1 ou 2 (passado como argumento)
# Inclui preparação de ambiente, chamada do setup, limpeza e organização das saídas

if [ -z "$1" ]; then
  echo "[ERRO] Informe o modo de execução: 1 ou 2"
  echo "Uso: $0 <modo>"
  exit 1
fi

MODE="$1"
START_TIME=$(date +%s)
echo "[FASE 3 - MODO $MODE] Início: $(date '+%Y-%m-%d %H:%M:%S')"

ROOT=$(pwd)
EXPS_DIR="$ROOT/exps"
OUTPUT_DIR="$ROOT/outputs_fase3"
SETUP_SCRIPT="speedupy.setup_exp.setup"

mkdir -p "$OUTPUT_DIR"

# Instalar dependências se necessário
pip install -r requirements.txt

# Executar scripts de preparação (se necessário)
#chmod +x ./run_before/dnacc_prepare.sh && ./run_before/dnacc_prepare.sh
#chmod +x ./run_before/epr_prepare.sh && ./run_before/epr_prepare.sh
#chmod +x ./run_before/heat_prepare.sh && ./run_before/heat_prepare.sh

# Lista dos experimentos
#EXPS=(
#  "belief_propagation/belief_propagation.py"
#  "cvar/cvar.py"
#  "diversity_sims/vince_sim.py"
#  "dnacc/basic_spheres/basic_spheres.py"
#  "dnacc/walking_colloid/walking_colloid.py"
#  "epr/epr_analyse.py"
#  "fft/fft.py"
#  "gauss_legendre_quadrature/gauss_legendre_quadrature.py"
#  "heat_distribution_lu/heat_distribution_lu.py"
#  "look_and_say/look_and_say.py"
#  "tiny/TINY_GSHCGP.py"
#)

EXPS=(
  "belief_propagation/belief_propagation.py"
  "cvar/cvar.py"
)

# Entradas por experimento
declare -A INPUTS
INPUTS[belief_propagation]="1000 5500 10000 14500 19000"
INPUTS[cvar]="1e6 5e6 10e6 50e6 100e6"
#INPUTS[diversity_sims]="1000000 2000000 3000000 4000000 5000000"
#INPUTS[basic_spheres]="2000000 5000000 8000000 11000000 13000000"
#INPUTS[walking_colloid]="-20 -50 -80 -110 -140"
#INPUTS[epr]="200 400 600 800 1000"
#INPUTS[fft]="2000 3500 5000 6500 8000"
#INPUTS[gauss_legendre_quadrature]="5000 7000 9000 11000 13000"
#INPUTS[heat_lu]="0.1 0.05 0.01 0.005 0.001"
#INPUTS[look_and_say]="45 46 47 48 49"
#INPUTS[tiny_example]="12 13 14 15 16"

for EXP_REL in "${EXPS[@]}"; do
  EXP_PATH="$EXPS_DIR/$EXP_REL"
  EXP_NAME=$(basename "$EXP_REL" .py)
  EXP_DIR=$(dirname "$EXP_REL")
  DEST_DIR="$EXPS_DIR/$EXP_DIR"

  IFS=' ' read -r -a ARGS <<< "${INPUTS[$EXP_NAME]}"

  if [ "$MODE" == "1" ]; then
    for ARG in "${ARGS[@]}"; do
      echo "[MODO 1] Preparando $EXP_NAME para entrada $ARG"
      rm -rf "$DEST_DIR/.speedupy"
      #python3.12 -m "$SETUP_SCRIPT" "$EXP_PATH"
      (cd "$DEST_DIR" && python3.12 -m speedupy.setup_exp.setup "$(basename "$EXP_PATH")")

      for i in 1 2; do
        echo "[MODO 1] Execução $i de $EXP_NAME com entrada $ARG"
        TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
        LOG_FILE="$OUTPUT_DIR/${EXP_NAME}_modo1_${ARG}_run${i}_${TIMESTAMP}.out"
        #python3.12 "$EXP_PATH" "$ARG" --exec-mode manual -s file --monitor-cache > "$LOG_FILE" 2>&1
        (cd "$DEST_DIR" && python3.12 "$(basename "$EXP_PATH")" "$ARG" --exec-mode manual -s file --monitor-cache > "$LOG_FILE" 2>&1)
      done

      echo "[MODO 1] Limpando cache do $EXP_NAME após entrada $ARG"
      rm -rf "$DEST_DIR/.speedupy"
    done
  elif [ "$MODE" == "2" ]; then
    echo "[MODO 2] Preparando $EXP_NAME (cache único para todas as entradas)"
    rm -rf "$DEST_DIR/.speedupy"
    #python3.12 -m "$SETUP_SCRIPT" "$EXP_PATH"
    (cd "$DEST_DIR" && python3.12 -m speedupy.setup_exp.setup "$(basename "$EXP_PATH")")

    for index in "${!ARGS[@]}"; do
      ARG="${ARGS[$index]}"
      if [ "$index" == "0" ]; then
        for i in 1 2; do
          echo "[MODO 2] Execução $i de $EXP_NAME com entrada $ARG"
          TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
          LOG_FILE="$OUTPUT_DIR/${EXP_NAME}_modo2_${ARG}_run${i}_${TIMESTAMP}.out"
          #python3.12 "$EXP_PATH" "$ARG" --exec-mode manual -s file --monitor-cache > "$LOG_FILE" 2>&1
          (cd "$DEST_DIR" && python3.12 "$(basename "$EXP_PATH")" "$ARG" --exec-mode manual -s file --monitor-cache > "$LOG_FILE" 2>&1)
        done
      else
        echo "[MODO 2] Execução única de $EXP_NAME com entrada $ARG"
        TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
        LOG_FILE="$OUTPUT_DIR/${EXP_NAME}_modo2_${ARG}_run1_${TIMESTAMP}.out"
        #python3.12 "$EXP_PATH" "$ARG" --exec-mode manual -s file --monitor-cache > "$LOG_FILE" 2>&1
        (cd "$DEST_DIR" && python3.12 "$(basename "$EXP_PATH")" "$ARG" --exec-mode manual -s file --monitor-cache > "$LOG_FILE" 2>&1)
      fi
    done

    echo "[MODO 2] Limpando cache do experimento $EXP_NAME após execuções"
    rm -rf "$DEST_DIR/.speedupy"
  else
    echo "[ERRO] Modo desconhecido: $MODE"
    exit 1
  fi
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "[FASE 3 - MODO $MODE] Fim: $(date '+%Y-%m-%d %H:%M:%S') — Duração: ${DURATION}s"
