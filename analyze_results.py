import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os


def print_aggregated_statistics(df, dataset_name, metric):
    """
    Вычисляет и выводит ключевые агрегированные статистики по метрике
    """
    data = df[metric]

    min_val = data.min()
    max_val = data.max()
    mean_val = data.mean()
    median_val = data.median()
    q75 = data.quantile(0.75)
    q95 = data.quantile(0.95)

    print(f"--- Статистика '{metric}' для: {dataset_name} ---")
    print(f"  Минимум:       {min_val:.6f}")
    print(f"  Максимум:      {max_val:.6f}")
    print(f"  Среднее:       {mean_val:.6f}")
    print(f"  Медиана:       {median_val:.6f}")
    print(f"  Квантиль 0.75: {q75:.6f}")
    print(f"  Квантиль 0.95: {q95:.6f}")
    print()


def plot_empirical_distribution(df, dataset_name, metric, bins=30):
    """
    Строит и сохраняет график эмпирического распределения
    """
    data = df[metric]

    plt.figure(figsize=(10, 6))
    sns.histplot(data, bins=bins, kde=True, color='steelblue', edgecolor='black', alpha=0.7)
    
    plt.title(f'Эмпирическое распределение: {metric}\nНабор тестов: {dataset_name}', fontsize=14, fontweight='bold')
    plt.xlabel(metric.capitalize(), fontsize=12)
    plt.ylabel('Количество графов', fontsize=12)
    plt.grid(axis='y', alpha=0.5, linestyle='--')
    
    mean_val = data.mean()
    q95_val = data.quantile(0.95)
    
    plt.axvline(mean_val, color='red', linestyle='dashed', linewidth=2, label=f'Среднее: {mean_val:.4f}')
    plt.axvline(q95_val, color='green', linestyle='dashed', linewidth=2, label=f'95%-Квантиль: {q95_val:.4f}')
    
    # Добавим границу 1.5
    if metric == 'ratio':
        plt.axvline(1.5, color='purple', linestyle='solid', linewidth=2.5, label='Теоретический предел (1.5)')
        
    plt.legend(fontsize=11)
    plt.tight_layout()
    
    # Сохраняем график
    clean_name = dataset_name.replace('.csv', '')
    filename = f'dist_{clean_name}_{metric}.png'
    plt.savefig(filename, dpi=300)
    plt.close()


def main():
    datasets = ['trees.csv', 'cyclic.csv', 'double_complete.csv', 'complete.csv']
    
    metrics_to_analyze = ['time', 'ratio']
    
    sns.set_theme(style="whitegrid", palette="muted")
    
    for dataset in datasets:
        if os.path.exists(dataset):
            df = pd.read_csv(dataset)
            
            for metric in metrics_to_analyze:
                print_aggregated_statistics(df, dataset, metric)
                plot_empirical_distribution(df, dataset, metric)
            print("\n")


if __name__ == "__main__":
    main()