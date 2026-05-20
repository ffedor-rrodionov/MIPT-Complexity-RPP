from gnp_utils import run_experiments
from gnp_utils import plot_ratio_comparisons, print_advanced_statistics
import pandas as pd
from tree_tests import tree_tests

def main():
    # 37 запусков на G(n, p)
    START_SEED = 42
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
    TREES_CNT = 170
    trees_result = tree_tests(TREES_CNT, START_SEED)
    trees_result.to_csv("trees.csv")
    print(trees_result)


if __name__ == "__main__":
    main()