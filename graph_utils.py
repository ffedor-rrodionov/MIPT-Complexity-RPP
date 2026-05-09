import networkx as nx


def print_multigraph_edges(G, graph_name):
    print(f"\n=== {graph_name} ===")
    if len(G.edges()) == 0:
        print("Граф пустой")
        return
        
    for u, v, key, data in G.edges(keys=True, data=True):
        req_str = "Да" if data.get('is_required') else "Нет"
        print(f"Ребро ({u} <-> {v}): вес = {data['weight']}, обязательное = {req_str}")


def load_graph(filepath):
    # Инициализируем неориентированный граф
    G = nx.Graph()
    
    with open(filepath, 'r') as file:
        for line in file:                
            u, v, weight, is_required = line.split()
            u, v = int(u), int(v)
            weight = float(weight)
            is_required = bool(int(is_required))
            
            # Добавляем ребра в граф
            G.add_edge(u, v, weight=weight, is_required=is_required)
            
    return G


def get_complete_graph(G):
    # Обязательные рёбра
    A_R = [(u, v) for u, v, attrs in G.edges(data=True) if attrs.get('is_required')]

    # Вершины, инциндентные обязательным рёбрам
    N_R = set()
    for u, v in A_R:
        N_R.add(u)
        N_R.add(v)

    # Построение полного графа G_R_C

    # Вычисляем кратчайшие пути, их стоимости между всеми парами вершин графа
    # Возвращает словарь словарей: shortest_paths[u][v] = кратчайшее расстояние
    shortest_paths = dict(nx.all_pairs_dijkstra_path_length(G, weight='weight'))

    # Создаем мультиграф, так как могут появиться параллельные рёбра
    G_R_C = nx.MultiGraph()

    # Переносим в него все обязательные рёбра
    for u, v in A_R:
        weight = G[u][v]['weight']
        G_R_C.add_edge(u, v, weight=weight, is_required=True)

    # Добавляем искуственные рёбра
    N_R_list = list(N_R)
    for i in range(len(N_R_list)):
        for j in range(i + 1, len(N_R_list)):
            u, v = N_R_list[i], N_R_list[j]
            dist = shortest_paths[u][v]
            G_R_C.add_edge(u, v, weight=dist, is_required=False)
            
    return G_R_C, N_R, shortest_paths


def simplify_graph(G_R_C, N_R, shortest_paths):
    # Упрощение графа G_R_C до G_R_S

    edges_to_remove = []

    # Проходим по всем рёбрам графа G_R_C. 
    for u, v, key, data in G_R_C.edges(keys=True, data=True):

        # Нельзя удалять обязательные рёбра
        if not data.get('is_required'):
            cost_uv = data['weight']
            
            # Правило b: Удаляем искусственное ребро, если параллельно ему 
            # уже есть обязательное ребро с точно таким же весом.
            has_parallel_required = False
            for k_edge, d_edge in G_R_C[u][v].items():
                if k_edge != key and d_edge.get('is_required'):
                    # Сравниваем с учетом погрешности вычислений
                    if abs(d_edge['weight'] - cost_uv) < 1e-9:
                        has_parallel_required = True
                        break
            
            if has_parallel_required:
                edges_to_remove.append((u, v, key))
                continue
                
            # Правило a: Удаляем искусственное ребро (u, v) если существует 
            # промежуточная вершина k из N_R, такая что путь через k стоит столько же
            is_transitive = False
            for k in N_R:
                if k != u and k != v:
                    cost_uk = shortest_paths[u][k]
                    cost_kv = shortest_paths[k][v]
                    
                    if abs(cost_uv - (cost_uk + cost_kv)) < 1e-9:
                        is_transitive = True
                        break
            
            if is_transitive:
                edges_to_remove.append((u, v, key))

    # Создаем финальный упрощенный граф G_R_S
    G_R_S = G_R_C.copy()
    G_R_S.remove_edges_from(edges_to_remove)
    
    return G_R_S


def get_simplified_graph(filepath):
    G = load_graph(filepath)
    G_R_C, N_R, shortest_paths = get_complete_graph(G)
    G_R_S = simplify_graph(G_R_C, N_R, shortest_paths)
    return G_R_S
