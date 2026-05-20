import networkx as nx
import time
from brute_utils import solve_rpp_brute_force


def load_graph(filepath):
    """Считывает граф из текстового файла формата: u v weight is_required"""
    G = nx.Graph()
    with open(filepath, 'r') as file:
        for line in file:
            if not line.strip(): 
                continue
            u, v, weight, is_required = line.split()
            G.add_edge(int(u), int(v), weight=float(weight), is_required=bool(int(is_required)))
    return G


def get_complete_graph(G):
    """Строит метрическое замыкание графа на вершинах N_R"""
    A_R = [(u, v) for u, v, attrs in G.edges(data=True) if attrs.get('is_required')]

    N_R = set()
    for u, v in A_R:
        N_R.add(u)
        N_R.add(v)

    # Вычисляем кратчайшие пути
    shortest_paths_lengths = dict(nx.all_pairs_dijkstra_path_length(G, weight='weight'))
    shortest_paths_nodes = dict(nx.all_pairs_dijkstra_path(G, weight='weight'))

    G_R_C = nx.MultiGraph()

    for u, v in A_R:
        weight = G[u][v]['weight']
        G_R_C.add_edge(u, v, weight=weight, is_required=True)

    # Добавляем искусственные транзитные рёбра между всеми вершинами N_R
    N_R_list = list(N_R)
    for i in range(len(N_R_list)):
        for j in range(i + 1, len(N_R_list)):
            u, v = N_R_list[i], N_R_list[j]
            dist = shortest_paths_lengths[u][v]
            G_R_C.add_edge(u, v, weight=dist, is_required=False)
            
    return G_R_C, N_R, shortest_paths_lengths, shortest_paths_nodes


def simplify_graph(G_R_C, N_R, shortest_paths_lengths):
    """Упрощение графа G_R_C до G_R_S путем удаления лишних транзитных путей"""
    edges_to_remove = []

    for u, v, key, data in G_R_C.edges(keys=True, data=True):
        if not data.get('is_required'):
            cost_uv = data['weight']
            
            # Правило b: Удаляем искусственное ребро, если есть параллельное обязательное
            has_parallel_required = False
            for k_edge, d_edge in G_R_C[u][v].items():
                if k_edge != key and d_edge.get('is_required'):
                    if abs(d_edge['weight'] - cost_uv) < 1e-9:
                        has_parallel_required = True
                        break
            
            if has_parallel_required:
                edges_to_remove.append((u, v, key))
                continue
                
            # Правило a: Удаляем транзитивное искусственное ребро
            is_transitive = False
            for k in N_R:
                if k != u and k != v:
                    cost_uk = shortest_paths_lengths[u][k]
                    cost_kv = shortest_paths_lengths[k][v]
                    if abs(cost_uv - (cost_uk + cost_kv)) < 1e-9:
                        is_transitive = True
                        break
            
            if is_transitive:
                edges_to_remove.append((u, v, key))

    G_R_S = G_R_C.copy()
    G_R_S.remove_edges_from(edges_to_remove)
    return G_R_S


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


def decode_eulerian_circuit(G_euler, abstract_circuit, shortest_paths_nodes):
    """Разворачивает абстрактный цикл в маршрут в исходном графе"""    
    decoded_edges = []
    G_track = G_euler.copy()
    
    for u, v in abstract_circuit:
        edge_key = None
        is_req = False
        
        for key, data in G_track[u][v].items():
            if data.get('is_required'):
                edge_key = key
                is_req = True
                break
                
        if edge_key is None:
            edge_key = list(G_track[u][v].keys())[0]
            is_req = G_track[u][v][edge_key].get('is_required', False)
            
        G_track.remove_edge(u, v, key=edge_key)

        if is_req:
            decoded_edges.append((u, v))
        else:
            path = shortest_paths_nodes[u][v]
            for i in range(len(path) - 1):
                decoded_edges.append((path[i], path[i+1]))

    route_nodes = [decoded_edges[0][0]]
    for edge in decoded_edges:
        route_nodes.append(edge[1])
        
    return decoded_edges, route_nodes


