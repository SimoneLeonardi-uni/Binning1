import csv
import os
import sys
import matplotlib.pyplot as plt
import numpy as np

def read_benchmark_results(csv_path):
    results = []
    with open(csv_path, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            results.append(
                {
                    "mode": row["mode"],
                    "scheduler": row["scheduler"],
                    "threads": int(row["threads"]),
                    "time_seconds": float(row["time_seconds"]),
                    "width": row.get("width", ""),
                    "height": row.get("height", ""),
                }
            )
    return results


def add_speedup_and_efficiency(results):
    # Baseline unica: solo il dato sequenziale, NON il parallelo a 1 thread.
    seq_baseline = None
    for r in results:
        if r["mode"] == "sequenziale" and r["threads"] == 1:
            seq_baseline = r["time_seconds"]
            break

    if seq_baseline is None:
        raise ValueError("Baseline sequenziale non trovata nel CSV")

    for r in results:
        if r["time_seconds"] <= 0:
            r["speedup"] = ""
            r["efficiency"] = ""
            continue

        speedup = seq_baseline / r["time_seconds"]
        r["speedup"] = speedup
        r["efficiency"] = speedup / r["threads"]

results=read_benchmark_results("benchmark_results.csv")
add_speedup_and_efficiency(results)

# Scrive i risultati arricchiti in un nuovo CSV
with open("benchmark_results_with_speedup.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = [
        "mode",
        "scheduler",
        "threads",
        "time_seconds",
        "width",
        "height",
        "speedup",
        "efficiency",
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for r in results:
        writer.writerow(r)
        
#grafici
#servono i grafici per speedup, efficienza, e tempo su threads per ogni scheduler e modalità (parallelo vs sequenziale). 
# --- CODICE PER I GRAFICI by gemini ---

def plot_benchmarks(results):
    # Organizziamo i dati per facilitare il plotting
    # Creiamo una chiave unica per ogni combinazione di modalità e scheduler
    data_series = {}
    seq_time = None
    excluded_threads = {1, 256}

    for r in results:
        if r["mode"] == "sequenziale":
            seq_time = r["time_seconds"]
            continue

        # Escludiamo i valori richiesti dall'analisi grafica
        if r["threads"] in excluded_threads:
            continue
        
        # Filtriamo i dati per i grafici: saltiamo i casi oltre i 128/256 se vogliamo focus sul sweet spot,
        # ma qui li includiamo tutti come nel tuo CSV
        label = f"{r['mode']} - {r['scheduler']}"
        if label not in data_series:
            data_series[label] = {"threads": [], "time": [], "speedup": [], "efficiency": []}
        
        data_series[label]["threads"].append(r["threads"])
        data_series[label]["time"].append(r["time_seconds"])
        data_series[label]["speedup"].append(r["speedup"])
        data_series[label]["efficiency"].append(r["efficiency"])

    # Setup stile grafici
    plt.style.use('seaborn-v0_8-muted') # o 'ggplot'
    fig, axes = plt.subplots(3, 1, figsize=(12, 18))
    plt.subplots_adjust(hspace=0.4)

    x_ticks = [2, 4, 8, 16, 32, 64, 128]

    # 1. GRAFICO TEMPI DI ESECUZIONE
    ax = axes[0]
    for label, d in data_series.items():
        ax.plot(d["threads"], d["time"], marker='o', label=label)
    
    if seq_time:
        ax.axhline(y=seq_time, color='r', linestyle='--', label="Sequenziale Puro")
    
    ax.set_xscale('log', base=2)
    ax.set_xticks(x_ticks)
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
    ax.set_title("Tempo di Esecuzione vs Numero di Thread", fontsize=14, fontweight='bold')
    ax.set_xlabel("Threads")
    ax.set_ylabel("Secondi")
    ax.legend()
    ax.grid(True, which="both", ls="-", alpha=0.5)

    # 2. GRAFICO SPEEDUP ASSOLUTO
    ax = axes[1]
    for label, d in data_series.items():
        ax.plot(d["threads"], d["speedup"], marker='s', label=label)
    
    # Linea Speedup Ideale (Bisettrice fino a 16 thread, poi teorica)
    max_threads = max([max(d["threads"]) for d in data_series.values()])
    ax.plot([1, max_threads], [1, max_threads], color='black', linestyle=':', label="Speedup Ideale (S=N)")
    
    ax.set_xscale('log', base=2)
    ax.set_yscale('log', base=2) # Spesso utile per lo speedup
    ax.set_xticks(x_ticks)
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
    ax.get_yaxis().set_major_formatter(plt.ScalarFormatter())
    ax.set_title("Speedup Assoluto (Rif. Sequenziale)", fontsize=14, fontweight='bold')
    ax.set_xlabel("Threads")
    ax.set_ylabel("Speedup (T_seq / T_par)")
    ax.legend()
    ax.grid(True, which="both", ls="-", alpha=0.5)

    # 3. GRAFICO EFFICIENZA
    ax = axes[2]
    for label, d in data_series.items():
        ax.plot(d["threads"], d["efficiency"], marker='^', label=label)
    
    ax.axhline(y=1.0, color='black', linestyle=':', label="Efficienza Massima (1.0)")
    ax.set_xscale('log', base=2)
    ax.set_xticks(x_ticks)
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
    ax.set_title("Efficienza Parallela", fontsize=14, fontweight='bold')
    ax.set_xlabel("Threads")
    ax.set_ylabel("Efficienza (Speedup / N)")
    ax.set_ylim(0, 1.1)
    ax.legend()
    ax.grid(True, which="both", ls="-", alpha=0.5)

    # Salvataggio
    plt.savefig("analisi_performance_parallela.png", dpi=300, bbox_inches='tight')
    print("Grafico salvato come 'analisi_performance_parallela.png'")

# Esegui la funzione
plot_benchmarks(results)