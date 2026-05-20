from gnp_utils import run_experiments
from gnp_utils import plot_ratio_comparisons, print_advanced_statistics
import pandas as pd
from brute_rpp import run_tests


def main():
    # 37 запусков на G(n, p)
    """seeds = list(range(42, 42 + 37)) 
    
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
    run_experiments(dense_cases, seeds)
    
    print("Генерация и решение на разреженных графах")
    run_experiments(sparse_cases, seeds)
    
    # Вывод статистик
    print_advanced_statistics(dense_cases, "Плотные графы")
    print_advanced_statistics(sparse_cases, "Разреженные графы")
    
    # Построение графиков
    plot_ratio_comparisons(dense_cases, sparse_cases, seeds)"""

    # Дальше тесты с известным оптимумом, используем полный перебор
    """ereq_samples = [1, 2, 3, 4, 5, 6]
    
    all_results = []
    
    for idx, e_req in enumerate(ereq_samples, start=1):
        df_result = run_tests(6, e_req, seed=idx)
        all_results.append(df_result)

    brute_force_results = pd.concat(all_results, axis=0)

    brute_force_results.to_csv('brute_tests.csv', index=True, encoding='utf-8')"""
    


if __name__ == "__main__":
    main()