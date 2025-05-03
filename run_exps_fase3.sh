#!/bin/bash

# Script Fase 3: Executa os 11 experimentos com métricas de cache e tempo consolidados

if [ $# -ne 1 ]; then
  echo "Uso: $0 modo1|modo2"
  exit 1
fi

MODO="$1"
if [ "$MODO" != "modo1" ] && [ "$MODO" != "modo2" ]; then
  echo "Modo inválido: $MODO. Use 'modo1' ou 'modo2'."
  exit 1
fi

START_TIME=$(date +%s)
echo "[FASE 3] Início: $(date '+%Y-%m-%d %H:%M:%S')"

ROOT=$(pwd)
EXPS_DIR="$ROOT/exps"
OUTPUT_DIR="$ROOT/outputs_fase3"
mkdir -p "$OUTPUT_DIR"

# Instala dependências
pip install -r speedupy/requirements.txt

# Prepara ambiente
#chmod +x ./run_before/*.sh
#./run_before/dnacc_prepare.sh
#./run_before/epr_prepare.sh
#./run_before/heat_prepare.sh

# Lista dos experimentos
EXPS=(
  "belief_propagation/belief_propagation.py"
  "cvar/cvar.py"
  #"diversity_sims/vince_sim.py"
  #"dnacc/basic_spheres/basic_spheres.py"
  #"dnacc/walking_colloid/walking_colloid.py"
  #"epr/epr_analyse.py"
  #"fft/fft.py"
  #"gauss_legendre_quadrature/gauss_legendre_quadrature.py"
  #"heat_distribution_lu/heat_distribution_lu.py"
  #"look_and_say/look_and_say.py"
  #"tiny/TINY_GSHCGP.py"
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
#INPUTS[heat_distribution_lu]="0.1 0.05 0.01 0.005 0.001"
#INPUTS[look_and_say]="45 46 47 48 49"
#INPUTS[tiny]="12 13 14 15 16"

for EXP_REL in "${EXPS[@]}"; do
  EXP_PATH="$EXPS_DIR/$EXP_REL"
  EXP_NAME=$(basename "$EXP_REL" .py)
  EXP_DIR=$(dirname "$EXP_REL")
  DEST_DIR="$EXPS_DIR/$EXP_DIR"
  IFS=' ' read -r -a ARGS <<< "${INPUTS[$EXP_NAME]}"

  for ARG in "${ARGS[@]}"; do
    if [ "$MODO" == "modo1" ]; then
      for RUN_ID in 1 2; do
        echo "[MODO1] Setup para $EXP_NAME entrada $ARG RUN $RUN_ID"
        rm -rf "$DEST_DIR/.speedupy"
        python3.12 -m speedupy.setup_exp.setup "$EXP_PATH"

        echo "[MODO1] Executando $EXP_NAME entrada $ARG RUN $RUN_ID"
        EXP_NAME="$EXP_NAME" ARG="$ARG" MODE="$MODO" RUN_ID="$RUN_ID" \
          #python3.12 "$EXP_PATH" "$ARG" --exec-mode manual -s file --monitor-cache
          (cd "$DEST_DIR" && EXP_NAME="$EXP_NAME" ARG="$ARG" MODE="$MODO" RUN_ID="$RUN_ID" python3.12 "$(basename "$EXP_PATH")" "$ARG" --exec-mode manual -s file --monitor-cache)

      done
      echo "[MODO1] Limpando cache após entrada $ARG"
      rm -rf "$DEST_DIR/.speedupy"

    elif [ "$MODO" == "modo2" ]; then
      echo "[MODO2] Setup para $EXP_NAME entrada $ARG"
      if [ "$ARG" == "${ARGS[0]}" ]; then
        rm -rf "$DEST_DIR/.speedupy"
        python3.12 -m speedupy.setup_exp.setup "$EXP_PATH"
        for RUN_ID in 1 2; do
          echo "[MODO2] Executando $EXP_NAME entrada $ARG RUN $RUN_ID"
          EXP_NAME="$EXP_NAME" ARG="$ARG" MODE="$MODO" RUN_ID="$RUN_ID" \
            #python3.12 "$EXP_PATH" "$ARG" --exec-mode manual -s file --monitor-cache
            (cd "$DEST_DIR" && EXP_NAME="$EXP_NAME" ARG="$ARG" MODE="$MODO" RUN_ID="$RUN_ID" python3.12 "$(basename "$EXP_PATH")" "$ARG" --exec-mode manual -s file --monitor-cache)
        done
      else
        RUN_ID=1
        echo "[MODO2] Executando $EXP_NAME entrada $ARG RUN $RUN_ID"
        EXP_NAME="$EXP_NAME" ARG="$ARG" MODE="$MODO" RUN_ID="$RUN_ID" \
          #python3.12 "$EXP_PATH" "$ARG" --exec-mode manual -s file --monitor-cache
          (cd "$DEST_DIR" && EXP_NAME="$EXP_NAME" ARG="$ARG" MODE="$MODO" RUN_ID="$RUN_ID" python3.12 "$(basename "$EXP_PATH")" "$ARG" --exec-mode manual -s file --monitor-cache)
      fi
    fi
  done

  echo "[FINALIZAÇÃO] Limpando cache e .pyc do $EXP_NAME"
  rm -rf "$DEST_DIR/.speedupy" "$DEST_DIR/__pycache__"
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "[FASE 3] Fim: $(date '+%Y-%m-%d %H:%M:%S') — Duração: ${DURATION}s"
