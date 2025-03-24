import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
from PIL import Image

os.makedirs("graphs", exist_ok=True)

# Directory where the .txt output files are located
OUTPUT_DIR = "./outputs"

# List of experiment names (each ending in .py)
experiments = [
    "quicksort.py",
    "look_and_say.py",
    "test_gauss_legendre_quadrature.py",
    "heat_distribution_lu.py",
    "test_compute_FFT_speedupy.py",
    #"curves_speedupy.py",
    "test_pernicious_numbers.py",
    "cvar_speedupy.py",
    "test_belief_propagation_speedupy.py",
    "basic_spheres.py",
    "walking_colloid.py",
    "vince_sim_speedupy.py",
    "TINY_GSHCGP.py",
    "analyse_speedupy.py",
    #"qho2_speedupy.py"
]

# Input values per experiment (5 inputs per experiment)
experiment_inputs = [
    ["1e1", "1e2", "1e3", "1e4", "1e5"],
    ["25", "30", "35", "40", "45"],
    ["1000", "2000", "3000", "4000", "5000"],
    ["0.1", "0.05", "0.01", "0.005", "0.001"],
    ["1000", "2000", "3000", "4000", "5000"],
    ["20000", "25000", "30000", "35000", "39000"],
    ["1e6", "5e6", "10e6", "50e6", "100e6"],
    ["1000", "2000", "3000", "4000", "5000"],
    ["40", "1000", "10000", "100000", "1000000"],
    ["-10", "-20", "-30", "-40", "-50"],
    ["1000000", "2000000", "3000000", "4000000", "5000000"],
    ["1", "3", "5", "7", "9"],
    ["100", "200", "300", "400", "500"]
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
    plt.savefig(os.path.join("graphs", f"graph_{exp_name}_matplotlib.png"))
    plt.close()

# --- Summary Table: Best Method for Largest Input ---
summary = []

for idx, exp in enumerate(experiments):
    exp_name = exp.replace(".py", "")
    inputs = experiment_inputs[idx]
    largest_input_index = -1  # Always the last input

    txt_files = [
        f"{exp}_output_manual.txt",
        f"{exp}_output_no_cache.txt",
        f"intra_args_{exp}_output_manual.txt",
        f"intra_exec_only_{exp}_output_manual.txt"
    ]

    method_labels = ["manual", "no cache", "intra args", "intra exec only"]

    best_time = float('inf')
    best_method = "N/A"

    for i, fname in enumerate(txt_files):
        path = os.path.join(OUTPUT_DIR, fname)
        if not os.path.exists(path):
            continue
        with open(path) as f:
            values = [float(line.strip()) for line in f]
        if len(values) != 10:
            continue
        medians = [np.median([values[j], values[j+1]]) for j in range(0, 10, 2)]
        largest_input_median = medians[largest_input_index]

        if largest_input_median < best_time:
            best_time = largest_input_median
            best_method = method_labels[i]

    summary.append([exp_name, f"{best_time:.2f}", best_method])

summary_df = pd.DataFrame(summary, columns=["Experiment", "Best Time", "Best Method"])
print("\nSummary: Best method per experiment (largest input only):")
print(summary_df.to_string(index=False))

# Export to CSV
summary_df.to_csv("graphs/summary_table.csv", index=False)
print("📄 CSV file saved: graphs/summary_table.csv")

fig, ax = plt.subplots(figsize=(10, len(summary)*0.5 + 1))
ax.axis('tight')
ax.axis('off')
table = ax.table(cellText=summary_df.values, colLabels=summary_df.columns, cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)

# Bold and slightly smaller font for first row and first column
for (row, col), cell in table.get_celld().items():
    if row == 0 or col == 0:
        cell.set_text_props(weight='bold', size=8)

plt.title("Best time per experiment (largest input only)", fontsize=12, pad=20)
summary_table_path = "graphs/summary_table.png"
plt.savefig(summary_table_path, bbox_inches='tight')
plt.close()
print("\n📊 Summary table saved as graphs/summary_table.png")

# --- Full Summary Table: Best Method per Input ---
full_summary = []

for idx, exp in enumerate(experiments):
    exp_name = exp.replace(".py", "")
    inputs = experiment_inputs[idx]

    txt_files = [
        f"{exp}_output_manual.txt",
        f"{exp}_output_no_cache.txt",
        f"intra_args_{exp}_output_manual.txt",
        f"intra_exec_only_{exp}_output_manual.txt"
    ]

    method_labels = ["manual", "no cache", "intra args", "intra exec only"]

    medians_all = []
    for fname in txt_files:
        path = os.path.join(OUTPUT_DIR, fname)
        if not os.path.exists(path):
            medians_all.append([np.inf]*5)
            continue
        with open(path) as f:
            values = [float(line.strip()) for line in f]
        if len(values) != 10:
            medians_all.append([np.inf]*5)
            continue
        medians = [np.median([values[j], values[j+1]]) for j in range(0, 10, 2)]
        medians_all.append(medians)

    row = [exp_name]
    for i in range(5):
        col_vals = [medians_all[m][i] for m in range(4)]
        min_val = min(col_vals)
        min_method = method_labels[col_vals.index(min_val)]
        row.append(f"{min_val:.2f}")
        row.append(min_method)
    full_summary.append(row)

# Criar cabeçalhos alternando entre input e método vencedor
full_columns = ["Experiment"]
for i, val in enumerate(inputs):
    full_columns.append(f"Input {i+1} exec. time (s)")
    full_columns.append(f"WM Input {i+1}")

full_df = pd.DataFrame(full_summary, columns=full_columns)
print("\nFull summary: Best method per input point:")
print(full_df.to_string(index=False))

fig, ax = plt.subplots(figsize=(16, len(full_summary)*0.5 + 1))
ax.axis('tight')
ax.axis('off')
table = ax.table(cellText=full_df.values, colLabels=full_df.columns, cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1.2, 1.2)

# Bold and slightly smaller font for first row and first column
for (row, col), cell in table.get_celld().items():
    if row == 0 or col == 0:
        cell.set_text_props(weight='bold', size=7)

plt.title("Best time and method per input for each experiment", fontsize=12, pad=20)
full_summary_path = "graphs/summary_table_full.png"
plt.savefig(full_summary_path, bbox_inches='tight')
plt.close()
print("\n📊 Full summary table saved as graphs/summary_table_full.png")

# Export full summary to CSV
full_df.to_csv("graphs/summary_table_full.csv", index=False)
print("📄 CSV file saved: graphs/summary_table_full.csv")

# --- Merge all PNGs into a single PDF ---
png_files = sorted([f for f in os.listdir("graphs") if f.startswith("graph_") and f.endswith(".png")])
for extra in ["summary_table.png", "summary_table_full.png"]:
    extra_path = os.path.join("graphs", extra)
    if os.path.exists(extra_path):
        png_files.append(extra)

image_paths = [os.path.join("graphs", f) for f in png_files]
images = [Image.open(f).convert("RGB") for f in image_paths]

if images:
    images[0].save(
        os.path.join("graphs", "all_experiments_graphs.pdf"),
        save_all=True,
        append_images=images[1:]
    )
    print("📄 PDF saved: graphs/all_experiments_graphs.pdf")
else:
    print("⚠️ No PNGs found to include in PDF.")
