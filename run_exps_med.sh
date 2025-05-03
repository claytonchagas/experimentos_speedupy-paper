#!/bin/bash

# Script de execução para FASE 3 – Análise do Cache Instrumentado com SpeeduPy
# Executa os 11 experimentos nos modos com cache (intra_exec e intra_exp), manualmente
# Para cada experimento, roda as 5 entradas definidas com --monitor-cache
# Inclui preparação de ambiente, chamada do setup, limpeza e organização das saídas

START_TIME=$(date +%s)
echo "[FASE 3] Início: $(date '+%Y-%m-%d %H:%M:%S')"

ROOT=$(pwd)
EXPS_DIR="$ROOT/exps"
SPEEDUPY_SRC="$ROOT/speedupy"
OUTPUT_DIR="$ROOT/outputs_fase3"
SETUP_SCRIPT="$ROOT/speedupy/setup_exp/setup.py"

# Limpeza de saída antiga (mas preserva logs)
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Instalar dependências se necessário
pip install -r speedupy/requirements.txt

# Executar scripts de preparação (se necessário)
chmod +x ./run_before/dnacc_prepare.sh && ./run_before/dnacc_prepare.sh
chmod +x ./run_before/epr_prepare.sh && ./run_before/epr_prepare.sh
chmod +x ./run_before/heat_prepare.sh && ./run_before/heat_prepare.sh

# Lista dos experimentos
EXPS=(
  "belief_propagation/belief_propagation.py"
  "cvar/cvar.py"
  "diversity_sims/vince_sim.py"
  "dnacc/basic_spheres/basic_spheres.py"
  "dnacc/walking_colloid/walking_colloid.py"
  "epr/epr_analyse.py"
  "fft/fft.py"
  "gauss_legendre_quadrature/gauss_legendre_quadrature.py"
  "heat_distribution_lu/heat_distribution_lu.py"
  "look_and_say/look_and_say.py"
  "tiny/TINY_GSHCGP.py"
)

# Entradas por experimento
declare -A INPUTS
INPUTS[belief_propagation]="1000 5500 10000 14500 19000"
INPUTS[cvar]="1e6 5e6 10e6 50e6 100e6"
INPUTS[diversity_sims]="1000000 2000000 3000000 4000000 5000000"
INPUTS[basic_spheres]="2000000 5000000 8000000 11000000 13000000"
INPUTS[walking_colloid]="-20 -50 -80 -110 -140"
INPUTS[epr]="200 400 600 800 1000"
INPUTS[fft]="2000 3500 5000 6500 8000"
INPUTS[gauss_legendre_quadrature]="5000 7000 9000 11000 13000"
INPUTS[heat_lu]="0.1 0.05 0.01 0.005 0.001"
INPUTS[look_and_say]="45 46 47 48 49"
INPUTS[tiny_example]="12 13 14 15 16"

# Modos de execução
MODES=("intra_exec" "intra_exp")

for MODE in "${MODES[@]}"; do
  for EXP_REL in "${EXPS[@]}"; do
    EXP_PATH="$EXPS_DIR/$EXP_REL"
    EXP_NAME=$(basename "$EXP_REL" .py)
    EXP_DIR=$(dirname "$EXP_REL")
    DEST_DIR="$EXPS_DIR/$EXP_DIR"

    # Copiar toda a pasta speedupy para o diretório do experimento
    cp -r "$SPEEDUPY_SRC" "$DEST_DIR/"

    # Entradas
    IFS=' ' read -r -a ARGS <<< "${INPUTS[$EXP_NAME]}"

    if [ "$MODE" == "intra_exp" ]; then
      echo "[MODE: $MODE] Setup único para $EXP_NAME"
      python3.12 "$SETUP_SCRIPT" "$EXP_PATH"
    fi

    for ARG in "${ARGS[@]}"; do
      if [ "$MODE" == "intra_exec" ]; then
        echo "[MODE: $MODE] Limpando cache e executando setup.py para entrada $ARG"
        rm -rf "$DEST_DIR/.speedupy/cache"
        python3.12 "$SETUP_SCRIPT" "$EXP_PATH"
      fi

      echo "[MODE: $MODE] Executando $EXP_NAME com entrada $ARG..."
      python3.12 "$EXP_PATH" "$ARG" --exec-mode manual -s file --monitor-cache \
        > "$OUTPUT_DIR/${EXP_NAME}_${MODE}_${ARG}.out" 2>&1
    done

    echo "[LIMPANDO CACHE E PASTA SPEEDUPY DO EXPERIMENTO $EXP_NAME APÓS $MODE]"
    rm -rf "$DEST_DIR/.speedupy/cache"
    rm -rf "$DEST_DIR/.speedupy/__pycache__"
    rm -rf "$DEST_DIR/speedupy"
  done
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "[FASE 3] Fim: $(date '+%Y-%m-%d %H:%M:%S') — Duração: ${DURATION}s"
