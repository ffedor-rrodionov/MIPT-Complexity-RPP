import random
import itertools
import pandas as pd
from graph_utils import get_graph_info
from tree_tests import generate_trees


def generate_cyclic(n, start_seed):
    trees = generate_trees(n, start_seed)

    for idx, t in enumerate(trees):
        random.seed(start_seed + idx + 10_000)

        num_vertices = t.number_of_nodes()
        num_edges_tree = t.number_of_edges()

        max_add = num_vertices * (num_vertices - 1) // 2 - num_edges_tree

        if max_add == 0:
            continue

        if num_edges_tree <= 5:
            low, high = 1, 2
        elif num_edges_tree <= 10:
            low, high = 1, 3
        else:
            low, high = 1, 4
        
        num_add = random.randint(low, min(high, max_add))

        missing_edges = [
            (u, v) for u, v in itertools.combinations(range(num_vertices), 2)
            if not t.has_edge(u, v)
        ]
        chosen = random.sample(missing_edges, num_add)

        for u, v in chosen:
            weight = random.randint(1, 10)
            t.add_edge(u, v, weight=weight, is_required=False)
    
    return trees


def cyclic_tests(cyclic_cnt: int, seed):
    all_info = []
    cyclic = generate_cyclic(cyclic_cnt, seed)
    for c in cyclic:
        all_info.append(get_graph_info(c))
    
    return pd.DataFrame(all_info)
