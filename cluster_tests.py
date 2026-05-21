import random
import networkx as nx
import pandas as pd
from graph_utils import get_graph_info


def generate_double_complete_graph(seed: int) -> nx.Graph:
    """
    Генерирует граф со структурой две клики + мост 
    """
    if seed is not None:
        random.seed(seed)

    K1 = random.randint(2, 7)
    K2 = random.randint(2, 7)
    
    # Первая клика
    G1 = nx.complete_graph(K1)
    for u, v in G1.edges():
        G1[u][v]['weight'] = random.randint(1, 10)
        G1[u][v]['is_required'] = False

    # Обязательные рёбра в G1
    edges_G1 = list(G1.edges())
    num_req_G1 = random.randint(1, min(4, len(edges_G1)))
    req_edges_G1 = random.sample(edges_G1, num_req_G1)
    for u, v in req_edges_G1:
        G1[u][v]['is_required'] = True

    # Вторая клика
    G2 = nx.complete_graph(K2)

    mapping = {old: old + K1 for old in G2.nodes()}
    G2 = nx.relabel_nodes(G2, mapping)

    for u, v in G2.edges():
        G2[u][v]['weight'] = random.randint(1, 10)
        G2[u][v]['is_required'] = False

    edges_G2 = list(G2.edges())
    num_req_G2 = random.randint(1, min(3, len(edges_G2)))
    req_edges_G2 = random.sample(edges_G2, num_req_G2)
    for u, v in req_edges_G2:
        G2[u][v]['is_required'] = True
     
    # Объединяем
    G = nx.Graph()
    G.add_nodes_from(G1.nodes())
    G.add_nodes_from(G2.nodes())
    G.add_edges_from(G1.edges(data=True))
    G.add_edges_from(G2.edges(data=True))

    # Добавляем перемычку
    bridge_u = random.choice(list(G1.nodes()))
    bridge_v = random.choice(list(G2.nodes()))
    bridge_weight = random.randint(1, 10)
    bridge_required = random.random() < 0.5
    G.add_edge(bridge_u, bridge_v, weight=bridge_weight, is_required=bridge_required)

    return G


def generate_double_complete_graphs(num_graphs: int, start_seed: int) -> list:
    """
    Создаёт список из num_graphs графов со структурой две клики + перемычка
    """
    graphs = []
    for i in range(num_graphs):
        g = generate_double_complete_graph(start_seed + i)
        graphs.append(g)
    return graphs


def double_complete_tests(num_graphs: int, seed: int) -> pd.DataFrame:
    all_info = []
    graphs = generate_double_complete_graphs(num_graphs, seed)
    for g in graphs:
        all_info.append(get_graph_info(g))
    return pd.DataFrame(all_info)