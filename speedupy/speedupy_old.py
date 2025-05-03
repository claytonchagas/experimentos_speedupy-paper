# speedupy.py — versão completa com instrumentação para Fase 3

import time, sys, os, atexit, hashlib, pickle
from functools import wraps
sys.path.append(os.path.dirname(__file__))

from execute_exp.services.factory import init_exec_mode, init_revalidation
from execute_exp.services.DataAccess import DataAccess, get_id
from execute_exp.SpeeduPySettings import SpeeduPySettings
from execute_exp.entitites.Metadata import Metadata
from SingletonMeta import SingletonMeta
from util import check_python_version
from logger.log import debug

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

#TODO: CORRIGIR IMPLEMENTAÇÃO
def maybe_deterministic(f):
    return f

# ================= INSTRUMENTAÇÃO PARA FASE 3 ====================
MONITOR = "--monitor-cache" in sys.argv
ARGS = " ".join(sys.argv).lower()
MODE = None
for arg in sys.argv:
    if "--exec-mode" in arg:
        parts = arg.split("=")
        if len(parts) == 2:
            MODE = parts[1]
SCRIPT_NAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]
LOG_NAME = f"{SCRIPT_NAME}_{MODE}_cachelog.txt" if MODE and MONITOR else None
CACHE_DIR = ".speedupy/cache"

cache_hits = 0
cache_misses = 0
cache_entries_created = 0
hit_total_time = 0.0

def get_cache_size_bytes():
    total = 0
    for root, _, files in os.walk(CACHE_DIR):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total

@atexit.register
def dump_cache_metrics():
    if not MONITOR or not LOG_NAME:
        return
    total_access = cache_hits + cache_misses
    hit_rate = cache_hits / total_access if total_access else 0.0
    avg_hit_overhead = hit_total_time / cache_hits if cache_hits else 0.0
    size_bytes = get_cache_size_bytes()
    with open(LOG_NAME, "w") as f:
        f.write(f"cache_entries_created: {cache_entries_created}\n")
        f.write(f"cache_hits: {cache_hits}\n")
        f.write(f"cache_misses: {cache_misses}\n")
        f.write(f"cache_hit_rate: {hit_rate:.4f}\n")
        f.write(f"cache_size_bytes: {size_bytes}\n")
        f.write(f"cache_overhead_per_hit: {avg_hit_overhead:.6f}\n")

# ================= FIM INSTRUMENTAÇÃO ====================

def _cache_doesnt_exist(cache) -> bool:
    return cache is None

def _execute_func_measuring_time(f, method_args, method_kwargs):
    start = time.perf_counter()
    result_value = f(*method_args, **method_kwargs)
    end = time.perf_counter()
    return result_value, end - start

check_python_version()

if SpeeduPySettings().exec_mode == ['no-cache']:
    def initialize_speedupy(f):
        return f

    def deterministic(f):
        return f

    def maybe_deterministic(f):
        return f

elif SpeeduPySettings().exec_mode == ['manual']:
    def maybe_deterministic(f):
        return f

else:
    def deterministic(f):
        @wraps(f)
        def wrapper(*method_args, **method_kwargs):
            global cache_hits, cache_misses, cache_entries_created, hit_total_time
            cache_key = hashlib.md5(pickle.dumps((f.__qualname__, method_args, method_kwargs))).hexdigest()
            cache_path = os.path.join(CACHE_DIR, cache_key)

            if os.path.exists(cache_path):
                if MONITOR:
                    t0 = time.time()
                with open(cache_path, "rb") as file:
                    result = pickle.load(file)
                if MONITOR:
                    hit_total_time += time.time() - t0
                    cache_hits += 1
                debug(f"cache hit for {f.__qualname__}({method_args})")
                return result
            else:
                result_value, _ = _execute_func_measuring_time(f, method_args, method_kwargs)
                os.makedirs(CACHE_DIR, exist_ok=True)
                with open(cache_path, "wb") as file:
                    pickle.dump(result_value, file)
                if MONITOR:
                    cache_entries_created += 1
                    cache_misses += 1
                debug(f"cache miss for {f.__qualname__}({method_args})")
                return result_value

        return wrapper
