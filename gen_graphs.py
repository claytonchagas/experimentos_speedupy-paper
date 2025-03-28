import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.table import Table
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

# Set non-interactive backend
import matplotlib
matplotlib.use('Agg')

# Experiment input labels
inputs_per_experiment = {
    "quicksort": ["1e1", "1e2", "1e3", "1e4", "1e5"],
    "look_and_say": ["25", "30", "35", "40", "45"],
    "gauss_legendre_quadrature": ["1000", "2000", "3000", "4000", "5000"],
    "heat_distribution_lu": ["0.1", "0.05", "0.01", "0.005", "0.001"],
    "fft_speedupy": ["1000", "2000", "3000", "4000", "5000"],
    "pernicious_numbers": ["20000", "25000", "30000", "35000", "39000"],
    "cvar_speedupy": ["1e6", "5e6", "10e6", "50e6", "100e6"],
    "belief_propagation_speedupy": ["1000", "2000", "3000", "4000", "5000"],
    "basic_spheres": ["40", "1000", "10000", "100000", "1000000"],
    "walking_colloid": ["-10", "-20", "-30", "-40", "-50"],
    "vince_sim_speedupy": ["1000000", "2000000", "3000000", "4000000", "5000000"],
    "TINY_GSHCGP": ["1", "3", "5", "7", "9"],
    "analyse_speedupy": ["100", "200", "300", "400", "500"],
    "qho2_speedupy": ["100", "500", "1000", "5000", "6000"],
    "curves_speedupy": ["1","2","3","4","5"] # os 8 inputs padrões deixam a legenda ruim
}

suffixes = [
    "output_no_cache",
    "output_spdpy_intra_args",
    "output_spdpy_intra_exec",
    "output_spdpy_intra_exp"
]
markers = ['o', '^', 'x', 's']

output_dir = "./outputs"
graph_dir = "./graphs"
os.makedirs(graph_dir, exist_ok=True)

experiments = list(inputs_per_experiment.keys())

def compute_medians(filepath):
    with open(filepath, "r") as f:
        values = [float(line.strip()) for line in f.readlines()]
    return [np.median(values[i:i+2]) for i in range(0, len(values), 2)]

summary_best_last = []
summary_all_points = []

for exp in experiments:
    inputs = inputs_per_experiment[exp]
    best_per_input = []
    methods_per_input = []
    medians_by_method = {}

    plt.figure(figsize=(10, 6))

    for idx, suf in enumerate(suffixes):
        fname = f"{exp}_{suf}.txt"
        fpath = os.path.join(output_dir, fname)
        if not os.path.exists(fpath):
            continue
        medians = compute_medians(fpath)
        medians_by_method[suf] = medians
        plt.plot(inputs, medians, label=suf.replace('output_', '').replace('spdpy_', 'speedupy_'), marker=markers[idx], linewidth=2)
        for i, median in enumerate(medians):
            plt.text(inputs[i], median + 0.01 * max(medians), f"{median:.2f}", ha='center')

    for i in range(len(inputs)):
        best_time = float('inf')
        best_method = ''
        for method, medians in medians_by_method.items():
            if medians[i] < best_time:
                best_time = medians[i]
                best_method = method
        best_per_input.append(f"{best_time:.2f} ({best_method.replace('output_', '').replace('spdpy_', 'speedupy_')})")
        methods_per_input.append(best_method)

    last_input = inputs[-1]
    best_last = best_per_input[-1]
    best_method_last = methods_per_input[-1].replace(".txt", "")
    time_val = best_last.split()[0]

    summary_best_last.append([exp, last_input, time_val, best_method_last.replace('output_', '').replace('spdpy_', 'speedupy_')])
    summary_all_points.append([exp] + best_per_input)

    plt.title(exp, fontsize=14)
    plt.xlabel("Input")
    plt.ylabel("Execution Time Median (s)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(graph_dir, f"{exp}_plot.png"))
    plt.close()

df_best_last = pd.DataFrame(summary_best_last, columns=["Experiment", "Input", "Time (s)", "Best Method"])
df_all_points = pd.DataFrame(summary_all_points, columns=["Experiment"] + [f"Input {i+1}" for i in range(5)])

# Print tables to terminal
print("\nBest time for the largest input:")
print(df_best_last.to_string(index=False))
print("\nBest method and time for each input:")
print(df_all_points.to_string(index=False))

# Save CSVs
df_best_last.to_csv(os.path.join(graph_dir, "best_last_input.csv"), index=False)
df_all_points.to_csv(os.path.join(graph_dir, "best_all_inputs.csv"), index=False)

def save_table_image(df, filename):
    fig, ax = plt.subplots(figsize=(12, len(df)*0.5 + 1))
    ax.set_axis_off()
    table = Table(ax, bbox=[0, 0, 1, 1])
    n_rows, n_cols = df.shape
    col_labels = list(df.columns)
    col_widths = [1.0 / n_cols] * n_cols

    for col_idx, col_name in enumerate(col_labels):
        cell = table.add_cell(0, col_idx, col_widths[col_idx], 0.5, text=col_name, loc='center', facecolor='#cccccc')
        cell.get_text().set_fontweight('bold')

    for row_idx, row in enumerate(df.values):
        for col_idx, val in enumerate(row):
            cell = table.add_cell(row_idx + 1, col_idx, col_widths[col_idx], 0.5, text=str(val), loc='center')
            if col_idx == 0:
                cell.get_text().set_fontweight('bold')

    ax.add_table(table)
    plt.savefig(os.path.join(graph_dir, filename))
    plt.close()

save_table_image(df_best_last, "summary_table_last_input.png")
save_table_image(df_all_points, "summary_table_all_inputs.png")

pdf_path = os.path.join(graph_dir, "all_graphs_and_tables.pdf")
with PdfPages(pdf_path) as pdf:
    for exp in experiments:
        img_path = os.path.join(graph_dir, f"{exp}_plot.png")
        if os.path.exists(img_path):
            img = Image.open(img_path).convert("RGB")
            fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
            ax.imshow(img)
            ax.axis('off')
            pdf.savefig(fig, dpi=300)
            plt.close()

    for table_img in ["summary_table_last_input.png", "summary_table_all_inputs.png"]:
        img_path = os.path.join(graph_dir, table_img)
        img = Image.open(img_path).convert("RGB")
        fig, ax = plt.subplots(figsize=(12, len(df_best_last)*0.5 + 1), dpi=300)
        ax.imshow(img)
        ax.axis('off')
        pdf.savefig(fig, dpi=300)
        plt.close()
