#!/bin/bash

ROOT_PATH="."

# Define origem e destino
ORIGEM="$ROOT_PATH/DNACC-with-speedupy/adapted_for_speedupy/dnacc_speedupy"
DESTINO="$ROOT_PATH/DNACC-with-speedupy/adapted_for_speedupy/examples/basic/dnacc"
DESTINO2="$ROOT_PATH/DNACC-with-speedupy/adapted_for_speedupy/examples/walking_colloid/dnacc"

# Verifica se a pasta de origem existe
if [ ! -d "$ORIGEM" ]; then
    echo "Erro: A pasta de origem '$ORIGEM' não existe."
    exit 1
fi

# Copia e renomeia a pasta
cp -r "$ORIGEM" "$DESTINO"

# Verifica se a cópia foi bem-sucedida
if [ $? -eq 0 ]; then
    echo "Pasta 1 copiada e renomeada com sucesso!"
else
    echo "Erro ao copiar a pasta 1."
    exit 1
fi

cp -r "$ORIGEM" "$DESTINO2"

if [ $? -eq 0 ]; then
    echo "Pasta 2 copiada e renomeada com sucesso!"
else
    echo "Erro ao copiar a pasta 2."
    exit 1
fi
