#!/usr/bin/env python3
# speedupy.py — versão final consolidada com suporte completo à Fase 3

import time, sys, os, atexit, hashlib, pickle, argparse
from functools import wraps
sys.path.append(os.path.dirname(__file__))

from execute_exp.services.factory import init_exec_mode, init_revalidation
from execute_exp.services.DataAccess import DataAccess, get_id
from execute_exp.SpeeduPySettings import SpeeduPySettings
from execute_exp.entitites.Metadata import Metadata
from SingletonMeta import SingletonMeta
from util import check_python_version
from logger.log import debug

check_python_version()

# Argumentos suportados (agora oficialmente com --monitor-cache)
parser = argparse.ArgumentParser()
parser.add_argument("input", nargs="?")
parser.add_argument("--exec-mode", required=True)
parser.add_argument("--monitor-cache", action="store_true")
parser.add_argument("-s", dest="store_mode")
args, unknown = parser.parse_known_args()

MONITOR = args.monitor_cache
MODE = args.exec_mode
SCRIPT_NAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]
LOG_NAME = f"{SCRIPT_NAME}_{MODE}_cachelog.txt" if MONITOR and MODE else None

# Diretórios
OUTPUT_DIR = "outputs_fase3"
# CACHE_DIR = ".speedupy/cache"  # versão antiga: colocava o cache na raiz do projeto
SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
CACHE_DIR = os.path.join(SCRIPT_DIR, ".speedupy", "cache")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Métricas
cache_hits = 0
cache_misses = 0
cache_entries_created = 0
hit_total_time = 0.0

# Tamanho do cache

def get_cache_size_bytes():
    total = 0
    for root, _, files in os.walk(CACHE_DIR):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total

# Registro das métricas ao final
@atexit.register
def dump_cache_metrics():
    if not MONITOR or not LOG_NAME:
        return
    total_access = cache_hits + cache_misses
    hit_rate = cache_hits / total_access if total_access else 0.0
    avg_overhead = hit_total_time / cache_hits if cache_hits else 0.0
    size_bytes = get_cache_size_bytes()
    log_path = os.path.join(OUTPUT_DIR, LOG_NAME)
    with open(log_path, "w") as f:
        f.write(f"cache_entries_created: {cache_entries_created}\n")
        f.write(f"cache_hits: {cache_hits}\n")
        f.write(f"cache_misses: {cache_misses}\n")
        f.write(f"cache_hit_rate: {hit_rate:.4f}\n")
        f.write(f"cache_size_bytes: {size_bytes}\n")
        f.write(f"cache_overhead_per_hit: {avg_overhead:.6f}\n")

# Decorador de funções determinísticas (instrumentado)
def deterministic(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global cache_hits, cache_misses, cache_entries_created, hit_total_time
        cache_key = hashlib.md5(pickle.dumps((func.__qualname__, args, kwargs))).hexdigest()
        cache_path = os.path.join(CACHE_DIR, cache_key)

        if os.path.exists(cache_path):
            start = time.time()
            with open(cache_path, "rb") as f:
                result = pickle.load(f)
            end = time.time()
            if MONITOR:
                cache_hits += 1
                hit_total_time += (end - start)
            return result
        else:
            result = func(*args, **kwargs)
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(cache_path, "wb") as f:
                pickle.dump(result, f)
            if MONITOR:
                cache_misses += 1
                cache_entries_created += 1
            return result
    return wrapper

# Compatibilidade com os modos e inicializações
class SpeeduPy(metaclass=SingletonMeta):
    def __init__(self):
        self.exec_mode = init_exec_mode()
        self.revalidation = init_revalidation(self.exec_mode)

def initialize_speedupy(f):
    @wraps(f)
    def wrapper(*method_args, **method_kwargs):
        start = time.perf_counter()
        DataAccess().init_data_access()
        f(*method_args, **method_kwargs)
        DataAccess().close_data_access()
        end = time.perf_counter()
        print(f"TOTAL EXECUTION TIME: {end - start}")
    return wrapper

def maybe_deterministic(f):
    return f
