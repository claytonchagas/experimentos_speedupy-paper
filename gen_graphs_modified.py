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
    "look_and_say": ["45", "46", "47", "48", "49"],
    "gauss_legendre_quadrature": ["5000", "7000", "9000", "11000", "13000"],
    "heat_distribution_lu": ["0.1", "0.05", "0.01", "0.005", "0.001"],
    "fft_speedupy": ["5000", "5500", "6000", "6500", "7000"],
    "pernicious_numbers": ["20000", "25000", "30000", "35000", "39000"],
    "cvar_speedupy": ["1e6", "5e6", "10e6", "50e6", "100e6"],
    "belief_propagation_speedupy": ["1000", "5500", "10000", "14500", "19000"],
    "basic_spheres": ["2000000", "5000000", "8000000", "11000000", "13000000"],
    "walking_colloid": ["-20", "-50", "-80", "-110", "-140"],
    "vince_sim_speedupy": ["1000000", "2000000", "3000000", "4000000", "5000000"],
    "TINY_GSHCGP": ["12", "13", "14", "15", "16"],
    "analyse_speedupy": ["100", "250", "500", "750", "1000"],
    "qho2_speedupy": ["4000", "4500", "5000", "5500", "6000"],
    "curves_speedupy": ["1", "2", "3", "4", "5"],
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

# Get list of experiments and create the numbered experiment names
experiments = list(inputs_per_experiment.keys())

# Function to clean experiment name (remove '_speedupy')
def clean_experiment_name(exp_name):
    return exp_name.replace('_speedupy', '')

# Create a mapping of original experiment name to numbered and cleaned name
numbered_experiment_names = {
    exp: f"{i+1}. {clean_experiment_name(exp)}" 
    for i, exp in enumerate(experiments)
}

def compute_medians(filepath, num_inputs):
    import numpy as np
    with open(filepath, "r") as f:
        values = [float(line.strip()) for line in f.readlines()]
    runs_per_input = len(values) // num_inputs
    medians = []
    for i in range(num_inputs):
        group = [values[i + j * num_inputs] for j in range(runs_per_input)]
        medians.append(np.median(group))
    return medians


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
        medians = compute_medians(fpath, len(inputs))
        medians_by_method[suf] = medians
        plt.plot(inputs, medians, label=suf.replace('output_', '').replace('spdpy_', 'speedupy_'), marker=markers[idx], linewidth=2)
        for i, median in enumerate(medians):
            # Increased precision to 4 decimal places
            plt.text(inputs[i], median + 0.01 * max(medians), f"{median:.4f}", ha='center')

    for i in range(len(inputs)):
        best_time = float('inf')
        best_method = ''
        for method, medians in medians_by_method.items():
            if medians[i] < best_time:
                best_time = medians[i]
                best_method = method
        # Increased precision to 4 decimal places
        best_per_input.append(f"{best_time:.4f} ({best_method.replace('output_', '').replace('spdpy_', 'speedupy_')})")
        methods_per_input.append(best_method)

    last_input = inputs[-1]
    best_last = best_per_input[-1]
    best_method_last = methods_per_input[-1].replace(".txt", "")
    time_val = best_last.split()[0]

    # Use the numbered and cleaned experiment name
    summary_best_last.append([numbered_experiment_names[exp], last_input, time_val, 
                             best_method_last.replace('output_', '').replace('spdpy_', 'speedupy_')])
    summary_all_points.append([numbered_experiment_names[exp]] + best_per_input)

    # Use the numbered and cleaned experiment name in plot title
    plt.title(numbered_experiment_names[exp], fontsize=14)
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
    # Tamanho da figura ajustado com base no número de colunas
    is_all_inputs = "all_inputs" in filename
    
    # Para a tabela all_inputs, usamos uma figura mais larga
    if is_all_inputs:
        fig_width = 28  # Maior largura para a tabela de todos os inputs
        col_widths = [0.17] + [0.166] * (len(df.columns) - 1)  # Primeira coluna um pouco maior
    else:
        fig_width = 20
        col_widths = None  # Distribui automaticamente
    
    fig, ax = plt.subplots(figsize=(fig_width, len(df) + 2))
    ax.set_axis_off()
    
    # Crie a tabela com larguras de coluna ajustadas
    table = plt.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1],
        colWidths=col_widths
    )
    
    # Aplique um tamanho de fonte grande
    table.auto_set_font_size(False)
    # base_fontsize = 18 if is_all_inputs else 16
    base_fontsize = 18
    
    # Ajuste as propriedades da tabela
    for (i, j), cell in table.get_celld().items():
        if i == 0:  # Cabeçalhos
            cell.set_text_props(fontsize=base_fontsize + 4, fontweight='bold')
            cell.set_facecolor('#cccccc')
        elif j == 0:  # Primeira coluna (nomes dos experimentos)
            cell.set_text_props(fontsize=base_fontsize + 2, fontweight='bold')
        else:  # Outras células
            cell.set_text_props(fontsize=base_fontsize)
        
        # Aumenta a altura das células
        cell.set_height(0.08)
        
        # Para a tabela all_inputs, ajustamos o alinhamento do texto
        if is_all_inputs and j > 0:
            # Usa wordwrap para células que podem conter muito texto
            cell.get_text().set_wrap(True)
    
    # Ajusta o tamanho para caber toda a tabela
    vertical_scale = 2.5
    table.scale(1, vertical_scale)  # Escala vertical aumentada
    
    plt.tight_layout()
    plt.savefig(os.path.join(graph_dir, filename), dpi=300, bbox_inches='tight')
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
