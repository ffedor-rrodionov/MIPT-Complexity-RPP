import networkx as nx


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