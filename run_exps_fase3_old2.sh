#!/bin/bash

# Script Fase 3 (atualizado com segurança): executa os experimentos monitorando cache
# e coleta as métricas, organizando os logs e mantendo os arquivos essenciais intactos

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
chmod +x ./run_before/*.sh
./run_before/dnacc_prepare.sh
#./run_before/epr_prepare.sh
#./run_before/heat_prepare.sh

# Define experimentos
EXPS=(
  #"belief_propagation/belief_propagation.py"
  #"cvar/cvar.py"
  #"diversity_sims/diversity_sims.py"
  #"dnacc/basic_spheres/basic_spheres.py"
  "dnacc/walking_colloid/walking_colloid.py"
  #"epr/epr.py"
  #"fft/fft.py"
  #"gauss_legendre_quadrature/gauss_legendre_quadrature.py"
  #"heat_distribution_lu/heat_distribution_lu.py"
  #"look_and_say/look_and_say.py"
  #"tiny_gshcgp/tiny_gshcgp.py"
)

# Entradas por experimento
declare -A INPUTS
#INPUTS[belief_propagation]="1000 5500 10000 14500 19000"
#INPUTS[cvar]="1e6 5e6 10e6 50e6 100e6"
#INPUTS[diversity_sims]="1000000 2000000 3000000 4000000 5000000"
#INPUTS[basic_spheres]="2000000 5000000 8000000 11000000 13000000"
INPUTS[walking_colloid]="-20 -50 -80 -110 -140"
#INPUTS[epr]="200 400 600 800 1000"
#INPUTS[fft]="2000 3500 5000 6500 8000"
#INPUTS[gauss_legendre_quadrature]="5000 7000 9000 11000 13000"
#INPUTS[heat_distribution_lu]="0.1 0.05 0.01 0.005 0.001"
#INPUTS[look_and_say]="45 46 47 48 49"
#INPUTS[tiny_gshcgp]="12 13 14 15 16"

for EXP_REL in "${EXPS[@]}"; do
  EXP_PATH="$EXPS_DIR/$EXP_REL"
  EXP_BASENAME=$(basename "$EXP_REL" .py)
  EXP_DIR=$(dirname "$EXP_REL")
  EXP_FOLDER=$(basename "$EXP_DIR")
  EXP_NAME="$EXP_FOLDER"  # usamos o nome da pasta como chave para INPUTS

  DEST_DIR="$EXPS_DIR/$EXP_DIR"
  mkdir -p "$OUTPUT_DIR/$EXP_NAME"
  IFS=' ' read -r -a ARGS <<< "${INPUTS[$EXP_NAME]}"

  cd "$DEST_DIR" || exit 1

  if [ "$MODO" == "modo1" ]; then
    for ARG in "${ARGS[@]}"; do
      echo "[MODO1] Setup para $EXP_NAME entrada $ARG"
      rm -rf .speedupy
      python3.12 -m speedupy.setup_exp.setup "$(basename "$EXP_PATH")"

      for RUN_ID in 1 2; do
        LOG_FILE="$OUTPUT_DIR/$EXP_NAME/${EXP_NAME}_${ARG}_run${RUN_ID}_$(date +%Y%m%d_%H%M%S).out"
        echo "[MODO1] Executando $EXP_NAME entrada $ARG RUN $RUN_ID"
        EXP_NAME="$EXP_NAME" ARG="$ARG" MODE="$MODO" RUN_ID="$RUN_ID" \
          python3.12 "$EXP_BASENAME.py" "$ARG" --exec-mode manual -s file --monitor-cache > "$LOG_FILE" 2>&1
      done

      echo "[MODO1] Limpando cache após entrada $ARG"
      rm -rf .speedupy
    done

  elif [ "$MODO" == "modo2" ]; then
    echo "[MODO2] Setup para $EXP_NAME"
    rm -rf .speedupy
    python3.12 -m speedupy.setup_exp.setup "$(basename "$EXP_PATH")"

    for i in "${!ARGS[@]}"; do
      ARG="${ARGS[$i]}"
      if [ "$i" -eq 0 ]; then
        for RUN_ID in 1 2; do
          LOG_FILE="$OUTPUT_DIR/$EXP_NAME/${EXP_NAME}_${ARG}_run${RUN_ID}_$(date +%Y%m%d_%H%M%S).out"
          echo "[MODO2] Executando $EXP_NAME entrada $ARG RUN $RUN_ID"
          EXP_NAME="$EXP_NAME" ARG="$ARG" MODE="$MODO" RUN_ID="$RUN_ID" \
            python3.12 "$EXP_BASENAME.py" "$ARG" --exec-mode manual -s file --monitor-cache > "$LOG_FILE" 2>&1
        done
      else
        RUN_ID=1
        LOG_FILE="$OUTPUT_DIR/$EXP_NAME/${EXP_NAME}_${ARG}_run${RUN_ID}_$(date +%Y%m%d_%H%M%S).out"
        echo "[MODO2] Executando $EXP_NAME entrada $ARG RUN $RUN_ID"
        EXP_NAME="$EXP_NAME" ARG="$ARG" MODE="$MODO" RUN_ID="$RUN_ID" \
          python3.12 "$EXP_BASENAME.py" "$ARG" --exec-mode manual -s file --monitor-cache > "$LOG_FILE" 2>&1
      fi
    done
  fi

  echo "[FINALIZAÇÃO] Limpando cache e pyc do $EXP_NAME"
  rm -rf .speedupy
  find . -name '*.pyc' -delete

  cd - > /dev/null || exit 1
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "[FASE 3] Fim: $(date '+%Y-%m-%d %H:%M:%S') — Duração: ${DURATION}s"
