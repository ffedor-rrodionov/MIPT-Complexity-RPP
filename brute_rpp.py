import networkx as nx
import itertools
import random
import pandas as pd
from build_solution import solve


def generate_all_graphs_nx(n: int, n_req: int, seed: int = None):
    """
    Генерирует все связные графы на n вершинах с случано назначенными стоимостями ребер
    В каждом графе ровно n_req ребер назначаются обязательными
    """
    if seed is not None:
        random.seed(seed)

    all_possible_edges = list(itertools.combinations(range(n), 2))
    max_possible_edges = len(all_possible_edges)

    if n_req > max_possible_edges:
        raise ValueError(f"Невозможно выбрать {n_req} обязательных ребер в графе на {n} вершинах, максимум {max_possible_edges}")

    graphs_dict = {}
    
    min_edges = max(n - 1, n_req)
    
    for r in range(min_edges, max_possible_edges + 1):
        for subset in itertools.combinations(all_possible_edges, r):
            
            G_test = nx.Graph()
            G_test.add_nodes_from(range(n))
            G_test.add_edges_from(subset)
            
            # Скипаем несвязные графы
            if not nx.is_connected(G_test):
                continue
                
            key = f"e={r}_n={n}_nreq={n_req}"
            if key not in graphs_dict:
                graphs_dict[key] = []
                
            G = nx.Graph()
            G.add_nodes_from(range(n))
            
            # Случайно выбираем n_req обязательных ребер из текущего подмножества
            required_edges_set = set(random.sample(subset, n_req))
            
            for u, v in subset:
                weight = random.randint(1, 20)
                is_req = (u, v) in required_edges_set
                
                G.add_edge(u, v, weight=weight, is_required=is_req)
                
            graphs_dict[key].append(G)
            
    return graphs_dict


def solve_rpp_brute_force(G: nx.Graph):
    """
    Находит точный оптимальный маршрут для задачи полным перебором.
    """
    required_edges = [
        (u, v, data['weight']) 
        for u, v, data in G.edges(data=True) 
        if data.get('is_required', False)
    ]
    
    if not required_edges:
        return 0

    dist = nx.floyd_warshall(G, weight='weight')
    
    min_total_cost = float('inf')
    
    start_node = required_edges[0][0]
    
    for perm in itertools.permutations(required_edges):
        k = len(perm)
        
        for dirs in itertools.product([True, False], repeat=k):
            current_cost = 0
            current_node = start_node
            
            for i, edge in enumerate(perm):
                u, v, weight = edge
                entry_node = u if dirs[i] else v
                exit_node = v if dirs[i] else u
                
                current_cost += dist[current_node][entry_node] + weight
                current_node = exit_node
                
            current_cost += dist[current_node][start_node]
            
            if current_cost < min_total_cost:
                min_total_cost = current_cost
                
    return min_total_cost


def run_tests(n: int, e_req: int, seed: int = None):
    """
    Запускает точный перебор и эвристику на всех сгенерированных графах
    Собирает результаты в датафрейм
    """

    # Генерируем графы
    graphs_dict = generate_all_graphs_nx(n, e_req, seed)
    
    results_data = []
    index_names = []
    
    for key, graph_list in graphs_dict.items():
        for i, G in enumerate(graph_list):
            row_name = f"{key}_graph{i}_seed{seed}"
            
            opt = solve_rpp_brute_force(G)
            
            if opt == float('inf'):
                raise ValueError("Обязательные ребра в разных КС")
                
            route_nodes, solver_cost, total_time = solve(G)
            
            ratio = (solver_cost / opt)
            
            results_data.append({
                'e_req': e_req,
                'opt': opt,
                'cost': solver_cost,
                'cost/opt': ratio,
                'time': total_time
            })
            index_names.append(row_name)
            
    results = pd.DataFrame(results_data, index=index_names)    
    return results