def find_mst(G_R_S):
    """Выделяет КС индуцируемые A_R и строит MST на графе из КС"""

    A_R_edges = []
    A_S_edges = []
    
    for u, v, key, attrs in G_R_S.edges(keys=True, data=True):
        if attrs.get('is_required'):
            A_R_edges.append((u, v, attrs['weight']))
        else:
            A_S_edges.append((u, v, attrs['weight']))

    start_time_mst = time.perf_counter()

    G_required_only = nx.MultiGraph()
    G_required_only.add_weighted_edges_from(A_R_edges)
    
    components = list(nx.connected_components(G_required_only))
    
    if len(components) <= 1:
        time_mst = time.perf_counter() - start_time_mst
        return [], time_mst

    node_to_comp_idx = {}
    for idx, comp in enumerate(components):
        for node in comp:
            node_to_comp_idx[node] = idx
            
    # граф для MST, где вершины - КС на обязательных ребрах 
    G_comp = nx.MultiGraph()
    G_comp.add_nodes_from(range(len(components)))
    
    # Добавляем транзитные мосты между компонентами
    for u, v, weight in A_S_edges:
        if u in node_to_comp_idx and v in node_to_comp_idx:
            comp_u = node_to_comp_idx[u]
            comp_v = node_to_comp_idx[v]
            if comp_u != comp_v:
                G_comp.add_edge(comp_u, comp_v, weight=weight, u_min=u, v_min=v)

    if not nx.is_connected(G_comp):
        raise ValueError("Ошибка! Исходный граф не является связным!")
                    
    mst_comp = nx.minimum_spanning_tree(G_comp, weight='weight', algorithm='kruskal')
    
    # Возвращаем транзитные рёбра E_MST
    E_MST = []
    for i, j, data in mst_comp.edges(data=True):
        E_MST.append((data['u_min'], data['v_min'], data['weight']))
    
    time_mst = time.perf_counter() - start_time_mst
        
    # Возвращаем ровно два значения
    return E_MST, time_mst


def build_rpp_solution(G_R_S, E_MST, shortest_paths_lengths, shortest_paths_nodes):
    """Ищет MWPM строит цикл"""
    start_time_matching = time.perf_counter()

    G_odd = nx.MultiGraph()
    
    for u, v, key, attrs in G_R_S.edges(keys=True, data=True):
        if attrs.get('is_required'):
            G_odd.add_edge(u, v, weight=attrs['weight'])
            
    for u, v, weight in E_MST:
        G_odd.add_edge(u, v, weight=weight)

    V_odd = [v for v, degree in G_odd.degree() if degree % 2 == 1]

    G_match = nx.Graph()
    for i in range(len(V_odd)):
        for j in range(i + 1, len(V_odd)):
            u, v = V_odd[i], V_odd[j]
            dist = shortest_paths_lengths[u][v]
            G_match.add_edge(u, v, weight=dist)

    matching = nx.min_weight_matching(G_match, weight='weight')


    G_euler = nx.MultiGraph()
    
    for u, v, key, attrs in G_R_S.edges(keys=True, data=True):
        if attrs.get('is_required'):
            G_euler.add_edge(u, v, weight=attrs['weight'], is_required=True)
            
    for u, v, weight in E_MST:
        G_euler.add_edge(u, v, weight=weight, is_required=False)

    for u, v in matching:
        weight = G_match[u][v]['weight']
        G_euler.add_edge(u, v, weight=weight, is_required=False)

    assert all(degree % 2 == 0 for v, degree in G_euler.degree()), "Остались нечетные вершины!"
    assert nx.is_connected(G_euler), "Граф не является связным!"

    abstract_circuit = list(nx.eulerian_circuit(G_euler))

    total_time = time.perf_counter() - start_time_matching

    total_cost = sum(data['weight'] for u, v, data in G_euler.edges(data=True))
    
    # распаковка путей
    physical_edges, route_nodes = decode_eulerian_circuit(G_euler, abstract_circuit, shortest_paths_nodes)
    
    return route_nodes, total_cost, total_time


def solve(G):
    G_R_C, N_R, shortest_paths_lengths, shortest_paths_nodes = get_complete_graph(G)
    
    G_R_S = simplify_graph(G_R_C, N_R, shortest_paths_lengths)

    E_MST, mst_time = find_mst(G_R_S)

    route_nodes, total_cost, build_time = build_rpp_solution(
        G_R_S, E_MST, shortest_paths_lengths, shortest_paths_nodes
    )

    total_time = build_time + mst_time
        
    return route_nodes, total_cost, total_time


def get_graph_info(G: nx.Graph):
    opt = solve_rpp_brute_force(G)
    route_nodes, solver_cost, total_time = solve(G)
    ratio = solver_cost / opt


    vertices = G.number_of_nodes()
    edges = G.number_of_edges()
    required_edges = sum(1 for u, v, attrs in G.edges(data=True) if attrs.get('is_required') == True)
    row = {"cost": solver_cost, "opt": opt, 
           "ratio": ratio, "time": total_time,
           "V": vertices, "E": edges, "R": required_edges}
    
    return row
