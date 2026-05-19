import networkx as nx
import time

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
        return components, []

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
        
    return E_MST, time_mst