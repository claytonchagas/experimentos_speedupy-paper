#!/usr/bin/env python3
# speedupy.py — Versão final com suporte completo (incluindo instrumentação da Fase 3)

import time
import os
import sys
import atexit
import pickle
import functools
from datetime import datetime

# Dependências para o sistema SpeeduPy original
sys.path.append(os.path.dirname(__file__))
from execute_exp.services.DataAccess import DataAccess
from util import check_python_version
from logger.log import debug
from SingletonMeta import SingletonMeta

import xxhash

check_python_version()

# Variáveis de ambiente do experimento
def get_env(var, default=None):
    return os.environ.get(var, default)

EXP_NAME = get_env("EXP_NAME", "unknown_exp")
MODE     = get_env("MODE",     "manual")
ARG      = get_env("ARG",      "unknown_arg")
RUN_ID   = get_env("RUN_ID",   "1")
START_TS = get_env("START_TIME_LOG", None)  # Opcional

# Diretórios e cache
PROJECT_ROOT = os.path.abspath(get_env("PROJECT_ROOT", os.getcwd()))
LOG_DIR = os.path.join(PROJECT_ROOT, "outputs_fase3")
os.makedirs(LOG_DIR, exist_ok=True)

SCRIPT_DIR = os.getcwd()
CACHE_DIR = os.path.join(SCRIPT_DIR, ".speedupy", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Métricas globais do cache
cache_hits = 0
cache_misses = 0
cache_entries_created = 0
hit_total_time = 0.0

def build_cache_key(func, args, kwargs):
    """
    Gera chave única para o cache a partir do nome da função e dos argumentos.
    """
    key = pickle.dumps((func.__name__, args, tuple(sorted(kwargs.items()))))
    return xxhash.xxh64(key).hexdigest()

def get_cache_size_bytes():
    """
    Retorna o tamanho total em bytes de todos os arquivos no diretório de cache.
    """
    total = 0
    for root, _, files in os.walk(CACHE_DIR):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total

@atexit.register
def dump_cache_metrics():
    """
    Grava as métricas do cache em arquivo de log ao final da execução.
    """
    global cache_hits, cache_misses, cache_entries_created, hit_total_time
    # Cálculos das métricas
    total_access = cache_hits + cache_misses
    hit_rate = cache_hits / total_access if total_access else 0.0
    overhead = hit_total_time / cache_hits if cache_hits else 0.0
    size_bytes = get_cache_size_bytes()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Nome do arquivo de log conforme padrões da experimentação
    filename = f"{EXP_NAME}_{MODE}_{ARG}_run{RUN_ID}_{timestamp}.txt"
    path = os.path.join(LOG_DIR, filename)
    
    with open(path, "w") as f:
        if START_TS:
            f.write(f"START_TIME_LOG: {START_TS}\n")
        f.write(f"TOTAL EXECUTION TIME: {execution_time:.6f}\n")
        f.write(f"cache_entries_created: {cache_entries_created}\n")
        f.write(f"cache_hits: {cache_hits}\n")
        f.write(f"cache_misses: {cache_misses}\n")
        f.write(f"cache_hit_rate: {hit_rate:.6f}\n")
        f.write(f"cache_size_bytes: {size_bytes}\n")
        f.write(f"cache_overhead_per_hit: {overhead:.6f}\n")

# Decorador de funções determinísticas (faz cache em disco)
def deterministic(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global cache_hits, cache_misses, cache_entries_created, hit_total_time
        # Se no modo no-cache, não fazemos cache
        if MODE == "no-cache":
            return func(*args, **kwargs)
        # Chave e caminho do arquivo de cache
        key = build_cache_key(func, args, kwargs)
        cache_file = os.path.join(CACHE_DIR, key + ".pkl")

        # Cache hit
        if os.path.exists(cache_file):
            start_hit = time.perf_counter()
            with open(cache_file, "rb") as f:
                result = pickle.load(f)
            hit_total_time += time.perf_counter() - start_hit
            cache_hits += 1
            #debug(f"Cache hit: {func.__name__}({args}, {kwargs})")
            return result

        # Cache miss
        cache_misses += 1
        result = func(*args, **kwargs)
        # Armazena no cache
        with open(cache_file, "wb") as f:
            pickle.dump(result, f)
        cache_entries_created += 1
        #debug(f"Cache miss: {func.__name__}({args}, {kwargs})")
        return result
    return wrapper

# Decorador de inicialização (Wrapa a função principal do experimento)
def initialize_speedupy(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        global execution_time
        start = time.perf_counter()
        # Inicializa acesso a dados (se usado)
        DataAccess().init_data_access()
        try:
            f(*args, **kwargs)
        finally:
            # Finaliza acesso a dados
            DataAccess().close_data_access()
            end = time.perf_counter()
            execution_time = end - start
            print(f"TOTAL EXECUTION TIME: {execution_time:.6f}")
        return
    return wrapper

# Placeholder para talvez aplicar revalidação (não usada explicitamente)
def maybe_deterministic(f):
    return f
