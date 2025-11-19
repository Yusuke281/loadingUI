import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os
import numpy as np
import scipy.stats as stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

def analyze_data(filepath):
    """
    CSVデータを読み込み、分析と可視化を行う関数。

    Args:
        filepath (str): 分析対象のCSVファイルへのパス。
    """
    # --- 1. データの読み込み ---
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません - {filepath}")
        return
    except Exception as e:
        print(f"エラー: ファイルの読み込み中に問題が発生しました - {e}")
        return

    print("--- CSVデータの最初の5行 ---")
    print(df.head())
    print("\n" + "="*50 + "\n")

    # --- 正規化・純粋なタスク時間の計算 ---
    df['pureTaskDuration'] = df['taskDuration'] - df['simulatedLoadingTime']
    df['pureTaskDuration'] = df['pureTaskDuration'].clip(lower=0)

    base_metrics = ['taskDuration', 'pureTaskDuration', 'mouseDistance', 'rageClicks']
    metrics_to_analyze = list(base_metrics)

    if 'optimalMouseDistance' in df.columns:
        df['normalizedMouseDistance'] = df['mouseDistance'] / df['optimalMouseDistance']
        df['normalizedMouseDistance'].replace([np.inf, -np.inf], np.nan, inplace=True)
        df['normalizedMouseDistance'].fillna(1, inplace=True)
        metrics_to_analyze.append('normalizedMouseDistance')
    else:
        print("警告: 'optimalMouseDistance' 列が見つかりません。正規化マウス移動距離の分析はスキップされます。")


    # --- 2. 基本統計量の表示 ---
    print("--- 全体の基本統計量 ---")
    print(df[metrics_to_analyze].describe())
    print("\n" + "="*50 + "\n")

    # --- 3. ローダーの種類ごとの集計 ---
    print("--- ローダーの種類ごとの平均値 ---")
    grouped_by_loader = df.groupby('loaderType')[metrics_to_analyze].mean()
    print(grouped_by_loader)
    print("\n" + "="*50 + "\n")
    
    print("--- ローダーの種類と待機時間ごとの平均値 ---")
    if 'simulatedLoadingTime' in df.columns:
        grouped_by_loader_time = df.groupby(['loaderType', 'simulatedLoadingTime'])[metrics_to_analyze].mean()
        print(grouped_by_loader_time)
        print("\n" + "="*50 + "\n")
    else:
        print("simulatedLoadingTime 列が見つからないため、この集計はスキップされました。")


    # --- 4. 仮説検定 (ANOVA & Tukey's HSD) ---
    print("\n" + "="*50 + "\n")
    print("--- 仮説検定: 分散分析 (ANOVA) ---")
    
    for metric in metrics_to_analyze:
        groups = [df[df['loaderType'] == loader][metric] for loader in df['loaderType'].unique()]
        f_val, p_val = stats.f_oneway(*groups)
        print(f"{metric}の分散分析: F値 = {f_val:.4f}, p値 = {p_val:.4f}")

    print("\n" + "="*50 + "\n")
    print("--- 仮説検定: 多重比較 (Tukey's HSD) ---")

    for metric in metrics_to_analyze:
        tukey_result = pairwise_tukeyhsd(endog=df[metric], groups=df['loaderType'], alpha=0.05)
        print(f"--- {metric}の多重比較結果 ---")
        print(tukey_result)
        print("\n" + "-"*50 + "\n")


    # --- 5. 可視化 ---
    output_dir = 'analysis_results'
    os.makedirs(output_dir, exist_ok=True)
    print(f"グラフは '{output_dir}' フォルダに保存されます。")

    sns.set_theme(style="whitegrid", font='Yu Gothic')

    # a. ローダーの種類別タスク時間
    plt.figure(figsize=(12, 7))
    sns.boxplot(data=df, x='loaderType', y='taskDuration', palette='viridis')
    plt.title('ローダーの種類別 タスク時間', fontsize=16)
    plt.xlabel('ローダーの種類', fontsize=12)
    plt.ylabel('タスク時間 (ms)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'duration_by_loader_boxplot.png'))
    plt.close()

    # b. ローダーの種類別純粋なタスク時間
    plt.figure(figsize=(12, 7))
    sns.boxplot(data=df, x='loaderType', y='pureTaskDuration', palette='viridis')
    plt.title('ローダーの種類別 純粋なタスク時間', fontsize=16)
    plt.xlabel('ローダーの種類', fontsize=12)
    plt.ylabel('純粋なタスク時間 (ms)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'pure_duration_by_loader_boxplot.png'))
    plt.close()

    # c. ローダーの種類別 正規化マウス移動距離 (非効率スコア)
    if 'normalizedMouseDistance' in metrics_to_analyze:
        plt.figure(figsize=(12, 7))
        sns.boxplot(data=df, x='loaderType', y='normalizedMouseDistance', palette='viridis')
        plt.title('ローダーの種類別 正規化マウス移動距離（非効率スコア）', fontsize=16)
        plt.xlabel('ローダーの種類', fontsize=12)
        plt.ylabel('非効率スコア (実績/最短)', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'normalized_distance_by_loader_boxplot.png'))
        plt.close()

    # d. ローダーの種類別レイジクリック数
    plt.figure(figsize=(12, 7))
    mean_rage_clicks = df.groupby('loaderType')['rageClicks'].mean().reset_index()
    sns.barplot(data=mean_rage_clicks, x='loaderType', y='rageClicks', palette='viridis')
    plt.title('ローダーの種類別 平均レイジクリック数', fontsize=16)
    plt.xlabel('ローダーの種類', fontsize=12)
    plt.ylabel('平均レイジクリック数', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'rageclicks_by_loader_barchart.png'))
    plt.close()
    
    print("\n分析が完了しました。")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ECサイト利用実験のCSVデータを分析します。')
    parser.add_argument('filepath', type=str, help='分析するCSVファイルのパス (例: task_timings.csv)')
    
    args = parser.parse_args()
    
    analyze_data(args.filepath)
