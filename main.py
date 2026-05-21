from gnp_utils import run_experiments
from gnp_utils import plot_ratio_comparisons, print_advanced_statistics
import pandas as pd
from tree_tests import tree_tests
from tree_add_tests import cyclic_tests
from cluster_tests import double_complete_tests
from complete_tests import complete_tests

def main():
    # 37 запусков на G(n, p)
    START_SEED = 67
    
    GNP_CNT = 37
    dense_cases = {
        40: {"p_edge": 0.5, "p_mandatory": 0.35, "results": {}}, 
        50: {"p_edge": 0.5, "p_mandatory": 0.3,  "results": {}}, 
        70: {"p_edge": 0.5, "p_mandatory": 0.25, "results": {}}
    }
    
    sparse_cases = {
        40: {"p_edge": 0.05, "p_mandatory": 0.15, "results": {}}, 
        50: {"p_edge": 0.05, "p_mandatory": 0.15, "results": {}}, 
        70: {"p_edge": 0.05, "p_mandatory": 0.10, "results": {}}
    }

    print("Генерация и решение на плотных графах")
    run_experiments(dense_cases, list(range(START_SEED, START_SEED + GNP_CNT)))
    
    print("Генерация и решение на разреженных графах")
    run_experiments(sparse_cases, list(range(START_SEED, START_SEED + GNP_CNT)))
    
    # Вывод статистик
    print_advanced_statistics(dense_cases, "Плотные графы")
    print_advanced_statistics(sparse_cases, "Разреженные графы")
    
    # Построение графиков для G(n, p)
    plot_ratio_comparisons(dense_cases, sparse_cases, list(range(START_SEED, START_SEED + GNP_CNT)))
    
    # Тесты для деревьев
    TREES_CNT = 350
    trees_result = tree_tests(TREES_CNT, START_SEED)
    trees_result.to_csv("trees.csv")
    print(trees_result)


    # Тесты для разреженных графов, близких к деревьям
    CYCLIC_CNT = 350
    cyclic_result = cyclic_tests(CYCLIC_CNT, START_SEED)
    cyclic_result.to_csv("cyclic.csv")
    print(cyclic_result[cyclic_result['ratio'] > 1.0])


    # Тесты для двух полных графов, соединённых ребром-перемычкой
    DOUBLE_COMPLETE_CNT = 350
    double_complete_result = double_complete_tests(DOUBLE_COMPLETE_CNT, START_SEED)
    double_complete_result.to_csv("double_complete.csv")
    print(double_complete_result[double_complete_result['ratio'] > 1.0])
    

    # Тесты для полных графов
    COMPLETE_CNT = 350
    complete_result = complete_tests(COMPLETE_CNT, START_SEED)
    complete_result.to_csv("complete.csv")
    print(complete_result[complete_result['ratio'] > 1.0])
    print(max(complete_result["ratio"]))


if __name__ == "__main__":
    main()