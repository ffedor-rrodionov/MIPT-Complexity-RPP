from code.graph_utils import get_graph_info
import pandas as pd
import random
import networkx as nx


def generate_tree(n: int, max_required: int, seed: int):
    """Генерирует дерево на n вершинах с помощью кода прюфера, используя """
    if seed is not None:
        random.seed(seed)
    
    if n < 3:
        raise ValueError("Нет смысла рассматривать деревья на менее чем 3 вершинах!")
    
    prufer_sequence = [random.randint(0, n - 1) for _ in range(n - 2)]
    tree = nx.from_prufer_sequence(prufer_sequence)

    all_edges = list(tree.edges())
    num_required = random.randint(1, min(max_required, len(all_edges)))

    required_edges = set(random.sample(all_edges, num_required))

    for u, v in all_edges:
        tree[u][v]['weight'] = random.randint(1, 10)
        
        if (u, v) in required_edges or (v, u) in required_edges:
            tree[u][v]['is_required'] = True
        else:
            tree[u][v]['is_required'] = False

    return tree


def generate_trees(tree_cnt: int, start_seed: int):
    """Генерирует заданное количество деревьев с  заданным сидом"""
    seeds = list(range(start_seed, start_seed + tree_cnt))
    result = []
    for seed in seeds:
        num_v = random.randint(3, 17)
        result.append(generate_tree(num_v, 7, seed))
    
    return result


def tree_tests(tree_cnt: int, seed):
    all_info = []
    trees = generate_trees(tree_cnt, seed)
    for t in trees:
        all_info.append(get_graph_info(t))
    
    return pd.DataFrame(all_info)
