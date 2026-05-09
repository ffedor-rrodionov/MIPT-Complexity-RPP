import networkx as nx

def find_components_and_mst(G_R_S):
    """
    Принимает упрощенный граф G_R_S, выделяет компоненты связности 
    обязательных рёбер и строит минимальное остовное дерево,
    используя транзитные рёбра графа.
    """

    A_R_edges = []
    A_S_edges = []
    
    for u, v, key, attrs in G_R_S.edges(keys=True, data=True):
        if attrs.get('is_required'):
            A_R_edges.append((u, v, attrs['weight']))
        else:
            A_S_edges.append((u, v, attrs['weight']))


    # Выделяем компоненты связности на обязательных ребрах
    # Строим подграф только из обязательных рёбер
    G_required_only = nx.MultiGraph()
    G_required_only.add_weighted_edges_from(A_R_edges)
    
    # Находим компоненты связности
    components = list(nx.connected_components(G_required_only))
    
    # Если граф обязательных рёбер уже связен MST не требуется
    if len(components) <= 1:
        return components, []

    # Построение MST на компонентах с использованием транзитных рёбер
    node_to_comp_idx = {}
    for idx, comp in enumerate(components):
        for node in comp:
            node_to_comp_idx[node] = idx
            
    # Создаем граф где вершины компоненты связности
    G_comp = nx.MultiGraph()
    G_comp.add_nodes_from(range(len(components)))
    
    for u, v, weight in A_S_edges:
        if u in node_to_comp_idx and v in node_to_comp_idx:
            comp_u = node_to_comp_idx[u]
            comp_v = node_to_comp_idx[v]
            
            # Если ребро соединяет разные компоненты
            if comp_u != comp_v:
                G_comp.add_edge(comp_u, comp_v, weight=weight, u_min=u, v_min=v)
                    

    if not nx.is_connected(G_comp):
        raise ValueError("Ошибка! Исходный граф не является связным!")
                    
    # находим минимальное остовное дерево
    mst_comp = nx.minimum_spanning_tree(G_comp, weight='weight')
    
    # Извлекаем физические транзитные рёбра E_MST
    E_MST = []
    for i, j, data in mst_comp.edges(data=True):
        E_MST.append((data['u_min'], data['v_min'], data['weight']))
    
        
    return components, E_MST
