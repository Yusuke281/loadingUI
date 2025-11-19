import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os
import json
import scipy.stats as stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# script.jsからコピーした実験試行データ
# 本来はscript.jsを直接読み込むのが望ましいが、簡略化のためハードコードする
EXPERIMENT_TRIALS_JSON = """
[
    { "taskHTML": "<strong>ブロッコリー</strong>と<strong>クッキー</strong>をカートに入れてください", "loader": "bar-color", "time": 5000 },
    { "taskHTML": "<strong>なす</strong>と<strong>オレンジジュース</strong>をカートに入れてください", "loader": "bar", "time": 5000 },
    { "taskHTML": "<strong>トマト</strong>と<strong>りんご</strong>をカートに入れてください", "loader": "none", "time": 1500 },
    { "taskHTML": "<strong>キウイ</strong>と<strong>コーラ</strong>をカートに入れてください", "loader": "spinner", "time": 3000 },
    { "taskHTML": "<strong>ピーマン</strong>と<strong>ケーキ</strong>をカートに入れてください", "loader": "none", "time": 3000 },
    { "taskHTML": "<strong>ほうれん草</strong>と<strong>オレンジ</strong>をカートに入れてください", "loader": "skeleton-color", "time": 5000 },
    { "taskHTML": "<strong>バナナ</strong>と<strong>チーズケーキ</strong>をカートに入れてください", "loader": "spinner", "time": 1500 },
    { "taskHTML": "<strong>にんじん</strong>と<strong>コーヒー</strong>をカートに入れてください", "loader": "bar-color", "time": 1500 },
    { "taskHTML": "<strong>ブロッコリー</strong>と<strong>緑茶</strong>をカートに入れてください", "loader": "none", "time": 5000 },
    { "taskHTML": "<strong>きゅうり</strong>と<strong>クッキー</strong>をカートに入れてください", "loader": "bar", "time": 3000 },
    { "taskHTML": "<strong>カリフラワー</strong>と<strong>メロン</strong>をカートに入れてください", "loader": "bar", "time": 1500 },
    { "taskHTML": "<strong>プリン</strong>と<strong>緑茶</strong>をカートに入れてください", "loader": "skeleton", "time": 5000 },
    { "taskHTML": "<strong>ピーマン</strong>と<strong>ポテトチップス</strong>をカートに入れてください", "loader": "spinner-color", "time": 3000 },
    { "taskHTML": "<strong>キウイ</strong>と<strong>なす</strong>をカートに入れてください", "loader": "skeleton-color", "time": 1500 },
    { "taskHTML": "<strong>チョコレート</strong>と<strong>にんじん</strong>をカートに入れてください", "loader": "spinner", "time": 5000 },
    { "taskHTML": "<strong>チーズケーキ</strong>と<strong>緑茶</strong>をカートに入れてください", "loader": "skeleton-color", "time": 3000 },
    { "taskHTML": "<strong>オレンジ</strong>と<strong>アイスクリーム</strong>をカートに入れてください", "loader": "skeleton", "time": 1500 },
    { "taskHTML": "<strong>りんご</strong>と<strong>ケーキ</strong>をカートに入れてください", "loader": "spinner-color", "time": 5000 },
    { "taskHTML": "<strong>トマト</strong>と<strong>いちご</strong>をカートに入れてください", "loader": "spinner-color", "time": 1500 },
    { "taskHTML": "<strong>バナナ</strong>と<strong>チョコレート</strong>をカートに入れてください", "loader": "bar-color", "time": 3000 },
    { "taskHTML": "<strong>パイナップル</strong>と<strong>ほうれん草</strong>をカートに入れてください", "loader": "skeleton", "time": 3000 }
]
"""
EXPERIMENT_TRIALS = json.loads(EXPERIMENT_TRIALS_JSON)

