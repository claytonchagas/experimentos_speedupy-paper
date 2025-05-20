import time, sys, os
from functools import wraps

sys.path.append(os.path.dirname(__file__))

from execute_exp.services.factory import init_exec_mode, init_revalidation
from execute_exp.services.DataAccess import DataAccess, get_id
from execute_exp.SpeeduPySettings import SpeeduPySettings
from execute_exp.entitites.Metadata import Metadata
from execute_exp.utils.persistance import load_samples, save_samples, make_serializable

from SingletonMeta import SingletonMeta
from util import check_python_version
from logger.log import debug
import numbers, statistics, math
from collections import defaultdict
from scipy import stats
import numpy as np

# Persistencia local para o maybe_deterministic
_SAMPLES = defaultdict(list, load_samples())

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


_MIN_NUM_EXEC = 4  # nº mínimo de execuções antes de analisar
_MIN_OCCURRENCE = 0.8  # para strategy 'counting'
_CONF_LEVEL = 0.95  # para strategy 'error'
_MAX_ERROR = 0.5  # margem de erro máxima no strategy 'error'



def _margin_error(lst):
    n = len(lst)
    if n < 2:
        return math.inf
    stdev = statistics.pstdev(lst)
    z = stats.t.ppf(_CONF_LEVEL, n - 1)
    return z * stdev / math.sqrt(n)

def _values_all_equal(buf):
  if not buf:
      return False
  first = buf[0]
  for v in buf[1:]:
      if isinstance(v, np.ndarray) or isinstance(first, np.ndarray):
          if not np.array_equal(v, first):
              return False
      else:
          if v != first:
              return False
  return True

def array_mode(buf):
    seen = []
    counts = []
    for v in buf:
        found = False
        for i, s in enumerate(seen):
            if np.array_equal(s, v):
                counts[i] += 1
                found = True
                break
        if not found:
            seen.append(v)
            counts.append(1)
    max_idx = np.argmax(counts)
    return seen[max_idx], counts[max_idx] / len(buf)


