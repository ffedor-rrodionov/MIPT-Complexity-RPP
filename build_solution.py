import networkx as nx
import time


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