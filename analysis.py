import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os
import numpy as np

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
    # 純粋なタスク時間
    df['pureTaskDuration'] = df['taskDuration'] - df['simulatedLoadingTime']
    df['pureTaskDuration'] = df['pureTaskDuration'].clip(lower=0)

    # 正規化マウス移動距離 (0除算を回避)
    # optimalMouseDistanceが0またはNaNの場合は、非効率スコアを1（最適）とする
    df['normalizedMouseDistance'] = df['mouseDistance'] / df['optimalMouseDistance']
    df['normalizedMouseDistance'].replace([np.inf, -np.inf], np.nan, inplace=True)
    df['normalizedMouseDistance'].fillna(1, inplace=True)


    # --- 2. 基本統計量の表示 ---
    print("--- 全体の基本統計量 ---")
    print(df[['taskDuration', 'pureTaskDuration', 'mouseDistance', 'normalizedMouseDistance', 'rageClicks']].describe())
    print("\n" + "="*50 + "\n")

    # --- 3. ローダーの種類ごとの集計 ---
    print("--- ローダーの種類ごとの平均値 ---")
    metrics_to_analyze = ['taskDuration', 'pureTaskDuration', 'mouseDistance', 'normalizedMouseDistance', 'rageClicks']
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


    # --- 4. 可視化 ---
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
