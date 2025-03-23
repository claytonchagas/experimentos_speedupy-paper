import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
from PIL import Image

# Directory where the .txt output files are located
OUTPUT_DIR = "./outputs"

# List of experiment names (each ending in .py)
experiments = [
    "quicksort.py",
    "look_and_say.py",
    "test_gauss_legendre_quadrature.py",
    "__main__.py",
    "test_compute_FFT_speedupy.py",
    "curves_speedupy.py",
    "test_pernicious_numbers.py",
    "cvar_speedupy.py",
    "test_belief_propagation_speedupy.py",
    "basic_spheres.py",
    "walking_colloid.py",
    "vince_sim_speedupy.py",
    "TINY_GSHCGP.py",
    "analyse_speedupy.py",
    "qho2_speedupy.py"
]

# Input values per experiment (5 inputs per experiment)
experiment_inputs = [
    ["1e1", "1e2", "1e3", "1e4", "1e5"],
    ["25", "30", "35", "40", "45"],
    ["1000", "2000", "3000", "4000", "5000"],
    ["0.1", "0.05", "0.01", "0.005", "0.001"],
    ["1000", "2000", "3000", "4000", "5000"],
    [
        "1576862 -8567453 1648423 542312 512 -20135 1455678 52349",
        "4341212 -12312419 123123 5423672 107 20135 145678 52349",
        "-11124 -11124 62412 1412 107501 201635 15678 57849",
        "43441212 -22523123 6219 5143228 107501 20135 1455678 5234567849",
        "-111243412 -124122123 62192412 5281412 107501 201422635 123455678 5234567849"
    ],
    ["20000", "25000", "30000", "35000", "39000"],
    ["1e6", "5e6", "10e6", "50e6", "100e6"],
    ["1000", "2000", "3000", "4000", "5000"],
    ["40", "1000", "10000", "100000", "1000000"],
    ["-10", "-20", "-30", "-40", "-50"],
    ["1000000", "2000000", "3000000", "4000000", "5000000"],
    ["1", "3", "5", "7", "9"],
    ["100", "200", "300", "400", "500"],
    ["100", "500", "1000", "5000", "10000"]
]

# Colors and markers for the 4 lines in each graph
colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']
markers = ['o', 's', '^', 'x']  # circle, square, triangle, X

# Loop through each experiment
for idx, exp in enumerate(tqdm(experiments, desc="Generating graphs")):
    exp_name = exp.replace(".py", "")
    inputs = experiment_inputs[idx]

    txt_files = [
        f"{exp}_output_manual.txt",
        f"{exp}_output_no_cache.txt",
        f"intra_args_{exp}_output_manual.txt",
        f"intra_exec_only_{exp}_output_manual.txt"
    ]

    plt.figure(figsize=(10, 6))
    for i, fname in enumerate(txt_files):
        path = os.path.join(OUTPUT_DIR, fname)
        if not os.path.exists(path):
            continue

        with open(path) as f:
            values = [float(line.strip()) for line in f]

        if len(values) != 10:
            continue

        medians = [np.median([values[j], values[j+1]]) for j in range(0, 10, 2)]

        label = fname.replace(".py", "").replace(".txt", "")
        label = label.replace("___", "_").replace("__", "_").replace("output_", "")
        label = label.replace("_manual", " (manual)").replace("_no_cache", " (no cache)")

        plt.plot(inputs, medians, marker=markers[i], label=label, color=colors[i], zorder=3)

        for x, y in zip(inputs, medians):
            plt.text(x, y + y * 0.03, f"{y:.2f}", ha='center', va='bottom', fontsize=8, zorder=4)

    plt.title(exp_name)
    plt.xlabel("Input")
    plt.ylabel("Execution Time (s)")
    plt.grid(True, linestyle="--", zorder=0)
    plt.legend(loc="upper left", fontsize=9)
    plt.tight_layout()
    plt.savefig(f"graph_{exp_name}_matplotlib.png")
    plt.close()

# --- Merge all PNGs into a single PDF ---
png_files = sorted([f for f in os.listdir('.') if f.startswith("graph_") and f.endswith(".png")])
images = [Image.open(f).convert("RGB") for f in png_files]

if images:
    images[0].save(
        "all_experiments_graphs.pdf",
        save_all=True,
        append_images=images[1:]
    )
    print("\n📄 PDF saved: all_experiments_graphs.pdf")
else:
    print("⚠️ No PNGs found to include in PDF.")
