from graph_utils import load_graph, get_complete_graph, simplify_graph
from find_mst import find_mst
from build_solution import build_rpp_solution


def main():
    filepath = 'graph_input.txt'

    G = load_graph(filepath)
    G_R_C, N_R, shortest_paths_lengths, shortest_paths_nodes = get_complete_graph(G)
    
    G_R_S = simplify_graph(G_R_C, N_R, shortest_paths_lengths)

    E_MST, mst_time = find_mst(G_R_S)

    route_nodes, total_cost, build_time = build_rpp_solution(
        G_R_S, E_MST, shortest_paths_lengths, shortest_paths_nodes
    )

    total_time = build_time + mst_time

    print(f"Время работы алгоритма: {total_time}")
    print(f"Стоимость маршрута: {total_cost}")
    print("Последовательность обхода вершин: ")
    print(" -> ".join(map(str, route_nodes)))

if __name__ == "__main__":
    main()