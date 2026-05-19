from gnp_utils import run_experiments
from gnp_utils import plot_ratio_comparisons, print_advanced_statistics


def main():
    # 37 запусков на G(n, p)
    seeds = list(range(42, 42 + 37)) 
    
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
    plot_ratio_comparisons(dense_cases, sparse_cases, seeds)


if __name__ == "__main__":
    main()