def analyze_survey_data(filepath):
    try:
        df_raw = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません - {filepath}")
        return
    except Exception as e:
        print(f"エラー: ファイルの読み込み中に問題が発生しました - {e}")
        return

    tidy_data = []
    for index, row in df_raw.iterrows():
        participant_name = row.iloc[1]
        for i in range(21):
            trial_info = EXPERIMENT_TRIALS[i]
            perceived_time_col = 3 + (i * 2)
            satisfaction_col = 4 + (i * 2)

            if satisfaction_col < len(row):
                tidy_data.append({
                    'participant': participant_name,
                    'trial': i + 1,
                    'loaderType': trial_info['loader'],
                    'simulatedLoadingTime': trial_info['time'],
                    'perceivedLoadingTime': row.iloc[perceived_time_col],
                    'satisfaction': row.iloc[satisfaction_col]
                })

    df = pd.DataFrame(tidy_data)

    satisfaction_mapping = {'不満': 1, 'やや不満': 2, 'どちらでもない': 3, 'やや満足': 4, '満足': 5}
    df['satisfaction_score'] = df['satisfaction'].map(satisfaction_mapping)

    df['perceivedLoadingTime'] = pd.to_numeric(df['perceivedLoadingTime'], errors='coerce')
    df['simulatedLoadingTime'] = df['simulatedLoadingTime'] / 1000

    df.dropna(subset=['perceivedLoadingTime', 'satisfaction_score'], inplace=True)

    print("--- 整形後のデータ (最初の5行) ---")
    print(df.head())
    print("\n" + "="*50 + "\n")

    print("--- ローダーの種類ごとの平均値 ---")
    grouped_stats = df.groupby('loaderType')[['perceivedLoadingTime', 'satisfaction_score']].mean()
    print(grouped_stats)
    print("\n" + "="*50 + "\n")

    # --- 5. 仮説検定 (ANOVA & Tukey's HSD) ---
    print("--- 仮説検定: 分散分析 (ANOVA) ---")
    
    # 満足度スコアのANOVA検定
    satisfaction_groups = [df[df['loaderType'] == loader]['satisfaction_score'] for loader in df['loaderType'].unique()]
    f_val_sat, p_val_sat = stats.f_oneway(*satisfaction_groups)
    print(f"満足度スコアの分散分析: F値 = {f_val_sat:.4f}, p値 = {p_val_sat:.4f}")

    # 体感読み込み時間のANOVA検定
    time_groups = [df[df['loaderType'] == loader]['perceivedLoadingTime'] for loader in df['loaderType'].unique()]
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


    # --- 6. 可視化 ---
    output_dir = 'survey_analysis_results'
    os.makedirs(output_dir, exist_ok=True)
    print(f"グラフは '{output_dir}' フォルダに保存されます。")

    sns.set_theme(style="whitegrid", font='Yu Gothic')

    plt.figure(figsize=(12, 7))
    sns.boxplot(data=df, x='loaderType', y='satisfaction_score', palette='viridis')
    plt.title('ローダーの種類別 満足度スコア', fontsize=16)
    plt.xlabel('ローダーの種類', fontsize=12)
    plt.ylabel('満足度スコア (1:不満 〜 5:満足)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'satisfaction_by_loader.png'))
    plt.close()

    plt.figure(figsize=(12, 7))
    sns.boxplot(data=df, x='loaderType', y='perceivedLoadingTime', palette='viridis')
    plt.title('ローダーの種類別 体感読み込み時間', fontsize=16)
    plt.xlabel('ローダーの種類', fontsize=12)
    plt.ylabel('体感読み込み時間 (秒)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'perceived_time_by_loader.png'))
    plt.close()

    plt.figure(figsize=(12, 7))
    sns.scatterplot(data=df, x='simulatedLoadingTime', y='perceivedLoadingTime', hue='loaderType', palette='viridis', s=100, alpha=0.7)
    max_val = max(df['simulatedLoadingTime'].max(), df['perceivedLoadingTime'].max())
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
    parser = argparse.ArgumentParser(description='Googleフォームのアンケート結果(CSV)を分析します。')
    parser.add_argument('filepath', type=str, help='分析するCSVファイルのパス (例: 無題のフォーム.csv)')

    args = parser.parse_args()

    analyze_survey_data(args.filepath)