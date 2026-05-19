import networkx as nx
import random
import numpy as np
import matplotlib.pyplot as plt
from graph_utils import load_graph
from build_solution import solve


def generate_rpp_test_case(n, p_edge, p_mandatory_prob, seed=None):
    """
    n: количество вершин
    p_edge: вероятность существования ребра
    p_mandatory_prob: вероятность того, что ребро станет обязательным
    """
    if seed is not None:
        random.seed(seed)

    while True:
        G = nx.erdos_renyi_graph(n, p_edge)
        if nx.is_connected(G):
            break
            
    mandatory_edges = []
    while not mandatory_edges:
        mandatory_edges = []
        for u, v in G.edges():
            if random.random() < p_mandatory_prob:
                mandatory_edges.append((u, v))
    
    nx.set_edge_attributes(G, False, "is_required")
    for u, v in mandatory_edges:
        G[u][v]["is_required"] = True
        
    for u, v in G.edges():
        G[u][v]["weight"] = random.randint(1, 20)
        
    total_mandatory_weight = sum(G[u][v]["weight"] for u, v in mandatory_edges)
        
    return G, total_mandatory_weight


def save_rpp_graph_to_txt(G, filename):
    """
    Сохраняет граф в текстовый файл.
    Формат строки: u v weight is_required
    """
    with open(filename, 'w') as f:
        for u, v, data in G.edges(data=True):
            weight = data.get('weight', 1.0)
            is_required = 1 if data.get('is_required', False) else 0
            
            f.write(f"{u} {v} {float(weight)} {is_required}\n")


def run_experiments(cases, seeds):
    for case, info in cases.items():
        for seed in seeds:
            G, req_sum = generate_rpp_test_case(case, info["p_edge"], 
                                       info["p_mandatory"], seed=seed)
            results = solve(G)
            
            info["results"][seed] = {
                "route": results[0], 
                "cost": results[1],
                "time": results[2], 
                "req_sum": req_sum,
                "ratio": results[1] / req_sum
            }


def print_advanced_statistics(cases, label):
    print(f"\n=== Статистика: {label} ===")
    print("-" * 95)
    print(f"{'N':<5} | {'Метрика':<10} | {'Mean':<10} | {'Median':<10} | {'Min':<10} | {'Max':<10} | {'25%, Q1':<10} | {'75%, Q3':<10}")
    print("-" * 95)
    
    for case, info in cases.items():
        if not info["results"]:
            continue
            
        times = [res["time"] for res in info["results"].values()]
        ratios = [res["ratio"] for res in info["results"].values()]
        
        for metric_name, data in [("Time (s)", times), ("Ratio", ratios)]:
            mean_val = np.mean(data)
            median_val = np.median(data)
            min_val = np.min(data)
            max_val = np.max(data)
            q25 = np.percentile(data, 25)
            q75 = np.percentile(data, 75)
            
            print(f"{case:<5} | {metric_name:<10} | {mean_val:<10.4f} | {median_val:<10.4f} | {min_val:<10.4f} | {max_val:<10.4f} | {q25:<10.4f} | {q75:<10.4f}")
    print("-" * 95)


def plot_ratio_comparisons(dense_cases, sparse_cases, seeds):
    for n in dense_cases.keys():
        if not dense_cases[n]["results"] or not sparse_cases[n]["results"]:
            continue
            
        dense_ratios = [dense_cases[n]["results"][seed]["ratio"] for seed in seeds]
        sparse_ratios = [sparse_cases[n]["results"][seed]["ratio"] for seed in seeds]
        
        plt.figure(figsize=(14, 6))
        
        plt.plot(seeds, dense_ratios, marker='o', linestyle='-', color='blue', 
                 label=f'Плотный (p={dense_cases[n]["p_edge"]})', linewidth=2, markersize=5)
        
        plt.plot(seeds, sparse_ratios, marker='s', linestyle='--', color='red', 
                 label=f'Разреженный (p={sparse_cases[n]["p_edge"]})', linewidth=2, markersize=5)
        
        plt.title(f'Сравнение отношения стоимости алгоритма к сумме обязательных ребер, N={n} вершин', fontsize=14)
        plt.xlabel('Seed, номер графа', fontsize=12)
        plt.ylabel('Ratio, cost \\ cost(E_R)', fontsize=12)
        
        plt.xticks(seeds, rotation=45, ha='right', fontsize=9)
        
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(fontsize=11)
        plt.tight_layout()
        
        filename = f'ratio_comparison_N{n}.png'
        plt.savefig(filename, dpi=300)
        print(f"Сохранен график: {filename}")
        plt.close()