def maybe_deterministic(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print("wrapper")
        mode = (
            SpeeduPySettings().exec_mode[0]
            if SpeeduPySettings().exec_mode
            else "manual"
        )
        if mode in ("no-cache", "manual"):
            return f(*args, **kwargs)

        func_hash = DataAccess().get_function_hash(f.__qualname__)
        func_call_hash = get_id(func_hash, args, kwargs)

        print(f"[DEBUG] Calling: {f.__qualname__}")
        print(f"[DEBUG] Func hash: {func_hash}")
        print(f"[DEBUG] Func call hash: {func_call_hash}")

        buf = _SAMPLES[func_call_hash]

        if len(buf) >= _MIN_NUM_EXEC:
            print("entrou")
            if mode == "accurate":
                if _values_all_equal(buf):
                    return buf[0]

            elif mode == "probabilistic":
                strategy = (
                    SpeeduPySettings().strategy[0]
                    if SpeeduPySettings().strategy
                    else "counting"
                )

                if strategy == "counting":
                    try:
                        moda, freq = array_mode(buf)
                        if freq >= _MIN_OCCURRENCE:
                            return moda
                    except statistics.StatisticsError:
                        pass

                elif strategy == "error":
                    mean = statistics.mean(buf)
                    if _margin_error(buf) <= _MAX_ERROR:
                        return mean

        # Fallback to real execution
        ret, elapsed = _execute_func_measuring_time(f, *args, **kwargs)
        md = Metadata(func_hash, args, kwargs, ret, elapsed)
        DataAccess().add_to_metadata(func_call_hash, md)

        strategy = (
            SpeeduPySettings().strategy[0]
            if SpeeduPySettings().strategy
            else "counting"
        )

        if mode == "accurate" or (mode == "probabilistic" and strategy == "counting"):
            buf.append(ret)
            save_samples(make_serializable(_SAMPLES))

            if len(buf) >= _MIN_NUM_EXEC:
                if mode == "accurate":
                    if _values_all_equal(buf):
                        DataAccess().create_cache_entry(f.__qualname__, args, kwargs, buf[0])
                elif strategy == "counting":
                    try:
                        moda, freq = array_mode(buf)
                        if freq >= _MIN_OCCURRENCE:
                            DataAccess().create_cache_entry(f.__qualname__, args, kwargs, moda)
                    except statistics.StatisticsError:
                        pass

        elif isinstance(ret, numbers.Number) and strategy == "error":
            buf.append(ret)
            save_samples(make_serializable(_SAMPLES))

            if len(buf) >= _MIN_NUM_EXEC:
                mean = statistics.mean(buf)
                if _margin_error(buf) <= _MAX_ERROR:
                    DataAccess().create_cache_entry(f.__qualname__, args, kwargs, mean)

        return ret

    return wrapper


# #TODO: CORRIGIR IMPLEMENTAÇÃO
# def maybe_deterministic(f):
#     @wraps(f)
#     def wrapper(*method_args, **method_kwargs):
#         func_hash = DataAccess().get_function_hash(f.__qualname__)
#         func_call_hash = get_id(func_hash, method_args, method_kwargs)
#         if SpeeduPy().revalidation.revalidation_in_current_execution(func_call_hash):
#             return_value, elapsed_time = _execute_func_measuring_time(f, *method_args, **method_kwargs)

#             md = Metadata(func_hash, method_args, method_kwargs, return_value, elapsed_time)
#             DataAccess().add_to_metadata(func_call_hash, md)
#             SpeeduPy().revalidation.calculate_next_revalidation(func_call_hash, md)
#             DataAccess().add_metadata_collected_to_a_func_call_prov(func_call_hash)
#         # else:
#         #     if (num_exec_BD < num_exec_min) and \
#         #        (num_exec_BD + num_exec_metadados >= num_exec_min):
#         #         atualizar_dados_BD_com_metadados()
#         #     if num_exec_BD >= num_exec_min:
#         #         if exec_mode.pode_acelerar_funcao():
#         #             Acelera! (exec_mode.get_func_call_cache)
#         #             revalidation.decrementar_cont_prox_revalidacao()
#         #         else:
#         #             Executa função!
#         #     else:
#         #         Executa função + Coleta Metadados!


#         # OLD IMPLEMENTATION
#         # c = DataAccess().get_cache_entry(f.__qualname__, method_args, method_kwargs)
#         # returns_2_freq = _get_function_call_return_freqs(f, method_args, method_kwargs)
#         # if _cache_exists(c):
#         #     debug("cache hit for {0}({1})".format(f.__name__, *method_args))
#         #     return c
#         # if _returns_exist(returns_2_freq):
#         #     debug("simulating {0}({1})".format(f.__name__, *method_args))
#         #     ret = _simulate_func_exec(returns_2_freq)
#         #     return ret
#         # else:
#         #     debug("cache miss for {0}({1})".format(f.__name__, *method_args))
#         #     return_value, elapsed_time = _execute_func(f, *method_args, **method_kwargs)
#         #     if _function_call_maybe_deterministic(f, method_args, method_kwargs):
#         #         debug("{0}({1} may be deterministic!)".format(f.__name__, *method_args))
#         #         # DataAccess().add_to_metadata(f.__qualname__, method_args, method_kwargs, return_value, elapsed_time)
#         #     return return_value
#     return wrapper

# OLD IMPLEMENTATION
# def _returns_exist(rets_2_freq:Optional[Dict]) -> bool:
#     return rets_2_freq is not None

# def _get_function_call_return_freqs(f, args:List, kwargs:Dict) -> Optional[Dict]:
#     f_hash = DataAccess().FUNCTIONS_2_HASHES[f.__qualname__]
#     return get_function_call_return_freqs(f_hash, args, kwargs)

# TODO: CORRIGIR IMPLEMENTAÇÃO
# def _function_call_maybe_deterministic(func: Callable, func_args:List, func_kwargs:Dict) -> bool:
#     func_hash = DataAccess().FUNCTIONS_2_HASHES[func.__qualname__]
#     func_call_hash = get_id(func_hash, func_args, func_kwargs)
#     #return func_call_hash not in Constantes().DONT_CACHE_FUNCTION_CALLS
#     return True


def deterministic(f):
    @wraps(f)
    def wrapper(*method_args, **method_kwargs):
        debug("calling {0}".format(f.__qualname__))
        c = DataAccess().get_cache_entry(f.__qualname__, method_args, method_kwargs)
        if _cache_doesnt_exist(c):
            debug("cache miss for {0}({1})".format(f.__qualname__, method_args))
            return_value = f(*method_args, **method_kwargs)
            DataAccess().create_cache_entry(
                f.__qualname__, method_args, method_kwargs, return_value
            )
            return return_value
        else:
            debug("cache hit for {0}({1})".format(f.__qualname__, method_args))
            return c

    return wrapper


def _cache_doesnt_exist(cache) -> bool:
    return cache is None


def _execute_func_measuring_time(f, *method_args, **method_kwargs):
    start = time.perf_counter()
    result_value = f(*method_args, **method_kwargs)
    end = time.perf_counter()
    return result_value, end - start


check_python_version()

if SpeeduPySettings().exec_mode == ["no-cache"]:

    def initialize_speedupy(f):
        @wraps(f)
        def wrapper(*method_args, **method_kwargs):
            start = time.perf_counter()
            f(*method_args, **method_kwargs)
            end = time.perf_counter()
            print(f"TOTAL EXECUTION TIME: {end - start}")

        return wrapper

    def deterministic(f):
        return f

    def maybe_deterministic(f):
        return f

elif SpeeduPySettings().exec_mode == ["manual"]:

    def maybe_deterministic(f):
        return f
