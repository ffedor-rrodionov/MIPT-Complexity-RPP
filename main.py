import networkx as nx
import graph_utils

if __name__ == "__main__":
    filepath = 'graph_input.txt'
    
    # Шаг 1: Загрузка исходного графа
    G_initial = graph_utils.load_graph(filepath)
    
    # Для вывода преобразуем во временный мультиграф
    G_initial_multi = nx.MultiGraph(G_initial)
    graph_utils.print_multigraph_edges(G_initial_multi, "1. Исходный граф (G)")
    
    # Шаг 2: Построение полного графа G_R_C
    G_R_C, N_R, shortest_paths = graph_utils.get_complete_graph(G_initial)
    graph_utils.print_multigraph_edges(G_R_C, "2. Полный граф (G_R_C) со всеми искусственными ребрами")
    
    # Шаг 3: Упрощение графа до G_R_S
    G_R_S = graph_utils.simplify_graph(G_R_C, N_R, shortest_paths)
    graph_utils.print_multigraph_edges(G_R_S, "3. Упрощенный граф (G_R_S) после применения правил a и b")