#!/bin/bash

ROOT_PATH="$(pwd)"

# Define origem e destino
ORIGEM="$ROOT_PATH/exps/dnacc/dnacc"
DESTINO="$ROOT_PATH/exps/dnacc/basic_spheres"
DESTINO2="$ROOT_PATH/exps/dnacc/walking_colloid"

# Apaga arquivos gerados pela execução do experimento
find $DESTINO2 -type f -name "*.dat" -delete

# Verifica se a pasta de origem existe ou se os diretórios já foram configurados
if [ ! -d "$ORIGEM" ]; then
    echo "Erro: A pasta de origem '$ORIGEM' não existe."
    exit 1
elif [[ -d "$DESTINO/dnacc" && -d "$DESTINO2/dnacc" ]]; then    
    exit 0
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

cd $ROOT_PATH
