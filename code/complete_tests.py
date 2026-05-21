import random
import networkx as nx
import pandas as pd
from code.graph_utils import get_graph_info


def generate_complete_graph(seed: int) -> nx.Graph:
    """
    Генерирует один полный граф, в котором:
    Число вершин от 5 до 20
    Все ребра имеют случайный вес от 1 до 10
    Случайно выбираются от 3 до 7 обязательных рёбер 
    """
    if seed is not None:
        random.seed(seed)

    V = random.randint(5, 20)
    G = nx.complete_graph(V)

    for u, v in G.edges():
        G[u][v]['weight'] = random.randint(1, 10)
        G[u][v]['is_required'] = False

    # Выбираем обязательные рёбра
    all_edges = list(G.edges())
    num_required = random.randint(3, 7)

    num_required = min(num_required, len(all_edges))
    required_edges = random.sample(all_edges, num_required)

    for u, v in required_edges:
        G[u][v]['is_required'] = True

    return G


def generate_complete_graphs(num_graphs: int, start_seed: int) -> list:
    """
    Создаёт список из num_graphs полных графов
    """
    graphs = []
    for i in range(num_graphs):
        g = generate_complete_graph(start_seed + i)
        graphs.append(g)
    return graphs


def complete_tests(num_graphs: int, seed: int) -> pd.DataFrame:
    all_info = []
    graphs = generate_complete_graphs(num_graphs, seed)
    for g in graphs:
        all_info.append(get_graph_info(g))
    return pd.DataFrame(all_info)