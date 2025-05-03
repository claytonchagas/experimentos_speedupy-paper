import os
import sys
import atexit
import time
import functools
from datetime import datetime
from inspect import signature

import mmh3
import xxhash
import numpy as np

import pickle

# Variáveis globais para métricas de cache
cache_hits = 0
cache_misses = 0
cache_entries_created = 0
hit_total_time = 0.0

# Diretório base do projeto (onde os logs devem ficar)
PROJECT_ROOT = os.path.abspath(os.getenv("PROJECT_ROOT", os.getcwd()))
LOG_DIR = os.path.join(PROJECT_ROOT, "outputs_fase3")
os.makedirs(LOG_DIR, exist_ok=True)

def get_env(var, default=None):
    return os.environ.get(var, default)

def build_cache_key(func, args, kwargs):
    key = pickle.dumps((func.__name__, args, tuple(sorted(kwargs.items()))))
    return xxhash.xxh64(key).hexdigest()

def deterministic(func):
    cache = {}
    # cache_dir = os.path.join(os.getcwd(), ".speedupy", "cache")
    cache_dir = os.path.join(os.path.dirname(sys.modules[func.__module__].__file__), ".speedupy", "cache")  # cria o cache na pasta do experimento

    os.makedirs(cache_dir, exist_ok=True)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global cache_hits, cache_misses, cache_entries_created, hit_total_time
        key = build_cache_key(func, args, kwargs)
        cache_file = os.path.join(cache_dir, key + ".pkl")

        if os.path.exists(cache_file):
            start_hit = time.perf_counter()
            with open(cache_file, "rb") as f:
                result = pickle.load(f)
            hit_total_time += time.perf_counter() - start_hit
            cache_hits += 1
            return result

        cache_misses += 1
        result = func(*args, **kwargs)
        with open(cache_file, "wb") as f:
            pickle.dump(result, f)
        cache_entries_created += 1
        return result

    return wrapper

def initialize_speedupy(main_func):
    @functools.wraps(main_func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            main_func(*args, **kwargs)
        finally:
            end = time.perf_counter()
            execution_time = end - start
            dump_cache_metrics(execution_time)
        return wrapper
    return wrapper

def dump_cache_metrics(execution_time):
    exp_name = get_env("EXP_NAME", "unknown_exp")
    mode = get_env("MODE", "unknown_mode")
    arg = get_env("ARG", "unknown_arg")
    run_id = get_env("RUN_ID", "unknown_run")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{exp_name}_{mode}_{arg}_run{run_id}_{timestamp}.txt"
    path = os.path.join(LOG_DIR, filename)

    hit_rate = cache_hits / (cache_hits + cache_misses) if (cache_hits + cache_misses) > 0 else 0.0
    # cache_dir = os.path.join(os.getcwd(), ".speedupy", "cache")
    cache_dir = os.path.join(os.path.dirname(sys.modules[func.__module__].__file__), ".speedupy", "cache")  # cria o cache na pasta do experimento
    cache_size = sum(os.path.getsize(os.path.join(dirpath, f))
                     for dirpath, _, files in os.walk(cache_dir) for f in files)
    overhead = hit_total_time / cache_hits if cache_hits > 0 else 0.0

    with open(path, "w") as f:
        f.write(f"TOTAL EXECUTION TIME: {execution_time:.6f}\n")
        f.write(f"cache_entries_created: {cache_entries_created}\n")
        f.write(f"cache_hits: {cache_hits}\n")
        f.write(f"cache_misses: {cache_misses}\n")
        f.write(f"cache_hit_rate: {hit_rate:.6f}\n")
        f.write(f"cache_size_bytes: {cache_size}\n")
        f.write(f"cache_overhead_per_hit: {overhead:.6f}\n")
