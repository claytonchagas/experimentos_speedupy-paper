import pandas as pd
inputs_per_experiment = {    
    "look_and_say": ["46", "48"],
    "gauss_legendre_quadrature": ["7000", "11000"],
    "heat_distribution_lu": ["0.05", "0.005"],
    "fft": ["4000", "6000"],
    "cvar": ["5e6", "50e6"],
    "belief_propagation": ["5500", "14500"],
    "basic_spheres": ["5000000", "11000000"],
    "walking_colloid": ["-50", "-110"],
    "vince_sim": ["2000000", "4000000"],
    "TINY_GSHCGP": ["13", "15"],
    "epr_analyse": ["400", "800"]
}

suffixes = [
    "_cache",
    "_no_cache",
    "_multiprocess",    
]

data_cache = []
data_no_cache = []
data_multiprocess = []

base_dir = "outputs_15mai2025/"


for chave, keys in inputs_per_experiment.items():    
    with open(base_dir+chave+"_cache.txt","r") as file:
        data_cache.append([round(float(line[:-1]),4) for line in file.readlines()])
    with open(base_dir+chave+"_no_cache.txt","r") as file:
        data_no_cache.append([round(float(line[:-1]),4) for line in file.readlines()])
    with open(base_dir+chave+"_multiprocess.txt","r") as file:
        data = file.readlines()
        data_multiprocess.append([data[1][:-1].split(": ")[-1], data[4][:-1].split(": ")[-1]])

def decision(cache_value, no_cache_value):
    return 'CACHE' if cache_value < no_cache_value else "NO CACHE"

def precision(decisor_value, real_value):
    return 'SUCESS' if decisor_value == real_value else "FAIL"

# Construção da nova tabela
linhas = []

for i, (chave, inputs) in enumerate(inputs_per_experiment.items()):
    cache_vals = data_cache[i]
    no_cache_vals = data_no_cache[i]
    decisor_vals = data_multiprocess[i]
    for j in range(len(inputs)):
        decisao = decision(cache_vals[j], no_cache_vals[j])
        linhas.append({
            "experimentos": chave,
            "inputs": inputs[j],
            "no_cache": no_cache_vals[j],
            "cache": cache_vals[j],
            "decisor": decisor_vals[j],
            "real deal": decisao,
            "precisão": precision(decisor_vals[j], decisao)
        })

df = pd.DataFrame(linhas)

# Exibe e salva
print(df.to_string(index=False))
df.to_csv("tabela_decisor.csv", index=False)
