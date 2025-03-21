#!/bin/bash
ROOT_PATH="$(pwd)"

DEST_DIR="$ROOT_PATH/epr-with-speedupy/analyse_speedupy.py"
cd $DEST_DIR
pip install matplotlib
python3.12 source.py 60 0.5
python3.12 station_py39.py SrcLeft.npy.gz
python3.12 station_py39.py SrcRight.npy.gz
cd $ROOT_PATH