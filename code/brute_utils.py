import networkx as nx
import itertools


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
