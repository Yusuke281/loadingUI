

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os
import json
import scipy.stats as stats

# survey_analysis.pyからコピーした実験試行データ
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

def create_color_group(df):
    """
    'loaderType'に基づいて'colorGroup'列を作成する関数。
    'none'ローダーは除外する。
    """
    # 'none'ローダーを除外
    df_filtered = df[df['loaderType'] != 'none'].copy()

    # 色の有無を判定する関数
    def assign_color_group(loader_type):
        if 'color' in loader_type:
            return 'Color'
        else:
            return 'No Color'

    df_filtered['colorGroup'] = df_filtered['loaderType'].apply(assign_color_group)
    return df_filtered

def analyze_data(behavior_path, survey_path):
    """
    行動データとアンケートデータを読み込み、「色あり」vs「色なし」で分析する。
    """
    # --- 1. データの読み込みと前処理 ---
    try:
        df_behavior = pd.read_csv(behavior_path)
        df_survey_raw = pd.read_csv(survey_path)
    except FileNotFoundError as e:
        print(f"エラー: ファイルが見つかりません - {e.filename}")
        return
    except Exception as e:
        print(f"エラー: ファイルの読み込み中に問題が発生しました - {e}")
        return

    # --- 行動データの処理 ---
    df_behavior['pureTaskDuration'] = (df_behavior['taskDuration'] - df_behavior['simulatedLoadingTime']).clip(lower=0)
    behavior_metrics = ['taskDuration', 'pureTaskDuration', 'mouseDistance', 'rageClicks']
    
    # --- アンケートデータの処理 ---
    tidy_data = []
    for index, row in df_survey_raw.iterrows():
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
                    'perceivedLoadingTime': row.iloc[perceived_time_col],
                    'satisfaction': row.iloc[satisfaction_col]
                })
    df_survey = pd.DataFrame(tidy_data)
    satisfaction_mapping = {'不満': 1, 'やや不満': 2, 'どちらでもない': 3, 'やや満足': 4, '満足': 5}
    df_survey['satisfaction_score'] = df_survey['satisfaction'].map(satisfaction_mapping)
    df_survey['perceivedLoadingTime'] = pd.to_numeric(df_survey['perceivedLoadingTime'], errors='coerce')
    df_survey.dropna(subset=['perceivedLoadingTime', 'satisfaction_score'], inplace=True)
    survey_metrics = ['perceivedLoadingTime', 'satisfaction_score']

    # --- データのマージ ---
    # trial番号をキーにして、行動データとアンケートデータをマージ
    df_merged = pd.merge(df_behavior, df_survey, on='trial', suffixes=('_beh', '_sur'))
    
    # loaderTypeが一致していることを確認（念のため）
    df_merged = df_merged[df_merged['loaderType_beh'] == df_merged['loaderType_sur']]
    df_merged.rename(columns={'loaderType_beh': 'loaderType'}, inplace=True)


    # --- 色グループの作成 ---
    df_analysis = create_color_group(df_merged)
    
    all_metrics = behavior_metrics + survey_metrics

    print("--- 「色あり」vs「色なし」グループの基本統計量 ---")
    print(df_analysis.groupby('colorGroup')[all_metrics].describe())
    print("\n" + "="*50 + "\n")

    # --- 2. 仮説検定 (t検定) ---
    print("--- 仮説検定: t検定 (Color vs No Color) ---")
    color_group = df_analysis[df_analysis['colorGroup'] == 'Color']
    no_color_group = df_analysis[df_analysis['colorGroup'] == 'No Color']

    for metric in all_metrics:
        # Welch's t-test (不等分散を仮定)
        t_stat, p_val = stats.ttest_ind(color_group[metric], no_color_group[metric], equal_var=False, nan_policy='omit')
        print(f"{metric}: t値 = {t_stat:.4f}, p値 = {p_val:.4f}")
        if p_val < 0.05:
            print(f"  -> 統計的に有意な差が見られます。")
    print("\n" + "="*50 + "\n")

    # --- 3. 可視化 ---
    output_dir = 'color_analysis_results'
    os.makedirs(output_dir, exist_ok=True)
    print(f"グラフは '{output_dir}' フォルダに保存されます。")

    sns.set_theme(style="whitegrid", font='Yu Gothic')
    
    plot_configs = {
        'taskDuration': {'title': '「色あり/なし」別 タスク時間', 'ylabel': 'タスク時間 (ms)'},
        'pureTaskDuration': {'title': '「色あり/なし」別 純粋なタスク時間', 'ylabel': '純粋なタスク時間 (ms)'},
        'mouseDistance': {'title': '「色あり/なし」別 マウス移動距離', 'ylabel': 'マウス移動距離 (pixels)'},
        'rageClicks': {'title': '「色あり/なし」別 平均レイジクリック数', 'ylabel': '平均レイジクリック数', 'plot_type': 'bar'},
        'perceivedLoadingTime': {'title': '「色あり/なし」別 体感読み込み時間', 'ylabel': '体感読み込み時間 (秒)'},
        'satisfaction_score': {'title': '「色あり/なし」別 満足度スコア', 'ylabel': '満足度スコア (1-5)'}
    }

    for metric, config in plot_configs.items():
        plt.figure(figsize=(8, 6))
        
        if config.get('plot_type') == 'bar':
            # Bar plot for mean values like rage clicks
            sns.barplot(data=df_analysis, x='colorGroup', y=metric, palette='viridis', order=['No Color', 'Color'])
        else:
            # Box plot for distribution
            sns.boxplot(data=df_analysis, x='colorGroup', y=metric, palette='viridis', order=['No Color', 'Color'])
            
        plt.title(config['title'], fontsize=16)
        plt.xlabel('ローダーのグループ', fontsize=12)
        plt.ylabel(config['ylabel'], fontsize=12)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{metric}_by_color_group.png'))
        plt.close()

    print("\n分析が完了しました。")
    print(f"実行方法: python {os.path.basename(__file__)} task_timings.csv 無題のフォーム.csv")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='行動データとアンケートデータを「色あり」vs「色なし」で分析します。')
    parser.add_argument('behavior_path', type=str, help='分析する行動データCSVのパス (例: task_timings.csv)')
    parser.add_argument('survey_path', type=str, help='分析するアンケートCSVのパス (例: 無題のフォーム.csv)')
    
    args = parser.parse_args()
    
    analyze_data(args.behavior_path, args.survey_path)
