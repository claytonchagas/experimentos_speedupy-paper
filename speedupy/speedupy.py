import time, sys, os
from functools import wraps
import multiprocessing, signal
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

def maybe_deterministic(f):
    return f
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

#TODO: CORRIGIR IMPLEMENTAÇÃO
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
            DataAccess().create_cache_entry(f.__qualname__, method_args, method_kwargs, return_value)
            return return_value
        else:
            debug("cache hit for {0}({1})".format(f.__qualname__, method_args))
            return c
    return wrapper

def _cache_doesnt_exist(cache) -> bool:
    return cache is None

def _execute_func_measuring_time(f, method_args, method_kwargs):
    start = time.perf_counter()
    result_value = f(*method_args, **method_kwargs)
    end = time.perf_counter()
    return result_value, end - start

# Variable used to obtain the time of the lowest function and its name
TIME_EXECUTION = 0.
LOWEST_FUNCTION = ""
WINNER_MODE = ""

# This function is used for execution porposes on each process
def function_executer(shared_dict, barrier, function, f_aux, *args, **kwargs):    
    pid = os.getpid()
    shared_dict["procs"] = shared_dict["procs"] + [pid]
    barrier.wait()            
    start = time.perf_counter()    
    res = function(f_aux,*args, **kwargs) if function.__qualname__ == "old_deterministic" else function(*args, **kwargs)
    end = time.perf_counter()
    total_time = end - start     
    for p in shared_dict["procs"]:
        if p != pid:
            os.kill(p, signal.SIGTERM)
    shared_dict["res"] = res  
    shared_dict["total_time"] = total_time
    shared_dict["function"] = f_aux.__qualname__
    shared_dict["mode"] = "CACHE" if function.__qualname__ == "old_deterministic" else "NO CACHE"

    return res

check_python_version()

if SpeeduPySettings().exec_mode == ['no-cache']:
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
    
    # def maybe_deterministic(f):
    #     return f
elif SpeeduPySettings().exec_mode == ['manual']:
    pass
    # def maybe_deterministic(f):
    #     return f

elif SpeeduPySettings().exec_mode == ['multiprocess']:    
    # def maybe_deterministic(f):
    #     return f    
    def initialize_speedupy(f):
        @wraps(f)
        def wrapper(*method_args, **method_kwargs):    
            start = time.perf_counter()
            DataAccess().init_data_access()
            f(*method_args, **method_kwargs)
            DataAccess().close_data_access()
            end = time.perf_counter()
            print(f"LOWEST FUNCTION: {LOWEST_FUNCTION}")
            print(f"WINNER MODE: {WINNER_MODE}")
            print(f"TOTAL EXECUTION TIME: {end - start}")         
            # print(f"TOTAL EXECUTION TIME: {TIME_EXECUTION}")        
        return wrapper
    
    # This function saves the manual mode 
    def old_deterministic(f, *args, **kwargs):
        f._primeira_chamada = False
        debug("calling {0}".format(f.__qualname__))        
        c = DataAccess().get_cache_entry(f.__qualname__, args, kwargs)
        if _cache_doesnt_exist(c):
            debug("cache miss for {0}({1})".format(f.__qualname__, args))
            return_value = f(*args, **kwargs)
            DataAccess().create_cache_entry(f.__qualname__, args, kwargs, return_value)
            return return_value
        else:
            debug("cache hit for {0}({1})".format(f.__qualname__, args))
            return c
        
    # Create two processes and executes the function in mode no-cache and manual
    def deterministic(f):
        f._primeira_chamada = True
        manager = multiprocessing.Manager()
        barrier = multiprocessing.Barrier(2)
        shared_dict = manager.dict()
        shared_dict["procs"] = []
        @wraps(f)
        def wrapper(*args, **kwargs):
            if f._primeira_chamada:
                f._primeira_chamada = False
                p1 = multiprocessing.Process(target=function_executer, args=(shared_dict, barrier, f, f, *args))
                p2 = multiprocessing.Process(target=function_executer, args=(shared_dict, barrier, old_deterministic, f, *args))
                
                p1.start()
                p2.start()

                p1.join()
                p2.join()
                    
                global TIME_EXECUTION, LOWEST_FUNCTION, WINNER_MODE    
                
                if shared_dict["total_time"] > TIME_EXECUTION:        
                    TIME_EXECUTION = shared_dict["total_time"]
                    LOWEST_FUNCTION = shared_dict["function"]
                    WINNER_MODE = shared_dict["mode"]
                
                return shared_dict["res"]
            else:
                return f(*args, **kwargs)
        return wrapper