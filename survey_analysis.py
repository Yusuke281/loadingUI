import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os
import scipy.stats as stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

def analyze_survey_data(filepath):
    """
    統合済みの実験データ(all_data.csv)を読み込み、
    アンケート項目（満足度、体感時間）に特化した分析と可視化を行う。
    """
    # --- 1. データの読み込み ---
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません - {filepath}")
        print("ヒント: 先に consolidate_data.py を実行して 'all_data.csv' を生成しましたか？")
        return
    except Exception as e:
        print(f"エラー: ファイルの読み込み中に問題が発生しました - {e}")
        return

    print("--- 読み込みデータ (最初の5行) ---")
    print(df.head())
    print("\n" + "="*50 + "\n")

    # --- 2. 基本統計量の表示 ---
    print("--- ローダーの種類ごとの平均値 ---")
    grouped_stats = df.groupby('loaderType')[['perceivedLoadingTime', 'satisfaction_score']].mean()
    print(grouped_stats)
    print("\n" + "="*50 + "\n")

    # --- 3. 仮説検定 (ANOVA & Tukey's HSD) ---
    print("--- 仮説検定: 分散分析 (ANOVA) ---")
    
    # 満足度スコアのANOVA検定
    satisfaction_groups = [df[df['loaderType'] == loader]['satisfaction_score'].dropna() for loader in df['loaderType'].unique()]
    f_val_sat, p_val_sat = stats.f_oneway(*satisfaction_groups)
    print(f"満足度スコアの分散分析: F値 = {f_val_sat:.4f}, p値 = {p_val_sat:.4f}")

    # 体感読み込み時間のANOVA検定
    time_groups = [df[df['loaderType'] == loader]['perceivedLoadingTime'].dropna() for loader in df['loaderType'].unique()]
    f_val_time, p_val_time = stats.f_oneway(*time_groups)
    print(f"体感読み込み時間の分散分析: F値 = {f_val_time:.4f}, p値 = {p_val_time:.4f}")
    print("\n" + "="*50 + "\n")

    # 多重比較 (Tukey's HSD)
    print("--- 仮説検定: 多重比較 (Tukey's HSD) ---")
    
    # 満足度スコアのTukey's HSD
    tukey_sat = pairwise_tukeyhsd(endog=df['satisfaction_score'], groups=df['loaderType'], alpha=0.05)
    print("--- 満足度スコアの多重比較結果 ---")
    print(tukey_sat)
    print("\n" + "="*50 + "\n")

    # 体感読み込み時間のTukey's HSD
    tukey_time = pairwise_tukeyhsd(endog=df['perceivedLoadingTime'], groups=df['loaderType'], alpha=0.05)
    print("--- 体感読み込み時間の多重比較結果 ---")
    print(tukey_time)
    print("\n" + "="*50 + "\n")


    # --- 4. 可視化 ---
    output_dir = 'survey_analysis_results'
    os.makedirs(output_dir, exist_ok=True)
    print(f"グラフは '{output_dir}' フォルダに保存されます。")

    sns.set_theme(style="whitegrid", font='Yu Gothic')

    # a. ローダーの種類別 満足度スコア
    plt.figure(figsize=(12, 7))
    sns.boxplot(data=df, x='loaderType', y='satisfaction_score', palette='viridis')
    plt.title('ローダーの種類別 満足度スコア', fontsize=16)
    plt.xlabel('ローダーの種類', fontsize=12)
    plt.ylabel('満足度スコア (1:不満 〜 5:満足)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'satisfaction_by_loader.png'))
    plt.close()

    # b. ローダーの種類別 体感読み込み時間
    plt.figure(figsize=(12, 7))
    sns.boxplot(data=df, x='loaderType', y='perceivedLoadingTime', palette='viridis')
    plt.title('ローダーの種類別 体感読み込み時間', fontsize=16)
    plt.xlabel('ローダーの種類', fontsize=12)
    plt.ylabel('体感読み込み時間 (秒)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'perceived_time_by_loader.png'))
    plt.close()

    # c. 実際の待ち時間と体感読み込み時間の関係
    plt.figure(figsize=(12, 7))
    # 'simulatedLoadingTime_sec' を使用するように修正
    sns.scatterplot(data=df, x='simulatedLoadingTime_sec', y='perceivedLoadingTime', hue='loaderType', palette='viridis', s=100, alpha=0.7)
    max_val = max(df['simulatedLoadingTime_sec'].max(), df['perceivedLoadingTime'].max())
    plt.plot([0, max_val], [0, max_val], ls="--", c=".3")
    plt.title('実際の待ち時間と体感読み込み時間の関係', fontsize=16)
    plt.xlabel('実際の待ち時間 (秒)', fontsize=12)
    plt.ylabel('体感読み込み時間 (秒)', fontsize=12)
    plt.grid(True)
    plt.legend(title='ローダーの種類')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'simulated_vs_perceived_time.png'))
    plt.close()

    print("\n分析が完了しました。")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='統合済みの実験データ(all_data.csv)からアンケート関連の分析を行います。')
    parser.add_argument('filepath', type=str, default='all_data.csv', nargs='?',
                        help='分析するCSVファイルのパス (デフォルト: all_data.csv)')

    args = parser.parse_args()
    analyze_survey_data(args.filepath)